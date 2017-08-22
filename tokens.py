from collections import namedtuple

Section = namedtuple('Section', 'name')
Indent = namedtuple('Indent', '')
Commit = namedtuple('Commit', 'hash message')
Symlink = namedtuple('Symlink', 'commithash')

# Metadata -- if multiple, refactor?
PRLink = namedtuple('PRLink', 'url')
