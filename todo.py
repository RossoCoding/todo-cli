import json
import sys
import argparse
from datetime import date, datetime, timedelta
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


def parse_due(due_str):
    if not due_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(due_str, fmt).date()
        except ValueError:
            continue
    return None


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def cmd_add(args):
    todos = load_todos()
    task = {
        "id": next_id(todos),
        "title": args.title,
        "done": False,
        "priority": args.priority,
        "due": args.due,
        "location": args.location,
    }
    todos.append(task)
    save_todos(todos)
    info = f"[추가] #{task['id']} [{task['priority']}] {task['title']}"
    if task["due"]:
        info += f" (마감: {task['due']})"
    if task["location"]:
        info += f" @ {task['location']}"
    print(info)


def cmd_list(args):
    todos = load_todos()
    if args.filter == "done":
        todos = [t for t in todos if t["done"]]
    elif args.filter == "undone":
        todos = [t for t in todos if not t["done"]]
    if not todos:
        print("할 일이 없습니다.")
        return
    todos = sorted(todos, key=lambda t: PRIORITY_ORDER.get(t.get("priority", "medium"), 1))
    tomorrow = date.today() + timedelta(days=1)
    for t in todos:
        status = "x" if t["done"] else " "
        priority = t.get("priority", "medium")
        line = f"  [{status}] #{t['id']} [{priority}] {t['title']}"
        if t.get("due"):
            line += f" (마감: {t['due']})"
        if t.get("location"):
            line += f" @ {t['location']}"
        due = parse_due(t.get("due"))
        if due and due == tomorrow and not t["done"]:
            line += " *** 내일 마감! ***"
        print(line)


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


def cmd_remind(args):
    todos = load_todos()
    tomorrow = date.today() + timedelta(days=1)
    upcoming = [
        t for t in todos
        if not t.get("done") and parse_due(t.get("due")) == tomorrow
    ]
    if not upcoming:
        print("내일 마감 예정인 항목이 없습니다.")
        return
    print(f"[알림] 내일 마감 예정 항목 {len(upcoming)}개:")
    for t in upcoming:
        line = f"  ! #{t['id']} [{t.get('priority', 'medium')}] {t['title']} (마감: {t['due']})"
        if t.get("location"):
            line += f" @ {t['location']}"
        print(line)


def main():
    parser = argparse.ArgumentParser(description="간단한 CLI Todo 앱")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="할 일 추가")
    p_add.add_argument("title", help="할 일 내용")
    p_add.add_argument("--priority", choices=["high", "medium", "low"], default="medium", help="우선순위 (기본값: medium)")
    p_add.add_argument("--due", default=None, help="마감 일시 (예: 2026-06-25 또는 2026-06-25 14:00)")
    p_add.add_argument("--location", default=None, help="장소")
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

    p_remind = sub.add_parser("remind", help="내일 마감 항목 알림")
    p_remind.set_defaults(func=cmd_remind)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
