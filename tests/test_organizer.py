import tempfile
import unittest
from datetime import date
from pathlib import Path

from organizer import (
    date_from_filename,
    execute_actions,
    plan_actions,
    sanitize_course_name,
)


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "inbox"
        self.output = self.root / "organized"
        self.source.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sanitize_course_name(self):
        self.assertEqual(sanitize_course_name(" 开源/软件：实践 "), "开源_软件：实践")
        with self.assertRaises(ValueError):
            sanitize_course_name("...")

    def test_date_from_filename(self):
        self.assertEqual(
            date_from_filename(Path("2026-10-31-讲义.pdf")), date(2026, 10, 31)
        )
        self.assertEqual(
            date_from_filename(Path("20261031-讲义.pdf")), date(2026, 10, 31)
        )
        self.assertIsNone(date_from_filename(Path("2026-02-30-讲义.pdf")))

    def test_copy_by_course_and_explicit_date(self):
        source_file = self.source / "第一讲.txt"
        source_file.write_text("实验手册", encoding="utf-8")
        actions = plan_actions(
            self.source, self.output, "开源软件开发与实践", date(2026, 10, 31)
        )
        count = execute_actions(actions)
        destination = self.output / "开源软件开发与实践" / "2026-10-31" / "第一讲.txt"
        self.assertEqual(count, 1)
        self.assertEqual(destination.read_text(encoding="utf-8"), "实验手册")
        self.assertTrue(source_file.exists())

    def test_dry_run_does_not_write(self):
        (self.source / "笔记.txt").write_text("内容", encoding="utf-8")
        actions = plan_actions(self.source, self.output, "课程", date(2026, 10, 31))
        execute_actions(actions, dry_run=True)
        self.assertFalse(self.output.exists())

    def test_duplicate_names_do_not_overwrite(self):
        (self.source / "a").mkdir()
        (self.source / "b").mkdir()
        (self.source / "a" / "笔记.txt").write_text("A", encoding="utf-8")
        (self.source / "b" / "笔记.txt").write_text("B", encoding="utf-8")
        actions = plan_actions(self.source, self.output, "课程", date(2026, 10, 31))
        execute_actions(actions)
        target_dir = self.output / "课程" / "2026-10-31"
        self.assertEqual((target_dir / "笔记.txt").read_text(encoding="utf-8"), "A")
        self.assertEqual((target_dir / "笔记-1.txt").read_text(encoding="utf-8"), "B")

    def test_output_inside_source_is_not_scanned(self):
        (self.source / "资料.txt").write_text("原始", encoding="utf-8")
        nested_output = self.source / "organized"
        actions = plan_actions(self.source, nested_output, "课程", date(2026, 10, 31))
        execute_actions(actions)
        second_actions = plan_actions(
            self.source, nested_output, "课程", date(2026, 10, 31)
        )
        self.assertEqual(len(second_actions), 1)
        self.assertEqual(second_actions[0].source, (self.source / "资料.txt").resolve())


if __name__ == "__main__":
    unittest.main()
