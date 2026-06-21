import json
import unittest
import tempfile
from datetime import date, timedelta
from pathlib import Path
from argparse import Namespace
from unittest.mock import patch

import todo


class TodoTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.data_file = Path(self.tmp.name)
        self.data_file.unlink()
        self.patcher = patch.object(todo, "DATA_FILE", self.data_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if self.data_file.exists():
            self.data_file.unlink()

    def _add(self, title, priority="medium", due=None, location=None):
        todo.cmd_add(Namespace(title=title, priority=priority, due=due, location=location))

    def test_add(self):
        self._add("테스트 항목")
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["title"], "테스트 항목")
        self.assertFalse(todos[0]["done"])
        self.assertEqual(todos[0]["id"], 1)
        self.assertEqual(todos[0]["priority"], "medium")

    def test_add_with_due_and_location(self):
        self._add("회의", due="2026-06-25 14:00", location="서울 카페")
        todos = todo.load_todos()
        self.assertEqual(todos[0]["due"], "2026-06-25 14:00")
        self.assertEqual(todos[0]["location"], "서울 카페")

    def test_add_multiple_ids(self):
        self._add("첫 번째")
        self._add("두 번째")
        self._add("세 번째")
        todos = todo.load_todos()
        self.assertEqual([t["id"] for t in todos], [1, 2, 3])

    def test_priority_sort(self):
        self._add("낮음", priority="low")
        self._add("높음", priority="high")
        self._add("중간", priority="medium")
        todos = todo.load_todos()
        sorted_todos = sorted(todos, key=lambda t: todo.PRIORITY_ORDER.get(t.get("priority", "medium"), 1))
        self.assertEqual([t["title"] for t in sorted_todos], ["높음", "중간", "낮음"])

    def test_done(self):
        self._add("완료할 항목")
        todo.cmd_done(Namespace(id=1))
        todos = todo.load_todos()
        self.assertTrue(todos[0]["done"])

    def test_done_invalid_id(self):
        self._add("항목")
        todo.cmd_done(Namespace(id=999))
        todos = todo.load_todos()
        self.assertFalse(todos[0]["done"])

    def test_delete(self):
        self._add("삭제할 항목")
        self._add("남길 항목")
        todo.cmd_delete(Namespace(id=1))
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["title"], "남길 항목")

    def test_delete_invalid_id(self):
        self._add("항목")
        todo.cmd_delete(Namespace(id=999))
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)

    def test_filter_done(self):
        self._add("미완료")
        self._add("완료")
        todo.cmd_done(Namespace(id=2))
        todos = todo.load_todos()
        done = [t for t in todos if t["done"]]
        undone = [t for t in todos if not t["done"]]
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0]["title"], "완료")
        self.assertEqual(len(undone), 1)
        self.assertEqual(undone[0]["title"], "미완료")

    def test_remind_tomorrow(self):
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self._add("내일 마감 항목", due=tomorrow)
        self._add("마감 없는 항목")
        todos = todo.load_todos()
        upcoming = [
            t for t in todos
            if not t.get("done") and todo.parse_due(t.get("due")) == date.today() + timedelta(days=1)
        ]
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0]["title"], "내일 마감 항목")

    def test_remind_excludes_done(self):
        tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self._add("완료된 내일 항목", due=tomorrow)
        todo.cmd_done(Namespace(id=1))
        todos = todo.load_todos()
        upcoming = [
            t for t in todos
            if not t.get("done") and todo.parse_due(t.get("due")) == date.today() + timedelta(days=1)
        ]
        self.assertEqual(len(upcoming), 0)

    def test_empty_list(self):
        todos = todo.load_todos()
        self.assertEqual(todos, [])


if __name__ == "__main__":
    unittest.main()
