"""
Timeline management for ChronoStack - handles temporal stack states and time travel.

The Timeline class manages multiple moments in time, each containing a stack state.
It supports:
- Creating new moments (advancing time)
- Rewinding to previous moments
- Branching to create alternate timelines
- Merging timelines
- Paradox detection and resolution
"""

import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Moment:
    """A single moment in time containing a stack state and metadata."""

    stack: List[Any]
    timestamp: int
    parent: Optional["Moment"] = None
    branch_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    branch_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "Moment":
        """Create a deep copy of this moment."""
        return Moment(
            stack=deepcopy(self.stack),
            timestamp=self.timestamp,
            parent=self.parent,  # Keep same parent reference
            branch_id=self.branch_id,
            branch_name=self.branch_name,
            metadata=deepcopy(self.metadata),
        )


class Timeline:
    """Manages temporal stack states and time travel operations."""

    def __init__(self):
        # Create initial moment with empty stack
        initial_moment = Moment(stack=[], timestamp=0, branch_name="main")
        self.moments: List[Moment] = [initial_moment]
        self.current_index: int = 0
        self.branches: Dict[str, List[Moment]] = {"main": self.moments}
        self.current_branch: str = "main"
        self.paradox_count: int = 0

    def current_moment(self) -> Moment:
        """Get the current moment."""
        return self.moments[self.current_index]

    def current_stack(self) -> List[Any]:
        """Get the current stack (reference to the actual stack)."""
        return self.current_moment().stack

    def tick(self) -> int:
        """Save current stack state and advance to a new moment in time."""
        # Create new moment based on current state
        current = self.current_moment()
        new_moment = Moment(
            stack=deepcopy(current.stack),
            timestamp=len(self.moments),
            parent=current,
            branch_id=current.branch_id,
            branch_name=current.branch_name,
        )

        self.moments.append(new_moment)
        self.current_index = len(self.moments) - 1

        # Update branch tracking (only if this moment list is different from branch list)
        if self.moments is not self.branches[self.current_branch]:
            self.branches[self.current_branch].append(new_moment)

        return new_moment.timestamp

    def rewind(self, steps: int = 1) -> int:
        """Go back n moments in time. Returns the new current timestamp."""
        if steps <= 0:
            return self.current_moment().timestamp

        # Can't rewind before the beginning
        new_index = max(0, self.current_index - steps)
        self.current_index = new_index

        return self.current_moment().timestamp

    def peek_future(self, steps: int = 1) -> Optional[Moment]:
        """Look ahead n moments. Creates speculative branch if future doesn't exist."""
        if steps <= 0:
            return self.current_moment()

        target_index = self.current_index + steps

        # If future exists, return it
        if target_index < len(self.moments):
            return self.moments[target_index]

        # Create speculative branch for the future
        return self._create_speculative_future(steps)

    def _create_speculative_future(self, steps: int) -> Moment:
        """Create a speculative future state by branching."""
        # Store current state
        original_branch = self.current_branch
        original_index = self.current_index
        
        # Create a speculative branch
        branch_name = f"speculative-{uuid.uuid4().hex[:8]}"
        self.branch(branch_name)

        # Advance to the desired future step by creating empty moments
        for _ in range(steps):
            # Create empty future moment
            current_stack = deepcopy(self.current_stack())
            self.tick()

        future_moment = self.current_moment()

        # Return to the original timeline position
        self.current_branch = original_branch
        self.moments = self.branches[original_branch]
        self.current_index = original_index

        return future_moment

    def branch(self, branch_name: Optional[str] = None) -> str:
        """Create a new timeline branch from the current moment."""
        if branch_name is None:
            branch_name = f"branch-{len(self.branches)}"

        # Create new branch starting from current moment
        current = self.current_moment()
        branch_start = current.copy()
        branch_start.branch_name = branch_name
        branch_start.branch_id = str(uuid.uuid4())[:8]

        # Create new branch with the starting moment
        new_branch_moments = [branch_start]
        self.branches[branch_name] = new_branch_moments

        # Switch to new branch
        self.current_branch = branch_name
        self.moments = new_branch_moments
        self.current_index = 0

        return branch_name

    def merge(self, source_branch: Optional[str] = None) -> bool:
        """Merge current branch back into its parent (or main branch)."""
        if self.current_branch == "main":
            return False  # Can't merge main branch

        if source_branch is None:
            source_branch = "main"  # Default to merging into main

        if source_branch not in self.branches:
            return False

        # Get the changes from current branch
        current_moment = self.current_moment()
        target_branch = self.branches[source_branch]

        # Find insertion point in target branch
        # For simplicity, merge at the end of target branch
        merged_moment = current_moment.copy()
        merged_moment.branch_name = source_branch
        merged_moment.timestamp = len(target_branch)

        target_branch.append(merged_moment)

        # Switch back to target branch
        self.current_branch = source_branch
        self.moments = target_branch
        self.current_index = len(target_branch) - 1

        return True

    def echo(self, steps_back: int) -> Any:
        """Copy a value from n moments ago."""
        if steps_back <= 0 or steps_back > self.current_index:
            return None

        past_index = self.current_index - steps_back
        past_moment = self.moments[past_index]

        if not past_moment.stack:
            return None

        return deepcopy(past_moment.stack[-1])  # Copy top value

    def send(self, value: Any, steps_back: int) -> bool:
        """Send a value back in time, potentially creating paradoxes."""
        if steps_back <= 0 or steps_back > self.current_index:
            return False

        target_index = self.current_index - steps_back
        target_moment = self.moments[target_index]

        # Store original value for paradox detection
        original_stack = deepcopy(target_moment.stack)

        # Send the value back
        target_moment.stack.append(deepcopy(value))

        # Check for paradox
        if self._would_create_paradox(target_index, original_stack):
            self.paradox_count += 1
            # Store paradox information
            target_moment.metadata["paradox"] = {
                "original_stack": original_stack,
                "sent_value": value,
                "sent_from_moment": self.current_index,
            }

        return True

    def _would_create_paradox(self, modified_index: int, original_stack: List[Any]) -> bool:  # noqa: ARG002
        """Check if modifying a past moment would create a paradox."""
        # Simple paradox detection: if the change would affect the computation
        # that led to sending the value, it's a paradox

        # For now, consider any change to past stack as potential paradox
        # More sophisticated logic could track data dependencies
        return True  # Conservative approach

    def detect_paradoxes(self) -> List[Tuple[int, Dict[str, Any]]]:
        """Find all paradoxes in the timeline."""
        paradoxes = []
        for i, moment in enumerate(self.moments):
            if "paradox" in moment.metadata:
                paradoxes.append((i, moment.metadata["paradox"]))
        return paradoxes

    def resolve_paradox(self, moment_index: int, strategy: str = "stable") -> bool:
        """Resolve a paradox using the specified strategy."""
        if moment_index >= len(self.moments):
            return False

        moment = self.moments[moment_index]
        if "paradox" not in moment.metadata:
            return False  # No paradox to resolve

        paradox_info = moment.metadata["paradox"]

        if strategy == "stable":
            # Keep the timeline that's most stable (fewest changes)
            # For now, keep the original timeline
            moment.stack = paradox_info["original_stack"]

        elif strategy == "accept":
            # Accept the change and recalculate
            # The sent value is already in the stack, so we keep it
            pass

        elif strategy == "fixed_point":
            # Find a fixed point where sent value equals computed value
            resolved_stack = self._resolve_fixed_point_paradox(
                moment_index, 
                paradox_info["sent_value"], 
                paradox_info["sent_from_moment"],
                paradox_info["original_stack"]
            )
            moment.stack = resolved_stack

        # Remove paradox marker
        del moment.metadata["paradox"]
        self.paradox_count -= 1

        return True

    def has_paradoxes(self) -> bool:
        """Check if timeline has any unresolved paradoxes."""
        return self.paradox_count > 0

    def _resolve_fixed_point_paradox(
        self, 
        moment_index: int, 
        sent_value: Any, 
        sent_from_moment: int,
        original_stack: List[Any],
        max_iterations: int = 100
    ) -> List[Any]:
        """
        Resolve a temporal paradox using fixed-point iteration.
        
        MATHEMATICAL FOUNDATION:
        ========================
        A temporal paradox occurs when a value sent to the past changes the computation
        that led to sending that value. A fixed point x satisfies: f(x) = x, where
        f represents the temporal computation from the modified moment to the sending moment.
        
        ALGORITHM:
        ==========
        1. Initialize with candidate stack = original_stack + [sent_value]
        2. Simulate computation f(candidate) to get computed_value  
        3. Check convergence: |computed_value - sent_value| < tolerance
        4. If not converged:
           a. Detect cycles in stack states to prevent infinite loops
           b. Apply gradient-based adjustment: stack' = adjust(stack, error, iteration)
           c. Repeat from step 2
        5. Return converged stack or fallback to original if max iterations reached
        
        CONVERGENCE PROPERTIES:
        ======================= 
        - Guaranteed termination via max_iterations limit
        - Cycle detection prevents infinite loops in state space
        - Gradient adjustment uses decreasing step size for stability
        - Numeric convergence tolerance handles floating-point precision
        - Fallback to original stack ensures mathematical consistency
        
        EXAMPLES OF FIXED POINTS:
        =========================
        - Simple: send value x, computation returns x → immediate convergence
        - Mathematical: send 5 to moment with [2, 3], if computation does 2+3=5 → fixed point
        - Convergent: iterative adjustment converges to stable value
        - Divergent: cycles detected, fallback to stable original state
        
        Args:
            moment_index: Index of moment containing the paradox
            sent_value: The value that was sent back in time
            sent_from_moment: The moment index that performed the send operation
            original_stack: The original stack state before temporal modification
            max_iterations: Maximum iterations to prevent infinite computation (default: 100)
            
        Returns:
            List[Any]: The resolved stack state that eliminates the paradox
            
        Raises:
            No exceptions - algorithm is designed to always return a valid stack state
            
        Time Complexity: O(max_iterations × stack_simulation_cost)
        Space Complexity: O(max_iterations × stack_size) for cycle detection
        """
        # Track convergence history to detect cycles
        seen_states = []
        current_stack = deepcopy(original_stack)
        
        for iteration in range(max_iterations):
            # Create candidate stack with sent value
            candidate_stack = deepcopy(current_stack) + [deepcopy(sent_value)]
            
            # Simulate the computation path from modified moment to sending moment
            computed_value = self._simulate_computation_to_send(
                moment_index, 
                sent_from_moment, 
                candidate_stack
            )
            
            # Check for fixed point: computed value should equal sent value
            if self._values_equal(computed_value, sent_value):
                # Fixed point found!
                return candidate_stack
            
            # Check for cycles (same stack state seen before)
            stack_signature = self._get_stack_signature(candidate_stack)
            if stack_signature in seen_states:
                # Cycle detected - no fixed point exists
                # Use the best approximation found so far
                return self._find_best_approximation(
                    original_stack, sent_value, seen_states
                )
            
            seen_states.append(stack_signature)
            
            # Adjust the stack for next iteration using gradient approach
            current_stack = self._adjust_stack_for_convergence(
                current_stack, 
                sent_value, 
                computed_value,
                iteration
            )
        
        # Max iterations reached - use stable fallback
        # Return the original stack as the most stable solution
        return deepcopy(original_stack)
    
    def _simulate_computation_to_send(
        self, 
        from_moment: int, 
        to_moment: int, 
        initial_stack: List[Any]
    ) -> Any:
        """
        Simulate what value would be computed and sent back to the past.
        
        This is a simplified simulation that models the typical pattern:
        the top value of the stack at the sending moment would be sent back.
        
        For a more complete implementation, this would need access to the 
        actual program AST to re-execute the computation path.
        """
        if to_moment <= from_moment:
            return None
            
        # Simplified computation: assume the value that gets sent is typically
        # the result of some computation on the values in the stack
        if not initial_stack:
            return None
            
        # Model common patterns in temporal programming:
        # 1. Simple passthrough - the sent value becomes the computed value
        # 2. Mathematical operations on stack values
        if len(initial_stack) == 1:
            return initial_stack[0]
        elif len(initial_stack) >= 2:
            # Simulate a common pattern: arithmetic operation on top two values
            try:
                a, b = initial_stack[-2], initial_stack[-1]
                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    # Use addition as the default operation simulation
                    return a + b
                else:
                    return b  # Return top value if not numeric
            except (IndexError, TypeError):
                return initial_stack[-1] if initial_stack else None
        
        return initial_stack[-1] if initial_stack else None
    
    def _values_equal(self, value1: Any, value2: Any, tolerance: float = 1e-10) -> bool:
        """Check if two values are equal within tolerance for numeric values."""
        if value1 is None and value2 is None:
            return True
        if value1 is None or value2 is None:
            return False
            
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            return abs(float(value1) - float(value2)) < tolerance
        else:
            return value1 == value2
    
    def _get_stack_signature(self, stack: List[Any]) -> str:
        """Get a string signature of the stack state for cycle detection."""
        try:
            return str(tuple(
                item if not isinstance(item, (list, dict)) else str(item) 
                for item in stack
            ))
        except (TypeError, RecursionError):
            # Fallback for unhashable types
            return str(len(stack))
    
    def _adjust_stack_for_convergence(
        self, 
        current_stack: List[Any], 
        target_value: Any, 
        computed_value: Any,
        iteration: int
    ) -> List[Any]:
        """
        Adjust the stack state to move toward convergence.
        
        Uses a simple gradient-like approach for numeric values.
        """
        if not current_stack:
            return [deepcopy(target_value)]
            
        adjusted_stack = deepcopy(current_stack)
        
        # If we have numeric values, try to adjust toward the target
        if (isinstance(target_value, (int, float)) and 
            isinstance(computed_value, (int, float)) and 
            len(adjusted_stack) > 0):
            
            # Simple adjustment: move the last value toward target
            if isinstance(adjusted_stack[-1], (int, float)):
                error = target_value - computed_value
                # Use decreasing step size to help convergence
                step_size = 0.5 / (iteration + 1)
                adjustment = error * step_size
                adjusted_stack[-1] += adjustment
        
        return adjusted_stack
    
    def _find_best_approximation(
        self, 
        original_stack: List[Any], 
        sent_value: Any, 
        seen_states: List[str]
    ) -> List[Any]:
        """
        Find the best approximation when no exact fixed point exists.
        
        For now, return the original stack as the most stable choice.
        """
        # In a more sophisticated implementation, this could:
        # 1. Find the state that minimizes the error
        # 2. Choose the state closest to the original
        # 3. Use domain-specific heuristics
        
        return deepcopy(original_stack)

    def get_timeline_info(self) -> Dict[str, Any]:
        """Get information about the current timeline state."""
        return {
            "current_moment": self.current_index,
            "total_moments": len(self.moments),
            "current_branch": self.current_branch,
            "branch_count": len(self.branches),
            "paradox_count": self.paradox_count,
            "stack_size": len(self.current_stack()),
        }

    def get_branch_info(self) -> Dict[str, Any]:
        """Get information about all branches."""
        branch_info = {}
        for branch_name, branch_moments in self.branches.items():
            branch_info[branch_name] = {
                "moment_count": len(branch_moments),
                "current": branch_name == self.current_branch,
                "branch_id": branch_moments[0].branch_id if branch_moments else None,
            }
        return branch_info

    def temporal_fold(self, operation: str) -> List[Any]:
        """Apply an operation across all moments in the timeline."""
        results = []
        for moment in self.moments:
            if moment.stack:
                if operation == "sum":
                    # Sum all numeric values in the stack
                    numeric_values = [x for x in moment.stack if isinstance(x, (int, float))]
                    results.append(sum(numeric_values) if numeric_values else 0)
                elif operation == "count":
                    results.append(len(moment.stack))
                elif operation == "max":
                    numeric_values = [x for x in moment.stack if isinstance(x, (int, float))]
                    results.append(max(numeric_values) if numeric_values else 0)
                elif operation == "min":
                    numeric_values = [x for x in moment.stack if isinstance(x, (int, float))]
                    results.append(min(numeric_values) if numeric_values else 0)
                elif operation == "top":
                    results.append(moment.stack[-1])
                elif operation == "bottom":
                    results.append(moment.stack[0])
                elif operation == "reverse":
                    results.append(list(reversed(moment.stack)))
                elif operation == "duplicate":
                    results.append(moment.stack + moment.stack)
                elif operation == "length":
                    if moment.stack and isinstance(moment.stack[-1], (str, list)):
                        results.append(len(moment.stack[-1]))
                    else:
                        results.append(0)
                elif operation == "+":
                    # Apply + operation to consecutive pairs in stack
                    if len(moment.stack) >= 2:
                        total = 0
                        for i in range(0, len(moment.stack) - 1, 2):
                            if isinstance(moment.stack[i], (int, float)) and isinstance(moment.stack[i+1], (int, float)):
                                total += moment.stack[i] + moment.stack[i+1]
                        results.append(total)
                    else:
                        results.append(0)
                elif operation == "*":
                    # Multiply all numeric values in the stack
                    numeric_values = [x for x in moment.stack if isinstance(x, (int, float))]
                    if numeric_values:
                        product = 1
                        for val in numeric_values:
                            product *= val
                        results.append(product)
                    else:
                        results.append(0)
                else:
                    # Default: get top value or apply custom operation
                    results.append(moment.stack[-1] if moment.stack else None)
            else:
                # Empty stack handling
                if operation in ["sum", "count", "max", "min", "*", "+"]:
                    results.append(0)  # Numeric operations default to 0
                elif operation == "length":
                    results.append(0)
                else:
                    results.append(None)  # Other operations return None for empty stacks

        return results

    def ripple(self, operation: str, value: Any) -> None:
        """Apply an operation to all future moments from current point."""
        for i in range(self.current_index + 1, len(self.moments)):
            moment = self.moments[i]
            
            if operation == "push":
                moment.stack.append(deepcopy(value))
            elif operation == "pop" and moment.stack:
                moment.stack.pop()
            elif operation == "clear":
                moment.stack.clear()
            elif operation == "reverse":
                moment.stack.reverse()
            elif operation == "duplicate" and moment.stack:
                moment.stack.append(deepcopy(moment.stack[-1]))
            elif operation == "multiply" and moment.stack and isinstance(value, (int, float)):
                # Multiply top value if numeric
                if isinstance(moment.stack[-1], (int, float)):
                    moment.stack[-1] *= value
            elif operation == "add" and moment.stack and isinstance(value, (int, float)):
                # Add to top value if numeric
                if isinstance(moment.stack[-1], (int, float)):
                    moment.stack[-1] += value
            elif operation == "subtract" and moment.stack and isinstance(value, (int, float)):
                # Subtract from top value if numeric
                if isinstance(moment.stack[-1], (int, float)):
                    moment.stack[-1] -= value
            elif operation == "divide" and moment.stack and isinstance(value, (int, float)) and value != 0:
                # Divide top value if numeric and non-zero divisor
                if isinstance(moment.stack[-1], (int, float)):
                    moment.stack[-1] /= value
            elif operation == "append" and moment.stack and isinstance(value, str):
                # Append to string if top value is string
                if isinstance(moment.stack[-1], str):
                    moment.stack[-1] += value
            elif operation == "replace":
                # Replace top value with new value
                if moment.stack:
                    moment.stack[-1] = deepcopy(value)
            elif operation == "swap" and len(moment.stack) >= 2:
                # Swap top two values
                moment.stack[-1], moment.stack[-2] = moment.stack[-2], moment.stack[-1]
