import os
import warnings
from typing import Optional

import pytest

from .mock_slurm import mock_slurm_clients


def pytest_addoption(parser):
    parser.addoption(
        "--slurm-root-directory",
        action="store",
        default=None,
        help="Specify the SLURM root directory for logs and data.",
    )


@pytest.fixture(scope="session")
def slurm_root_directory(tmp_path_factory, request):
    path = request.config.getoption("--slurm-root-directory")
    if path:
        return path
    return str(tmp_path_factory.mktemp("slurm_root"))


@pytest.fixture(scope="session")
def slurm_parameters(request) -> dict:
    url = os.environ.get("SLURM_URL", "mock")
    token = os.environ.get("SLURM_TOKEN", "mock")
    user_name = os.environ.get("SLURM_USER", "mock")
    mock = url == "mock" or token == "mock" or user_name == "mock"
    slurm_root_directory = request.config.getoption("--slurm-root-directory")
    if not mock and not slurm_root_directory:
        mock = True
        warnings.warn(
            "cannot use SLURM when the pytest argument '--slurm-root-directory ...' is not provided",
            UserWarning,
        )
    return {
        "url": url,
        "token": token,
        "user_name": user_name,
        "mock": mock,
    }


@pytest.fixture(scope="session")
def slurm_log_directory(
    slurm_root_directory, tmp_path_factory, slurm_parameters
) -> Optional[str]:
    if slurm_parameters["mock"]:
        return str(tmp_path_factory.mktemp("slurm_logs"))
    if slurm_root_directory:
        return os.path.join(
            slurm_root_directory, slurm_parameters["user_name"], "slurm_logs"
        )


@pytest.fixture(scope="session")
def slurm_data_directory(
    slurm_root_directory, tmp_path_factory, slurm_parameters
) -> Optional[str]:
    if slurm_parameters["mock"]:
        return str(tmp_path_factory.mktemp("slurm_data"))
    if slurm_root_directory:
        return os.path.join(
            slurm_root_directory, slurm_parameters["user_name"], "slurm_data"
        )


@pytest.fixture(scope="session")
def slurm_client_kwargs(
    slurm_log_directory, tmp_path_factory, slurm_parameters
) -> dict:
    params = dict(slurm_parameters)
    mock = params.pop("mock")
    params["log_directory"] = slurm_log_directory
    if mock:
        tmpdir = tmp_path_factory.mktemp("slurm_mock")
        with mock_slurm_clients(tmpdir):
            yield params
    else:
        yield params
