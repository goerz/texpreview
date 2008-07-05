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
#    but WITHOut ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

""" This module contains the CompilerOutputPrinter class """

import TexpreviewPrinter as Out
VERB_SILENT = Out.VERB_SILENT
VERB_ERR    = Out.VERB_ERR
VERB_WARN   = Out.VERB_WARN
VERB_STATUS = Out.VERB_STATUS
VERB_DEBUG  = Out.VERB_DEBUG

class CompilerOutputPrinter:
    """ Pretty print the output of the compiler and other tools.
        Also, parse the output and set flags

        Modes: 'none', 'latex', 'bibtex', 'makeindex'
        Flags: ...
    """
    def __init__(self):
        self.mode = 'none'
    def write(self, infile):
        """ Print out the text found in the open filehandle 'infile'
        """
        for line in infile:
            level = level_from_line(line, self.mode)
            Out.write(line, level, stream='sub')

def level_from_line(line, mode='none'):
    """ Parse a line of text, and return the level of the line """
    return VERB_STATUS
