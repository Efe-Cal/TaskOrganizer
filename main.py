from rich.console import Console
from datetime import datetime, timedelta
import re
import keyboard
import os
import json

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

def render_ascii_schedule(tasks):
    current_time = datetime.now()
    lines = []
    for idx, task in enumerate(tasks):
        start_str = current_time.strftime('%H:%M')
        duration_td = parse_duration(task['duration'])
        finish_time = current_time + duration_td
        finish_str = finish_time.strftime('%H:%M')
        # Height: 1 line per 10 minutes, at least 1 line
        height = max(1, int(duration_td.total_seconds() // 600))
        block_lines = []
        for i in range(height):
            if i == 0:
                time_label = f"{start_str} - {finish_str}"
            else:
                time_label = " " * len(f"{start_str} - {finish_str}")
            if i == height // 2:
                content = f"{task['name']} ({task['duration']})"
            else:
                content = ""
            block_lines.append(f"{time_label:<15} | {content:<30}")
        lines.extend(block_lines)
        current_time = finish_time
    return lines

def display_tasks_with_cursor(tasks, cursor_idx, moving_idx=None):
    os.system('cls' if os.name == 'nt' else 'clear')
    console = Console()
    console.print("[bold yellow]Reorder Your Tasks[/bold yellow]\n")
    lines = []
    current_time = datetime.now()
    for idx, task in enumerate(tasks):
        start_str = current_time.strftime('%H:%M')
        duration_td = parse_duration(task['duration'])
        finish_time = current_time + duration_td
        finish_str = finish_time.strftime('%H:%M')
        # Height: 1 line per 10 minutes, at least 1 line
        height = max(1, int(duration_td.total_seconds() // 600))
        block_lines = []
        for i in range(height):
            if i == 0:
                time_label = f"{start_str} - {finish_str}"
            else:
                time_label = " " * len(f"{start_str} - {finish_str}")
            if i == height // 2:
                content = f"{task['name']} ({task['duration']})"
            else:
                content = ""
            block_lines.append((time_label, content))
        style = "on blue" if idx == cursor_idx else ("on green" if moving_idx is not None and idx == moving_idx else "")
        for time_label, content in block_lines:
            if style:
                lines.append(f"[{style}]{time_label:<15} | {content:<30}[/{style}]")
            else:
                lines.append(f"{time_label:<15} | {content:<30}")
        current_time = finish_time
    for line in lines:
        console.print(line)
    if moving_idx is not None:
        console.print("\n[bold magenta]Use arrow keys to move the task. Press space to drop.[/bold magenta]")
    else:
        console.print("\n[bold magenta]Use arrow keys to move the cursor. Press space to pick up a task.[/bold magenta]")

def reorder_tasks(tasks):
    cursor_idx = 0
    moving = False
    moving_idx = None
    console = Console()
    while True:
        display_tasks_with_cursor(tasks, cursor_idx, moving_idx)
        event = keyboard.read_event(suppress=True)
        if event.event_type != 'down':
            continue
        if event.name == 'esc':
            break
        if event.name == 'a':
            console.print("\n[bold yellow]Add a new task[/bold yellow]")
            name = console.input("[green]Enter task name: [/green]")
            duration = console.input("[yellow]Enter task duration (e.g., 30m, 1h): [/yellow]")
            tasks.append({'name': name, 'duration': duration})
            cursor_idx = len(tasks) - 1
            continue
        if event.name == 'e' and tasks:
            console.print(f"\n[bold yellow]Edit task: {tasks[cursor_idx]['name']} ({tasks[cursor_idx]['duration']})[/bold yellow]")
            new_name = console.input(f"[green]Enter new name (leave blank to keep '{tasks[cursor_idx]['name']}'): [/green]")
            new_duration = console.input(f"[yellow]Enter new duration (leave blank to keep '{tasks[cursor_idx]['duration']}'): [/yellow]")
            if new_name.strip():
                tasks[cursor_idx]['name'] = new_name
            if new_duration.strip():
                tasks[cursor_idx]['duration'] = new_duration
            continue
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
    tasks = []
    # Check for existing schedule.json
    if os.path.exists("schedule.json"):
        console.print("[bold yellow]A saved schedule was found.[/bold yellow]")
        choice = console.input("[cyan]Continue with existing schedule? (y/n): [/cyan]").strip().lower()
        if choice == 'y':
            with open("schedule.json", "r", encoding="utf-8") as f:
                tasks = json.load(f)
        else:
            console.print("[italic]Starting with a new schedule.[/italic]")
    if not tasks:
        while True:
            name = console.input("[green]Enter task name (or type 'done' to finish): [/green]")
            if name.lower() == 'done':
                break
            duration = console.input("[yellow]Enter task duration (e.g., 30m, 1h): [/yellow]")
            tasks.append({'name': name, 'duration': duration})
            console.print(f"[bold green]Task '{name}' with duration '{duration}' added.[/bold green]\n")
    if tasks:
        reorder_tasks(tasks)
        # After reordering, print the final ascii schedule and write to file
        ascii_lines = render_ascii_schedule(tasks)
        console.print("\n[bold green]Final Schedule:[/bold green]")
        for line in ascii_lines:
            console.print(line)
        with open("schedule.txt", "w", encoding="utf-8") as f:
            for line in ascii_lines:
                f.write(line + "\n")
        console.print("\n[bold cyan]Schedule written to schedule.txt[/bold cyan]")
        # Ask to save as JSON
        save_json = console.input("\n[cyan]Save this schedule? (y/n): [/cyan]").strip().lower()
        if save_json == 'y':
            with open("schedule.json", "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            console.print("[bold green]Schedule saved[/bold green]")
    else:
        console.print("[italic]No tasks added.[/italic]")
    console.print("\n[bold cyan]Thank you for using Task Organizer![/bold cyan]")

if __name__ == "__main__":
    main()
