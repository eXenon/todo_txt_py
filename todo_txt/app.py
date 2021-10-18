from os import remove, environ
from shutil import copyfile
from typing import List

import click

from .task import Task

# Default values
#todo_file = "todo.txt"
backup_file = "backup.txt"
error_file = "error.txt"
done_file = "done.txt"

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def list_tasks(tasks: List[Task]):
    for i, item in enumerate(tasks):
        print(f"[{i}]: {str(item)}")


def read_tasks_from_file(todo_file) -> List[Task]:
    try:
        with open(todo_file, "r") as file:
            lines = file.readlines()
            return [Task(line) for line in lines]
    except FileNotFoundError:
        # TODO: use a proper logger
        print('Input file does not exists', todo_file)
        exit(-1)


def write_tasks_to_file(tasks: List[Task], todo_file):
    copyfile(todo_file, backup_file)
    lines = "\n".join(str(task) for task in tasks)
    try:
        with open(todo_file, "w") as file:
            file.write(lines + "\n")
    except Exception:
        print("An error happened in file writing")
        copyfile(todo_file, error_file)
        copyfile(backup_file, todo_file)
    finally:
        remove(backup_file)


@click.group()
@click.pass_context
@click.option("--todo_file", type=click.Path(exists=True), required=False)
def cli(ctx, todo_file):
    """todo.txt in Python"""

    # todo file
    ctx.ensure_object(dict)
    ctx.obj['todo_file'] = 'todo.txt'   # default value
    todo_environ = environ.get("TODO_FILE")
    if todo_environ:
        ctx.obj['todo_file'] = todo_environ

    if todo_file:
        ctx.obj['todo_file'] = todo_file



@cli.command()
@click.pass_context
def list(ctx):
    """List all tasks"""
    tasks = read_tasks_from_file(ctx.obj['todo_file'])
    for i, item in enumerate(tasks):
        print(f"[{i}]: {str(item)}")


@cli.command()
@click.pass_context
@click.argument("tasknum", type=click.INT, required=True)
# @click.option("--when", click.DATE, default=now())  # DATE type doesn't exist
def complete(tasknum: int):
    """Mark task TASKNUM as completed"""
    tasks = read_tasks_from_file()
    tasks[tasknum].complete()
    write_tasks_to_file(tasks)


@cli.command()
@click.pass_context
@click.argument("words", type=click.STRING, nargs=-1, required=True)
def add(words: List[str]):
    """Add a new task to the list"""
    tasks = read_tasks_from_file()
    task = Task(" ".join(words))
    tasks.append(task)
    write_tasks_to_file(tasks)


def uppercase_first_char(s: str) -> str:
    return s.upper()[0]


@cli.command()
@click.pass_context
@click.argument("tasknum", type=click.INT, required=True)
@click.argument("priority", type=click.STRING, required=True)
def prioritise(tasknum: int, priority: str):
    """Set the priority for task TASKNUM to PRIORITY ('A'...'Z')"""
    tasks = read_tasks_from_file()
    priority = uppercase_first_char(priority)
    assert len(priority) == 1 and priority[0] in alphabet
    tasks[tasknum].set_priority(priority)
    write_tasks_to_file(tasks)


@cli.command()
@click.pass_context
@click.argument("tasknum", type=click.INT, required=True)
def deprioritise(tasknum: int):
    """Remove any priority from task TASKNUM"""
    tasks = read_tasks_from_file()
    tasks[tasknum].unset_priority()
    write_tasks_to_file(tasks)


@cli.command()
@click.pass_context
@click.argument("tasknum", type=click.INT, required=True)
def delete(tasknum: int):
    """Remove task TASKNUM from the list"""
    tasks = read_tasks_from_file()
    del tasks[tasknum]
    write_tasks_to_file(tasks)


@cli.command()
@click.pass_context
def report():
    """Summarise the task list"""
    tasks = read_tasks_from_file()
    total = len(tasks)
    done = len([task for task in tasks if task.completed is not None])
    print(f"{total} tasks, {done} completed ({done * 100.0 / total:.1f}%)")
    priorities = {}
    for task in tasks:
        p = task.priority
        if p is not None:
            if p in priorities:
                priorities[p] += 1
            else:
                priorities[p] = 1
    if priorities != {}:
        print("Task counts by priority:")
        for (priority, count) in sorted(priorities.items()):
            print(f"({priority}) -> {count}")

