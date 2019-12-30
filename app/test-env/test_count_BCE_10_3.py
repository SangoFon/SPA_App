# BCE_10_3
# EXERCISE TEAM 2

# Kyle Kawakami
# Meleah Hall
# Wenxing Luo

"""Test the tasks.count() API function."""

import pytest
import tasks
from tasks import Task


def test_count():
    """tasks.count(none) should return an integer."""
    # GIVEN an initialized tasks db
    # THEN returned task_count is of type int
    task_count = tasks.count()
    assert isinstance(task_count, int)

@pytest.fixture(autouse=True)
def initialized_tasks_db(tmpdir):
    """Connect to db before testing, disconnect after."""
    # Setup : start db
    tasks.start_tasks_db(str(tmpdir), 'tiny')

    yield  # this is where the testing happens

    # Teardown : stop db
    tasks.stop_tasks_db()
