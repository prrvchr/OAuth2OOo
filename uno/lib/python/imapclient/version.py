# Copyright (c) 2025, Menno Smits
# Released subject to the New BSD License
# Please see http://en.wikipedia.org/wiki/BSD_licenses

from importlib import metadata
from typing import Tuple

<<<<<<< HEAD
version = metadata.version("imapclient")
=======
version_info = (3, 1, 0, "final")
>>>>>>> 6bdf97b2 (new version 1.7.0)


def _make_version_info() -> Tuple[int, int, int, str]:
    major, minor, micro = version.split(".")
    return (int(major), int(minor), int(micro), "final")


<<<<<<< HEAD
# This is for backwards compatibility with older versions of IMAPClient only
version_info = _make_version_info()
=======
version = _imapclient_version_string(version_info)

maintainer = "IMAPClient Maintainers"
maintainer_email = "imapclient@groups.io"

author = "Menno Finlay-Smits"
author_email = "hello@menno.io"
>>>>>>> 6bdf97b2 (new version 1.7.0)
