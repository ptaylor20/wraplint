"""Individual line-based checks used by the linter.

Each check takes the raw lines of a file (as returned by readlines(), so
each entry still has its trailing newline) and returns a list of Finding
objects. Line and column numbers are 1-based, matching how editors and
compilers report positions.
"""

import textwrap
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


def _paragraphs(lines):
    # Groups consecutive non-blank lines into paragraphs of (line_no, text)
    # pairs, the same way a hand-wrapping editor would treat blank lines as
    # paragraph breaks.
    para = []
    for i, raw in enumerate(lines, start=1):
        text = _strip_newline(raw)
        if text.strip() == "":
            if para:
                yield para
                para = []
        else:
            para.append((i, text))
    if para:
        yield para


def check_ragged_wrap(lines, max_length, threshold=15):
    # A hand-wrapped paragraph keeps every line but its last close to the
    # same width. If one of those interior lines falls well short of that
    # width, it's usually a sign someone edited the line (added or removed
    # a few words) and never reflowed the rest of the paragraph to match.
    findings = []
    for para in _paragraphs(lines):
        if len(para) < 2:
            continue
        body = para[:-1]
        wrap_width = max(len(text) for _, text in body)
        if wrap_width < max_length - threshold:
            continue
        for line_no, text in body:
            if wrap_width - len(text) >= threshold:
                findings.append(
                    Finding(
                        line_no,
                        len(text) + 1,
                        "WL004",
                        f"line wraps at {len(text)} chars, short of the "
                        f"paragraph's {wrap_width}-char wrap width",
                    )
                )
    return findings


def rewrap_lines(lines, max_length):
    # Reflows each blank-line-separated paragraph to max_length, the fix
    # for the ragged-wrap problem WL004 flags: join a paragraph's words
    # back into one stream and let textwrap re-break it, rather than
    # trying to patch individual overlong or short lines in place.
    output = []
    para_words = []

    def flush():
        if not para_words:
            return
        text = " ".join(para_words)
        wrapped = textwrap.wrap(text, width=max_length) or [""]
        output.extend(line + "\n" for line in wrapped)

    for raw in lines:
        text = _strip_newline(raw)
        if text.strip() == "":
            flush()
            para_words = []
            output.append("\n")
        else:
            para_words.extend(text.split())
    flush()
    return output


def run_checks(lines, max_length=79):
    findings = []
    findings.extend(check_line_length(lines, max_length))
    findings.extend(check_trailing_whitespace(lines))
    findings.extend(check_tabs(lines))
    findings.extend(check_ragged_wrap(lines, max_length))
    findings.sort(key=lambda f: (f.line, f.column))
    return findings
