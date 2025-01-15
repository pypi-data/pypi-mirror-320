import json
import logging
import cloudpickle
from collections import defaultdict
from os.path import isabs
from pathlib import Path
from typing import Any, List, Mapping

import pytest
from pytest_harvest import create_results_bag_fixture, get_session_results_dct
from pytest_harvest.xdist_api import is_xdist_worker

from .json_encoder import AdvancedJsonEncoder
from .models import EvalResult

# Constants
EVAL_MARK_NAME = "eval"
EVAL_ANALYSIS_MARK_NAME = "eval_analysis"

# Fixtures
eval_bag = create_results_bag_fixture("fixture_store", name="eval_bag")


@pytest.fixture(scope="function")
def eval_bag_results(request) -> Mapping[str, Mapping[str, Any]]:
    """Fixture that provides access to evaluation results."""
    ret = simple_eval_results(request.session)
    
    if not request.session.config.getoption("--run-eval"):
        if (request.session.config.out_path / "eval-results-raw.json").exists():
            with open(request.session.config.out_path / "eval-results-raw.json", "r") as f:
                ret.update(json.load(f))
    return ret


@pytest.fixture(scope="function")
def eval_results(request, eval_bag_results) -> List[EvalResult]:
    """Fixture that provides access to evaluation results as EvalResult objects."""
    marker = eval_analysis_marker(request.node.own_markers)
    if not marker:
        raise ValueError(
            f"Only tests marked with {EVAL_ANALYSIS_MARK_NAME} can use the eval_results fixture"
        )

    return [
        EvalResult.from_result_bag(v)
        for k, v in eval_bag_results.items()
        if v["eval_name"] == marker.kwargs["name"]
    ]


def pytest_addoption(parser, pluginmanager):
    """Add options to the pytest CLI."""
    group = parser.getgroup("Evals", "Evals configuration")
    group.addoption(
        "--out-path",
        action="store",
        default="./test-out/",
        help="Path to store test artifacts",
    )
    group.addoption(
        "--supress-failed-exit-code",
        action="store_true",
        default=False,
        help="Supress failed exit code. Useful for CI/CD with a separate step for test analysis",
    )
    group.addoption(
        "--run-eval",
        action="store_true",
        default=False,
        help="Run evaluation tests(mark with @pytest.mark.eval)",
    )
    group.addoption(
        "--run-eval-analysis",
        action="store_true",
        default=False,
        help="Run evaluation analysis tests(mark with @pytest.mark.eval_analysis)",
    )


def pytest_configure(config):
    """Configure the pytest session with the options."""
    config.addinivalue_line(
        "markers",
        "eval: mark test as evaluation test. Evaluation tests will only run when --run-eval is passed",
    )
    config.addinivalue_line(
        "markers",
        "eval_analysis: mark test as an evaluation analysis. Analysis tests MUST run after all other tests. Analysis tests will only run when --run_eval-analysis is passed",
    )

    out_path = Path(config.getoption("--out-path"))
    if not isabs(out_path):
        out_path = Path(config.invocation_dir / out_path)
    config.out_path = out_path
    config.out_path.mkdir(exist_ok=True)

@pytest.fixture
def out_path(request):
    return request.config.out_path

def is_xdist_session(config):
    """Check if the session is a xdist session."""
    return (
        hasattr(config, "workerinput")
        or hasattr(config, "workerid")
        or config.getoption("dist", "no") != "no"
    )


def eval_analysis_marker(markers: list[pytest.Mark]) -> pytest.Mark | None:
    """Get the eval_analysis marker if present."""
    m = next((m for m in markers if m.name == EVAL_ANALYSIS_MARK_NAME), None)
    if m and "name" not in m.kwargs:
        raise ValueError(
            f"Marker {EVAL_ANALYSIS_MARK_NAME} must have a 'name' argument"
        )
    return m


