""" Example from pytest documentation

https://pytest.org/en/stable/example/simple.html#incremental-testing-test-steps
"""

from typing import Dict, Tuple
import pytest

# store history of failures per test class name and per index in parametrize
# (if parametrize used)
_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):

    if "incremental" in item.keywords:
        # incremental marker is used

        # The following condition was modifed from the example linked above.
        # We don't want to step out of the incremental testing block if
        # a previous test was marked "Skipped". For instance if MPI tests
        # are skipped because mpi4py is not installed, still continue with
        # all other tests that do not require mpi4py
        if call.excinfo is not None and not call.excinfo.typename == "Skipped":
            # the test has failed, but was not skiped

            # retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test (if parametrize is used in
            # combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the original name of the
            # failed test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test (if parametrize is used in
            # combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the first test function to fail for this
            # class name and index
            test_name = _test_failed_incremental[cls_name].get(
                parametrize_index, None)
            # if name found, test has failed for the combination of class name
            # and test name
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))