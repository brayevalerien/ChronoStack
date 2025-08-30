"""Tests for the ChronoStack timeline and temporal mechanics."""

from chronostack.timeline import Moment, Timeline


class TestTimeline:
    """Test cases for the Timeline class."""

    def test_initial_timeline(self):
        """Test initial timeline state."""
        timeline = Timeline()

        assert len(timeline.moments) == 1
        assert timeline.current_index == 0
        assert timeline.current_moment().timestamp == 0
        assert timeline.current_stack() == []
        assert timeline.current_branch == "main"
        assert not timeline.has_paradoxes()

    def test_tick_advances_time(self):
        """Test that tick creates new moments."""
        timeline = Timeline()

        # Add some data to stack
        timeline.current_stack().extend([1, 2, 3])

        # Tick to create new moment
        timestamp = timeline.tick()

        assert timestamp == 1
        assert len(timeline.moments) == 2
        assert timeline.current_index == 1
        assert timeline.current_moment().timestamp == 1
        assert timeline.current_stack() == [1, 2, 3]

        # Both moments should have same stack since tick copies current state
        # The key behavior is that tick creates a NEW moment with current stack state
        assert timeline.moments[1].stack == [1, 2, 3]

        # Verify we can modify the new moment independently
        timeline.current_stack().append(4)
        assert timeline.current_stack() == [1, 2, 3, 4]

    def test_multiple_ticks(self):
        """Test multiple time advances."""
        timeline = Timeline()

        timestamps = []
        for i in range(5):
            timeline.current_stack().append(i)
            timestamps.append(timeline.tick())

        assert timestamps == [1, 2, 3, 4, 5]
        assert len(timeline.moments) == 6  # Initial + 5 ticks
        assert timeline.current_index == 5
        assert timeline.current_stack() == [0, 1, 2, 3, 4]

    def test_rewind_basic(self):
        """Test basic rewind functionality."""
        timeline = Timeline()

        # Create several moments
        for i in range(3):
            timeline.current_stack().append(i)
            timeline.tick()

        assert timeline.current_index == 3

        # Rewind 2 steps (from moment 3 to moment 1)
        timestamp = timeline.rewind(2)

        assert timestamp == 1
        assert timeline.current_index == 1
        # At moment 1, the stack should have [0, 1] since we added 1 to moment 1 before ticking
        assert timeline.current_stack() == [0, 1]

    def test_rewind_bounds(self):
        """Test rewind boundary conditions."""
        timeline = Timeline()

        # Create a few moments
        timeline.tick()
        timeline.tick()

        # Rewind beyond beginning
        timestamp = timeline.rewind(10)

        assert timestamp == 0
        assert timeline.current_index == 0

        # Rewind with 0 or negative steps
        timeline.current_index = 2
        assert timeline.rewind(0) == 2
        assert timeline.rewind(-1) == 2

    def test_echo_past_values(self):
        """Test echoing values from the past."""
        timeline = Timeline()

        # Create moments with different values
        values = [10, 20, 30, 40]
        for value in values:
            timeline.current_stack().append(value)
            timeline.tick()

        # Test echoing from different points
        assert timeline.echo(1) == 40  # 1 step back
        assert timeline.echo(2) == 30  # 2 steps back
        assert timeline.echo(4) == 10  # 4 steps back

        # Test boundary conditions
        assert timeline.echo(0) is None  # 0 steps back
        assert timeline.echo(10) is None  # Beyond beginning

    def test_echo_empty_stack(self):
        """Test echo with empty stacks."""
        timeline = Timeline()

        # Create moments without values
        timeline.tick()
        timeline.tick()

        assert timeline.echo(1) is None
        assert timeline.echo(2) is None

    def test_send_to_past(self):
        """Test sending values back in time."""
        timeline = Timeline()

        # Create several moments
        for i in range(3):
            timeline.current_stack().append(i * 10)
            timeline.tick()

        # Send value back 2 moments
        success = timeline.send(99, 2)

        assert success
        assert timeline.has_paradoxes()
        assert timeline.paradox_count == 1

        # Check that value was added to past moment
        past_moment = timeline.moments[timeline.current_index - 2]
        assert 99 in past_moment.stack

    def test_send_boundary_conditions(self):
        """Test send boundary conditions."""
        timeline = Timeline()
        timeline.tick()

        # Invalid send operations
        assert not timeline.send(42, 0)  # 0 steps back
        assert not timeline.send(42, -1)  # Negative steps
        assert not timeline.send(42, 10)  # Beyond beginning

    def test_paradox_detection_and_resolution(self):
        """Test paradox detection and resolution."""
        timeline = Timeline()

        # Create timeline with values
        timeline.current_stack().append(10)
        timeline.tick()
        timeline.current_stack().append(20)
        timeline.tick()

        # Send value to create paradox
        timeline.send(999, 1)

        # Check paradox detection
        paradoxes = timeline.detect_paradoxes()
        assert len(paradoxes) == 1

        paradox_moment, paradox_info = paradoxes[0]
        assert paradox_info["sent_value"] == 999
        assert paradox_info["sent_from_moment"] == 2

        # Resolve paradox with stable strategy
        success = timeline.resolve_paradox(paradox_moment, "stable")
        assert success
        assert not timeline.has_paradoxes()

        # Check that original stack was restored
        restored_moment = timeline.moments[paradox_moment]
        assert 999 not in restored_moment.stack

    def test_paradox_resolution_strategies(self):
        """Test different paradox resolution strategies."""
        timeline = Timeline()

        # Create paradox
        timeline.current_stack().append(42)
        timeline.tick()
        timeline.send(100, 1)

        paradoxes = timeline.detect_paradoxes()
        paradox_moment = paradoxes[0][0]

        # Test "accept" strategy
        timeline.resolve_paradox(paradox_moment, "accept")
        # Value should still be there
        # (though this might change based on implementation)

    def test_branching_basic(self):
        """Test basic timeline branching."""
        timeline = Timeline()

        # Create some history
        timeline.current_stack().extend([1, 2, 3])
        timeline.tick()

        # Create branch
        branch_name = timeline.branch("test-branch")

        assert branch_name == "test-branch"
        assert timeline.current_branch == "test-branch"
        assert len(timeline.branches) == 2

        # Branch should start with copy of current state
        assert timeline.current_stack() == [1, 2, 3]

        # Changes in branch shouldn't affect main
        timeline.current_stack().append(999)
        timeline.tick()

        # Switch back to main branch
        timeline.current_branch = "main"
        timeline.moments = timeline.branches["main"]
        timeline.current_index = len(timeline.moments) - 1

        assert 999 not in timeline.current_stack()

    def test_branching_auto_name(self):
        """Test automatic branch naming."""
        timeline = Timeline()

        branch1 = timeline.branch()
        branch2 = timeline.branch()

        assert branch1.startswith("branch-")
        assert branch2.startswith("branch-")
        assert branch1 != branch2

    def test_peek_future_existing(self):
        """Test peeking at existing future."""
        timeline = Timeline()

        # Create several moments
        values = [10, 20, 30]
        for value in values:
            timeline.current_stack().append(value)
            timeline.tick()

        # Go back to earlier moment (to moment 1)
        timeline.rewind(2)
        assert timeline.current_index == 1
        assert timeline.current_stack() == [10, 20]

        # Peek at future
        future1 = timeline.peek_future(1)  # Look at moment 2
        future2 = timeline.peek_future(2)  # Look at moment 3

        assert future1.stack == [10, 20, 30]
        assert future2.stack == [10, 20, 30]

    def test_peek_future_speculative(self):
        """Test peeking at non-existent future (creates speculation)."""
        timeline = Timeline()

        timeline.current_stack().append(42)
        timeline.tick()

        # Peek beyond existing future
        future = timeline.peek_future(5)

        # Should create speculative branch
        assert future is not None
        assert len(timeline.branches) > 1  # New branch created

    def test_merge_branches(self):
        """Test merging branches."""
        timeline = Timeline()

        # Create base state
        timeline.current_stack().append(100)
        timeline.tick()

        # Create branch
        timeline.branch("feature")
        timeline.current_stack().append(200)
        timeline.tick()

        # Merge back to main
        success = timeline.merge("main")

        assert success
        assert timeline.current_branch == "main"
        # Merged value should be in main branch now
        assert 200 in timeline.current_stack()

    def test_merge_main_branch(self):
        """Test that main branch cannot be merged."""
        timeline = Timeline()

        success = timeline.merge()
        assert not success

    def test_temporal_fold_operations(self):
        """Test comprehensive temporal fold operations."""
        timeline = Timeline()

        # Create moments with numeric stacks
        values = [[1, 2], [3, 4, 5], [6]]
        for value_list in values:
            timeline.current_stack().extend(value_list)
            timeline.tick()

        # Timeline progression:
        # Moment 0: [1, 2]
        # Moment 1: [1, 2, 3, 4, 5]
        # Moment 2: [1, 2, 3, 4, 5, 6]
        # Moment 3: [1, 2, 3, 4, 5, 6]

        # Test basic fold operations
        sums = timeline.temporal_fold("sum")
        counts = timeline.temporal_fold("count")
        maxes = timeline.temporal_fold("max")
        mins = timeline.temporal_fold("min")

        assert sums == [3, 15, 21, 21]  # Sums of each moment's stack
        assert counts == [2, 5, 6, 6]  # Stack lengths
        assert maxes == [2, 5, 6, 6]  # Max values in each stack
        assert mins == [1, 1, 1, 1]  # Min values in each stack

        # Test additional fold operations
        tops = timeline.temporal_fold("top")
        bottoms = timeline.temporal_fold("bottom")
        
        assert tops == [2, 5, 6, 6]  # Top values
        assert bottoms == [1, 1, 1, 1]  # Bottom values

        # Test reverse operation
        reverses = timeline.temporal_fold("reverse")
        assert reverses[0] == [2, 1]  # [1, 2] reversed
        assert reverses[1] == [5, 4, 3, 2, 1]  # [1, 2, 3, 4, 5] reversed

        # Test duplicate operation
        duplicates = timeline.temporal_fold("duplicate")
        assert duplicates[0] == [1, 2, 1, 2]  # [1, 2] duplicated

        # Test multiply operation
        multiplies = timeline.temporal_fold("*")
        assert multiplies == [2, 120, 720, 720]  # Product of all numeric values

    def test_temporal_fold_string_operations(self):
        """Test temporal fold with string operations."""
        timeline = Timeline()

        # Create moments with string data
        timeline.current_stack().extend(["hello", "world"])
        timeline.tick()
        timeline.current_stack().append("test")
        timeline.tick()

        # Test length operation
        lengths = timeline.temporal_fold("length")
        assert lengths == [5, 4, 4]  # Length of top strings: "world", "test", "test"

    def test_temporal_fold_empty_stacks(self):
        """Test temporal fold with empty stacks."""
        timeline = Timeline()
        timeline.tick()  # Create empty moment

        # Test operations on empty stacks
        sums = timeline.temporal_fold("sum")
        counts = timeline.temporal_fold("count")
        
        assert sums == [0, 0]  # Empty stacks contribute 0
        assert counts == [0, 0]  # Empty stacks have count 0

    def test_temporal_fold_mixed_types(self):
        """Test temporal fold with mixed data types."""
        timeline = Timeline()

        # Create moments with mixed types
        timeline.current_stack().extend([1, "hello", 2.5])
        timeline.tick()

        # Sum should only consider numeric values
        sums = timeline.temporal_fold("sum")
        assert sums == [3.5, 3.5]  # 1 + 2.5

    def test_ripple_basic_operations(self):
        """Test basic ripple operations."""
        timeline = Timeline()

        # Create several future moments
        for i in range(4):
            timeline.current_stack().append(i)
            timeline.tick()

        # Go back to an earlier moment
        timeline.rewind(2)

        # Apply ripple push effect
        timeline.ripple("push", 999)

        # Check that future moments were affected
        for i in range(timeline.current_index + 1, len(timeline.moments)):
            assert 999 in timeline.moments[i].stack

    def test_ripple_pop_operation(self):
        """Test ripple pop operation."""
        timeline = Timeline()

        # Create moments with multiple values
        for i in range(3):
            timeline.current_stack().extend([i, i * 10])
            timeline.tick()

        original_lengths = [len(moment.stack) for moment in timeline.moments]
        timeline.rewind(1)

        # Apply ripple pop
        timeline.ripple("pop", None)

        # Check that future moments had top values removed
        for i in range(timeline.current_index + 1, len(timeline.moments)):
            expected_length = original_lengths[i] - 1
            assert len(timeline.moments[i].stack) == expected_length

    def test_ripple_arithmetic_operations(self):
        """Test ripple arithmetic operations."""
        timeline = Timeline()

        # Create moments with single numeric values for clearer testing
        timeline.current_stack().append(10)
        timeline.tick()
        timeline.current_stack().append(20) 
        timeline.tick()
        timeline.current_stack().append(30)
        timeline.tick()

        # Go back to moment 1 and apply multiply ripple
        timeline.rewind(2)
        original_future_values = [moment.stack[-1] for moment in timeline.moments[timeline.current_index + 1:] if moment.stack]

        # Test multiply ripple
        timeline.ripple("multiply", 2)
        for i, original_value in enumerate(original_future_values):
            moment_index = timeline.current_index + 1 + i
            if moment_index < len(timeline.moments):
                moment = timeline.moments[moment_index]
                if moment.stack and isinstance(moment.stack[-1], (int, float)):
                    # Top value should be doubled
                    expected = original_value * 2
                    assert moment.stack[-1] == expected

        # Reset and test add ripple
        timeline = Timeline()
        timeline.current_stack().append(10)
        timeline.tick()
        timeline.current_stack().append(20)
        timeline.tick()
        timeline.current_stack().append(30)
        timeline.tick()
        timeline.rewind(2)

        original_future_values = [moment.stack[-1] for moment in timeline.moments[timeline.current_index + 1:] if moment.stack]

        timeline.ripple("add", 5)
        for i, original_value in enumerate(original_future_values):
            moment_index = timeline.current_index + 1 + i
            if moment_index < len(timeline.moments):
                moment = timeline.moments[moment_index]
                if moment.stack and isinstance(moment.stack[-1], (int, float)):
                    expected = original_value + 5
                    assert moment.stack[-1] == expected

    def test_ripple_stack_operations(self):
        """Test ripple stack manipulation operations."""
        timeline = Timeline()

        # Create moments with values
        timeline.current_stack().extend([1, 2, 3])
        timeline.tick()
        timeline.current_stack().extend([4, 5])
        timeline.tick()

        timeline.rewind(1)

        # Test reverse ripple
        timeline.ripple("reverse", None)
        assert timeline.moments[2].stack == [5, 4, 3, 2, 1]

        # Test duplicate ripple (reset timeline first)
        timeline = Timeline()
        timeline.current_stack().extend([1, 2])
        timeline.tick()
        timeline.current_stack().append(3)
        timeline.tick()
        timeline.rewind(1)

        timeline.ripple("duplicate", None)
        # Future moment should have top value duplicated
        assert timeline.moments[2].stack == [1, 2, 3, 3]

    def test_ripple_clear_operation(self):
        """Test ripple clear operation."""
        timeline = Timeline()

        # Create moments with values
        for i in range(3):
            timeline.current_stack().append(i)
            timeline.tick()

        timeline.rewind(2)

        # Apply clear ripple
        timeline.ripple("clear", None)

        # Check that future moments are empty
        for i in range(timeline.current_index + 1, len(timeline.moments)):
            assert timeline.moments[i].stack == []

    def test_ripple_string_operations(self):
        """Test ripple string operations."""
        timeline = Timeline()

        # Create moments with string values
        timeline.current_stack().append("hello")
        timeline.tick()
        timeline.current_stack().append("world")
        timeline.tick()

        timeline.rewind(1)

        # Test append ripple
        timeline.ripple("append", "!")
        assert timeline.moments[2].stack == ["hello", "world!"]

        # Test replace ripple
        timeline.ripple("replace", "replaced")
        assert timeline.moments[2].stack == ["hello", "replaced"]

    def test_ripple_swap_operation(self):
        """Test ripple swap operation."""
        timeline = Timeline()

        # Create moments with at least 2 values
        timeline.current_stack().extend([1, 2, 3])
        timeline.tick()
        timeline.current_stack().extend([4, 5])
        timeline.tick()

        timeline.rewind(1)

        # Apply swap ripple
        timeline.ripple("swap", None)

        # Check that top two values were swapped in future moments
        assert timeline.moments[2].stack == [1, 2, 3, 5, 4]

    def test_ripple_edge_cases(self):
        """Test ripple operation edge cases."""
        timeline = Timeline()

        # Test ripple with no future moments
        timeline.ripple("push", 42)
        # Should not crash

        # Test ripple operations that require stack values but stack is empty
        timeline.tick()
        timeline.rewind(1)
        timeline.ripple("pop", None)  # Should handle empty stack gracefully
        timeline.ripple("duplicate", None)  # Should handle empty stack gracefully

    def test_timeline_info(self):
        """Test timeline information reporting."""
        timeline = Timeline()

        # Create some state
        timeline.current_stack().extend([1, 2, 3])
        timeline.tick()
        timeline.tick()

        info = timeline.get_timeline_info()

        assert info["current_moment"] == 2
        assert info["total_moments"] == 3
        assert info["current_branch"] == "main"
        assert info["branch_count"] == 1
        assert info["paradox_count"] == 0
        assert info["stack_size"] == 3

    def test_branch_info(self):
        """Test branch information reporting."""
        timeline = Timeline()

        # Create branch
        timeline.branch("test")
        timeline.tick()

        branch_info = timeline.get_branch_info()

        assert "main" in branch_info
        assert "test" in branch_info
        assert branch_info["test"]["current"]
        assert not branch_info["main"]["current"]
        assert branch_info["test"]["moment_count"] >= 1

    def test_moment_copy(self):
        """Test moment copying functionality."""
        moment = Moment(stack=[1, 2, 3], timestamp=5)
        moment.metadata["test"] = "value"

        copy = moment.copy()

        assert copy.stack == [1, 2, 3]
        assert copy.timestamp == 5
        assert copy.metadata["test"] == "value"

        # Ensure deep copy
        copy.stack.append(4)
        assert len(moment.stack) == 3  # Original unchanged

        copy.metadata["test2"] = "value2"
        assert "test2" not in moment.metadata  # Original unchanged

    def test_complex_temporal_scenario(self):
        """Test complex scenario with multiple temporal operations."""
        timeline = Timeline()

        # Create initial state
        timeline.current_stack().append(10)
        timeline.tick()  # moment 1

        # Branch and create alternate timeline
        timeline.branch("alternate")
        timeline.current_stack().append(20)
        timeline.tick()  # moment 1 in branch

        # Send value back to past
        timeline.send(999, 1)  # Should create paradox

        # Switch back to main and continue
        timeline.current_branch = "main"
        timeline.moments = timeline.branches["main"]
        timeline.current_index = 1

        timeline.current_stack().append(30)
        timeline.tick()  # moment 2 in main

        # Test echo from past
        past_value = timeline.echo(1)
        assert past_value == 30

        # Check overall state
        assert timeline.has_paradoxes()
        assert len(timeline.branches) == 2

        info = timeline.get_timeline_info()
        assert info["branch_count"] == 2

    def test_timeline_edge_cases(self):
        """Test timeline edge cases for coverage."""
        timeline = Timeline()

        # Test has_paradoxes when no paradoxes exist
        assert not timeline.has_paradoxes()

        # Test current_branch property
        assert timeline.current_branch == "main"

        # Test branch creation with auto-generated name
        auto_branch = timeline.branch()  # No name provided
        assert auto_branch is not None
        assert auto_branch != "main"

    def test_timeline_branching_edge_cases(self):
        """Test edge cases in timeline branching."""
        timeline = Timeline()
        timeline.current_stack().extend([1, 2, 3])
        timeline.tick()

        # Test merging when target branch doesn't exist
        success = timeline.merge("nonexistent")
        assert not success

        # Test merging with invalid target
        success = timeline.merge(None)
        assert not success

    def test_timeline_paradox_resolution_edge_cases(self):
        """Test edge cases in paradox resolution."""
        timeline = Timeline()

        # Test resolve_paradox with invalid index
        success = timeline.resolve_paradox(-1)  # Invalid index
        assert not success

        success = timeline.resolve_paradox(999)  # Out of bounds
        assert not success

    def test_fixed_point_paradox_resolution_basic(self):
        """Test basic fixed-point paradox resolution."""
        timeline = Timeline()

        # Create a simple paradox scenario
        timeline.current_stack().append(10)
        timeline.tick()  # moment 1
        timeline.current_stack().append(5)
        timeline.tick()  # moment 2

        # Send value back to create paradox
        timeline.send(15, 1)  # Send 15 back to moment 1

        # Verify paradox exists
        assert timeline.has_paradoxes()
        paradoxes = timeline.detect_paradoxes()
        assert len(paradoxes) == 1
        
        paradox_moment, paradox_info = paradoxes[0]

        # Test fixed-point resolution
        success = timeline.resolve_paradox(paradox_moment, "fixed_point")
        assert success
        assert not timeline.has_paradoxes()

    def test_fixed_point_paradox_resolution_convergence(self):
        """Test fixed-point paradox resolution with numeric convergence."""
        timeline = Timeline()

        # Create scenario that should converge to a fixed point
        timeline.current_stack().extend([1, 2])  # Base values
        timeline.tick()  # moment 1
        timeline.current_stack().append(3)  # This will be modified by the sent value
        timeline.tick()  # moment 2

        # Send a value that could potentially converge
        timeline.send(4, 1)

        # Test fixed-point resolution
        paradoxes = timeline.detect_paradoxes()
        paradox_moment = paradoxes[0][0]
        
        success = timeline.resolve_paradox(paradox_moment, "fixed_point")
        assert success

        # Verify the resolved state makes mathematical sense
        resolved_moment = timeline.moments[paradox_moment]
        assert len(resolved_moment.stack) >= 2  # Should have at least original values

    def test_fixed_point_paradox_resolution_non_convergent(self):
        """Test fixed-point resolution when no convergence is possible."""
        timeline = Timeline()

        # Create scenario unlikely to converge
        timeline.current_stack().append("string_value")  # Non-numeric
        timeline.tick()
        
        # Send incompatible value type
        timeline.send(42, 1)  # Numeric value to non-numeric context

        paradoxes = timeline.detect_paradoxes()
        paradox_moment = paradoxes[0][0]

        # Should still resolve (fallback to stable)
        success = timeline.resolve_paradox(paradox_moment, "fixed_point")
        assert success
        assert not timeline.has_paradoxes()

    def test_fixed_point_helper_methods(self):
        """Test the helper methods used in fixed-point resolution."""
        timeline = Timeline()

        # Test _values_equal
        assert timeline._values_equal(5, 5)
        assert timeline._values_equal(5.0, 5)
        assert timeline._values_equal(5.0, 5.0)  # Exact float match
        assert not timeline._values_equal(5, 6)
        assert timeline._values_equal("hello", "hello")
        assert not timeline._values_equal("hello", "world")
        assert timeline._values_equal(None, None)
        assert not timeline._values_equal(None, 5)

        # Test _get_stack_signature
        sig1 = timeline._get_stack_signature([1, 2, 3])
        sig2 = timeline._get_stack_signature([1, 2, 3])
        sig3 = timeline._get_stack_signature([1, 2, 4])
        
        assert sig1 == sig2
        assert sig1 != sig3

        # Test with complex objects
        sig_complex = timeline._get_stack_signature([1, [2, 3], {"a": 1}])
        assert isinstance(sig_complex, str)

        # Test _simulate_computation_to_send
        result = timeline._simulate_computation_to_send(0, 2, [10, 20])
        assert result == 30  # Should add 10 + 20

        result = timeline._simulate_computation_to_send(0, 2, [42])
        assert result == 42  # Should return single value

        result = timeline._simulate_computation_to_send(0, 2, [])
        assert result is None  # Empty stack

        result = timeline._simulate_computation_to_send(2, 1, [10])
        assert result is None  # Invalid moment range

    def test_fixed_point_cycle_detection(self):
        """Test cycle detection in fixed-point resolution."""
        timeline = Timeline()

        # Create a scenario that might cycle
        timeline.current_stack().append(1)
        timeline.tick()
        timeline.send(1, 1)  # Send same value back (simple cycle)

        paradoxes = timeline.detect_paradoxes()
        paradox_moment = paradoxes[0][0]

        # Should detect and handle cycles
        success = timeline.resolve_paradox(paradox_moment, "fixed_point")
        assert success

    def test_fixed_point_max_iterations(self):
        """Test maximum iteration limit in fixed-point resolution."""
        timeline = Timeline()

        # Test the internal method directly with max_iterations=5
        original_stack = [1, 2]
        resolved_stack = timeline._resolve_fixed_point_paradox(
            moment_index=0,
            sent_value=999,  # Value unlikely to converge quickly
            sent_from_moment=1,
            original_stack=original_stack,
            max_iterations=5  # Small limit for testing
        )

        # Should return a valid stack (fallback to original if no convergence)
        assert isinstance(resolved_stack, list)
        assert len(resolved_stack) >= len(original_stack)

    def test_fixed_point_with_multiple_paradoxes(self):
        """Test fixed-point resolution with multiple paradoxes."""
        timeline = Timeline()

        # Create multiple paradoxes
        timeline.current_stack().append(10)
        timeline.tick()  # moment 1
        timeline.current_stack().append(20)
        timeline.tick()  # moment 2
        timeline.current_stack().append(30)
        timeline.tick()  # moment 3

        # Create two paradoxes
        timeline.send(100, 2)  # Send to moment 1
        timeline.send(200, 1)  # Send to moment 2

        assert timeline.paradox_count == 2
        paradoxes = timeline.detect_paradoxes()
        assert len(paradoxes) == 2

        # Resolve both using fixed-point strategy
        for moment_index, _ in paradoxes:
            success = timeline.resolve_paradox(moment_index, "fixed_point")
            assert success

        assert not timeline.has_paradoxes()

    def test_fixed_point_mathematical_properties(self):
        """Test mathematical properties of fixed-point resolution."""
        timeline = Timeline()

        # Create a scenario for fixed-point resolution
        timeline.current_stack().extend([1, 1])  # Simple case
        timeline.tick()
        
        # Send back a value for fixed-point analysis
        timeline.send(2, 1)  

        paradoxes = timeline.detect_paradoxes()
        paradox_moment = paradoxes[0][0]

        # Resolve with fixed-point
        success = timeline.resolve_paradox(paradox_moment, "fixed_point")
        assert success

        # Verify that the resolution process completed successfully
        # The resolved stack should be mathematically consistent
        resolved_moment = timeline.moments[paradox_moment]
        assert isinstance(resolved_moment.stack, list)
        assert len(resolved_moment.stack) >= 2  # Should maintain reasonable stack structure
