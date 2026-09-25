import argparse
import sys

from . import checks


def _read_lines(path):
    if path == "-":
        return sys.stdin.readlines()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def _run_fix(paths, max_length):
    exit_code = 0
    for path in paths:
        try:
            lines = _read_lines(path)
        except OSError as exc:
            print(f"wraplint: {path}: {exc.strerror}", file=sys.stderr)
            exit_code = 1
            continue

        fixed = checks.rewrap_lines(lines, max_length)
        if path == "-":
            sys.stdout.writelines(fixed)
        elif fixed != lines:
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(fixed)
            print(f"wraplint: reformatted {path}")
    return exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="wraplint", description="Check text files for line-wrapping problems."
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=["-"],
        help="files to check, or - for stdin (default: -)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=79,
        help="maximum allowed line length (default: 79)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="rewrap paragraphs to --max-length in place instead of reporting problems",
    )
    args = parser.parse_args(argv)

    if args.fix:
        return _run_fix(args.files, args.max_length)

    had_findings = False
    for path in args.files:
        try:
            lines = _read_lines(path)
        except OSError as exc:
            print(f"wraplint: {path}: {exc.strerror}", file=sys.stderr)
            had_findings = True
            continue

        display_name = "<stdin>" if path == "-" else path
        for finding in checks.run_checks(lines, max_length=args.max_length):
            print(
                f"{display_name}:{finding.line}:{finding.column}: "
                f"{finding.code} {finding.message}"
            )
            had_findings = True

    return 1 if had_findings else 0


if __name__ == "__main__":
    sys.exit(main())
