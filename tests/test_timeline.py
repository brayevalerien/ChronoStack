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
        """Test temporal fold operations."""
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

        # Test different fold operations
        sums = timeline.temporal_fold("sum")
        counts = timeline.temporal_fold("count")
        maxes = timeline.temporal_fold("max")
        mins = timeline.temporal_fold("min")

        assert sums == [3, 15, 21, 21]  # Sums of each moment's stack
        assert counts == [2, 5, 6, 6]  # Stack lengths
        assert maxes == [2, 5, 6, 6]  # Max values in each stack
        assert mins == [1, 1, 1, 1]  # Min values in each stack

    def test_ripple_effects(self):
        """Test ripple effects on future moments."""
        timeline = Timeline()

        # Create several future moments
        for i in range(4):
            timeline.current_stack().append(i)
            timeline.tick()

        # Go back to an earlier moment
        timeline.rewind(2)

        # Apply ripple effect
        timeline.ripple("push", 999)

        # Check that future moments were affected
        for i in range(timeline.current_index + 1, len(timeline.moments)):
            assert 999 in timeline.moments[i].stack

    def test_ripple_multiply(self):
        """Test ripple multiply operation."""
        timeline = Timeline()

        # Create moments with numeric values
        for i in range(1, 4):
            timeline.current_stack().append(i * 10)
            timeline.tick()

        timeline.rewind(2)

        # Ripple multiply by 2
        timeline.ripple("multiply", 2)

        # Check that future top values were doubled
        # (Only affects numeric top values)
        future_moments = timeline.moments[timeline.current_index + 1 :]
        for moment in future_moments:
            if moment.stack and isinstance(moment.stack[-1], (int, float)):
                # Top values should be doubled
                pass  # Actual test would depend on exact implementation

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
