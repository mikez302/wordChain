#! /usr/bin/env python3

import argparse
import pickle
import random
from collections import deque
from itertools import chain
from multiprocessing import Pool


def load_word_list(filename="/usr/share/dict/words"):
    with open(filename) as word_file:
        return set(word_file.read().splitlines())


def load_word_graph(filename="wordGraph.pickle"):
    with open(filename, "rb") as word_graph_file:
        return pickle.load(word_graph_file)


def save_word_graph(word_graph, filename="wordGraph.pickle"):
    with open(filename, "wb") as word_graph_file:
        pickle.dump(word_graph, word_graph_file)


def get_close_words(word, all_words, all_chars):
    result = set()
    for pos in range(len(word)):
        prefix = word[:pos]
        suffix = word[pos + 1:]
        for char in all_chars:
            test_word = prefix + char + suffix
            if test_word != word and test_word in all_words:
                result.add(test_word)
    return result


def make_word_graph(all_words):
    all_chars = set(chain(*all_words))
    word_list = list(all_words)
    argument_generator = ((w, all_words, all_chars) for w in word_list)
    with Pool() as pool:
        word_sets = pool.starmap(get_close_words, argument_generator)
    return dict(zip(word_list, word_sets))


def make_word_graph_simple(all_words):
    all_chars = set(chain(*all_words))
    return {w: get_close_words(w, all_words, all_chars) for w in all_words}


def find_word_chain(initial, goal, word_graph):
    if len(initial) != len(goal):
        return None
    word_queue = deque([initial])
    predecessors = {}

    while word_queue:
        word = word_queue.popleft()
        for neighbor in word_graph[word]:
            if neighbor not in predecessors:
                word_queue.append(neighbor)
                predecessors[neighbor] = word
                if neighbor == goal:
                    result = [goal]
                    while result[-1] != initial:
                        result.append(predecessors[result[-1]])
                    return list(reversed(result))
    return None


def test(word_graph):
    for word_length in range(3, 8):
        words = [w for w in word_graph if len(w) == word_length]
        for _ in range(3):
            initial, goal = random.sample(words, 2)
            print_word_chain(initial, goal, word_graph)
            print()


def print_word_chain(initial, goal, word_graph):
    print('Finding shortest path from "{}" to "{}"'.format(initial, goal))
    path = find_word_chain(initial, goal, word_graph)
    print(path or 'No path found between "{}" and "{}"'.format(initial, goal))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("initial_word", nargs="?", help="Initial word")
    parser.add_argument("goal_word", nargs="?", help="Goal word")
    args = parser.parse_args()

    if len([x for x in (args.initial_word, args.goal_word) if x is not None]) == 1:
        parser.error("Initial word and goal word must be given together.")

    try:
        word_graph = load_word_graph()
    except FileNotFoundError:
        all_words = load_word_list()
        word_graph = make_word_graph(all_words)
        save_word_graph(word_graph)

    if args.initial_word and args.goal_word:
        print_word_chain(args.initial_word, args.goal_word, word_graph)
    else:
        test(word_graph)
