# ChronoStack

A stack-based programming language with time travel mechanics. ChronoStack lets you manipulate not just data on a stack, but time itself—creating temporal loops, branching timelines, and resolving paradoxes.

## Features

- **Stack-Based Operations**: Traditional stack manipulation (push, pop, dup, swap, rot)
- **Temporal Operations**: Travel through time, create branches, and modify the past
- **Timeline Management**: Multiple timelines with branching and merging capabilities
- **Paradox Resolution**: Automatic detection and resolution of temporal paradoxes
- **Word Definitions**: Define custom operations using `:name ... ;` syntax
- **Control Flow**: Conditional execution and loops
- **Interactive REPL**: Explore temporal mechanics interactively

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ChronoStack

# Install with uv (recommended)
uv install

# Or with pip
pip install -e .
```

## Quick Start

### Running the REPL
```bash
uv run python main.py
# or
python main.py
```

### Executing Files
```bash
uv run python main.py examples/fibonacci.cstack
```

### Creating Examples
```bash
python main.py --example fibonacci.cstack
```

## Language Overview

### Basic Stack Operations
```chronostack
5 3 +          # Push 5 and 3, add them → [8]
1 2 3 dup      # Duplicate top element → [1, 2, 3, 3]
1 2 swap       # Swap top two → [2, 1]
1 2 3 rot      # Rotate top 3 → [2, 3, 1]
```

### Temporal Operations
```chronostack
42 tick        # Save current state and advance time
2 rewind       # Go back 2 moments
1 echo         # Get value from 1 moment ago
99 2 send      # Send 99 back 2 moments (creates paradox!)
```

### Timeline Branching
```chronostack
"main" tick           # Create a moment
"experiment" branch   # Create new timeline branch
10 20 + tick         # Do work in branch
"main" merge         # Merge changes back
```

### Word Definitions
```chronostack
:double dup + ;       # Define a word called 'double'
5 double             # Use it → [10]
```

### Control Flow
```chronostack
1 [ 42 ] if          # If true, execute block → [42]
3 [ "hello" ] loop   # Loop 3 times → ["hello", "hello", "hello"]
```

## Core Concepts

### The Stack
ChronoStack uses a stack data structure where values are pushed and popped in Last-In-First-Out (LIFO) order.

### Timeline Mechanics
Every operation creates a new "moment" in time. You can:
- **tick**: Save current state and advance to a new moment
- **rewind n**: Go back n moments in time
- **echo n**: Retrieve a value from n moments ago
- **send value n**: Send a value back n moments, potentially creating paradoxes

### Branches and Parallel Timelines
Create alternate timelines that share history but diverge:
- **branch name**: Create a new timeline branch
- **merge target**: Merge current branch into target timeline

### Paradox Resolution
When temporal operations create inconsistencies, ChronoStack automatically resolves them by:
1. Detecting the paradox
2. Trying multiple resolution strategies
3. Choosing the most stable outcome

## Built-in Operations

### Stack Operations
- `push`: Duplicate top element
- `pop`: Remove top element
- `dup`: Duplicate top element
- `swap`: Swap top two elements
- `rot`: Rotate top three elements

### Math Operations
- `+`, `-`, `*`, `/`, `%`: Basic arithmetic
- `<`, `>`, `=`: Comparisons (return 1 for true, 0 for false)
- `and`, `or`, `not`: Logical operations

### Temporal Operations
- `tick`: Advance to new moment
- `rewind n`: Go back n moments
- `echo n`: Get value from n moments ago
- `send value n`: Send value to past
- `peek-future n`: Look ahead n moments
- `temporal-fold operation`: Apply operation across all moments
- `ripple operation`: Apply operation to future moments

### Timeline Operations
- `branch name`: Create new timeline
- `merge target`: Merge timelines
- `paradox!`: Force paradox resolution

### Control Flow
- `if`: Execute block if condition is true
- `loop`: Execute block n times
- `when-stable`: Execute only if no paradoxes

## REPL Commands

The interactive REPL supports these debugging commands:
- `.stack`: Show current stack
- `.timeline`: Show timeline visualization
- `.moment`: Show current moment index
- `.branches`: Show all timeline branches
- `.words`: Show defined words
- `.clear`: Clear the stack
- `.reset`: Reset to initial state
- `.help`: Show help

## Example Programs

### Fibonacci with Time Travel
```chronostack
# Define fibonacci using temporal mechanics
:fib
    dup 2 < if [ pop 1 ] [
        dup 1 - echo 2 - echo +
    ] ;

# Calculate fibonacci of 5
5 fib
```

### Paradox Example
```chronostack
# Create a temporal paradox
10 tick              # Start with 10
dup 2 * tick        # Calculate 10 * 2 = 20
999 2 send          # Send 999 back - creates paradox!
0 rewind            # Check result after resolution
```

### Quantum Coin Flip
```chronostack
# Simulate quantum superposition with branches
"quantum" tick
"heads" branch
1 tick              # Heads timeline
"quantum" merge
"tails" branch  
0 tick              # Tails timeline
```

## Development

### Running Tests
```bash
uv run pytest
```

### Code Quality
```bash
uv run ruff check
uv run ruff format
```

### Coverage
```bash
uv run pytest --cov=chronostack
```

## Architecture

- **Lexer** (`chronostack/lexer.py`): Tokenizes ChronoStack source code
- **Parser** (`chronostack/parser.py`): Builds Abstract Syntax Tree (AST)
- **Timeline** (`chronostack/timeline.py`): Manages temporal mechanics and paradox resolution
- **Interpreter** (`chronostack/interpreter.py`): Executes programs with stack and temporal operations
- **REPL** (`chronostack/repl.py`): Interactive command-line interface

## Contributing

This is a toy language for exploring temporal programming concepts. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

*ChronoStack: Where time is just another dimension to program with.*