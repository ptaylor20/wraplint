"""Individual line-based checks used by the linter.

Each check takes the raw lines of a file (as returned by readlines(), so
each entry still has its trailing newline) and returns a list of Finding
objects. Line and column numbers are 1-based, matching how editors and
compilers report positions.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    line: int
    column: int
    code: str
    message: str


def _strip_newline(line):
    return line.rstrip("\n").rstrip("\r")


def check_line_length(lines, max_length):
    findings = []
    for i, raw in enumerate(lines, start=1):
        text = _strip_newline(raw)
        if len(text) > max_length:
            findings.append(
                Finding(
                    i,
                    max_length + 1,
                    "WL001",
                    f"line exceeds {max_length} characters ({len(text)})",
                )
            )
    return findings


def check_trailing_whitespace(lines):
    findings = []
    for i, raw in enumerate(lines, start=1):
        text = _strip_newline(raw)
        stripped = text.rstrip(" \t")
        if stripped != text:
            findings.append(
                Finding(i, len(stripped) + 1, "WL002", "trailing whitespace")
            )
    return findings


def check_tabs(lines):
    # A tab renders at whatever width the terminal or editor picks, so any
    # line-length or wrap-column check downstream of this one is only
    # trustworthy once tabs are gone.
    findings = []
    for i, raw in enumerate(lines, start=1):
        text = _strip_newline(raw)
        col = text.find("\t")
        if col != -1:
            findings.append(
                Finding(i, col + 1, "WL003", "tab character makes wrap width ambiguous")
            )
    return findings


def run_checks(lines, max_length=79):
    findings = []
    findings.extend(check_line_length(lines, max_length))
    findings.extend(check_trailing_whitespace(lines))
    findings.extend(check_tabs(lines))
    findings.sort(key=lambda f: (f.line, f.column))
    return findings
