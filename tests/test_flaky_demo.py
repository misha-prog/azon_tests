import pytest

@pytest.mark.flaky(reruns=2, reruns_delay=1)
def test_flaky_with_reruns():
    ...