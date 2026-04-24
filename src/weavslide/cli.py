"""weavslide CLI"""

import argparse
import sys

from weavslide import __version__


def cmd_validate(args: argparse.Namespace) -> None:
    print("validate: not implemented yet")


def cmd_build(args: argparse.Namespace) -> None:
    print("build: not implemented yet")


def main() -> None:
    """weavslide - 自动生成讲桌展示和 AI 配音的工具"""
    parser = argparse.ArgumentParser(
        prog="weavslide",
        description="自动生成讲桌展示和 AI 配音的工具",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="验证输入文件")
    validate_parser.set_defaults(func=cmd_validate)

    build_parser = subparsers.add_parser("build", help="构建讲桌展示")
    build_parser.set_defaults(func=cmd_build)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
