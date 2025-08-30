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
        self.debug_mode = False
        self.breakpoints = set()
        self.step_count = 0

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
        elif cmd == "debug":
            self.toggle_debug_mode()
        elif cmd.startswith("step"):
            parts = cmd.split()
            steps = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
            self.debug_step(steps)
        elif cmd == "breakpoint" or cmd == "bp":
            self.show_breakpoints()
        elif cmd.startswith("bp-add"):
            parts = cmd.split()
            if len(parts) > 1:
                self.add_breakpoint(parts[1])
        elif cmd.startswith("bp-remove"):
            parts = cmd.split()
            if len(parts) > 1:
                self.remove_breakpoint(parts[1])
        elif cmd.startswith("query"):
            query_str = cmd[5:].strip()  # Remove "query" prefix
            if query_str:
                self.execute_temporal_query(query_str)
            else:
                self.show_query_help()
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
  .debug     - Toggle debug mode
  .step [n]  - Execute n operations in debug mode (default 1)
  .bp        - Show breakpoints
  .bp-add    - Add breakpoint
  .bp-remove - Remove breakpoint
  .query     - Show temporal query help
  .query <q> - Execute temporal query

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

    def toggle_debug_mode(self) -> None:
        """Toggle debug mode on/off."""
        self.debug_mode = not self.debug_mode
        status = "enabled" if self.debug_mode else "disabled"
        print(f"Debug mode {status}")

    def debug_step(self, steps: int) -> None:
        """Execute a number of operations in debug mode."""
        if not self.debug_mode:
            print("Debug mode not enabled. Use .debug to enable.")
            return
        print(f"Debug step: executing {steps} operation(s)")
        self.step_count += steps
        print(f"Total debug steps taken: {self.step_count}")

    def show_breakpoints(self) -> None:
        """Show current breakpoints."""
        if not self.breakpoints:
            print("No breakpoints set")
            return
        print("Breakpoints:")
        for bp in sorted(self.breakpoints):
            print(f"  {bp}")

    def add_breakpoint(self, target: str) -> None:
        """Add a breakpoint."""
        self.breakpoints.add(target)
        print(f"Breakpoint added: {target}")

    def remove_breakpoint(self, target: str) -> None:
        """Remove a breakpoint."""
        if target in self.breakpoints:
            self.breakpoints.remove(target)
            print(f"Breakpoint removed: {target}")
        else:
            print(f"Breakpoint not found: {target}")

    def show_query_help(self) -> None:
        """Show temporal query language help."""
        print("""
Temporal Query Language:
  moments                 - List all moments
  moments where paradox   - Filter moments with paradoxes
  branches                - List all branches  
  branch <name>           - Show specific branch
  values > 10             - Find moments where top stack value > 10
  values = "hello"        - Find moments with specific value
  count                   - Count total moments
  max                     - Find maximum values
  sum                     - Sum all values
  timeline                - Show full timeline structure

Examples:
  .query moments where paradox
  .query values > 50
  .query branch main
  .query count
""")

    def execute_temporal_query(self, query: str) -> None:
        """Execute a temporal query."""
        query = query.strip().lower()
        timeline = self.interpreter.timeline
        
        if query == "moments":
            print("All moments:")
            for i, moment in enumerate(timeline.moments):
                stack_str = self.format_stack_list(moment.stack)
                branch = moment.branch_name if hasattr(moment, 'branch_name') else timeline.current_branch
                print(f"  M{i}: {stack_str} (branch: {branch})")
                
        elif query == "moments where paradox":
            print("Moments with paradoxes:")
            for i, moment in enumerate(timeline.moments):
                if "paradox" in moment.metadata:
                    stack_str = self.format_stack_list(moment.stack)
                    print(f"  M{i}: {stack_str} [PARADOX]")
                    
        elif query == "branches":
            branch_info = timeline.get_branch_info()
            print("Branches:")
            for branch_name, info in branch_info.items():
                current = " (current)" if info["current"] else ""
                print(f"  {branch_name}: {info['moment_count']} moments{current}")
                
        elif query.startswith("branch "):
            branch_name = query[7:].strip()
            if branch_name in timeline.branches:
                moments = timeline.branches[branch_name]
                print(f"Branch '{branch_name}':")
                for i, moment in enumerate(moments):
                    stack_str = self.format_stack_list(moment.stack)
                    print(f"  M{i}: {stack_str}")
            else:
                print(f"Branch '{branch_name}' not found")
                
        elif query.startswith("values >"):
            try:
                threshold = float(query.split(">")[1].strip())
                print(f"Moments with values > {threshold}:")
                for i, moment in enumerate(timeline.moments):
                    for value in moment.stack:
                        if isinstance(value, (int, float)) and value > threshold:
                            stack_str = self.format_stack_list(moment.stack)
                            print(f"  M{i}: {stack_str}")
                            break
            except (ValueError, IndexError):
                print("Invalid query format. Use: values > <number>")
                
        elif query.startswith("values ="):
            target = query.split("=")[1].strip().strip('"')
            print(f"Moments containing '{target}':")
            for i, moment in enumerate(timeline.moments):
                if target in moment.stack or str(target) in [str(v) for v in moment.stack]:
                    stack_str = self.format_stack_list(moment.stack)
                    print(f"  M{i}: {stack_str}")
                    
        elif query == "count":
            total = len(timeline.moments)
            branch_counts = {name: len(moments) for name, moments in timeline.branches.items()}
            print(f"Total moments: {total}")
            print("Per branch:")
            for branch, count in branch_counts.items():
                print(f"  {branch}: {count}")
                
        elif query == "max":
            max_values = []
            for i, moment in enumerate(timeline.moments):
                numeric_values = [v for v in moment.stack if isinstance(v, (int, float))]
                if numeric_values:
                    max_val = max(numeric_values)
                    max_values.append((i, max_val))
            
            if max_values:
                overall_max = max(max_values, key=lambda x: x[1])
                print(f"Maximum value: {overall_max[1]} at moment {overall_max[0]}")
                print("All maximums:")
                for moment_idx, val in max_values:
                    print(f"  M{moment_idx}: {val}")
            else:
                print("No numeric values found")
                
        elif query == "sum":
            total_sum = 0
            moment_sums = []
            for i, moment in enumerate(timeline.moments):
                numeric_values = [v for v in moment.stack if isinstance(v, (int, float))]
                moment_sum = sum(numeric_values) if numeric_values else 0
                moment_sums.append((i, moment_sum))
                total_sum += moment_sum
                
            print(f"Total sum across timeline: {total_sum}")
            print("Per moment:")
            for moment_idx, val in moment_sums:
                if val != 0:
                    print(f"  M{moment_idx}: {val}")
                    
        elif query == "timeline":
            if len(timeline.branches) > 1:
                print(timeline.get_timeline_tree_visualization())
            else:
                self.show_timeline()
                
        else:
            print(f"Unknown query: {query}")
            print("Use .query for help")


def main() -> None:
    """Entry point for the REPL."""
    repl = ChronoStackREPL()
    repl.run()


if __name__ == "__main__":
    main()
