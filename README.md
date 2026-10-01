# todo-cli

A simple command-line to-do list manager. Pure Python standard library — no dependencies to
install to run it.

## Usage

```bash
python todo.py add "buy milk"
python todo.py add "walk the dog"
python todo.py list
#  1. [ ] buy milk
#  2. [ ] walk the dog

python todo.py done 1
python todo.py list
#  1. [x] buy milk
#  2. [ ] walk the dog

python todo.py rm 2
```

Tasks are stored in `~/.todo-cli.json` by default; pass `--file path/to/file.json` to use a
different store (handy for keeping separate lists per project).

## Running the tests

```bash
pip install pytest
pytest tests/ -q
```