def eval_marker(markers: list[pytest.Mark]) -> pytest.Mark | None:
    """Get the eval marker if present."""
    m = next((m for m in markers if m.name == EVAL_MARK_NAME), None)
    if m and "name" not in m.kwargs:
        raise ValueError(f"Marker {EVAL_MARK_NAME} must have a 'name' argument")
    return m


def pytest_collection_modifyitems(config, items):
    """Modify the collection of items."""
    if (
        is_xdist_session(config)
        and config.getoption("--run-eval")
        and config.getoption("--run-eval-analysis")
    ):
        raise ValueError(
            "In xdist sessions, evaluation analysis must run after the evaluation tests "
            "(as a separated execution). Therefore, --run-eval and --run-eval-analysis "
            "cannot be used together"
        )

    run_eval = config.getoption("--run-eval")
    run_analysis = config.getoption("--run-eval-analysis")
    skip_eval = pytest.mark.skip(reason="need --run-eval option to run")
    skip_analysis = pytest.mark.skip(reason="need --run-eval-analysis option to run")

    for item in items[:]:
        is_eval = eval_marker(item.own_markers) is not None
        is_analysis = eval_analysis_marker(item.own_markers) is not None

        if is_analysis and is_eval:
            raise ValueError(
                f"{item.nodeid} is marked as both `{EVAL_MARK_NAME}` and "
                f"`{EVAL_ANALYSIS_MARK_NAME}`."
            )

        if run_eval or run_analysis:
            if is_eval and not run_eval:
                item.add_marker(skip_eval)
            elif is_analysis and not run_analysis:
                item.add_marker(skip_analysis)
            elif not is_eval and not is_analysis:
                items.remove(item)
        else:
            if is_eval:
                item.add_marker(skip_eval)
            if is_analysis:
                item.add_marker(skip_analysis)


def pytest_sessionfinish(session):
    """Handle session finish."""
    prev_exitstatus = getattr(session, "exitstatus", 0)
    if bool(session.config.getoption("--supress-failed-exit-code", False)):
        session.exitstatus = 0

    if is_xdist_worker(session):
        return

    if (
        session.config.getoption("--run-eval")
        and prev_exitstatus != pytest.ExitCode.INTERNAL_ERROR
    ):
        res = simple_eval_results(session)
        with open(session.config.out_path / "eval-results-raw.json", "w") as f:
            json.dump(res, f, cls=AdvancedJsonEncoder)


def simple_eval_results(session):
    """Get simple evaluation results from the session."""
    res = get_session_results_dct(session, results_bag_fixture_name="eval_bag")

    ret = defaultdict(dict)
    for k, v in res.items():
        obj = v.get("pytest_obj", None)
        if not obj or not hasattr(obj, "pytestmark"):
            continue

        e_marker = eval_marker(obj.pytestmark)
        if not e_marker:
            continue

        ret[k] = {k1: v1 for k1, v1 in v.items() if k1 != "pytest_obj"}
        ret[k]["pytest_obj_name"] = v["pytest_obj"].__name__
        ret[k]["eval_name"] = e_marker.kwargs["name"]

    return ret


# XDist harvesting configuration
XDIST_HARVESTED_PATH = Path("./.xdist_harvested/")


def pytest_harvest_xdist_worker_dump(worker_id, session_items, fixture_store) -> bool:
    """Dump worker results using cloudpickle."""
    with open(XDIST_HARVESTED_PATH / f"{worker_id}.pkl", "wb") as f:
        try:
            cloudpickle.dump((session_items, fixture_store), f)
        except Exception as e:
            logging.warning(
                f"Error while pickling worker {worker_id}'s harvested results: [{e.__class__}] {e}"
            )
    return True


def pytest_harvest_xdist_load():
    """Load worker results using cloudpickle."""
    workers_saved_material = dict()
    for pkl_file in XDIST_HARVESTED_PATH.glob("*.pkl"):
        wid = pkl_file.stem
        with pkl_file.open("rb") as f:
            workers_saved_material[wid] = cloudpickle.load(f)
    return workers_saved_material
