import contextlib
import json
import os
import tempfile
import subprocess
from typing import Dict, Any

from nebari.hookspecs import hookimpl, NebariStage

from .utils import download_tf_profile_binary


class TFProfileStage(NebariStage):
    name = "tf-profile"
    # This should run after all stages are executed
    priority = 100

    # working_dir = os.getcwd()
    _reports_output_dir = None
    _stages: list = []

    def __init__(self):
        super().__init__()
        self._reports_output_dir = self._get_reports_output_dir()
    
    def _get_reports_output_dir(self):
        _ = os.environ.get(
            "NEBARI_REPORTS_OUTPUT_DIR", os.path.join(os.getcwd(), "reports")
        )

        if os.mkdir(_, exist_ok=True):
            return _
        else:
            raise Exception(f"Could not create reports output directory: {_}")

    def _stage_log_filename(self, mode: str = None, stage: str = None):
        """
        Returns the log file name for a stage and mode, following the pattern:
        terraform_<mode>_<stage>.log

        Args:
            mode (str): The terraform mode (apply, destroy)
            stage (str): The stage name

        Example:
            _stage_log_filename(mode="apply", stage="03-kubernetes-initialize")
            Returns: terraform_apply_03-kubernetes-initialize.log
        """
        return f"terraform_{mode}_{stage}.log"

    def _run_tf_profile(self, mode=["apply", "destroy"]):
        with tempfile.TemporaryDirectory(delete=False) as tmp_dir:
            # We call this function every time we need to run tf-profile
            # but it won't download the binary if it already exists.
            binary_path = download_tf_profile_binary(version="v0.4.0")

            for stage in self._get_stages():
                _report_filename = f"{self._reports_output_dir}/{stage}.report"
                with open(_report_filename, "w") as f:
                    subprocess.call(
                        [
                            binary_path,
                            "stats",
                            self._stage_log_filename(mode=mode, stage=stage),
                        ],
                        stdout=f,
                    )

    def _get_stages(self):
        return self._stages

    def _set_stages(self, stages):
        self._stages = stages

    @contextlib.contextmanager
    def deploy(self, stage_outputs: Dict[str, Dict[str, Any]]):
        self._set_stages(stage_outputs.keys())
        self._run_tf_profile(mode="apply")
        yield

    @contextlib.contextmanager
    def destroy(
        self, stage_outputs: Dict[str, Dict[str, Any]], status: Dict[str, bool]
    ):
        self._run_tf_profile(mode="destroy")
        yield

    def check(self, stage_outputs: Dict[str, Dict[str, Any]], disable_prompt: bool = False) -> bool:
        # TODO: Check if the reports directory exists and has non-empty files
        pass
        

@hookimpl
def nebari_stage():
    return [TFProfileStage]
