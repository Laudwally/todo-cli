#!/usr/bin/env python3
"""A simple command-line to-do list manager. Stores tasks in a local JSON file."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_STORE_PATH = Path.home() / ".todo-cli.json"


@dataclass
class Task:
    text: str
    done: bool = False

    def to_dict(self) -> dict:
        return {"text": self.text, "done": self.done}

    @staticmethod
    def from_dict(data: dict) -> "Task":
        return Task(text=data["text"], done=data.get("done", False))


@dataclass
class TodoList:
    tasks: list[Task] = field(default_factory=list)

    def add(self, text: str) -> Task:
        task = Task(text=text)
        self.tasks.append(task)
        return task

    def complete(self, index: int) -> Task:
        task = self._get(index)
        task.done = True
        return task

    def remove(self, index: int) -> Task:
        task = self._get(index)
        self.tasks.pop(index - 1)
        return task

    def _get(self, index: int) -> Task:
        if index < 1 or index > len(self.tasks):
            raise IndexError(f"No task #{index}. You have {len(self.tasks)} task(s).")
        return self.tasks[index - 1]

    def to_dict(self) -> dict:
        return {"tasks": [t.to_dict() for t in self.tasks]}

    @staticmethod
    def from_dict(data: dict) -> "TodoList":
        return TodoList(tasks=[Task.from_dict(t) for t in data.get("tasks", [])])


def load(path: Path) -> TodoList:
    if not path.exists():
        return TodoList()
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return TodoList()
    return TodoList.from_dict(json.loads(content))


def save(todo_list: TodoList, path: Path) -> None:
    path.write_text(json.dumps(todo_list.to_dict(), indent=2), encoding="utf-8")


def format_list(todo_list: TodoList) -> str:
    if not todo_list.tasks:
        return "No tasks yet. Add one with: todo add \"buy milk\""
    lines = []
    for i, task in enumerate(todo_list.tasks, start=1):
        box = "[x]" if task.done else "[ ]"
        lines.append(f"{i:>2}. {box} {task.text}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo", description="A simple command-line to-do list.")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_STORE_PATH,
        help=f"Path to the JSON store (default: {DEFAULT_STORE_PATH})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="Show all tasks")

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("text", help="Task description")

    done_parser = subparsers.add_parser("done", help="Mark a task as complete")
    done_parser.add_argument("index", type=int, help="Task number (from `todo list`)")

    rm_parser = subparsers.add_parser("rm", help="Remove a task")
    rm_parser.add_argument("index", type=int, help="Task number (from `todo list`)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    todo_list = load(args.file)

    try:
        if args.command == "list":
            print(format_list(todo_list))
            return 0

        if args.command == "add":
            task = todo_list.add(args.text)
            save(todo_list, args.file)
            print(f"Added: {task.text}")
            return 0

        if args.command == "done":
            task = todo_list.complete(args.index)
            save(todo_list, args.file)
            print(f"Completed: {task.text}")
            return 0

        if args.command == "rm":
            task = todo_list.remove(args.index)
            save(todo_list, args.file)
            print(f"Removed: {task.text}")
            return 0

    except IndexError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
