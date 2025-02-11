import importlib.util
import sys
from types import ModuleType
from uuid import uuid4

import pytest

import prefect
from prefect.docker import docker_client
from prefect.utilities.importtools import (
    from_qualified_name,
    lazy_import,
    to_qualified_name,
)


def my_fn():
    pass


class Foo:
    pass


@pytest.mark.parametrize(
    "obj,expected",
    [
        (to_qualified_name, "prefect.utilities.importtools.to_qualified_name"),
        (prefect.tasks.Task, "prefect.tasks.Task"),
        (prefect.tasks.Task.__call__, "prefect.tasks.Task.__call__"),
        (lambda x: x + 1, "tests.utilities.test_importtools.<lambda>"),
        (my_fn, "tests.utilities.test_importtools.my_fn"),
    ],
)
def test_to_qualified_name(obj, expected):
    assert to_qualified_name(obj) == expected


@pytest.mark.parametrize("obj", [to_qualified_name, prefect.tasks.Task, my_fn, Foo])
def test_to_and_from_qualified_name_roundtrip(obj):
    assert from_qualified_name(to_qualified_name(obj)) == obj


@pytest.fixture
def pop_docker_module():
    # Allows testing of `lazy_import` on a clean sys
    orginal = sys.modules.pop("docker")
    try:
        yield
    finally:
        sys.modules["docker"] = orginal


@pytest.mark.usefixtures("pop_docker_module")
def test_lazy_import():
    docker: ModuleType("docker") = lazy_import("docker")
    assert isinstance(docker, importlib.util._LazyModule)
    assert isinstance(docker, ModuleType)
    assert callable(docker.from_env)


@pytest.mark.service("docker")
def test_lazy_import_does_not_break_type_comparisons():
    docker = lazy_import("docker")
    docker.errors = lazy_import("docker.errors")

    with docker_client() as client:
        try:
            client.containers.get(uuid4().hex)  # Better not exist
        except docker.errors.NotFound:
            pass

    # The exception should not raise but can raise if `lazy_import` creates a duplicate
    # copy of the `docker` module


def test_lazy_import_fails_for_missing_modules():
    with pytest.raises(ModuleNotFoundError, match="flibbidy"):
        lazy_import("flibbidy", error_on_import=True)


def test_lazy_import_allows_deferred_failure_for_missing_module():
    module = lazy_import("flibbidy", error_on_import=False)
    assert isinstance(module, ModuleType)
    with pytest.raises(ModuleNotFoundError, match=f"No module named 'flibbidy'") as exc:
        module.foo
    assert (
        "module = lazy_import" in exc.exconly()
    ), "Exception should contain original line in message"


def test_lazy_import_includes_help_message_for_missing_modules():
    with pytest.raises(
        ModuleNotFoundError, match="No module named 'flibbidy'.\nHello world"
    ):
        lazy_import("flibbidy", error_on_import=True, help_message="Hello world")


def test_lazy_import_includes_help_message_in_deferred_failure():
    module = lazy_import(
        "flibbidy",
        error_on_import=False,
        help_message="No module named 'flibbidy'.*Hello world",
    )
    assert isinstance(module, ModuleType)
    with pytest.raises(
        ModuleNotFoundError, match="No module named 'flibbidy'.*Hello world"
    ):
        module.foo
