#!/usr/bin/env python3
"""
Tests for sorting module: sorting.py
"""

import pytest
from sorting import is_sorted, insertion_sort, merge_sort, quick_sort


def test_is_sorted():
    assert is_sorted([]) is True
    assert is_sorted([1]) is True
    assert is_sorted([1, 2, 3, 4, 5]) is True
    assert is_sorted([1, 3, 2, 4]) is False
    assert is_sorted([5, 4, 3, 2, 1], reverse=True) is True
    assert is_sorted([1, 2, 3], reverse=True) is False
    assert is_sorted(["apple", "banana", "cherry"]) is True
    assert is_sorted(["cherry", "banana", "apple"], reverse=True) is True


def test_insertion_sort():
    assert insertion_sort([]) == []
    assert insertion_sort([42]) == [42]
    assert insertion_sort([5, 2, 9, 1, 5, 6]) == [1, 2, 5, 5, 6, 9]
    assert insertion_sort([5, 2, 9, 1, 5, 6], reverse=True) == [9, 6, 5, 5, 2, 1]
    # Test key function
    words = ["banana", "fig", "apple"]
    assert insertion_sort(words, key=len) == ["fig", "apple", "banana"]


def test_merge_sort():
    assert merge_sort([]) == []
    assert merge_sort([10]) == [10]
    data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    sorted_data = [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
    assert merge_sort(data) == sorted_data
    assert merge_sort(data, reverse=True) == sorted_data[::-1]
    
    # Test key function with dictionaries or objects
    items = [{"val": 3}, {"val": 1}, {"val": 2}]
    sorted_items = [{"val": 1}, {"val": 2}, {"val": 3}]
    assert merge_sort(items, key=lambda x: x["val"]) == sorted_items


def test_quick_sort():
    assert quick_sort([]) == []
    assert quick_sort([7]) == [7]
    data = [38, 27, 43, 3, 9, 82, 10]
    sorted_data = [3, 9, 10, 27, 38, 43, 82]
    assert quick_sort(data) == sorted_data
    assert quick_sort(data, reverse=True) == sorted_data[::-1]

    # Test with duplicate elements and large ranges
    large_data = list(range(100, 0, -1))
    assert quick_sort(large_data) == list(range(1, 101))
    
    # Test key function
    strings = ["zebra", "ant", "cat"]
    assert quick_sort(strings) == ["ant", "cat", "zebra"]
