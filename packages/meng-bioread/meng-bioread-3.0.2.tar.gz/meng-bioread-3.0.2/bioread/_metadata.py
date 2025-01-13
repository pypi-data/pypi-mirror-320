# coding: utf8
# Part of the bioread package for reading BIOPAC data.
#
# Copyright (c) 2023 Board of Regents of the University of Wisconsin System
#
# Written Nate Vack <njvack@wisc.edu> with research from John Ollinger
# at the Waisman Laboratory for Brain Imaging and Behavior, University of
# Wisconsin-Madison
# Project home: http://github.com/njvack/bioread

# NOTE: This file must not import anything, or it will break installation.

version_tuple = (3, 0, 2)
version = ".".join([str(p) for p in version_tuple])
version_description = "bioread {0}".format(version)

author = "Original author: Nate Vack, current maintainer: Meng"
author_email = "Original author: njvack@wisc.edu, current maintainer: Meng"
license = "MIT"
copyright = (
    "Copyright (c) 2023 Boards of Regent of the University of Wisconsin System"  # noqa
)
url = "https://github.com/Schweik7/bioread"
