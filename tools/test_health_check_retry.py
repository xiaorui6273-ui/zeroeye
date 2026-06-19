#!/usr/bin/env python3
"""Unit tests for retry/backoff behavior in health_check.py."""

import os
import sys
import socket
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Ensure tools/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.health_check import (
    retry_with_backoff,
    check_disk_usage,
    check_memory_usage,
    check_load_average,
    check_tcp_port,
)


class TestRetryWithBackoff(unittest.TestCase):
    """Tests for the retry_with_backoff helper."""

    def test_succeeds_first_try(self):
        """No retry needed when the function succeeds immediately."""
        call_count = 0

        def fn():
            nonlocal call_count
            call_count += 1
            return "OK", "all good", 100

        result = retry_with_backoff(fn, max_retries=3, base_delay=0.01)
        self.assertEqual(result, ("OK", "all good", 100))
        self.assertEqual(call_count, 1)

    def test_retries_on_transient_failure(self):
        """Retries on OSError and returns success on second attempt."""
        call_count = 0

        def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("transient I/O error")
            return "OK", "recovered", 50

        result = retry_with_backoff(fn, max_retries=3, base_delay=0.01)
        self.assertEqual(result, ("OK", "recovered", 50))
        self.assertEqual(call_count, 2)

    def test_retries_on_socket_timeout(self):
        """Retries on socket.timeout."""
        call_count = 0

        def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise socket.timeout("timed out")
            return "OK", "connected", 10

        result = retry_with_backoff(fn, max_retries=3, base_delay=0.01)
        self.assertEqual(result, ("OK", "connected", 10))
        self.assertEqual(call_count, 2)

    def test_retries_on_connection_error(self):
        """Retries on ConnectionError."""
        call_count = 0

        def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("connection reset")
            return "OK", "connected", 20

        result = retry_with_backoff(fn, max_retries=3, base_delay=0.01)
        self.assertEqual(result, ("OK", "connected", 20))
        self.assertEqual(call_count, 3)

    def test_gives_up_after_max_retries(self):
        """Returns CRITICAL after exhausting all retries."""
        call_count = 0

        def fn():
            nonlocal call_count
            call_count += 1
            raise OSError("persistent failure")

        result = retry_with_backoff(fn, max_retries=3, base_delay=0.01)
        self.assertEqual(result[0], "CRITICAL")
        self.assertIn("Failed after 3 attempts", result[1])
        self.assertEqual(call_count, 3)

    def test_non_retryable_exception_propagates(self):
        """Non-retryable exceptions (e.g. ValueError) propagate immediately."""
        call_count = 0

        def fn():
            nonlocal call_count
            call_count += 1
            raise ValueError("bad input")

        with self.assertRaises(ValueError):
            retry_with_backoff(fn, max_retries=3, base_delay=0.01)
        self.assertEqual(call_count, 1)

    def test_custom_retryable_exceptions(self):
        """Accepts custom retryable exception types."""
        call_count = 0

        def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("transient")
            return "OK", "ok", 1

        result = retry_with_backoff(
            fn, max_retries=3, base_delay=0.01,
            retryable_exceptions=(ValueError,),
        )
        self.assertEqual(result, ("OK", "ok", 1))
        self.assertEqual(call_count, 2)

    def test_exponential_backoff_timing(self):
        """Verifies exponential backoff delays between retries."""
        call_count = 0
        delays = []
        original_sleep = __import__("time").sleep

        def fn():
            nonlocal call_count
            call_count += 1
            raise OSError("fail")

        with patch("time.sleep", side_effect=lambda d: delays.append(d)):
            retry_with_backoff(fn, max_retries=3, base_delay=0.1, backoff_factor=2.0)

        # 2 delays for 3 retries (no sleep after last attempt)
        self.assertEqual(len(delays), 2)
        self.assertAlmostEqual(delays[0], 0.1, places=5)
        self.assertAlmostEqual(delays[1], 0.2, places=5)


class TestHealthChecksWithRetry(unittest.TestCase):
    """Tests that health check functions use retry and preserve result shapes."""

    def test_check_disk_usage_returns_tuple(self):
        """check_disk_usage returns a 3-tuple (status, detail, pct)."""
        result = check_disk_usage("/")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        status, detail, pct = result
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertIsInstance(detail, str)
        self.assertIsInstance(pct, (int, float))

    def test_check_memory_usage_returns_tuple(self):
        """check_memory_usage returns a 3-tuple (status, detail, pct)."""
        result = check_memory_usage()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        status, detail, pct = result
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertIsInstance(detail, str)
        self.assertIsInstance(pct, (int, float))

    def test_check_load_average_returns_tuple(self):
        """check_load_average returns a 3-tuple (status, detail, load)."""
        result = check_load_average()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        status, detail, load = result
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertIsInstance(detail, str)
        self.assertIsInstance(load, (int, float))

    def test_check_tcp_port_returns_tuple(self):
        """check_tcp_port returns a 3-tuple (status, detail, latency)."""
        # Use a port that's likely closed to test error path
        result = check_tcp_port("127.0.0.1", 59999, timeout=1)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        status, detail, latency = result
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertIsInstance(detail, str)
        self.assertIsInstance(latency, (int, float))

    @patch("socket.create_connection")
    def test_check_tcp_port_retries_on_timeout(self, mock_conn):
        """check_tcp_port retries on socket.timeout."""
        mock_conn.side_effect = socket.timeout("timed out")
        result = check_tcp_port("localhost", 9999, timeout=1)
        self.assertEqual(result[0], "CRITICAL")
        # Should have been called max_retries (3) times
        self.assertEqual(mock_conn.call_count, 3)

    @patch("os.statvfs")
    def test_check_disk_usage_retries_on_oserror(self, mock_statvfs):
        """check_disk_usage retries on OSError."""
        mock_statvfs.side_effect = OSError("transient I/O error")
        result = check_disk_usage("/")
        self.assertEqual(result[0], "CRITICAL")
        self.assertIn("Failed after", result[1])
        # Should have been called max_retries (3) times
        self.assertEqual(mock_statvfs.call_count, 3)


class TestRetryPreservesExistingBehavior(unittest.TestCase):
    """Ensure retry wrapper doesn't change successful-path behavior."""

    def test_disk_usage_normal_operation(self):
        """Disk usage check works normally with retry wrapper."""
        status, detail, pct = check_disk_usage("/")
        # On a real filesystem this should be OK or WARNING
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertGreater(pct, 0)
        self.assertLessEqual(pct, 100)

    def test_memory_usage_normal_operation(self):
        """Memory usage check works normally with retry wrapper."""
        status, detail, pct = check_memory_usage()
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertGreater(pct, 0)

    def test_load_average_normal_operation(self):
        """Load average check works normally with retry wrapper."""
        status, detail, load = check_load_average()
        self.assertIn(status, ("OK", "WARNING", "CRITICAL"))
        self.assertGreater(load, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
