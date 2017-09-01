#!/usr/bin/env python

# Copyright 2017 Matthew Nakayama
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""Converts old-style column-formatted reports into OSD files"""

import enum
import pyexcel_ods3
import pprint
import sys


class ReportFile:
    def __init__(self, path, field_str=None):
        self._path = path
        self._field_offset = 0
        self._fields = {}

    def add_field(self, field_id, length):
        """ Adds a field length to the configuration."""
        self._fields[field_id] = (self._field_offset, self._field_offset
                                  + length)
        self._field_offset += length
        # print(self._fields)

    def read_line(self, line):
        record = {}
        for field_id, interval in self._fields.items():
            start, end = interval
            record[field_id] = line[start:end].rstrip()
        return record

    def read(self):
        records = []
        with open(self._path, 'r') as file:
            for line in file:
                if line.rstrip() != '':
                    records.append(self.read_line(line))
                # else: ignore line
        return records


class ArgumentReaderStates(enum.Enum):
    INITAL = enum.auto()
    READ_INPUT_FILE = enum.auto()
    READ_FIELD_CONFIG = enum.auto()
    READ_INPUT_FLAGS = enum.auto()
    READ_FIELD_ID = enum.auto()
    READ_FIELD_LEN = enum.auto()


class ArgumentReader:
    """State machine that interprets arguments from the command line"""
    def __init__(self, argv):
        self._state = ArgumentReaderStates.INITAL
        self.reports = []

        self.read_arguments(argv)

    def read_arguments(self, argv):
        for arg in argv[1:]:

            if self._state == ArgumentReaderStates.READ_INPUT_FLAGS:
                if arg == '-f':
                    self._state = ArgumentReaderStates.READ_FIELD_ID
                    # print("reading fields")
            elif (self._state == ArgumentReaderStates.INITAL
                    or self._state == ArgumentReaderStates.READ_INPUT_FLAGS):

                if arg == '-i':
                    self._state = ArgumentReaderStates.READ_INPUT_FILE
            elif self._state == ArgumentReaderStates.READ_INPUT_FILE:
                report_path = arg
                report = ReportFile(report_path)
                self.reports.append(report)
                self._state = ArgumentReaderStates.READ_INPUT_FLAGS

            elif self._state == ArgumentReaderStates.READ_FIELD_ID:
                field_id = arg
                self._state = ArgumentReaderStates.READ_FIELD_LEN

            elif self._state == ArgumentReaderStates.READ_FIELD_LEN:
                field_len = int(arg)
                report.add_field(field_id, field_len)
                self._state = ArgumentReaderStates.READ_INPUT_FLAGS

        if not len(self.reports):
            print("Error: No input files specified.")


def main():
    # unfortunately, we can't use argparse, because we need a state machine to
    # read the command line arguments.
    argument_reader = ArgumentReader(sys.argv)
    for report in argument_reader.reports:
        pprint.pprint(report.read())
if __name__ == "__main__":
    main()
