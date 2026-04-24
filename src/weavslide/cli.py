"""weavslide CLI"""

import argparse
import sys
from pathlib import Path

from weavslide import __version__
from weavslide.parser import parse_slide_file


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate .slide.html files."""
    files = args.files
    if not files:
        files = sorted(Path.cwd().glob("*.slide.html"))
        if not files:
            print("没有找到 .slide.html 文件", file=sys.stderr)
            sys.exit(0)

    total = 0
    valid = 0

    for filepath in files:
        if isinstance(filepath, str):
            filepath = Path(filepath)

        total += 1
        result = parse_slide_file(filepath)

        if result.is_valid:
            valid += 1
        else:
            print(f"\n{filepath}", file=sys.stderr)
            for err in result.errors:
                line_info = f"第 {err.line} 行" if err.line else "文件"
                print(f"  {line_info}: {err.message}", file=sys.stderr)

    invalid = total - valid
    if invalid == 0:
        print(f"\n全部 {total} 个文件验证通过", file=sys.stderr)
        sys.exit(0)
    else:
        print(
            f"\n共 {total} 个文件，{valid} 个有效，{invalid} 个无效",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_build(args: argparse.Namespace) -> None:
    print("build: not implemented yet")


def main() -> None:
    """weavslide - 自动生成讲座展示和 AI 配音的工具"""
    parser = argparse.ArgumentParser(
        prog="weavslide",
        description="自动生成讲座展示和 AI 配音的工具",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="验证输入文件")
    validate_parser.add_argument(
        "files",
        nargs="*",
        help="要验证的 .slide.html 文件（不指定则扫描当前目录）",
    )
    validate_parser.set_defaults(func=cmd_validate)

    build_parser = subparsers.add_parser("build", help="构建讲座展示")
    build_parser.set_defaults(func=cmd_build)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
