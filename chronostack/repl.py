"""
REPL (Read-Eval-Print Loop) interface for ChronoStack.

Provides an interactive command-line interface with:
- Code execution
- Stack display
- Timeline visualization
- Debugging commands
- Help system
"""

from typing import List

from chronostack.interpreter import Interpreter, InterpreterError
from chronostack.lexer import Lexer
from chronostack.parser import ParseError, Parser


class ChronoStackREPL:
    """Interactive REPL for ChronoStack language."""

    def __init__(self):
        self.interpreter = Interpreter()
        self.running = True

    def run(self) -> None:
        """Start the REPL loop."""
        print("ChronoStack REPL v0.1.0")
        print("A stack-based programming language with time travel mechanics")
        print("Type .help for commands, .quit to exit")
        print()

        while self.running:
            try:
                line = input("chronostack> ").strip()
                if not line:
                    continue

                if line.startswith("."):
                    self.handle_command(line)
                else:
                    self.execute_code(line)
                    self.display_stack()

            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

    def execute_code(self, code: str) -> None:
        """Execute ChronoStack code."""
        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            self.interpreter.execute_program(ast)
        except (ParseError, InterpreterError) as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def display_stack(self) -> None:
        """Display the current stack state."""
        stack_display = self.interpreter.get_stack_display()
        moment = self.interpreter.timeline.current_moment().timestamp
        branch = self.interpreter.timeline.current_branch
        print(f"Stack: {stack_display} | Moment: {moment} | Branch: {branch}")

    def handle_command(self, command: str) -> None:
        """Handle REPL commands."""
        cmd = command[1:].lower()  # Remove the '.' prefix

        if cmd == "help":
            self.show_help()
        elif cmd == "quit" or cmd == "exit":
            self.running = False
        elif cmd == "stack":
            self.show_stack()
        elif cmd == "timeline":
            self.show_timeline()
        elif cmd == "branches":
            self.show_branches()
        elif cmd == "moment":
            self.show_moment()
        elif cmd == "words":
            self.show_words()
        elif cmd == "clear":
            self.clear_stack()
        elif cmd == "reset":
            self.reset_interpreter()
        elif cmd == "info":
            self.show_info()
        else:
            print(f"Unknown command: {cmd}")
            print("Type .help for available commands")

    def show_help(self) -> None:
        """Show help information."""
        print("""
ChronoStack REPL Commands:
  .help      - Show this help
  .quit      - Exit the REPL
  .stack     - Show current stack with details
  .timeline  - Show timeline (tree view for multiple branches)
  .branches  - Show branch structure
  .moment    - Show current moment info
  .words     - Show defined words
  .clear     - Clear the current stack
  .reset     - Reset interpreter (clear everything)
  .info      - Show interpreter state info

Stack Operations:
  push pop dup swap rot

Temporal Operations:
  tick rewind peek-future branch merge paradox!
  echo send temporal-fold ripple

Math Operations:
  + - * / %

Comparison Operations:
  < > =

Logical Operations:
  and or not

Control Flow:
  if loop when-stable

Word Definition:
  :name ... ;

Code Blocks:
  [ ... ]

Examples:
  5 3 +              # Add 5 and 3
  42 tick            # Save state and advance time
  :double dup + ;    # Define a word
  5 double           # Use the word
  [ 1 + ] 5 loop     # Loop 5 times
""")

    def show_stack(self) -> None:
        """Show detailed stack information."""
        stack = self.interpreter.current_stack()
        if not stack:
            print("Stack: empty")
            return

        print(f"Stack (depth {len(stack)}):")
        for i, item in enumerate(reversed(stack)):
            index = len(stack) - 1 - i
            item_str = self.format_stack_item(item)
            marker = " <-- top" if index == len(stack) - 1 else ""
            print(f"  [{index}] {item_str}{marker}")

    def format_stack_item(self, item) -> str:
        """Format a stack item for display."""
        if isinstance(item, str):
            return f'"{item}"'
        elif isinstance(item, list):
            if len(item) <= 3:
                inner = " ".join(str(x) for x in item)
                return f"[{inner}]"
            else:
                return f"[...{len(item)} items...]"
        else:
            return str(item)

    def show_timeline(self) -> None:
        """Show timeline with ASCII tree visualization."""
        timeline = self.interpreter.timeline
        
        # Check if there are multiple branches - use tree view if so
        if len(timeline.branches) > 1:
            print(timeline.get_timeline_tree_visualization())
        else:
            # Use simple linear view for single branch
            print(f"Timeline (branch: {timeline.current_branch}):")
            for i, moment in enumerate(timeline.moments):
                marker = " <-- current" if i == timeline.current_index else ""
                stack_str = self.format_stack_list(moment.stack)
                paradox = " [PARADOX]" if "paradox" in moment.metadata else ""
                print(f"  Moment {i}: {stack_str}{paradox}{marker}")

    def format_stack_list(self, stack: List) -> str:
        """Format a stack list for display."""
        if not stack:
            return "[]"
        items = []
        for item in stack:
            if isinstance(item, str):
                items.append(f'"{item}"')
            else:
                items.append(str(item))
        return f"[{' '.join(items)}]"

    def show_branches(self) -> None:
        """Show branch structure."""
        branch_info = self.interpreter.timeline.get_branch_info()
        print("Branches:")

        for branch_name, info in branch_info.items():
            current_marker = " <-- current" if info["current"] else ""
            print(f"  {branch_name}: {info['moment_count']} moments{current_marker}")

    def show_moment(self) -> None:
        """Show current moment information."""
        moment = self.interpreter.timeline.current_moment()
        info = self.interpreter.timeline.get_timeline_info()

        print(f"Current moment: {moment.timestamp}")
        print(f"Stack: {self.format_stack_list(moment.stack)}")
        print(f"Branch: {moment.branch_name} (ID: {moment.branch_id})")
        print(f"Total moments: {info['total_moments']}")
        print(f"Paradoxes: {info['paradox_count']}")

    def show_words(self) -> None:
        """Show defined words."""
        words = self.interpreter.words
        if not words:
            print("No words defined")
            return

        print("Defined words:")
        for word_name in sorted(words.keys()):
            print(f"  {word_name}")

    def clear_stack(self) -> None:
        """Clear the current stack."""
        self.interpreter.current_stack().clear()
        print("Stack cleared")

    def reset_interpreter(self) -> None:
        """Reset the interpreter completely."""
        self.interpreter = Interpreter()
        print("Interpreter reset")

    def show_info(self) -> None:
        """Show complete interpreter state information."""
        info = self.interpreter.get_state_info()

        print("Interpreter State:")
        print(f"  Stack size: {info['stack_size']}")
        print(f"  Current moment: {info['timeline_moment']}")
        print(f"  Current branch: {info['timeline_branch']}")
        print(f"  Has paradoxes: {info['has_paradoxes']}")
        print(f"  Defined words: {len(info['defined_words'])}")
        if info["call_stack"]:
            print(f"  Call stack: {' -> '.join(info['call_stack'])}")


def main() -> None:
    """Entry point for the REPL."""
    repl = ChronoStackREPL()
    repl.run()


if __name__ == "__main__":
    main()
