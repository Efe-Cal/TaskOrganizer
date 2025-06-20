from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta
import re
import keyboard
import os
import time

def parse_duration(duration_str):
    duration_str = duration_str.strip().lower()
    hours = 0
    minutes = 0
    matches = re.findall(r"(\d+)\s*h", duration_str)
    if matches:
        hours = int(matches[0])
    matches = re.findall(r"(\d+)\s*m", duration_str)
    if matches:
        minutes = int(matches[0])
    return timedelta(hours=hours, minutes=minutes)

def display_tasks_with_cursor(tasks, cursor_idx, moving_idx=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    console = Console()
    table = Table(title="[bold yellow]Reorder Your Tasks[/bold yellow]")
    table.add_column("Start", style="cyan")
    table.add_column("Finish", style="cyan")
    table.add_column("Task Name", style="bold")
    table.add_column("Duration", style="magenta")
    current_time = datetime.now()
    for idx, task in enumerate(tasks):
        start_str = current_time.strftime('%H:%M')
        duration_td = parse_duration(task['duration'])
        finish_time = current_time + duration_td
        finish_str = finish_time.strftime('%H:%M')
        row_style = "on blue" if idx == cursor_idx else ("on green" if moving_idx is not None and idx == moving_idx else None)
        table.add_row(start_str, finish_str, task['name'], task['duration'], style=row_style)
        current_time = finish_time
    console.print(table)
    if moving_idx is not None:
        console.print("[bold magenta]Use arrow keys to move the task. Press space to drop.[/bold magenta]")
    else:
        console.print("[bold magenta]Use arrow keys to move the cursor. Press space to pick up a task.[/bold magenta]")

def reorder_tasks(tasks):
    cursor_idx = 0
    moving = False
    moving_idx = None
    while True:
        display_tasks_with_cursor(tasks, cursor_idx, moving_idx)
        event = keyboard.read_event(suppress=True)
        if event.event_type != 'down':
            continue
        if event.name == 'esc':
            break
        if not moving:
            if event.name == 'down':
                cursor_idx = min(len(tasks) - 1, cursor_idx + 1)
            elif event.name == 'up':
                cursor_idx = max(0, cursor_idx - 1)
            elif event.name == 'space':
                moving = True
                moving_idx = cursor_idx
        else:
            if event.name == 'down' and moving_idx < len(tasks) - 1:
                tasks[moving_idx], tasks[moving_idx + 1] = tasks[moving_idx + 1], tasks[moving_idx]
                moving_idx += 1
            elif event.name == 'up' and moving_idx > 0:
                tasks[moving_idx], tasks[moving_idx - 1] = tasks[moving_idx - 1], tasks[moving_idx]
                moving_idx -= 1
            elif event.name == 'space':
                cursor_idx = moving_idx
                moving = False
                moving_idx = None
    return tasks

def main():
    console = Console()
    console.print("[bold cyan]Welcome to Task Organizer![/bold cyan]")
    tasks = []
    while True:
        name = console.input("[green]Enter task name (or type 'done' to finish): [/green]")
        if name.lower() == 'done':
            break
        duration = console.input("[yellow]Enter task duration (e.g., 30m, 1h): [/yellow]")
        tasks.append({'name': name, 'duration': duration})
        console.print(f"[bold green]Task '{name}' with duration '{duration}' added.[/bold green]\n")
    if tasks:
        console.print("\n[bold yellow]Press any key to start reordering tasks. Press [esc] to finish.[/bold yellow]")
        keyboard.read_event()  # Wait for any key
        reorder_tasks(tasks)
        # After reordering, print the final table
        table = Table(title="Your Tasks (Final Order)")
        table.add_column("Start", style="cyan")
        table.add_column("Finish", style="cyan")
        table.add_column("Task Name", style="bold")
        table.add_column("Duration", style="magenta")
        current_time = datetime.now()
        for task in tasks:
            start_str = current_time.strftime('%H:%M')
            duration_td = parse_duration(task['duration'])
            finish_time = current_time + duration_td
            finish_str = finish_time.strftime('%H:%M')
            table.add_row(start_str, finish_str, task['name'], task['duration'])
            current_time = finish_time
        console.print(table)
    else:
        console.print("[italic]No tasks added.[/italic]")
    console.print("\n[bold cyan]Thank you for using Task Organizer![/bold cyan]")

if __name__ == "__main__":
    main()
