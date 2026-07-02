"""Drift guard: the committed models.py must equal a fresh generation from the
committed schema. If this fails, refresh the schema copy and regenerate the
models with the canonical command below (also documented in the README)."""
import subprocess
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Canonical generation command. Keep in sync with the README.
GEN_ARGS = [
    "--input", "schema/algo-feed.schema.json",
    "--input-file-type", "jsonschema",
    "--output-model-type", "pydantic_v2.BaseModel",
    "--target-python-version", "3.9",
    "--use-standard-collections",
    "--disable-timestamp",
    "--enum-field-as-literal", "all",
    "--collapse-root-models",
]


def _generate(out_path: pathlib.Path) -> str:
    subprocess.run(
        [sys.executable, "-m", "datamodel_code_generator", *GEN_ARGS, "--output", str(out_path)],
        cwd=ROOT,
        check=True,
    )
    return out_path.read_text()


def test_models_match_committed(tmp_path):
    fresh = _generate(tmp_path / "models.py")
    committed = (ROOT / "src/hlt_algo_feed/models.py").read_text()
    assert fresh == committed, "model drift: regenerate models.py (see README / GEN_ARGS)"
