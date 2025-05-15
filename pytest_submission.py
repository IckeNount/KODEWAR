import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--submission",
        action="store",
        default=None,
        help="Path to the submission file"
    )

@pytest.fixture
def get_submission_path(request):
    submission_path = request.config.getoption("--submission")
    if submission_path is None:
        pytest.fail("--submission argument is required")
    return submission_path 