import fileinput
from tokens import Section, Indent, Commit, Symlink, PRLink, HorizRule
import sys

# TODO
# - links
# - maybe use OOP to avoid passing many args
# - maybe require a commit to be marked in order to be symlinked (good
# for maintainability)
# - a tool for checking if you're up-to-date with all commits
# - give line number on error

VERBOSE_ERRORS = True

def main():
    # Parse
    parsed_file = []
    for i, line in enumerate(fileinput.input(), 1):
        try:
            parsed_file.append(parse_line(line))
        except Exception as e:
            fail(i, e, 'parsing')

    # for line in parsed_file:
    #     print(' ' * 2 * len(line), line)

    # First pass: Find symlinked commits and PR link
    symlinked = set()
    pr_url = None
    for i, line in enumerate(parsed_file, 1):
        try:
            for token in line:
                if is_symlink(token):
                    symlinked.add(token.commithash)
                if is_prlink(token):
                    pr_url = token.url
        except Exception as e:
            fail(i, e, 'first pass')

    # Second pass: Format output
    print_header()
    prev_line_was_indented = False
    for i, line in enumerate(parsed_file, 1):
        try:
            is_indented = False

            # Check indentation so we can add newline after an indented block
            if is_indent(line[0]):
                prev_line_was_indented = True
            else:
                if prev_line_was_indented:
                    print()
                prev_line_was_indented = False

            for token in line:
                if is_indent(token):
                    is_indented = True
                elif is_section(token):
                    print_section(token)
                elif is_commit(token):
                    is_symlinked = token.hash in symlinked
                    print_commit(token, is_indented, is_symlinked, pr_url)
                elif is_symlink(token):
                    print_symlink(token, is_indented, pr_url)
                elif is_prlink(token):
                    pass
                elif is_horizrule(token):
                    print_horizrule()
                else:
                    raise ValueError
        except Exception as e:
            fail(i, e, 'second pass')

def fail(lineno, exc, stage):
    print('\nError on line', lineno, 'during', stage, file=sys.stderr)
    if VERBOSE_ERRORS:
        print()
        raise exc
    exit(1)

header = """## Logical commit groups

(Is this helpful? This is generated by a script, by the way.)

Asterisks: These commits are logically grouped below but mostly in
commit order. Some commits were were hard to reorder (rebase conflicts) so I
put asterisks where I moved commits out of their actual git commit order (but
left them in order as well, ~struck through~.)
"""
def print_header():
    print(header)

def print_section(token):
    name = token.name
    print('\n**{}**'.format(name))

def print_commit(token, is_indented, is_symlinked, pr_url):
    print_bullet(is_indented)
    if is_symlinked:
        print('~', end='')
    print_link_start(pr_url, token.hash)
    print(token.hash, token.message, end='')
    print_link_end(pr_url, token.hash)
    if is_symlinked:
        print('~', end='')
    print()

def print_link_start(pr_url, commithash):
    if pr_url:
        print('[', end='')

def print_link_end(pr_url, commithash):
    if pr_url:
        print(']({}/commits/{})'.format(pr_url, commithash), end='')

def print_symlink(token, is_indented, pr_url):
    print_bullet(is_indented)
    print_link_start(pr_url, token.commithash)
    print(token.commithash + '\*', end='')
    print_link_end(pr_url, token.commithash)
    print()

def print_bullet(is_indented):
    if is_indented:
        print('* ', end='')
    else:
        print('• ', end='')

def print_horizrule():
    print('----')

def parse_line(line):
    line = line.rstrip()
    if line == '':  # may not be needed
        return []
    elif line == '----':
        return [HorizRule()]
    elif line.startswith('  '):
        return [Indent()] + parse_line(line[2:])
    elif line.startswith('* '):
        return [Section(line[2:])]
    elif line.startswith('# @ '):
        return [Symlink(line[4:])]
    elif line.startswith('# '):
        hash, message = line[2:].split(maxsplit=1)
        return [Commit(hash, message)]
    elif line.startswith('! '):
        key, value = line[2:].split(maxsplit=1)
        if key == 'PR':
            return [PRLink(value)]
        else:
            raise ValueError
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

def is_prlink(token):
    return type(token).__name__ == 'PRLink'

def is_horizrule(token):
    return type(token).__name__ == 'HorizRule'

if __name__ == '__main__':
    main()
