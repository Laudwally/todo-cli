import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402

from todo import TodoList, format_list, load, main, save  # noqa: E402


def test_add_and_list():
    todo_list = TodoList()
    todo_list.add("buy milk")
    todo_list.add("walk the dog")
    assert [t.text for t in todo_list.tasks] == ["buy milk", "walk the dog"]
    assert all(not t.done for t in todo_list.tasks)


def test_complete_marks_done():
    todo_list = TodoList()
    todo_list.add("buy milk")
    todo_list.complete(1)
    assert todo_list.tasks[0].done is True


def test_remove_deletes_task():
    todo_list = TodoList()
    todo_list.add("buy milk")
    todo_list.add("walk the dog")
    todo_list.remove(1)
    assert [t.text for t in todo_list.tasks] == ["walk the dog"]


def test_invalid_index_raises():
    todo_list = TodoList()
    todo_list.add("buy milk")
    with pytest.raises(IndexError):
        todo_list.complete(5)


def test_format_list_empty():
    assert "No tasks yet" in format_list(TodoList())


def test_format_list_shows_checkbox_state():
    todo_list = TodoList()
    todo_list.add("buy milk")
    todo_list.complete(1)
    todo_list.add("walk the dog")
    text = format_list(todo_list)
    assert "[x] buy milk" in text
    assert "[ ] walk the dog" in text


def test_save_and_load_roundtrip(tmp_path):
    store = tmp_path / "todo.json"
    todo_list = TodoList()
    todo_list.add("buy milk")
    todo_list.complete(1)
    save(todo_list, store)

    reloaded = load(store)
    assert len(reloaded.tasks) == 1
    assert reloaded.tasks[0].text == "buy milk"
    assert reloaded.tasks[0].done is True


def test_load_missing_file_returns_empty_list(tmp_path):
    store = tmp_path / "does-not-exist.json"
    todo_list = load(store)
    assert todo_list.tasks == []


def test_load_empty_existing_file_returns_empty_list(tmp_path):
    store = tmp_path / "empty.json"
    store.write_text("", encoding="utf-8")
    todo_list = load(store)
    assert todo_list.tasks == []


def test_cli_add_then_list(tmp_path, capsys):
    store = tmp_path / "todo.json"
    main(["--file", str(store), "add", "buy milk"])
    capsys.readouterr()

    main(["--file", str(store), "list"])
    out = capsys.readouterr().out
    assert "buy milk" in out


def test_cli_done_on_missing_index_errors(tmp_path, capsys):
    store = tmp_path / "todo.json"
    main(["--file", str(store), "add", "buy milk"])
    capsys.readouterr()

    exit_code = main(["--file", str(store), "done", "9"])
    err = capsys.readouterr().err
    assert exit_code == 1
    assert "No task #9" in err
