import random

import pytest

@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_flaky_with_reruns():
    ...

@pytest.mark.flaky(reruns=3, reruns_delay=1)
def test_reruns():
    assert random.choice([True, False])