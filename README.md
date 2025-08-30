# ChronoStack

A revolutionary stack-based programming language with time travel mechanics. ChronoStack lets you manipulate not just data on a stack, but time itself—creating temporal loops, branching timelines, and resolving paradoxes. It's Turing complete and features a sophisticated temporal computation model.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Test Coverage](https://img.shields.io/badge/coverage-78%25-green.svg)](https://github.com)
[![Tests](https://img.shields.io/badge/tests-142%20passing-brightgreen.svg)](https://github.com)

## Key Features

### Core Capabilities
- **Stack-Based Architecture**: Traditional stack operations (push, pop, dup, swap, rot) with temporal enhancements
- **Time Travel Operations**: Navigate through computational history with `tick`, `rewind`, and `peek-future`
- **Timeline Branching**: Create alternate computational realities with `branch` and `merge`
- **Paradox Resolution**: Sophisticated fixed-point algorithm automatically resolves temporal paradoxes
- **Turing Completeness**: Proven computational completeness with Rule 110 implementation

### Advanced Features
- **ASCII Tree Visualization**: Beautiful timeline visualization showing branch hierarchies
- **Temporal Query Language**: SQL-like queries for timeline analysis
- **Debug Mode**: Step-through execution with breakpoints
- **Comprehensive Error Handling**: Temporal context in all error messages
- **Interactive REPL**: Rich command-line interface with 20+ commands

## Installation

```bash
# Clone the repository
git clone https://github.com/brayevalerien/ChronoStack.git
cd ChronoStack

# Install with uv (recommended)
uv install

# Or with pip
pip install -e .
```

## Quick Start

### Interactive REPL
```bash
uv run python main.py
# or
python main.py
```

Once in the REPL:
```chronostack
chronostack> 5 3 +
Stack: [8] | Moment: 0 | Branch: main

chronostack> tick
Stack: [8 1] | Moment: 1 | Branch: main

chronostack> 42 2 send  # Send 42 back 2 moments
Stack: [8 1 True] | Moment: 1 | Branch: main

chronostack> 2 rewind
Stack: [42 8] | Moment: 0 | Branch: main
```

### Execute Programs
```bash
# Run example programs
python main.py examples/fibonacci.cstack -v  # With visualization
python main.py examples/rule110_clean.cstack  # Rule 110 automaton
python main.py examples/paradox_demo.cstack   # Paradox resolution
```

## Language Reference

### Stack Operations
| Operation | Description | Example |
|-----------|-------------|---------|
| `push` | Push value onto stack | `42 push` |
| `pop` | Remove top value | `pop` |
| `dup` | Duplicate top value | `5 dup` results in `[5, 5]` |
| `swap` | Exchange top two values | `1 2 swap` results in `[2, 1]` |
| `rot` | Rotate top three values | `1 2 3 rot` results in `[2, 3, 1]` |

### Temporal Operations
| Operation | Description | Example |
|-----------|-------------|---------|
| `tick` | Save state and advance time | `42 tick` |
| `rewind n` | Go back n moments | `2 rewind` |
| `peek-future n` | Look ahead n moments | `1 peek-future` |
| `branch [name]` | Create alternate timeline | `"experimental" branch` |
| `merge [target]` | Merge timeline | `"main" merge` |
| `paradox!` | Resolve all paradoxes | `paradox!` |
| `echo n` | Copy value from n moments ago | `2 echo` |
| `send n` | Send value n moments into past | `99 3 send` |
| `temporal-fold op` | Apply operation across timeline | `"sum" temporal-fold` |
| `ripple op val` | Apply to all future moments | `"push" 100 ripple` |

### Math & Logic Operations
```chronostack
10 5 +     # Addition: 15
10 3 -     # Subtraction: 7
4 5 *      # Multiplication: 20
10 2 /     # Division: 5
10 3 %     # Modulo: 1
5 3 >      # Greater than: 1 (true)
1 1 and    # Logical AND: 1
0 not      # Logical NOT: 1
```

### Control Flow
```chronostack
# Conditional execution
5 3 > [ "Five is greater" ] if

# Loops
3 [ "Hello" ] loop  # Executes 3 times

# Stable timeline execution
[ "No paradoxes!" ] when-stable
```

### Word Definitions
```chronostack
# Define custom operations
:double dup + ;
:square dup * ;

5 double    # Result: 10
3 square    # Result: 9
```

## REPL Commands

### Basic Commands
- `.help` - Show command help
- `.quit` - Exit REPL
- `.stack` - Show detailed stack
- `.timeline` - Display timeline (tree view for branches)
- `.branches` - List all branches
- `.moment` - Current moment info
- `.words` - List defined words
- `.info` - Complete interpreter state

### Debug Commands
- `.debug` - Toggle debug mode
- `.step [n]` - Execute n operations in debug
- `.bp` - Show breakpoints
- `.bp-add <name>` - Add breakpoint
- `.bp-remove <name>` - Remove breakpoint

### Temporal Query Language
```chronostack
.query moments                # List all moments
.query moments where paradox  # Find paradoxes
.query branches               # List branches
.query values > 100          # Find large values
.query max                   # Find maximum values
.query sum                   # Sum all values
.query timeline              # Full timeline structure
```

## Example Programs

### Fibonacci Sequence
```chronostack
:fib
    dup 2 < if [ pop 1 ] [
        dup 1 - fib
        swap 1 - fib +
    ] ;

8 fib  # Calculate 8th Fibonacci number
```

### Time Loop with Paradox
```chronostack
10 tick        # Save state
20 tick        # Advance
99 2 send      # Send 99 back 2 moments
paradox!       # Resolve the paradox
```

### Rule 110 Cellular Automaton
```chronostack
# Demonstrates Turing completeness
# See examples/rule110_clean.cstack
"..........#.........." tick
".........###........." tick
"........##..#........" tick
# ... evolution continues
```

### Multi-Dimensional Branching
```chronostack
10 tick
"alpha" branch
20 tick
"beta" branch
30 tick
"main" merge
# Complex timeline with multiple branches
```

## Project Structure

```
ChronoStack/
├── chronostack/          # Core interpreter
│   ├── lexer.py         # Tokenization
│   ├── parser.py        # AST generation
│   ├── interpreter.py   # Execution engine
│   ├── timeline.py      # Temporal mechanics
│   └── repl.py          # Interactive interface
├── examples/            # 16 example programs
│   ├── fibonacci.cstack
│   ├── rule110_*.cstack # Rule 110 implementations
│   ├── paradox_demo.cstack
│   └── ...
├── tests/              # 142 comprehensive tests
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_interpreter.py
│   ├── test_timeline.py
│   └── test_repl.py
└── main.py            # Entry point
```

## Testing

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=chronostack

# Specific test file
uv run pytest tests/test_timeline.py -v
```

Current test coverage: **78%** with 142 tests passing.

## Advanced Features

### Fixed-Point Paradox Resolution
ChronoStack implements a sophisticated algorithm to resolve temporal paradoxes:
1. Detects circular causality loops
2. Attempts multiple resolution strategies
3. Finds fixed points where sent values equal computed values
4. Ensures timeline consistency

### ASCII Tree Visualization
Beautiful timeline visualization for complex branching:
```
Timeline Tree:

└── main (3 moments)
    │    M0: [10]
    │    M1: [10 20]
    ├── experiment-a (2 moments) (from main@1)
    │   │    M1: [10 20 900]
    │   └── experiment-b (1 moment) (from experiment-a@1)
    │        │    M1: [10 20 450]
    └── comparison (1 moment) (from main@2) [P:1] <-- current
         │    M2: [10 20 3000] [PARADOX]
```

### Temporal Query Language
SQL-like queries for timeline analysis:
```chronostack
.query moments where paradox     # Find all paradoxes
.query values > 100             # Find moments with values > 100
.query branch experiment-a      # Examine specific branch
.query max                      # Find maximum values across timeline
```

## Contributing

ChronoStack is an experimental language exploring the intersection of stack-based programming and temporal computation. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Inspired by Forth and concatenative programming languages
- Temporal mechanics influenced by science fiction time travel concepts
- Rule 110 proving Turing completeness (Matthew Cook, 2004)
- Built with Python 3.8+ using only standard library modules

## Roadmap

- [x] Core interpreter with temporal mechanics
- [x] Fixed-point paradox resolution
- [x] ASCII tree visualization
- [x] Temporal query language
- [x] Debug mode with breakpoints
- [x] Rule 110 implementation
- [ ] Visual timeline browser (web-based)
- [ ] More paradox resolution strategies
- [ ] Quantum superposition operations
- [ ] Temporal optimization compiler

---

**ChronoStack**: Where computation meets time travel.

*"The future influences the past as much as the past influences the future."*