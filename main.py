import os

if not os.environ.get("CACHE_DIR"):
    from tempfile import gettempdir
    from conda_oci_mirror import defaults

    os.environ["CACHE_DIR"] = defaults.CACHE_DIR = os.path.join(
        gettempdir(), "oras-cache"
    )

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from conda_forge_metadata.oci import get_oci_artifact_data


app = FastAPI()


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse("/docs")


@app.get("/{channel}/{subdir}/{artifact}")
def artifact_metadata(channel: str, subdir: str, artifact: str):
    """
    Get metadata for a conda package from the conda-forge or bioconda channel.
    """
    if len(channel) > 50:
        raise HTTPException(status_code=400, detail="Channel name too long")
    if len(subdir) > 20:
        raise HTTPException(status_code=400, detail="Subdir name too long")
    if len(artifact) > 100:
        raise HTTPException(status_code=400, detail="Artifact name too long")
    if not artifact.endswith(".conda") and not artifact.endswith(".tar.bz2"):
        raise HTTPException(
            status_code=400,
            detail="Artifact extension not supported. Use .conda or .tar.bz2.",
        )

    data = get_oci_artifact_data(
        channel=channel,
        subdir=subdir,
        artifact=artifact,
    )
    if data:
        return data
    return {"error": "Artifact not found"}
