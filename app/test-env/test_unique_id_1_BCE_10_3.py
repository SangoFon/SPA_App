# BCE_10_3
# EXERCISE TEAM 2

# Kyle Kawakami
# Meleah Hall
# Wenxing Luo

"""Test tasks.unique_id()."""

import pytest
import tasks

#
# add xfail
#
@pytest.mark.xfail(reason='assert 1 != 1')
def test_unique_id():
    """Calling unique_id() twice should return different numbers."""
    id_1 = tasks.unique_id()
    id_2 = tasks.unique_id()
    assert id_1 != id_2


@pytest.fixture(autouse=True)
def initialized_tasks_db(tmpdir):
    """Connect to db before testing, disconnect after."""
    tasks.start_tasks_db(str(tmpdir), 'tiny')
    yield
    tasks.stop_tasks_db()
