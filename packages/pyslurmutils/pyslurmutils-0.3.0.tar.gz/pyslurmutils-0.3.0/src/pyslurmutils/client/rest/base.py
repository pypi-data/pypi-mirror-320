"""Low-level SLURM API to submit, cancel and monitor jobs"""

import os
import time
import json
import requests
import logging
from pprint import pformat
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Iterator, List, Optional, Tuple, Union, Generator

from .. import defaults
from .. import os_utils
from .. import utils
from ..errors import RemoteHttpError
from ..errors import raise_chained_errors
from ..log_utils import log_file_monitor


logger = logging.getLogger(__name__)


class SlurmBaseRestClient:
    """Low-level SLURM API to submit, cancel and monitor jobs.
    This class does not contain any job-related state."""

    VERSION = "0.0.41"
    FINISHED_STATES = "FAILED", "COMPLETED", "CANCELLED", "TIMEOUT"

    def __init__(
        self,
        url: str = "",
        user_name: str = "",
        token: str = "",
        parameters: Optional[dict] = None,
        log_directory: Optional[str] = None,
        std_split: Optional[bool] = False,
        request_options: Optional[dict] = None,
    ):
        """
        :param url: SLURM REST API
        :param user_name: User name on SLURM
        :param token: SLURM access token for the user
        :param parameters: SLURM job parameters
        :param log_directory: SLURM log directory
        :param std_split: Split standard output and standard error
        :param request_options: GET, POST and DELETE options
        """
        if not url:
            raise ValueError("Requires the SLURM REST url")
        if not token:
            raise ValueError("Requires a SLURM user token")
        if not user_name:
            raise ValueError("Requires a SLURM user name")
        self._url = url
        self._user_name = user_name.rstrip()
        self._token = token.replace("SLURM_JWT=", "").rstrip()
        self._parameters = parameters
        if log_directory:
            log_directory = log_directory.format(user_name=user_name)
        self._log_directory = log_directory
        self._std_split = std_split
        self._request_options = request_options

    def get_headers(self) -> dict:
        return {"X-SLURM-USER-NAME": self._user_name, "X-SLURM-USER-TOKEN": self._token}

    def get(
        self,
        path: str,
        request_options: Optional[dict] = None,
        error_msg: Optional[str] = None,
        raise_on_error: bool = True,
    ) -> dict:
        request_options = self._parse_request_options(request_options)
        response = requests.get(self._url + path, **request_options)
        return self._handle_response(
            response, raise_on_error=raise_on_error, error_msg=error_msg
        )

    def delete(
        self,
        path: str,
        request_options: Optional[dict] = None,
        error_msg: Optional[str] = None,
        raise_on_error: bool = True,
    ) -> dict:
        request_options = self._parse_request_options(request_options)
        response = requests.delete(self._url + path, **request_options)
        return self._handle_response(
            response, raise_on_error=raise_on_error, error_msg=error_msg
        )

    def post(
        self,
        path: str,
        json: Optional[dict] = None,
        request_options: Optional[dict] = None,
        raise_on_error: bool = True,
        error_msg: Optional[str] = None,
    ) -> dict:
        request_options = self._parse_request_options(request_options)
        if json:
            request_options["json"] = json
            logger.debug("POST %s\n%s", path, pformat(json))
        else:
            logger.debug("POST %s", path)
        response = requests.post(self._url + path, **request_options)
        return self._handle_response(
            response, raise_on_error=raise_on_error, error_msg=error_msg
        )

    def _parse_request_options(self, request_options: Optional[dict]) -> dict:
        merged = utils.merge_mappings(self._request_options, request_options)
        if merged.get("headers") is None:
            merged["headers"] = self.get_headers()
        return merged

    def server_has_api(self, request_options: Optional[dict] = None) -> bool:
        response = self.get("/openapi", request_options=request_options)
        return self.VERSION == response["info"]["version"]

    def submit_job(
        self,
        script: str,
        parameters: Optional[dict] = None,
        metadata: Optional[Union[str, dict]] = None,
        request_options: Optional[dict] = None,
    ) -> int:
        """Returns the SLURM job ID"""
        # https://slurm.schedmd.com/rest_api.html#slurmctldSubmitJob
        job = self._create_job_properties(parameters=parameters, metadata=metadata)
        job_recipe = {"script": script, "job": job}
        job_name = job["name"]

        response = self.post(
            f"/slurm/v{self.VERSION}/job/submit",
            json=job_recipe,
            request_options=request_options,
            error_msg=f"failed to submit SLURM job '{job_name}'",
        )

        job_id = response["job_id"]
        user_msg = response.get("job_submit_user_msg", "")
        if user_msg:
            logger.info(
                "SLURM job '%s' submitted (Job ID: %s): %s", job_name, job_id, user_msg
            )
        else:
            logger.info("SLURM job '%s' submitted (Job ID: %s)", job_name, job_id)
        return job_id

    def cancel_job(self, job_id: int, request_options: Optional[dict] = None) -> None:
        # https://slurm.schedmd.com/rest_api.html#slurmctldCancelJob
        self.delete(
            f"/slurm/v{self.VERSION}/job/{job_id}", request_options=request_options
        )

    def clean_job_artifacts(
        self,
        job_id: int,
        properties: Optional[dict] = None,
        request_options: Optional[dict] = None,
    ) -> None:
        if properties is None:
            properties = self.get_job_properties(
                job_id, raise_on_error=False, request_options=request_options
            )
        if properties is None:
            return
        self._cleanup_job_log_artifact(job_id, properties.get("standard_output"))
        self._cleanup_job_log_artifact(job_id, properties.get("standard_error"))

    @contextmanager
    def clean_job_artifacts_context(
        self,
        job_id: int,
        properties: Optional[dict] = None,
        request_options: Optional[dict] = None,
    ) -> Generator[None, None, None]:
        try:
            yield
        finally:
            self.clean_job_artifacts(
                job_id,
                properties=properties,
                request_options=request_options,
            )

    def get_job_properties(
        self, job_id: int, raise_on_error=True, request_options: Optional[dict] = None
    ) -> Optional[dict]:
        # https://slurm.schedmd.com/rest_api.html#slurmctldGetJob
        response = self.get(
            f"/slurm/v{self.VERSION}/job/{job_id}",
            request_options=request_options,
            raise_on_error=raise_on_error,
            error_msg=f"Failed to get properties of SLURM Job ID {job_id}",
        )
        jobs = response.get("jobs", list())
        if len(jobs) != 1:
            return None
        return jobs[0]

    def get_all_job_properties(
        self,
        raise_on_error=True,
        request_options: Optional[dict] = None,
        filter=None,
        update_time=None,
    ) -> List[dict]:
        # https://slurm.schedmd.com/rest_api.html#slurmctldGetJob
        path = f"/slurm/v{self.VERSION}/jobs"
        if update_time:
            path = f"{path}?update_time={update_time.timestamp()}"
        response = self.get(
            path,
            request_options=request_options,
            raise_on_error=raise_on_error,
            error_msg="failed to get SLURM job properties",
        )
        jobs = response.get("jobs", list())
        return list(self._filter_job_properties(jobs, filter))

    def get_stdout_stderr(
        self, job_id: int, raise_on_error=True, request_options: Optional[dict] = None
    ) -> Tuple["_StdInfo", Optional["_StdInfo"]]:
        properties = self.get_job_properties(
            job_id, raise_on_error=raise_on_error, request_options=request_options
        )
        if properties is None:
            properties = dict()
        ofilename = properties.get("standard_output")
        ofilename, ocontent = self._read_log(job_id, ofilename)
        efilename = properties.get("standard_error")
        efilename, econtent = self._read_log(job_id, efilename)
        if efilename is None:
            std = _StdInfo(name="STDOUT/STDERR", filename=ofilename, content=ocontent)
            return std, None
        else:
            stdout = _StdInfo(name="STDOUT", filename=ofilename, content=ocontent)
            stderr = _StdInfo(name="STDERR", filename=efilename, content=econtent)
            return stdout, stderr

    def get_status(self, job_id: int, request_options=None) -> str:
        # https://curc.readthedocs.io/en/latest/running-jobs/squeue-status-codes.html
        properties = self.get_job_properties(job_id, request_options=request_options)
        return properties.get("job_state", "UNKNOWN")

    def get_full_status(self, job_id: int, request_options=None) -> dict:
        properties = self.get_job_properties(job_id, request_options=request_options)
        return {
            "status": properties.get("job_state", "UNKNOWN"),
            "description": properties.get("state_description", ""),
            "reason": properties.get("state_reason", ""),
            "exit_code": self._parse_exit_code(properties.get("exit_code", "")),
        }

    def is_finished(self, job_id: int) -> bool:
        return self.get_status(job_id) in self.FINISHED_STATES

    def wait_finished(
        self,
        job_id: int,
        progress: bool = False,
        timeout: Optional[float] = None,
        period: float = 0.5,
    ) -> str:
        job_state = None
        t0 = time.time()
        while job_state not in self.FINISHED_STATES:
            job_state = self.get_status(job_id)
            time.sleep(period)
            if progress:
                print(".", end="", flush=True)
            if timeout is not None and (time.time() - t0) > timeout:
                raise TimeoutError
        status = self.get_full_status(job_id)
        logger.info("Job '%s' finished: %s", job_id, pformat(status))
        return job_state

    def print_stdout_stderr(self, job_id: int):
        stdout, stderr = self.get_stdout_stderr(job_id, raise_on_error=False)
        print()
        print("".join(stdout.lines()))
        if stderr is not None:
            print("".join(stderr.lines()))

    def log_stdout_stderr(
        self, job_id: int, logger=None, level=logging.INFO, **log_options
    ) -> None:
        if logger is None:
            logger = logger
        stdout, stderr = self.get_stdout_stderr(job_id, raise_on_error=False)
        stdout = "".join(stdout.lines())
        if stderr is None:
            logger.log(level, "\n%s", stdout, **log_options)
        else:
            stderr = "".join(stderr.lines())
            logger.log(level, "\n%s\n%s", stdout, stderr, **log_options)

    @contextmanager
    def redirect_stdout_stderr(
        self, job_id: int, request_options: Optional[dict] = None
    ) -> Generator[None, None, None]:
        """Redirect logs files to the local root logger within this context."""
        properties = self.get_job_properties(
            job_id, raise_on_error=False, request_options=request_options
        )
        if properties is None:
            properties = dict()
        ofilename = properties.get("standard_output")
        efilename = properties.get("standard_error")
        ofilename = self._parse_filename(job_id, ofilename)
        efilename = self._parse_filename(job_id, efilename)
        with log_file_monitor([ofilename, efilename]):
            yield

    def _handle_response(
        self, response, raise_on_error: bool = True, error_msg: Optional[str] = None
    ):
        try:
            response.raise_for_status()
        except Exception as e:
            if response.status_code in (400, 500):
                if not raise_on_error:
                    return dict()
                if not error_msg:
                    error_msg = str(e)
                if response.status_code == 500:
                    error_msg = f"{error_msg} (SLURM token expired?)"
                else:
                    error_msg = f"{error_msg} (Invalid SLURM parameter?)"
                raise RemoteHttpError(error_msg)
            raise
        data = response.json()
        if raise_on_error:
            self._raise_on_error(data.get("errors"), error_msg=error_msg)
        return data

    def _filter_job_properties(
        self, jobs: List[dict], filter: Optional[dict]
    ) -> Iterator[dict]:
        if filter is None:
            filter = dict()
        filter.setdefault("user_name", self._user_name)
        filter = {k: v for k, v in filter.items() if v is not None}
        for properties in jobs:
            if self._match_filter(properties, None, filter):
                yield properties

    def _match_filter(
        self, properties: dict, name: str, value: Optional[Union[str, dict]]
    ) -> bool:
        if name is None:
            return all(
                self._match_filter(properties, name, value)
                for name, value in value.items()
            )
        elif isinstance(value, str):
            return properties.get(name) == value
        else:
            properties = properties.get(name, dict())
            return all(self._match_filter(properties, k, v) for k, v in value.items())

    def _parse_exit_code(self, exit_code: Optional[int]) -> Optional[int]:
        if not exit_code:
            return
        return exit_code // 256

    def _read_log(
        self, job_id: int, filename: Optional[str]
    ) -> Tuple[str, Optional[List[str]]]:
        filename = self._parse_filename(job_id, filename)
        if filename is None:
            return None, None
        try:
            with open(filename) as f:
                return filename, list(f)
        except FileNotFoundError:
            return None, None

    def _cleanup_job_log_artifact(self, job_id: int, filename: Optional[str]) -> None:
        filename = self._parse_filename(job_id, filename)
        if filename is None or filename == "/dev/null":
            return None
        try:
            os.remove(filename)
        except (FileNotFoundError, PermissionError):
            return None

    def _parse_filename(self, job_id: int, filename: Optional[str]) -> Optional[str]:
        if not filename:
            return None
        return filename.replace("%j", str(job_id))

    def _raise_on_error(
        self, errors: Optional[List[dict]], error_msg: Optional[str] = None
    ):
        if not errors:
            return
        errors = [self._parse_error(error) for error in errors]
        if error_msg:
            errors.append(error_msg + " (token expired?)")
        raise_chained_errors(errors)

    def _parse_error(self, error: dict) -> str:
        description = error.get("error", "<no error description>")
        description = error.get("description", description)
        error_code = error.get("error_code", "<no error code>")
        error_code = error.get("error_number", description)
        return f"{description} (error code: {error_code})"

    def _create_job_properties(
        self,
        parameters: Optional[dict] = None,
        metadata: Optional[Union[str, dict]] = None,
    ) -> dict:
        # https://slurm.schedmd.com/rest_api.html#v0.0.41_job_properties
        parameters = utils.merge_mappings(self._parameters, parameters)
        if not parameters.get("environment"):
            # Cannot be empty
            parameters["environment"] = {"_DUMMY_VAR": "dummy_value"}

        job_name = self._ensure_job_name(parameters)

        parameters["standard_input"] = "/dev/null"
        if self._log_directory:
            os_utils.makedirs(self._log_directory)
            filetemplate = f"{self._log_directory}/{job_name}.%j"
            if self._std_split:
                parameters["standard_output"] = filetemplate + ".out"
                parameters["standard_error"] = filetemplate + ".err"
            else:
                parameters["standard_output"] = filetemplate + ".outerr"
        else:
            parameters["standard_output"] = "/dev/null"
            parameters["standard_error"] = "/dev/null"

        if metadata:
            if not isinstance(metadata, str):
                metadata = json.dumps(metadata)
            parameters["comment"] = metadata

        return parameters

    def _ensure_job_name(self, parameters: dict) -> str:
        job_name = parameters.get("name")
        if not job_name:
            job_name = defaults.JOB_NAME
            parameters["name"] = job_name
        return job_name


@dataclass
class _StdInfo:
    """Information about a SLURM job stdout/stderr log file"""

    name: str
    filename: Optional[str]
    content: Optional[List[str]]

    def lines(self) -> List[str]:
        title = f"{self.name}: {self.filename}\n"
        line = "-" * len(title) + "\n"
        if self.content is None:
            return [title, line, " <not found>"]
        elif not self.content:
            return [title, line, " <empty>"]
        else:
            return [title, line] + self.content
