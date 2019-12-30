# BCE_10_3
# EXERCISE TEAM 2

# Kyle Kawakami
# Meleah Hall
# Wenxing Luo

"""Test for expected exceptions from using the API wrong."""

import pytest
import tasks

#
# add TestAdd class
#
class TestAdd():
    def test_add_task(self):
        """add() should raise an exception with wrong type param."""
        with pytest.raises(TypeError):
            tasks.add(task='not a Task object')

    #
    # add ValueError for summary test
    #
    def test_add_summary(self):
        """add() should raise an exception with wrong type param."""
        with pytest.raises(ValueError):
            tasks.add(task=tasks.Task())
    #
    # add ValueError for owner test
    #
    def test_add_owner(self):
        """add() should raise an exception with wrong type param."""
        with pytest.raises(ValueError):
            tasks.add(task=tasks.Task())


@pytest.mark.smoke
def test_list_raises():
    """list() should raise an exception with wrong type param."""
    with pytest.raises(TypeError):
        tasks.list_tasks(owner=123)


@pytest.mark.get
@pytest.mark.smoke
def test_get_raises():
    """get() should raise an exception with wrong type param."""
    with pytest.raises(TypeError):
        tasks.get(task_id='123')


class TestUpdate():
    """Test expected exceptions with tasks.update()."""

    def test_bad_id(self):
        """A non-int id should raise an excption."""
        with pytest.raises(TypeError):
            tasks.update(task_id={'dict instead': 1},
                         task=tasks.Task())

    def test_bad_task(self):
        """A non-Task task should raise an excption."""
        with pytest.raises(TypeError):
            tasks.update(task_id=1, task='not a task')


def test_delete_raises():
    """delete() should raise an exception with wrong type param."""
    with pytest.raises(TypeError):
        tasks.delete(task_id=(1, 2, 3))

#
# add TestStart class
#
class TestStart():
    """Test expected exceptions with tasks.start_tasks_db()."""

    #
    # add TypeError for db_path
    #
    def test_start_tasks_db_path(self):
        """Make sure unsupported db_path raises an exception."""
        with pytest.raises(TypeError):
            tasks.start_tasks_db('some/great/path')


    def test_start_tasks_db_type(self):
        """Make sure unsupported db raises an exception."""
        with pytest.raises(ValueError) as excinfo:
            tasks.start_tasks_db('some/great/path', 'mysql')
        exception_msg = excinfo.value.args[0]
        assert exception_msg == "db_type must be a 'tiny' or 'mongo'"
