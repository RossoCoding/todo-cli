import json
import sys
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_FILE = Path(__file__).parent / "data" / "todos.json"


def load_todos():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def next_id(todos):
    return max((t["id"] for t in todos), default=0) + 1


def cmd_add(args):
    todos = load_todos()
    task = {"id": next_id(todos), "title": args.title, "done": False}
    todos.append(task)
    save_todos(todos)
    print(f"[추가] #{task['id']} {task['title']}")


def cmd_list(args):
    todos = load_todos()
    if args.filter == "done":
        todos = [t for t in todos if t["done"]]
    elif args.filter == "undone":
        todos = [t for t in todos if not t["done"]]
    if not todos:
        print("할 일이 없습니다.")
        return
    for t in todos:
        status = "x" if t["done"] else " "
        print(f"  [{status}] #{t['id']} {t['title']}")


def cmd_done(args):
    todos = load_todos()
    for t in todos:
        if t["id"] == args.id:
            t["done"] = True
            save_todos(todos)
            print(f"[완료] #{t['id']} {t['title']}")
            return
    print(f"ID {args.id}를 찾을 수 없습니다.")


def cmd_delete(args):
    todos = load_todos()
    remaining = [t for t in todos if t["id"] != args.id]
    if len(remaining) == len(todos):
        print(f"ID {args.id}를 찾을 수 없습니다.")
        return
    save_todos(remaining)
    print(f"[삭제] #{args.id}")


def main():
    parser = argparse.ArgumentParser(description="간단한 CLI Todo 앱")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="할 일 추가")
    p_add.add_argument("title", help="할 일 내용")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="할 일 목록 보기")
    p_list.add_argument("--filter", choices=["done", "undone"], default=None, help="done: 완료된 항목만 / undone: 미완료 항목만")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="완료 처리")
    p_done.add_argument("id", type=int, help="완료할 항목 ID")
    p_done.set_defaults(func=cmd_done)

    p_del = sub.add_parser("delete", help="항목 삭제")
    p_del.add_argument("id", type=int, help="삭제할 항목 ID")
    p_del.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
