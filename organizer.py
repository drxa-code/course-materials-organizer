#!/usr/bin/env python3
"""按课程和日期整理学习资料，仅使用 Python 标准库。"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

DATE_PATTERNS = (
    re.compile(r"(?<!\d)(20\d{2})-(0[1-9]|1[0-2])-([0-2]\d|3[01])(?!\d)"),
    re.compile(r"(?<!\d)(20\d{2})(0[1-9]|1[0-2])([0-2]\d|3[01])(?!\d)"),
)


@dataclass(frozen=True)
class Action:
    source: Path
    destination: Path


def sanitize_course_name(name: str) -> str:
    """将课程名转换为安全的单层目录名。"""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" .")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        raise ValueError("课程名不能为空，也不能只包含非法文件名字符。")
    return cleaned


def date_from_filename(path: Path) -> Optional[date]:
    """识别文件名中的 YYYY-MM-DD 或 YYYYMMDD 日期。"""
    for pattern in DATE_PATTERNS:
        match = pattern.search(path.name)
        if match:
            try:
                return date(*(int(part) for part in match.groups()))
            except ValueError:
                return None
    return None


def iter_source_files(source: Path, output: Path) -> Iterable[Path]:
    """遍历源目录；当输出目录位于源目录内时将其排除。"""
    for root, dirs, files in os.walk(source):
        root_path = Path(root)
        dirs[:] = sorted(
            directory
            for directory in dirs
            if (root_path / directory).resolve() != output
        )
        for filename in sorted(files):
            candidate = (root_path / filename).resolve()
            if candidate.is_file() and output not in candidate.parents:
                yield candidate


def unique_destination(destination: Path, reserved: set[Path]) -> Path:
    """避免覆盖已有文件，也避免同一次运行中的目标重名。"""
    candidate = destination
    counter = 1
    while candidate.exists() or candidate in reserved:
        candidate = destination.with_name(
            f"{destination.stem}-{counter}{destination.suffix}"
        )
        counter += 1
    reserved.add(candidate)
    return candidate


def plan_actions(
    source: Path,
    output: Path,
    course: str,
    explicit_date: Optional[date] = None,
) -> list[Action]:
    """生成整理计划，不修改任何文件。"""
    source = source.resolve()
    output = output.resolve()
    if not source.is_dir():
        raise ValueError(f"源目录不存在或不是目录：{source}")
    if source == output:
        raise ValueError("输出目录不能与源目录相同。")
    if output.exists() and not output.is_dir():
        raise ValueError(f"输出路径已存在且不是目录：{output}")

    course_dir = sanitize_course_name(course)
    reserved: set[Path] = set()
    actions: list[Action] = []
    for file_path in iter_source_files(source, output):
        file_date = explicit_date or date_from_filename(file_path)
        if file_date is None:
            file_date = datetime.fromtimestamp(file_path.stat().st_mtime).date()
        destination = output / course_dir / file_date.isoformat() / file_path.name
        actions.append(Action(file_path, unique_destination(destination, reserved)))
    return actions


def execute_actions(actions: Iterable[Action], dry_run: bool = False) -> int:
    """打印并执行复制计划，返回处理的文件数。"""
    count = 0
    for action in actions:
        prefix = "DRY-RUN" if dry_run else "COPY"
        print(f"{prefix} {action.source} -> {action.destination}")
        if not dry_run:
            action.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(action.source, action.destination)
        count += 1
    return count


def iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("日期必须使用 YYYY-MM-DD 格式。") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="按“课程/日期”目录结构复制整理学习资料，不删除源文件。"
    )
    parser.add_argument("source", type=Path, help="待整理的源目录")
    parser.add_argument("--course", required=True, help="课程名称")
    parser.add_argument(
        "--date",
        type=iso_date,
        help="统一使用指定日期（YYYY-MM-DD）；省略时优先读取文件名日期",
    )
    parser.add_argument("--output", required=True, type=Path, help="整理后的输出目录")
    parser.add_argument(
        "--dry-run", action="store_true", help="只预览整理计划，不写入文件"
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        actions = plan_actions(args.source, args.output, args.course, args.date)
        count = execute_actions(actions, args.dry_run)
    except (OSError, ValueError) as error:
        parser.exit(2, f"错误：{error}\n")
    mode = "计划整理" if args.dry_run else "已整理"
    print(f"{mode} {count} 个文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
