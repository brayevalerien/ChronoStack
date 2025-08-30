#!/usr/bin/env python3
"""
ChronoStack - A stack-based programming language with time travel mechanics.

Main entry point providing both REPL mode and file execution mode.
"""

import argparse
import sys
from pathlib import Path

from chronostack.interpreter import Interpreter, InterpreterError
from chronostack.lexer import Lexer
from chronostack.parser import ParseError, Parser
from chronostack.repl import ChronoStackREPL


def execute_file(filename: str, debug: bool = False, visualize: bool = False) -> None:
    """Execute a ChronoStack file."""
    try:
        file_path = Path(filename)
        if not file_path.exists():
            print(f"Error: File '{filename}' not found")
            sys.exit(1)

        with open(file_path, encoding="utf-8") as f:
            code = f.read()

        # Parse and execute
        lexer = Lexer(code)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        interpreter = Interpreter()
        interpreter.execute_program(ast)

        # Show results
        if debug or visualize:
            print("Execution completed.")
            print(f"Final stack: {interpreter.get_stack_display()}")

            if visualize:
                show_timeline_visualization(interpreter)

        else:
            # Just show final stack
            stack = interpreter.current_stack()
            if stack:
                print("Final stack:", interpreter.get_stack_display())

    except ParseError as e:
        print(f"Parse error: {e}")
        sys.exit(1)
    except InterpreterError as e:
        print(f"Runtime error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def show_timeline_visualization(interpreter: Interpreter) -> None:
    """Show ASCII visualization of the timeline."""
    timeline = interpreter.timeline
    print("\nTimeline Visualization:")
    print("=" * 50)

    # Use tree visualization for multiple branches, simple view for single branch
    if len(timeline.branches) > 1:
        print(timeline.get_timeline_tree_visualization())
    else:
        # Simple linear view for single branch
        print(f"Current branch: {timeline.current_branch}")
        print(f"Current moment: {timeline.current_index}")
        
        print("\nMoments:")
        for i, moment in enumerate(timeline.moments):
            marker = ">>>" if i == timeline.current_index else "   "
            paradox = " [PARADOX]" if "paradox" in moment.metadata else ""
            stack_str = format_stack_for_viz(moment.stack)
            print(f"{marker} {i:2d}: {stack_str}{paradox}")

    # Show timeline info
    timeline_info = timeline.get_timeline_info()
    if timeline_info["paradox_count"] > 0:
        print(f"\nWarning: {timeline_info['paradox_count']} unresolved paradoxes detected!")


def format_stack_for_viz(stack) -> str:
    """Format stack for visualization."""
    if not stack:
        return "[]"
    if len(stack) <= 5:
        items = []
        for item in stack:
            if isinstance(item, str):
                items.append(f'"{item}"')
            elif isinstance(item, list):
                items.append(f"[{len(item)}]")
            else:
                items.append(str(item))
        return f"[{' '.join(items)}]"
    else:
        return f"[...{len(stack)} items...]"


def create_example_file(filename: str) -> None:
    """Create an example ChronoStack file in the examples/ directory."""
    # Ensure examples directory exists
    Path("examples").mkdir(exist_ok=True)

    examples = {
        "fibonacci.cstack": """
# Fibonacci using temporal mechanics
:fib
    dup 2 < if [ pop 1 ] [
        dup 1 - echo 2 - echo +
    ] ;

# Calculate fibonacci of 5
5 fib
echo 0  # Show the result
""",
        "palindrome.cstack": """
# Palindrome checker using temporal-fold
"racecar"
dup "count" temporal-fold
[ dup echo ] "first" temporal-fold
[ swap echo ] "last" temporal-fold
= if [ "Palindrome!" ] [ "Not palindrome" ]
""",
        "time_travel.cstack": """
# Time travel example
42 tick        # Save state: [42], advance to moment 1
"hello" tick   # Save state: [42 "hello"], advance to moment 2
999 2 send     # Send 999 back 2 moments (creates paradox!)

# Check what happened
0 rewind       # Go back to beginning
# Stack now has [999 42] due to time travel
""",
        "branching.cstack": """
# Timeline branching example
1 2 3 tick          # Create initial state
"main-branch" branch # Create new branch
10 20 + tick        # Do work in branch
"main" merge        # Merge back to main
# Result combines both timelines
""",
    }

    if filename not in examples:
        print(f"Available examples: {', '.join(examples.keys())}")
        return

    filepath = Path("examples") / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(examples[filename])
    print(f"Created example file: {filepath}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ChronoStack - A stack-based language with time travel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start interactive REPL
  %(prog)s script.cstack      # Execute a file
  %(prog)s -d script.cstack   # Execute with debug info
  %(prog)s -v script.cstack   # Execute with visualization
  %(prog)s --example fibonacci.cstack  # Create example file
""",
    )

    parser.add_argument("file", nargs="?", help="ChronoStack file to execute")
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
    parser.add_argument(
        "-v", "--visualize", action="store_true", help="Show timeline visualization"
    )
    parser.add_argument(
        "--example",
        metavar="NAME",
        help="Create an example file (fibonacci.cstack, palindrome.cstack, etc.)",
    )
    parser.add_argument("--version", action="version", version="ChronoStack 0.1.0")

    args = parser.parse_args()

    # Create example file
    if args.example:
        create_example_file(args.example)
        return

    # Execute file
    if args.file:
        execute_file(args.file, args.debug, args.visualize)
    else:
        # Start REPL
        repl = ChronoStackREPL()
        repl.run()


if __name__ == "__main__":
    main()
