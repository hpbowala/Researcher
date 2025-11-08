"""
Tests for the main module.
"""

from researcher import __version__
from researcher.main import main


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_main_function():
    """Test that main function can be called."""
    # This test just ensures the function can be called without error
    main()
    assert True  # If we get here, the function executed successfully
