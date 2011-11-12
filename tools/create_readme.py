#!/usr/bin/env python

# A quick and dirty tool from extracting a subset of our documentation and
# converting it into a Github/BitBucket-friendly README.rst file.
#
# Mark Shroyer
# Tue Nov  8 22:14:45 EST 2011

from __future__ import print_function

import re
from os.path import realpath, dirname, join

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
        sub1_line = re.sub(r':(?:[\w\d]+:)+`~(?:[\w\d]+\.)+([\w\d]+)`', r'``\1``', line)
        sub2_line = re.sub(r':(?:[\w\d]+:)+`([\w\d\.]+)`', r'``\1``', sub1_line)
        self.lines.append(sub2_line)

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

def print_sections(reader, dest, section_names):
    for section in reader.sections:
        if section.name in section_names:
            print(section.get_text(), file=dest)

if __name__ == '__main__':
    project_root = realpath(join(dirname(__file__), '..'))

    reader = RstReader(join(project_root, "doc", "overview.rst"))
    with open(join(project_root, "README.rst"), "w") as out_file:
        print_sections(reader, out_file, set(["Introduction"]))

        print("""Getting Pointfree
-----------------

``pointfree``'s full documentation can be found on the web at:

http://pointfree.rtfd.org/

For the latest version of the module, visit its Github page:

https://github.com/markshroyer/pointfree/

""", file=out_file)
        
        print_sections(reader, out_file, set(["Examples"]))
