"""
    Dummy conftest.py for volvo_connected.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

# import pytest
import sys
if (sys.path[1] != "/workspaces/volvo_connected/src"):
    sys.path.insert(1, "/workspaces/volvo_connected/src")