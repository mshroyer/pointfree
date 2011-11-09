#!/usr/bin/env python

# A quick and dirty tool from extracting a subset of our documentation and
# converting it into a Github/BitBucket-friendly README.rst file.
#
# Mark Shroyer
# Tue Nov  8 22:14:45 EST 2011

import os, re

def section_delimiter(line):
    if len(line) == 0:
        return False
    last_char = line[0]
    for char in line:
        if char != last_char:
            return False
    return last_char

class RstSection(object):
    def __init__(self, name=None):
        self.name = name
        self.lines = []

    def add_line(self, line):
        sub_line = re.sub(r':(?:[\w\d]+:)+`([\w\d\.]+)`', r'``\1``', line)
        self.lines.append(sub_line)

    def get_text(self):
        return "\n".join(self.lines)

class RstReader(object):
    def __init__(self, filename):
        self.filename = filename

        section = RstSection()
        self.sections = [section]

        prev_line = ""
        with open(self.filename) as f:
            for line_raw in f.readlines():
                line = line_raw.rstrip("\n")
                if (len(prev_line) > 0) and (len(line) >= len(prev_line)) and section_delimiter(line):
                    section = RstSection(prev_line)
                    section.add_line(prev_line)
                    self.sections.append(section)
                else:
                    section.add_line(prev_line)
                prev_line = line

            section.add_line(line)

if __name__ == '__main__':
    reader = RstReader(os.path.join("doc", "overview.rst"))
    with open("README.rst", "w") as out_file:
        for section in reader.sections:
            if section.name in set(["Introduction", "Examples"]):
                print >> out_file, section.get_text()
