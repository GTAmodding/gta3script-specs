#!/usr/bin/env python3
"""
    Usage: cat SPECIFICATION.md | python3 toc.py
"""
import sys

class Node:
    def __init__(self, *, name):
        self.name = name
        self.childs = []

    def add_child(self, *, name):
        self.childs.append(Node(name=name))

def lower_right(node, depth):
    assert depth >= 2
    for k in range(depth-2):
        node = node.childs[-1]
    return node

def print_tree(node, depth):
    if depth > 0:
        identation = ' ' * ((depth-1) * 2)
        filename = 'SPECIFICATION.md'
        href = ''.join(c for c in node.name if c.isalnum() or c in (' ', '-', '_'))
        href = href.lower().replace(' ', '-')
        print('{}- [{}]({}#{})'.format(identation, node.name, filename, href))
    for child in node.childs:
        print_tree(child, depth+1)

def main():
    root = Node(name='__root__')
    last_line = None

    # Build the TOC tree
    for line in sys.stdin:
        if line.startswith('==='):
            lower_right(root, 1).add_child(name=last_line)
        elif line.startswith('---'):
            lower_right(root, 2).add_child(name=last_line)
        elif line.startswith('#'):
            name = line.lstrip('#')
            depth = len(line) - len(name)
            lower_right(root, depth).add_child(name=name.strip())
        else:
            last_line = line.strip()

    # Print the TOC
    print('# GTA3script Specification')
    print('')
    print('**Table of Contents**')
    print_tree(root, 0)


if __name__ == "__main__":
    main()
