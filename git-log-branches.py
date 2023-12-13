#!/usr/bin/env python3

"""
Usage: git-log-branches.py other_branch

Draws an ASCII art picture of two branches side by side, so you can see what commits are on one branch but not the other.
"""

import subprocess
import sys


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    their_branch = sys.argv[1]
    log_diff(their_branch)


def log_diff(their_branch):
    # log their_branch..HEAD. use the format {short_hash} {subject} - {author}
    # don't use more than 60 characters per line
    # truncate author to 20 characters
    fmt = "--pretty=format:%h %<(30,trunc)%s - %<(18,trunc)%an"
    ours = subprocess.check_output(
        ["git", "log", fmt, f"{their_branch}..HEAD"], encoding="utf-8"
    ).splitlines()
    theirs = subprocess.check_output(
        ["git", "log", fmt, f"HEAD..{their_branch}"], encoding="utf-8"
    ).splitlines()
    our_branch = subprocess.check_output(
        ["git", "branch", "--show-current"], encoding="utf-8"
    ).strip()
    merge_base = subprocess.check_output(
        ["git", "merge-base", "HEAD", their_branch], encoding="utf-8"
    ).strip()
    previous_commits = subprocess.check_output(
        ["git", "log", "-n", "10", fmt, merge_base],
        encoding="utf-8",
    ).splitlines()
    format_commits(ours, theirs, previous_commits, our_branch, their_branch)


BL = "└"
BR = "┘"
TL = "┌"
TR = "┐"
H = "─"
V = "│"
SPLIT_B = "┴"
SPLIT_T = "┬"


def boxify(lines, title):
    # assume all lines are the same length
    # get max length
    width = max(len(line) for line in lines)
    top = TL + H * width + TR
    bottom = BL + H * width + BR

    title_centered = title.center(width)
    return (
        [title_centered, top]
        + [V + line + " " * (width - len(line)) + V for line in lines]
        + [bottom]
    )


def replace_pos(s, pos, c):
    return s[:pos] + c + s[pos + 1 :]


def format_commits(ours, theirs, previous_commits, our_branch, their_branch):
    format_string = "{:<62}    {:<62}"
    # zip them together put put whitespace at the beginning in the shorter one
    if len(ours) == 0:
        ours = ["(no commits)"]
    if len(theirs) == 0:
        theirs = ["(no commits)"]
    if len(ours) < len(theirs):
        ours = [""] * (len(theirs) - len(ours)) + ours
    else:
        theirs = [""] * (len(ours) - len(theirs)) + theirs
    ours = boxify(ours, our_branch)
    # replace 30th character of last line   with SPLIT_T
    ours[-1] = replace_pos(ours[-1], 45, SPLIT_T)
    theirs = boxify(theirs, their_branch)
    theirs[-1] = replace_pos(theirs[-1], 7, SPLIT_T)

    for our, their in zip(ours, theirs):
        print(format_string.format(our, their))

    previous_commits.append(".....")
    prev = boxify(previous_commits, "")[1:]
    prev[0] = replace_pos(prev[0], 40, SPLIT_B)
    prev[0] = replace_pos(prev[0], 12, SPLIT_B)
    for line in prev:
        print("{:<33}{}".format("", line))


if __name__ == "__main__":
    main()
