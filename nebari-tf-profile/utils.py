import logging
import io
import platform
import sys
import tempfile
import urllib
import zipfile
from pathlib import Path


logger = logging.getLogger(__name__)

from . import constants


def download_tf_profile_binary(version=constants.TF_PROFILE_VERSION):
    os_mapping = {
        "linux": "linux",
        "win32": "windows",
        "darwin": "darwin",
    }

    architecture_mapping = {
        "x86_64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
    }

    _source = "https://github.com/datarootsio/tf-profile/releases"
    download_url = f"{_source}/download/{version}/tf-profile-{version}-{os_mapping[sys.platform]}-{architecture_mapping[platform.machine()]}.zip"
    
    filename_directory = Path(tempfile.gettempdir()) / "tf-profile" / version
    filename_path = filename_directory / "tf-profile"

    if not filename_path.is_file():
        logger.info(
            f"downloading and extracting terraform binary from url={download_url} to path={filename_path}"
        )
        with urllib.request.urlopen(download_url) as f:
            bytes_io = io.BytesIO(f.read())
        download_file = zipfile.ZipFile(bytes_io)
        download_file.extract("tf-profile", filename_directory)

    filename_path.chmod(0o555)
    return filename_path
