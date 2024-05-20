# nebari-tf-profile-plugin

This extension uses [`tf-profile`](https://github.com/datarootsio/tf-profile) to parse Nebari's deploy and destroy Terraform output and summarize the duration and number of resources modified. It does this on a per-stage basis, creating one subfolder for each one of them.

## Installation
After installing Nebari, run:

```bash
git clone https://github.com/nebari-dev/nebari-tf-profile-plugin
pip install .
```

## Usage
To use the plugin, you just need to run either (or both) of `nebari deploy` and `nebari destroy`. The results will be stored in the current working directory, unless another output path is specified using the `NEBARI_TF_PROFILE_RESULTS_PATH` environment variable.
