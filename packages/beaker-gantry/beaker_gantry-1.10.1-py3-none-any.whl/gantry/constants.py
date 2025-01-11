DEFAULT_IMAGE = "ai2/conda"

ENTRYPOINT = "entrypoint.sh"

GITHUB_TOKEN_SECRET = "GITHUB_TOKEN"

CONDA_ENV_FILE = "environment.yml"

CONDA_ENV_FILE_ALTERNATE = "environment.yaml"

PIP_REQUIREMENTS_FILE = "requirements.txt"

RUNTIME_DIR = "/gantry-runtime"

RESULTS_DIR = "/results"

METRICS_FILE = f"{RESULTS_DIR}/metrics.json"

NFS_MOUNT = "/net/nfs.cirrascale"

CLUSTERS_WITHOUT_NFS = {
    "ai2/jupiter-cirrascale",
    "ai2/jupiter-cirrascale-2",
    "ai2/saturn-cirrascale",
    "ai2/neptune-cirrascale",
}
