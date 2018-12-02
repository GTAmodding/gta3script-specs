#!/usr/bin/env python3
"""
    This script preprocesses an Asciidoc document, gathering all grammar
    productions and dumping it into a `AUTO_REPLACE_WITH_GRAMMAR` section.
"""
import sys

class GrammarPreprocessor:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    @staticmethod
    def emit_error(block, error):
        print('invalid grammar block: ' + error, file=sys.stderr)
        print(block, file=sys.stderr)
        sys.exit(1)

    @staticmethod
    def is_grammar_block(block):
        first_line = block.split('\n', 1)[0]
        if first_line.startswith('#') and 'informative' in first_line:
            return False
        return ':=' in block

    def validate_grammar(self, block):
        expect_semicolon = False
        for i in range(len(block)):
            if block[i] == ':' and i+1 != len(block) and block[i+1] == '=':
                if expect_semicolon:
                    return self.emit_error(block, 'missing semicolon')
                expect_semicolon = True
            if block[i] == ';':
                if not expect_semicolon:
                    return self.emit_error(block, 'unexpected semicolon')
                expect_semicolon = False
        if expect_semicolon:
            return self.emit_error(block, 'missing semicolon')

    def read_block(self):
        lines = []
        for line in self.reader:
            self.writer.write(line)
            if line.startswith('---'):
                break
            lines.append(line)
        return ''.join(lines)

    def process(self):
        grammar = []
        for line in self.reader:
            if line.startswith('AUTO_REPLACE_WITH_GRAMMAR'):
                self.writer.write('----\n')
                self.writer.write('# The GTA3script Grammar (informative)\n\n')
                self.writer.write('\n'.join(grammar))
                self.writer.write('----\n')
                continue
            self.writer.write(line)
            if line.startswith('---'):
                block = self.read_block()
                if self.is_grammar_block(block):
                    self.validate_grammar(block)
                    grammar.append(block)


if __name__ == '__main__':
    pp = GrammarPreprocessor(sys.stdin, sys.stdout)
    pp.process()
