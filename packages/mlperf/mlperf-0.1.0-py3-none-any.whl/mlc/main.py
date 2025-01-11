import argparse

# Base class for CLI actions
class Action:
    def execute(self, args):
        raise NotImplementedError("Subclasses must implement the execute method")

# Child classes for specific entities (Repo, Script, Cache)
class RepoAction(Action):
    def pull(self, args):
        print(f"Pulling repository: {args.details}")

    def list(self, args):
        print("Listing all repositories.")

class ScriptAction(Action):
    def run(self, args):
        print(f"Running script with identifier: {args.details}")

    def list(self, args):
        print("Listing all scripts.")

class CacheAction(Action):
    def show(self, args):
        print(f"Showing cache with identifier: {args.details}")

    def list(self, args):
        print("Listing all caches.")

# Factory to get the appropriate action class
def get_action(target):
    actions = {
        'repo': RepoAction(),
        'script': ScriptAction(),
        'cache': CacheAction()
    }
    return actions.get(target, None)

# Main CLI function
def main():
    parser = argparse.ArgumentParser(prog='cli', description='A CLI tool for managing repos, scripts, and caches.')

    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subcommands that apply to all targets
    for action in ['pull', 'run', 'show', 'list']:
        action_parser = subparsers.add_parser(action, help=f'{action.capitalize()} a target.')
        action_parser.add_argument('target', choices=['repo', 'script', 'cache'], help='Target type (repo, script, cache).')
        action_parser.add_argument('details', nargs='?', help='Details or identifier (optional for list).')

    # Parse arguments
    args = parser.parse_args()

    # Get the action handler for the target
    action = get_action(args.target)

    # Dynamically call the method (e.g., pull, list, show)
    if action and hasattr(action, args.command):
        method = getattr(action, args.command)
        method(args)
    else:
        print(f"Error: '{args.command}' is not supported for {args.target}.")

if __name__ == '__main__':
    main()

