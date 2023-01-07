#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Tool that converts autokey phrase expansions to espanso phrase expansions
#
# Ansgar Grunseid
# grunseid.com
# grunseid@gmail.com
#
# License: MIT
#

"""Tool that converts autokey phrase expansions to espanso phrase expansions

Usage:
  autokey-phrases-to-espanso-phrases.py [options] <autokey-cfg-directory>
  autokey-phrases-to-espanso-phrases.py -h | --help
  autokey-phrases-to-espanso-phrases.py --version

Options:
  --indent=<num-spaces>   The number of spaces to indent. [default: 2]
  --preserve-case=<bool>  Preserve case, w->with and W->WITH, or not [default: true]
  -h --help               Show this help information.
  --version               Show version.

Examples:
  autokey-phrases-to-espanso-phrases.py /path/to/autokey/configuration/directory
"""


import json
from glob import iglob
import os.path as path

from icecream import ic
from docopt import docopt


def main(autokeyCfgDir, preserveCase, indentation):
    if not path.isdir(autokeyCfgDir):
        raise ValueError(f'{autokeyCfgDir} not a directory. directory required')

    phrases = []
    matchTxtFiles = path.join(autokeyCfgDir, '*.txt')
    for txtpath in iglob(matchTxtFiles):
        dirname, fname = path.split(txtpath)
        fname = '.' + fname.rsplit('.', 1)[0] + '.json'
        jspath = path.join(dirname, fname)

        # make sure the matching .json file both exists and is valid json
        if not path.isfile(jspath):
            print(f'{txtpath} has no matching .json file. skipping')
            continue

        js = None
        with open(jspath, 'r') as f:
            try:
                js = json.load(f)
            except Exception:
                print(f"{txtpath}'s .json file is invalid json. skipping")
                continue

        if js.get('type').lower() != 'phrase':
            continue

        with open(txtpath, 'r') as f:
            replacement = f.read()

        abbreviation = js.get('abbreviation', {})
        triggers = abbreviation.get('abbreviations')
        wordOnly = bool(abbreviation.get('wordChars'))

        phrases.append((triggers, wordOnly, replacement))

    for triggers, wordOnly, replacement in phrases:
        # example yaml espanso phrase replacement config:
        #
        #   - trigger: "alh"
        #     replace: "although"
        #     word: true
        #     propagate_case: true
        #
        # wrt backslashes: for reasons unknown, the abbreviation "\'",
        # or a backslash followed by a single quote, triggers on every
        # typed single quote, even without a typed prefix backslash
        # first. for this exception, the backslash needs to be a double
        # backslash, "\\'", in the yaml cfg
        #
        # this backslash behavior doesnt occur with other abbreviations,
        # like '\brain'; '\brain' doesn't need to become '\\brain'
        triggers = [t.replace("\\'", "\\\\'") for t in triggers]
        triggersStr = str(triggers).replace("\\\\", "\\")
        s = (
            f'{indentation}- triggers: {triggersStr}\n'
            f'{indentation}  replace: "{replacement}"\n'
            f'{indentation}  word: {str(wordOnly).lower()}\n'
            f'{indentation}  propagate_case: {str(preserveCase).lower()}')
        print(s)


if __name__ == '__main__':
    args = docopt(__doc__)  # Raises SystemExit.

    autokeyCfgDir = args.get('<autokey-cfg-directory>')
    preserveCase = args.get('--preserve-case')
    indentation = ' ' * int(args.get('--indent'))

    main(autokeyCfgDir, preserveCase, indentation)
