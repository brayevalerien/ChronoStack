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
        # Create a speculative branch
        branch_name = f"speculative-{uuid.uuid4().hex[:8]}"
        self.branch(branch_name)

        # Advance to the desired future step
        for _ in range(steps):
            self.tick()

        future_moment = self.current_moment()

        # Return to the original timeline position
        self.current_branch = "main"
        self.current_index = self.current_index - steps

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
            # This is complex and would require re-execution
            # For now, fall back to stable strategy
            moment.stack = paradox_info["original_stack"]

        # Remove paradox marker
        del moment.metadata["paradox"]
        self.paradox_count -= 1

        return True

    def has_paradoxes(self) -> bool:
        """Check if timeline has any unresolved paradoxes."""
        return self.paradox_count > 0

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
                    if all(isinstance(x, (int, float)) for x in moment.stack):
                        results.append(sum(moment.stack))
                elif operation == "count":
                    results.append(len(moment.stack))
                elif operation == "max":
                    if all(isinstance(x, (int, float)) for x in moment.stack):
                        results.append(max(moment.stack))
                elif operation == "min":
                    if all(isinstance(x, (int, float)) for x in moment.stack):
                        results.append(min(moment.stack))
                else:
                    results.append(moment.stack[-1])  # Default: get top value
            else:
                results.append(0)  # Empty stack contributes 0

        return results

    def ripple(self, operation: str, value: Any) -> None:
        """Apply an operation to all future moments from current point."""
        for i in range(self.current_index + 1, len(self.moments)):
            moment = self.moments[i]
            if operation == "push":
                moment.stack.append(deepcopy(value))
            elif (operation == "multiply" and moment.stack
                  and isinstance(moment.stack[-1], (int, float)) and isinstance(value, (int, float))):
                moment.stack[-1] *= value
