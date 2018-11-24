#!/usr/bin/env python3
"""
    usage: cat SPECIFICATION.md | python3 grammar.py
"""
import sys


def emit_error(block, msg):
    print('invalid grammar block: ' + msg, file=sys.stderr)
    print(block, file=sys.stderr)
    sys.exit(1)

def validate_grammar(block):
    expect_semicolon = False
    for i in range(len(block)):
        if block[i] == ':' and i+1 != len(block) and block[i+1] == '=':
            if expect_semicolon:
                return emit_error(block, 'missing semicolon')
            expect_semicolon = True
        if block[i] == ';':
            if not expect_semicolon:
                return emit_error(block, 'unexpected semicolon')
            expect_semicolon = False
    if expect_semicolon:
        return emit_error(block, 'missing semicolon')

def process_block(block):
    validate_grammar(block)
    if block.startswith('#') and 'Lexical Grammar' in block:
        return
    print(block)

def make_grammar():
    in_code_blocks = False
    current_block = ""
    for line in sys.stdin:
        if line.startswith('```'):
            if ':=' in current_block:
                process_block(current_block)
            in_code_blocks = not in_code_blocks
            current_block = ""
            continue
        if in_code_blocks:
            current_block += line.rstrip()
            current_block += '\n'

if __name__ == '__main__':
    make_grammar()
