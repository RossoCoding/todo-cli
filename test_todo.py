import json
import unittest
import tempfile
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

    def test_add(self):
        todo.cmd_add(Namespace(title="테스트 항목"))
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["title"], "테스트 항목")
        self.assertFalse(todos[0]["done"])
        self.assertEqual(todos[0]["id"], 1)

    def test_add_multiple_ids(self):
        todo.cmd_add(Namespace(title="첫 번째"))
        todo.cmd_add(Namespace(title="두 번째"))
        todo.cmd_add(Namespace(title="세 번째"))
        todos = todo.load_todos()
        self.assertEqual([t["id"] for t in todos], [1, 2, 3])

    def test_done(self):
        todo.cmd_add(Namespace(title="완료할 항목"))
        todo.cmd_done(Namespace(id=1))
        todos = todo.load_todos()
        self.assertTrue(todos[0]["done"])

    def test_done_invalid_id(self, ):
        todo.cmd_add(Namespace(title="항목"))
        todo.cmd_done(Namespace(id=999))
        todos = todo.load_todos()
        self.assertFalse(todos[0]["done"])

    def test_delete(self):
        todo.cmd_add(Namespace(title="삭제할 항목"))
        todo.cmd_add(Namespace(title="남길 항목"))
        todo.cmd_delete(Namespace(id=1))
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["title"], "남길 항목")

    def test_delete_invalid_id(self):
        todo.cmd_add(Namespace(title="항목"))
        todo.cmd_delete(Namespace(id=999))
        todos = todo.load_todos()
        self.assertEqual(len(todos), 1)

    def test_filter_done(self):
        todo.cmd_add(Namespace(title="미완료"))
        todo.cmd_add(Namespace(title="완료"))
        todo.cmd_done(Namespace(id=2))
        todos = todo.load_todos()
        done = [t for t in todos if t["done"]]
        undone = [t for t in todos if not t["done"]]
        self.assertEqual(len(done), 1)
        self.assertEqual(done[0]["title"], "완료")
        self.assertEqual(len(undone), 1)
        self.assertEqual(undone[0]["title"], "미완료")

    def test_empty_list(self):
        todos = todo.load_todos()
        self.assertEqual(todos, [])


if __name__ == "__main__":
    unittest.main()
