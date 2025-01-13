#!/usr/bin/env python
# coding: utf8
# Part of the bioread package for reading BIOPAC data.
#
# Copyright (c) 2023 Board of Regents of the University of Wisconsin System
#
# Written Nate Vack <njvack@wisc.edu> with research from John Ollinger
# at the Waisman Laboratory for Brain Imaging and Behavior, University of
# Wisconsin-Madison
# Project home: http://github.com/njvack/bioread
#
# This script pulls all the markers from an AcqKnowledge file and writes it
# to a delimited format.

"""Print the event markers from an AcqKnowledge file.

Usage:
  acq_markers [options] <file>...
  acq_markers -h | --help
  acq_markers --version

Options:
  -o <file>     Write to a file instead of standard output.
"""

from __future__ import unicode_literals, absolute_import, division, with_statement

import sys
import csv

from docopt import docopt
from bioread import reader
from bioread import _metadata as meta


FIELDS = [
    "filename",
    "time (s)",
    "label",
    "channel",
    "date_created",
    "type_code",
    "type",
]


def u8fx():
    if isinstance("x", str):
        return lambda s: s
    else:
        return lambda s: s.encode("utf-8")


uf = u8fx()


def marker_formatter(acq_filename, graph_sample_msec):
    """Return a function that turns a marker into a dict."""

    def f(marker):
        return {
            "filename": uf(acq_filename),
            "time (s)": (marker.sample_index * graph_sample_msec) / 1000,
            "label": uf(marker.text),
            "channel": uf(marker.channel_name or "Global"),
            "date_created": uf(marker.date_created_str),
            "type_code": uf(marker.type_code or "None"),
            "type": uf(marker.type),
        }

    return f


def acq_markers_output_file(input_filenames, output_filename):
    with open(output_filename, "w") as f:
        return acq_markers(input_filenames, f)


def acq_markers(input_filenames, output_stream=None):
    """out示范输出
    [{'filename': '1103-6-活动没启动.acq', 'time (s)': 148.288, 'label': 'Segment 1',
    'channel': 'Global', 'date_created': '2023-11-03T07:11:38   .905000+00:00',
    'type_code': 'apnd', 'type': 'Append'}, ...]
    其中时间为ISO 8601格式，可以datetime.fromisoformat(time_str1)转换为datetime格式"""
    if output_stream is None:
        out = []
    else:
        out = csv.DictWriter(output_stream, FIELDS, delimiter=str("\t"))
        out.writeheader()
    for fname in input_filenames:
        with open(fname, "rb") as infile:
            r = reader.Reader.read_headers(infile)
            mf = marker_formatter(fname, r.graph_header.sample_time)
            for m in r.datafile.event_markers:
                if output_stream is None:
                    out.append(mf(m))
                else:
                    out.writerow(mf(m))
    if output_stream is None:
        return out


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    pargs = docopt(__doc__, args, version=meta.version_description)

    if pargs["-o"]:
        return acq_markers_output_file(pargs["<file>"], pargs["-o"])
    else:
        return acq_markers(pargs["<file>"], sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
