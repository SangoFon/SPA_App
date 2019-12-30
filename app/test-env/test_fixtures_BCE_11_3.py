import pytest
import time


@pytest.fixture(scope='module')
def some_turple():
    #​"""Report test durations after each function."""​
​    start = time.time()
​ ​   yield (1,None,{'age':27})
​    stop = time.time()
​    delta = stop - start
​    ​print​(​'​​\n​​test duration : {:0.3} seconds'​.format(delta))



def test_some_turple(some_turple):

    assert some_turple[2]['age'] == 42


def test_some_turple(some_turple):

    assert some_turple[2]['age'] == 27
