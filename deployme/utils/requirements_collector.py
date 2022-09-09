from contextlib import suppress
import os
import subprocess
import unittest.mock

from merge_requirements.manage_file import Merge
from pipreqsnb import pipreqsnb


__all__ = ["CustomMerge", "pip_reqs_nb_mocked"]


class CustomMerge(Merge):
    """
    Custom merge method inherited from Merge class
    in merge_requirements.manage_file
    """

    def __init__(self, mf):
        super().__init__(mf)

    def pickup_deps(self, ignore_prefixes: list, unique=True):
        """
        Custom method to pick up dependencies

        Args:
            ignore_prefixes (list): list of prefixes to ignore
            unique (bool): if True, return unique dependencies

        Returns:
            list: list of dependencies

        """

        array = []

        for key, value in self.dict_libs.items():
            if len(value) > 0:
                array.append("".join("{}=={}".format(key, value)))
            else:
                array.append("".join("{}".format(key)))

        result = cleanup_deps(array, ignore_prefixes)

        if unique:
            result = list(set(result))

        return result


def cleanup_deps(deps: list, ignore_prefixes: list) -> list:
    """
    Cleanup dependencies from unwanted prefixes

    Args:
        deps (list): List of dependencies
        ignore_prefixes (list): List of prefixes to ignore

    Returns:
        list: List of dependencies without unwanted prefixes

    Raises:
        None

    """

    cleaned = []

    for dep in deps:

        if (
            next((p for p in ignore_prefixes if p in dep), None)
            is not None
        ):
            continue

        cleaned.append(dep)

    return cleaned


def pip_reqs_nb_mocked():
    def call(args):

        retcode = subprocess.Popen(
            f"pipreqs {args}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        ).wait()

        if retcode != 0:
            raise Exception(
                "Error while running requirements generation."
            )

    with unittest.mock.patch(
        "pipreqsnb.pipreqsnb.run_pipreqs", call
    ), suppress(TypeError):
        pipreqsnb.main()
