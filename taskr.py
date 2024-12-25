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
        self.tasks = []
        self.config = {}

    def config_setup(self):
        """Set up the configuration file and load its values."""
        config_path = 'config.json'
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding='utf-8') as config_file:
                json.dump(self.DEFAULT_CONFIG, config_file, indent=4)
            print("Config file created with default values.")

        with open(config_path, 'r', encoding='utf-8') as config_file:
            try:
                self.config = json.load(config_file)
            except json.JSONDecodeError:
                with open(config_path, 'w', encoding='utf-8') as config_file_write:
                    json.dump(self.DEFAULT_CONFIG, config_file_write, indent=4)
                print("Config file was invalid or empty. Defaults written.")
                self.config = self.DEFAULT_CONFIG
        print(f"Config loaded: {self.config}")

    def save(self):
        """Save tasks to the tasks.json file."""
        tasks_path = 'tasks.json'
        if not os.path.exists(tasks_path):
            with open(tasks_path, 'w', encoding='utf-8') as tasks_file:
                json.dump(self.tasks, tasks_file, indent=4)
            print("Tasks file created with current tasks.")
            return

        try:
            with open(tasks_path, 'r', encoding='utf-8') as tasks_file:
                existing_tasks = json.load(tasks_file)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_tasks = []

        existing_tasks.extend(
            task for task in self.tasks if task not in existing_tasks)

        with open(tasks_path, 'w', encoding='utf-8') as tasks_file:
            json.dump(existing_tasks, tasks_file, indent=4)
        print("Tasks saved successfully.")

    def manual_save(self):
        """Manually trigger a save of tasks."""
        self.save()

    def view_config(self):
        """Display the current configuration settings."""
        print(json.dumps(self.config, indent=4))

    def update_config(self, key, value):
        """Update a configuration key with a new value."""
        self.config[key] = value
        with open('config.json', 'w', encoding='utf-8') as config_file:
            json.dump(self.config, config_file, indent=4)
        print(f"Config updated: {key} = {value}")

    def add_task(self, description):
        """Add a new task with the given description."""
        task = {
            'id': len(self.tasks) + 1,
            'description': description,
            'status': 'not started',
            'created_time': datetime.now().isoformat(),
            'updated_time': datetime.now().isoformat()
        }
        self.tasks.append(task)
        print(f"Task added: {task['description']}")
        if self.config.get("autosave", True):
            self.save()

    def remove_task(self, task_id):
        """Remove a task by its ID."""
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        print(f"Task {task_id} removed")
        if self.config.get("autosave", True):
            self.save()

    def update_task(self, task_id, description):
        """Update a task's description by its ID."""
        for task in self.tasks:
            if task['id'] == task_id:
                task['description'] = description
                task['updated_time'] = datetime.now().isoformat()
                print(f"Task {task_id} updated to: {description}")
                if self.config.get("autosave", True):
                    self.save()
                return
        print(f"Task {task_id} not found")

    def change_task_status(self, task_id, status):
        """Change the status of a task by its ID."""
        if status not in ["not started", "in progress", "review", "done"]:
            print(
                "Invalid status. Valid options are: 'not started', 'in progress', 'review', 'done'.")
            return
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = status
                task['updated_time'] = datetime.now().isoformat()
                print(f"Task {task_id} status updated to: {status}")
                if self.config.get("autosave", True):
                    self.save()
                return
        print(f"Task {task_id} not found")

    def list_tasks(self, status=None):
        """List tasks, optionally filtered by status."""
        filtered_tasks = self.tasks
        if status:
            filtered_tasks = [
                task for task in self.tasks if task['status'] == status]
        if not filtered_tasks:
            print("No tasks available")
        else:
            for task in filtered_tasks:
                print(f"[{task['id']}] {task['description']} - Status: {task['status']} - Created: {task['created_time']} - Updated: {task['updated_time']}")


def main():
    """Main function to handle CLI commands."""
    manager = TaskManager()
    manager.config_setup()

    parser = argparse.ArgumentParser(
        description="A simple CLI task management app")
    subparsers = parser.add_subparsers(dest='command')

    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('description', type=str,
                            help='Description of the task')

    parser_remove = subparsers.add_parser('remove', help='Remove a task by ID')
    parser_remove.add_argument(
        'task_id', type=int, help='ID of the task to remove')

    parser_update = subparsers.add_parser('update', help='Update a task by ID')
    parser_update.add_argument(
        'task_id', type=int, help='ID of the task to update')
    parser_update.add_argument(
        'description', type=str, help='New description of the task')

    parser_status = subparsers.add_parser(
        'status', help='Change the status of a task')
    parser_status.add_argument(
        'task_id', type=int, help='ID of the task to update status for')
    parser_status.add_argument(
        'status', type=str, help="New status ('not started', 'in progress', 'review', 'done')")

    parser_list = subparsers.add_parser('list', help='List tasks by status')
    parser_list.add_argument('--status', type=str, choices=[
                             'not started', 'in progress', 'review', 'done'], help='Filter tasks by status')

    subparsers.add_parser('save', help='Manually save tasks')

    parser_config = subparsers.add_parser(
        'config', help='Manage configuration settings')
    config_subparsers = parser_config.add_subparsers(dest='config_command')

    config_subparsers.add_parser('view', help='View the configuration')

    parser_update_config = config_subparsers.add_parser(
        'update', help='Update the configuration')
    parser_update_config.add_argument(
        'key', type=str, help='Configuration key to update')
    parser_update_config.add_argument(
        'value', type=str, help='New value for the configuration key')

    args = parser.parse_args()

    if args.command == 'add':
        manager.add_task(args.description)
    elif args.command == 'remove':
        manager.remove_task(args.task_id)
    elif args.command == 'update':
        manager.update_task(args.task_id, args.description)
    elif args.command == 'status':
        manager.change_task_status(args.task_id, args.status)
    elif args.command == 'list':
        manager.list_tasks(status=args.status)
    elif args.command == 'save':
        manager.manual_save()
    elif args.command == 'config':
        if args.config_command == 'view':
            manager.view_config()
        elif args.config_command == 'update':
            manager.update_config(args.key, args.value)
        else:
            print("Invalid config command. Use 'view' or 'update'.")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
