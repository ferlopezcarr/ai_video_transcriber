"""Unit tests for summarizer_lmstudio_agent.py"""

import pytest
from src.infrastructure.outbound.agents.adapters.summarizer_lmstudio_agent import (
    calculate_min_summary_lines,
)


class TestCalculateMinSummaryLines:
    """Tests for the calculate_min_summary_lines function."""

    def test_zero_duration(self):
        """Test with zero duration returns base lines."""
        result = calculate_min_summary_lines(duration_seconds=0)
        assert result == 50  # base_lines default

    def test_negative_duration(self):
        """Test with negative duration returns base lines."""
        result = calculate_min_summary_lines(duration_seconds=-100)
        assert result == 50

    def test_none_duration(self):
        """Test with None duration returns base lines."""
        result = calculate_min_summary_lines(duration_seconds=None)
        assert result == 50

    def test_very_short_video(self):
        """Test with very short video (30 seconds) respects min_lines."""
        result = calculate_min_summary_lines(duration_seconds=30)
        # 30s = 0.5 min -> 50 + (0.5 * 15) = 57.5 -> 57
        # But min_lines is 20 by default, so should be max(20, 57) = 57
        assert result == 57

    def test_five_minute_video(self):
        """Test with 5-minute video."""
        result = calculate_min_summary_lines(duration_seconds=300)
        # 300s = 5 min -> 50 + (5 * 15.0) = 125
        assert result == 125

    def test_fifteen_minute_video(self):
        """Test with 15-minute video."""
        result = calculate_min_summary_lines(duration_seconds=900)
        # 900s = 15 min -> 50 + (15 * 15.0) = 275
        assert result == 275

    def test_seventeen_minute_video(self):
        """Test with 17-minute video."""
        result = calculate_min_summary_lines(duration_seconds=1020)
        # 1020s = 17 min -> 50 + (17 * 15.0) = 305
        assert result == 305

    def test_thirty_minute_video(self):
        """Test with 30-minute video."""
        result = calculate_min_summary_lines(duration_seconds=1800)
        # 1800s = 30 min -> 50 + (30 * 15.0) = 500
        assert result == 500

    def test_sixty_minute_video(self):
        """Test with 60-minute video."""
        result = calculate_min_summary_lines(duration_seconds=3600)
        # 3600s = 60 min -> 50 + (60 * 15.0) = 950
        assert result == 950

    def test_two_hour_video(self):
        """Test with 2-hour video."""
        result = calculate_min_summary_lines(duration_seconds=7200)
        # 7200s = 120 min -> 50 + (120 * 15.0) = 1850
        assert result == 1850

    def test_max_lines_cap(self):
        """Test that max_lines cap is enforced."""
        # Very long video that would exceed max_lines
        result = calculate_min_summary_lines(duration_seconds=20000)
        # 20000s = 333.33 min -> 50 + (333.33 * 15.0) = 5050
        # Should be capped at max_lines (2000)
        assert result == 2000

    def test_custom_base_lines(self):
        """Test with custom base_lines parameter."""
        result = calculate_min_summary_lines(duration_seconds=300, base_lines=100)
        # 300s = 5 min -> 100 + (5 * 15.0) = 175
        assert result == 175

    def test_custom_lines_per_minute(self):
        """Test with custom lines_per_minute parameter."""
        result = calculate_min_summary_lines(duration_seconds=300, lines_per_minute=20.0)
        # 300s = 5 min -> 50 + (5 * 20.0) = 150
        assert result == 150

    def test_custom_max_lines(self):
        """Test with custom max_lines parameter."""
        result = calculate_min_summary_lines(duration_seconds=10000, max_lines=500)
        # 10000s = 166.67 min -> 50 + (166.67 * 15.0) = 2550
        # Should be capped at custom max_lines (500)
        assert result == 500

    def test_custom_min_lines(self):
        """Test with custom min_lines parameter."""
        result = calculate_min_summary_lines(duration_seconds=10, min_lines=100)
        # 10s = 0.167 min -> 50 + (0.167 * 15.0) = 52.5 -> 52
        # Should be raised to min_lines (100)
        assert result == 100

    def test_all_custom_parameters(self):
        """Test with all custom parameters."""
        result = calculate_min_summary_lines(
            duration_seconds=600,  # 10 minutes
            base_lines=30,
            lines_per_minute=10.0,
            max_lines=1000,
            min_lines=50,
        )
        # 600s = 10 min -> 30 + (10 * 10.0) = 130
        assert result == 130

    @pytest.mark.parametrize(
        "duration,expected",
        [
            (0, 50),
            (60, 65),  # 1 min: 50 + 15 = 65
            (120, 80),  # 2 min: 50 + 30 = 80
            (180, 95),  # 3 min: 50 + 45 = 95
            (240, 110),  # 4 min: 50 + 60 = 110
            (300, 125),  # 5 min: 50 + 75 = 125
        ],
    )
    def test_parametrized_durations(self, duration, expected):
        """Test multiple durations using parametrize."""
        result = calculate_min_summary_lines(duration_seconds=duration)
        assert result == expected

    def test_rounding_behavior(self):
        """Test that fractional minutes are handled correctly."""
        # 90 seconds = 1.5 minutes -> 50 + (1.5 * 15) = 72.5 -> rounds to 72
        result = calculate_min_summary_lines(duration_seconds=90)
        assert result == 72

    def test_min_lines_floor_for_tiny_video(self):
        """Test that min_lines floor is applied for very short videos."""
        # 1 second video with high min_lines
        result = calculate_min_summary_lines(duration_seconds=1, min_lines=100)
        # Would calculate to ~50, but should be raised to 100
        assert result == 100
