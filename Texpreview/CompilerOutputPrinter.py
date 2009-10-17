# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2008 by Michael Goerz                                   #
#    http://www.physik.fu-berlin.de/~goerz                                 #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

# This module is loosely based on some code by Brad Miller, which is part of
# the TexMate Latex Bundle

""" This module contains parsers for the output of the different latex 
    compilers 
"""


import re
import os
from struct import unpack
import TexpreviewPrinter as Out
VERB_SILENT = Out.VERB_SILENT
VERB_ERR    = Out.VERB_ERR
VERB_WARN   = Out.VERB_WARN
VERB_STATUS = Out.VERB_STATUS
VERB_DEBUG  = Out.VERB_DEBUG


numRuns = 0

class CompilerOutputPrinter(object):
    """Master Class for Parsing Tex Typesetting Streams"""
    def __init__(self, input_stream):
        self.input_stream = input_stream
        self.done = False
        self.numErrs = 0
        self.numWarns = 0
        self.isFatal = False
        self.warn_patterns = [( re.compile('warning', re.I),           False ),
                              ( re.compile('^(over|under)full', re.I), False ) ]
        self.err_patterns = [( re.compile('error', re.I), False ), 
                             ( re.compile('^!', re.I),    True  ) ]

    def parseStream(self):
        """docstring for parseStream"""
        line = self.input_stream.readline()

        VERB_CURR = VERB_STATUS
        keep_verb = False

        while line and not self.done:
            line = line

            if (line.rstrip() == ''):
                keep_verb = False
                VERB_CURR = VERB_STATUS

            # process matching patterns until we find one
            for (pat, pat_keep_verb) in self.warn_patterns:
                myMatch = pat.search(line)
                if myMatch:
                    self.numWarns += 1
                    keep_verb = pat_keep_verb
                    VERB_CURR = VERB_WARN
                    break
            for (pat, pat_keep_verb) in self.err_patterns:
                myMatch = pat.search(line)
                if myMatch:
                    self.numErrs += 1
                    keep_verb = pat_keep_verb
                    VERB_CURR = VERB_ERR
                    break

            Out.write("DEBUG: writing %s line\n" % VERB_CURR, VERB_DEBUG, stream='sub')
            Out.write(line, VERB_CURR, stream='sub')
            if not keep_verb:
                VERB_CURR = VERB_STATUS

            line = self.input_stream.readline()

        return self.isFatal, self.numErrs, self.numWarns


