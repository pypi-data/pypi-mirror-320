import os
import sys
import logging
import subprocess
from tempfile import NamedTemporaryFile
from typing import Optional
from unittest.mock import patch
from contextlib import ExitStack, contextmanager
from concurrent.futures import ThreadPoolExecutor

import pytest
from ..client import SlurmBaseRestClient
from ..client import SlurmScriptRestClient
from ..client import SlurmPyConnRestClient
from ..client.errors import RemoteHttpError

logger = logging.getLogger(__name__)

_MAX_JOBS = 50


@contextmanager
def mock_slurm_clients(tmpdir):
    last_job_id = 0
    jobs = dict()

    def _get(
        self,
        path: str,
        request_options=None,
        error_msg: Optional[str] = None,
        raise_on_error: bool = True,
    ):
        if path == "/openapi":
            return {"info": {"version": SlurmBaseRestClient.VERSION}}
        elif path.startswith("/slurm/v0.0.41/job/"):
            job_id = int(path.split("/")[-1])
            job_info = jobs.get(job_id)
            if job_info is None:
                if raise_on_error:
                    raise RemoteHttpError(error_msg)
                else:
                    return dict()
            logger.debug("SLURM mock backend: get job %s", job_id)
            return {"jobs": [job_info]}
        elif path == "/slurm/v0.0.41/jobs":
            logger.debug("SLURM mock backend: get jobs (# %d)", len(jobs))
            return {"jobs": list(jobs.values())}
        else:
            raise NotImplementedError(path)

    def _delete(
        self,
        path: str,
        request_options=None,
        error_msg: Optional[str] = None,
        raise_on_error: bool = True,
    ):
        if path.startswith("/slurm/v0.0.41/job/"):
            job_id = int(path.split("/")[-1])
            job_info = jobs.get(job_id)
            if job_info is None:
                if raise_on_error:
                    raise RemoteHttpError(error_msg)
            else:
                job_info["job_state"] = "CANCELLED"
                logger.debug("SLURM mock backend: cancel job %s", last_job_id)
        else:
            raise NotImplementedError(path)

    def _post(
        self,
        path: str,
        json: Optional[dict] = None,
        request_options=None,
        raise_on_error: bool = True,
        error_msg: Optional[str] = None,
    ):
        nonlocal last_job_id
        if path == "/slurm/v0.0.41/job/submit":
            last_job_id += 1
            job_info = {
                "job_id": last_job_id,
                "job_state": "PENDING",
                **json["job"],
                "user_name": self._user_name,
            }
            jobs[last_job_id] = job_info
            logger.debug("SLURM mock backend: recieved job %s", last_job_id)

            lines = json["script"].split("\n")
            shebang = lines[0]
            if "bash" in shebang:
                if sys.platform == "win32":
                    pytest.skip("bash script does not run on windows")
            elif "python" in shebang:
                pass
            else:
                assert False, f"Unknown script starting with '{shebang}'"

            pool.submit(_job_main, json, job_info, str(tmpdir))
            return job_info
        else:
            raise NotImplementedError(path)

    with ExitStack() as stack:
        for cls in (
            SlurmBaseRestClient,
            SlurmScriptRestClient,
            SlurmPyConnRestClient,
        ):
            ctx = ThreadPoolExecutor(max_workers=_MAX_JOBS)
            pool = stack.enter_context(ctx)
            ctx = patch.object(cls, "get", _get)
            stack.enter_context(ctx)
            ctx = patch.object(cls, "post", _post)
            stack.enter_context(ctx)
            ctx = patch.object(cls, "delete", _delete)
            stack.enter_context(ctx)
        yield


def _job_main(json: dict, job_info: dict, tmpdir):
    cmd = []
    lines = json["script"].split("\n")
    shebang = lines[0]
    if "bash" in shebang:
        suffix = ".sh"
    elif "python" in shebang:
        if sys.platform == "win32":
            lines.pop(0)
            cmd = [sys.executable]
        suffix = ".py"
    else:
        assert False, f"Unknown script starting with '{shebang}'"

    with NamedTemporaryFile("w", delete=False, dir=tmpdir, suffix=suffix) as script:
        script.write("\n".join(lines))
        filename = script.name
    os.chmod(filename, 0o755)
    cmd.append(filename)

    env = json["job"].get("environment", dict())
    env = {k: str(v) for k, v in env.items()}
    env = {**os.environ, **env}
    env["SLURM_JOB_ID"] = str(job_info["job_id"])

    standard_output = json["job"].get("standard_output")
    standard_error = json["job"].get("standard_error")

    if standard_output is None:
        stdout = None
    elif standard_output == "/dev/null":
        stdout = None
        standard_output = None
    else:
        stdout = subprocess.PIPE

    if standard_error is None:
        stderr = None
    elif standard_error == "/dev/null":
        stderr = None
        standard_error = None
    else:
        stderr = stdout or subprocess.PIPE

    with subprocess.Popen(
        cmd, stdout=stdout, stderr=stderr, env=env, cwd=os.getcwd()
    ) as proc:
        logger.debug("SLURM mock backend: job %s started", job_info["job_id"])
        job_info["job_state"] = "RUNNING"
        outs, errs = proc.communicate(timeout=15)

        if standard_output is not None:
            outfile = standard_output.replace("%j", str(job_info["job_id"]))
            with open(outfile, "wb") as f:
                f.write(outs)

        if standard_error is not None:
            errfile = standard_error.replace("%j", str(job_info["job_id"]))
            with open(errfile, "wb") as f:
                f.write(errs)

        if job_info["job_state"] != "CANCELLED":
            if proc.returncode:
                job_info["job_state"] = "FAILED"
                logger.debug("SLURM mock backend: job %s failed", job_info["job_id"])
            else:
                job_info["job_state"] = "COMPLETED"
                logger.debug("SLURM mock backend: job %s completed", job_info["job_id"])
