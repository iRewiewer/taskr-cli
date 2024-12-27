import argparse
import json
import os
from datetime import datetime


class TaskManager:
    """The Taskr App class"""
    DEFAULT_CONFIG = {
        "autosave": True
    }

    def __init__(self):
        self.config = {}
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def config_setup(self):
        """Set up the configuration file and load its values."""
        config_path = os.path.join(self.base_path, 'config.json')
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding='utf-8') as config_file:
                json.dump(self.DEFAULT_CONFIG, config_file, indent=4)
            print("[Taskr] Config file created with default values.")

        with open(config_path, 'r', encoding='utf-8') as config_file:
            try:
                self.config = json.load(config_file)
            except json.JSONDecodeError:
                with open(config_path, 'w', encoding='utf-8') as config_file_write:
                    json.dump(self.DEFAULT_CONFIG, config_file_write, indent=4)
                print("[Taskr] Config file was invalid or empty. Defaults written.")
                self.config = self.DEFAULT_CONFIG

    def load_tasks(self):
        """Load tasks from the tasks.json file."""
        tasks_path = os.path.join(self.base_path, 'tasks.json')
        if os.path.exists(tasks_path):
            try:
                with open(tasks_path, 'r', encoding='utf-8') as tasks_file:
                    tasks = json.load(tasks_file)
                print("[Taskr] Tasks loaded successfully.")
                return tasks
            except (json.JSONDecodeError, FileNotFoundError):
                print("[Taskr] Tasks file is empty or corrupted. Starting fresh.")
                return []
        else:
            print("[Taskr] No existing tasks found. Starting fresh.")
            return []

    def save_tasks(self, tasks):
        """Save tasks to the tasks.json file."""
        tasks_path = os.path.join(self.base_path, 'tasks.json')
        with open(tasks_path, 'w', encoding='utf-8') as tasks_file:
            json.dump(tasks, tasks_file, indent=4)
        print("[Taskr] Tasks saved successfully.")

    def add_task(self, description):
        """Add a new task with the given description."""
        tasks = self.load_tasks()
        task = {
            'id': len(tasks) + 1,
            'description': description,
            'status': 'not started',
            'created_time': datetime.now().isoformat(),
            'updated_time': datetime.now().isoformat()
        }
        tasks.append(task)
        print(f"[Taskr] Task added: {task['description']}")
        if self.config.get("autosave", True):
            self.save_tasks(tasks)

    def remove_task(self, task_id):
        """Remove a task by its ID."""
        tasks = self.load_tasks()
        initial_task_count = len(tasks)
        tasks = [task for task in tasks if task['id'] != task_id]
        if len(tasks) < initial_task_count:
            print(f"[Taskr] Task {task_id} removed")
            # Reassign IDs
            for index, task in enumerate(tasks):
                task['id'] = index + 1
            if self.config.get("autosave", True):
                self.save_tasks(tasks)
        else:
            print(f"[Taskr] Task {task_id} not found")

    def update_task(self, task_id, description):
        """Update a task's description by its ID."""
        tasks = self.load_tasks()
        for task in tasks:
            if task['id'] == task_id:
                task['description'] = description
                task['updated_time'] = datetime.now().isoformat()
                print(f"[Taskr] Task {task_id} updated to: {description}")
                if self.config.get("autosave", True):
                    self.save_tasks(tasks)
                return
        print(f"[Taskr] Task {task_id} not found")

    def change_task_status(self, task_id, status):
        """Change the status of a task by its ID."""
        tasks = self.load_tasks()
        if status not in ["not started", "in progress", "review", "done"]:
            print(
                "[Taskr] Invalid status. Valid options are: 'not started', 'in progress', 'review', 'done'.")
            return
        for task in tasks:
            if task['id'] == task_id:
                task['status'] = status
                task['updated_time'] = datetime.now().isoformat()
                print(f"[Taskr] Task {task_id} status updated to: {status}")
                if self.config.get("autosave", True):
                    self.save_tasks(tasks)
                return
        print(f"[Taskr] Task {task_id} not found")

    def list_tasks(self, status=None, show_all=False):
        """List tasks, optionally filtered by status, or show all."""
        tasks = self.load_tasks()
        if not status and not show_all:
            print(
                "[Taskr] Use '--status' to filter tasks by their status or '--show-all' to display all tasks.")
            return

        filtered_tasks = tasks if show_all else [
            task for task in tasks if task['status'] == status]
        if not filtered_tasks:
            print("[Taskr] No tasks available")
        else:
            for task in filtered_tasks:
                print(f"[{task['id']}] {task['description']} - Status: {task['status']} - Created: {task['created_time']} - Updated: {task['updated_time']}")


def handle_task_commands(manager, args):
    """Handle task-related commands."""
    if args.command == 'add':
        manager.add_task(args.description)
    elif args.command == 'remove':
        manager.remove_task(args.task_id)
    elif args.command == 'update':
        manager.update_task(args.task_id, args.description)
    elif args.command == 'status':
        manager.change_task_status(args.task_id, args.status)
    elif args.command == 'list':
        manager.list_tasks(status=args.status, show_all=args.show_all)


def handle_config_commands(manager, args):
    """Handle configuration-related commands."""
    if args.config_command == 'view':
        manager.view_config()
    elif args.config_command == 'update':
        manager.update_config(args.key, args.value)
    else:
        print("[Taskr] Invalid config command. Use 'view' or 'update'.")


def main():
    """Main function to handle CLI commands."""
    manager = TaskManager()
    manager.config_setup()

    parser = argparse.ArgumentParser(
        description="A simple CLI task management app")
    subparsers = parser.add_subparsers(dest='command')

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('description', type=str,
                            help='Description of the task')

    # Remove command
    parser_remove = subparsers.add_parser('remove', help='Remove a task by ID')
    parser_remove.add_argument(
        'task_id', type=int, help='ID of the task to remove')

    # Update command
    parser_update = subparsers.add_parser('update', help='Update a task by ID')
    parser_update.add_argument(
        'task_id', type=int, help='ID of the task to update')
    parser_update.add_argument(
        'description', type=str, help='New description of the task')

    # Status command
    parser_status = subparsers.add_parser(
        'status', help='Change the status of a task')
    parser_status.add_argument(
        'task_id', type=int, help='ID of the task to update status for')
    parser_status.add_argument(
        'status', type=str, help="New status ('not started', 'in progress', 'review', 'done')")

    # List command
    parser_list = subparsers.add_parser(
        'list', help='List tasks by status or show all tasks')
    parser_list.add_argument('--status', type=str, choices=[
                             'not started', 'in progress', 'review', 'done'], help='Filter tasks by status')
    parser_list.add_argument(
        '--show-all', action='store_true', help='Display all tasks regardless of status')

    # Config command
    parser_config = subparsers.add_parser(
        'config', help='Manage configuration settings')
    config_subparsers = parser_config.add_subparsers(dest='config_command')

    # View Config subcommand
    config_subparsers.add_parser('view', help='View the configuration')

    # Update Config subcommand
    parser_update_config = config_subparsers.add_parser(
        'update', help='Update the configuration')
    parser_update_config.add_argument(
        'key', type=str, help='Configuration key to update')
    parser_update_config.add_argument(
        'value', type=str, help='New value for the configuration key')

    args = parser.parse_args()

    if args.command in ['add', 'remove', 'update', 'status', 'list']:
        handle_task_commands(manager, args)
    elif args.command == 'config':
        handle_config_commands(manager, args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
