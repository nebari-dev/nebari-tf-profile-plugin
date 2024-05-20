import contextlib
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

from nebari.hookspecs import NebariStage

from .constants import TF_PROFILE_VERSION
from .utils import download_tf_profile_binary


class TFProfileStage(NebariStage):
    name = "tf-profile"
    # This should run after all stages are executed
    priority = 100

    # working_dir = os.getcwd()
    _reports_output_dir = None
    _stages: list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"TFProfileStage: {kwargs}")
        self._reports_output_dir = self._get_reports_output_dir()

    def _get_reports_output_dir(self):
        _ = os.environ.get(
            "NEBARI_TF_PROFILE_RESULTS_PATH",
            os.path.join(os.getcwd(), "tf-profile-reports"),
        )
        try:
            os.makedirs(_, exist_ok=True)
            return _
        except Exception as e:
            raise Exception(f"Could not create reports output directory: {_}", e)
            # raise Exception(f"Could not create reports output directory: {_}")

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
        output_dir = os.getenv("NEBARI_EXPORT_LOG_FILES_PATH", Path.cwd().as_posix())
        _last_timestamp_log_dir = sorted(
            Path(output_dir).iterdir(), key=os.path.getmtime
        )[-1]

        return (
            Path(output_dir) / _last_timestamp_log_dir / f"terraform_{mode}_{stage}.log"
        )

    def _run_tf_profile_subcommand(
        self, binary_path, subcommand: str, stage: str, mode: str, output_filename: Path
    ):
        """
        _summary_

        Parameters
        ----------
        binary_path : _type_
            _description_
        subcommand : str
            _description_
        stage : str
            _description_
        mode : str
            _description_
        output_filename : Path
            _description_
        """
        _stage_name = stage.split("/")[-1]
        with open(output_filename, "a") as f:
            subprocess.call(
                [
                    binary_path,
                    subcommand,
                    self._stage_log_filename(mode=mode, stage=_stage_name),
                ],
                stdout=f,
            )

    def _create_markdown_report(self, filenames: dict[str, list[str]]):
        """
        _summary_

        Parameters
        ----------
        stage_name : str
            _description_
        contents : str
            _description_
        """
        # write some logic to add the contents of a file inside the following html component: <Details><Summary>here goes stage name</Summary>```Here goes the contents of the file```</Details>

        _output_filename = f"{self._reports_output_dir}/report.md"
        with open(_output_filename, "w") as f:
            for stage_name, files in filenames.items():
                f.write(f"<Details><Summary>{stage_name}</Summary>")
                for file in files:
                    with open(file, "r") as _f:
                        f.write(f"```{_f.read()}```")
                f.write("</Details>")

    def _run_tf_profile(self, mode=["apply", "destroy"]):
        binary_path = download_tf_profile_binary(version=TF_PROFILE_VERSION)

        filenames = {}
        for stage in self._get_stages():
            _stage_name = stage.split("/")[-1]
            filenames[_stage_name] = []
            for subcommand in ["stats", "table"]:
                _output_filename = (
                    f"{self._reports_output_dir}/{_stage_name}.{subcommand}"
                )
                filenames[_stage_name].append(_output_filename)
                self._run_tf_profile_subcommand(
                    binary_path, subcommand, stage, mode, _output_filename
                )

        if os.getenv("NEBARI_TF_PROFILE_CREATE_REPORT"):
            self._create_markdown_report(filenames)

    def _get_stages(self):
        return self._stages

    def _set_stages(self, stages):
        self._stages = stages

    @contextlib.contextmanager
    def deploy(
        self, stage_outputs: Dict[str, Dict[str, Any]], disable_prompt: bool = False
    ):
        self._set_stages(stage_outputs.keys())
        self._run_tf_profile(mode="apply")
        yield

    @contextlib.contextmanager
    def destroy(
        self,
        stage_outputs: Dict[str, Dict[str, Any]],
        status: Dict[str, bool],
        **kwargs,
    ):
        print(f"TFProfileStage: Destroy: {stage_outputs}")
        self._run_tf_profile(mode="destroy")
        yield

    def check(
        self, stage_outputs: Dict[str, Dict[str, Any]], disable_prompt: bool = False
    ) -> bool:
        # TODO: Check if the reports directory exists and has non-empty files
        pass
