# wraplint

A linter for line-wrapping problems in plain text and markdown files.

Text files that get edited by hand over a long time tend to accumulate
wrapping problems that don't show up until someone opens the file in a
narrower terminal, pipes it through a diff tool, or pastes it somewhere
that doesn't soft-wrap: lines that run past a sane width, trailing
whitespace left over from an edit, tabs mixed in with spaces that make the
"width" of a line depend on the reader's tab setting. None of this is
caught by a normal code linter, because it isn't code.

wraplint reads one or more files (or stdin) and reports each problem with
a file name, line number, and column, the same way a compiler warning
would.

## Usage

Check a file:

```
$ wraplint notes.txt
notes.txt:12:80: WL001 line exceeds 79 characters (94)
notes.txt:12:82: WL002 trailing whitespace
notes.txt:30:1: WL003 tab character makes wrap width ambiguous
```

Check multiple files, with a custom width:

```
$ wraplint --max-length 72 README.md CHANGELOG.md
```

Read from stdin (the default when no files are given, or pass `-`
explicitly):

```
$ cat notes.txt | wraplint
$ pbpaste | wraplint -
```

The exit code is 0 if no problems were found, 1 otherwise, so it's usable
as a pre-commit check or in CI:

```
$ wraplint docs/*.md || echo "wrapping problems found"
```

## Checks

| code  | meaning                                              |
|-------|-------------------------------------------------------|
| WL001 | line is longer than the configured max (default 79)  |
| WL002 | line has trailing whitespace                          |
| WL003 | line contains a tab character                         |
| WL004 | line in a hand-wrapped paragraph falls short of the paragraph's wrap width |

## Install

No dependencies beyond the standard library. Run it straight from a
checkout:

```
$ python -m wraplint.cli notes.txt
```

or install it locally with `pip install -e .` to get the `wraplint`
command on your PATH.

## Status

Early. The checks above cover the mechanical problems (length, whitespace,
tabs) and the first heuristic one (ragged hand-wrapping). Rewrapping with
`--fix`, markdown-aware code block and URL handling, and per-line ignores
are still to come.
