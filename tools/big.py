#!/usr/bin/env python3
import sys

def main():
    i = 0
    f = None
    accum = ""
    prev_line = ""
    for line in sys.stdin:
        if line.startswith('==='):
            assert False
        elif line.startswith('---'):
            line = line.replace('-', '=')
            if f is not None:
                f.close()
            href = ''.join(c for c in prev_line.rstrip('\n').split('\n')[-1] if c.isalnum() or c in (' ', '-', '_'))
            href = href.lower().replace(' ', '-')
            f = open(f'core/{i:02}-{href}.md', 'w')
            if i == 0:
                print(accum, file=f, end='')
            i = i + 1
        elif line.startswith('#'):
            name = line.lstrip('#')
            depth = len(line) - len(name)
            if depth == 1 and 'Regular' in line: # HACK
                pass
            else:
                line = ('#' * (depth-1)) + name
        else:
            line = line

        if f is not None:
            print(prev_line, file=f, end='')

        if f is None:
            prev_line = prev_line + line
        else:
            prev_line = line

    print(prev_line, file=f, end='')
    f.close()


if __name__ == "__main__":
    main()
