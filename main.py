import fileinput
from tokens import Section, Indent, Commit, Symlink

# TODO
# - links

def main():
    parsed_file = [parse_line(line) for line in fileinput.input()]

    # for line in parsed_file:
    #     print(' ' * 2 * len(line), line)

    # First pass: Find symlinked commits
    symlinked = set()
    for line in parsed_file:
        for token in line:
            if is_symlink(token):
                symlinked.add(token.commithash)

    # Second pass: Format output
    for line in parsed_file:
        is_indented = False
        for token in line:
            if is_indent(token):
                is_indented = True
            elif is_section(token):
                print_section(token)
            elif is_commit(token):
                is_symlinked = token.hash in symlinked
                print_commit(token, is_indented, is_symlinked)
            elif is_symlink(token):
                print_symlink(token, is_indented)
            else:
                raise ValueError

def print_section(token):
    name = token.name
    print('\n**{}**'.format(name))

def print_commit(token, is_indented, is_symlinked):
    print_bullet(is_indented)
    if is_symlinked:
        print('~', end='')
    print(token.hash, token.message, end='')
    if is_symlinked:
        print('~', end='')
    print()

def print_symlink(token, is_indented):
    print_bullet(is_indented)
    print(token.commithash)

def print_bullet(is_indented):
    if is_indented:
        print('* ', end='')
    else:
        print('\n• ', end='')

def parse_line(line):
    line = line.rstrip()
    if line == '':  # may not be needed
        return []
    elif line.startswith('  '):
        return [Indent()] + parse_line(line[2:])
    elif line.startswith('* '):
        return [Section(line[2:])]
    elif line.startswith('# @ '):
        return [Symlink(line[4:])]
    elif line.startswith('# '):
        hash, message = line[2:].split(maxsplit=1)
        return [Commit(hash, message)]
    else:
        raise ValueError

def is_symlink(token):
    return type(token).__name__ == 'Symlink'

def is_commit(token):
    return type(token).__name__ == 'Commit'

def is_indent(token):
    return type(token).__name__ == 'Indent'

def is_section(token):
    return type(token).__name__ == 'Section'

if __name__ == '__main__':
    main()
