"""weavslide CLI"""

import argparse
import sys
from importlib.resources import files as _resource_files
from pathlib import Path

import jinja2

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

        relpath = filepath.relative_to(Path.cwd())
        print(f"{relpath} ... {'通过' if result.is_valid else '失败'}", file=sys.stderr)

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


def _load_template(args: argparse.Namespace) -> jinja2.Template:
    """Load template from --template argument, or fall back to the built-in template.j2."""
    if args.template:
        source = Path(args.template).read_text(encoding="utf-8")
    else:
        source = (
            _resource_files("weavslide")
            .joinpath("template.j2")
            .read_text(encoding="utf-8")
        )
    return jinja2.Environment(autoescape=False).from_string(source)


def cmd_build(args: argparse.Namespace) -> None:
    """Assemble all .slide.html files into slides.html."""

    files = args.files
    if not files:
        files = sorted(Path.cwd().glob("*.slide.html"))
        if not files:
            print("没有找到 .slide.html 文件", file=sys.stderr)
            sys.exit(0)

    slides: list[dict] = []
    for filepath in files:
        if isinstance(filepath, str):
            filepath = Path(filepath)
        result = parse_slide_file(filepath)
        if not result.is_valid:
            print(f"跳过无效文件: {filepath.relative_to(Path.cwd())}", file=sys.stderr)
            continue
        slides.append({"content": result.slide_html, "number": len(slides) + 1})

    if not slides:
        print("没有有效的 slide 内容", file=sys.stderr)
        sys.exit(1)

    template = _load_template(args)
    html = template.render(title="Slides", slides=slides)

    output = Path.cwd() / args.output
    output.write_text(html, encoding="utf-8")
    print(f"已生成 {output} ({len(slides)} 页)", file=sys.stderr)


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
    build_parser.add_argument(
        "files",
        nargs="*",
        help="要构建的 .slide.html 文件（不指定则扫描当前目录）",
    )
    build_parser.add_argument(
        "-o",
        "--output",
        default="slides.html",
        help="输出文件路径（默认 slides.html）",
    )
    build_parser.add_argument(
        "--template",
        default=None,
        help="自定义 Jinja2 模板文件路径（默认使用内置 template.j2）",
    )
    build_parser.set_defaults(func=cmd_build)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
