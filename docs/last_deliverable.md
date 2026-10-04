The LeetCode problem "Maximum Number of Occurrences of a Substring" has been solved.

### Design Decisions
- **Insight**: The problem constraints allow for an optimization. Any substring of length $L$ (where $minSize < L \le maxSize$) that satisfies the `maxLetters` constraint contains a substring of length `minSize` that also satisfies the same constraint. Thus, we only need to count occurrences of substrings with exactly `minSize` length.
- **Implementation**: I utilized a `collections.Counter` to track the frequencies of valid substrings of length `minSize`. The time complexity is $O(n \cdot minSize)$ due to string slicing and set creation, which is efficient for the given constraints.

### Verification
- The solution was implemented in `solution.py`.
- Verified against provided test cases:
    - `"aababcaab", 2, 3, 4` $\rightarrow$ Expected: 2
    - `"aaaa", 1, 3, 3` $\rightarrow$ Expected: 2
- The script successfully executed and passed all assertions.

The code is now ready for submission.