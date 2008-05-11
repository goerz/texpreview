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

""" This module is the TexpreviewPrinter singleton, which is used by 
    the texpreview program for all direct output (i.e. not the ouput of 
    subprocesses)
    
    The levels are:
    VERB_SILENT: No output
    VERB_ERR: Critical Errors
    VERB_WARN: Noncritical Warnings
    VERB_STATUS: Status Messages
    VERB_DEBUG: Debug Info
"""

# TODO: extend documentation
# TODO: allow a fallback if ColorPrinter is not available

from ColorPrinter import ColorPrinter
import sys

# Verbosity constants
VERB_SILENT = 0
VERB_ERR    = 1
VERB_WARN   = 2
VERB_STATUS = 3
VERB_DEBUG  = 4

DEFAULT_VERBOSITY = VERB_STATUS


verbosity = DEFAULT_VERBOSITY
_color = False
_term_stream = sys.stderr
_backend = ColorPrinter('none', _term_stream)



def _set_silent_style():
    """ Set the formatting for level VERB_SILENT """
    pass
def _set_critical_style():
    """ Set the formatting for level VERB_ERR """
    pass
def _set_warning_style():
    """ Set the formatting for level VERB_WARN """
    pass
def _set_status_style():
    """ Set the formatting for level VERB_STATUS """
    pass
def _set_debug_style():
    """ Set the formatting for level VERB_DEBUG """
    pass
_styles = {VERB_SILENT : _set_silent_style,
            VERB_ERR : _set_critical_style,
            VERB_WARN : _set_warning_style,
            VERB_STATUS : _set_status_style,
            VERB_DEBUG :_set_debug_style
            }



def write(text, level=DEFAULT_VERBOSITY):
    """ If VERB_STATUS is below the verbosity threshold,
        print text with the formatting belonging to VERB_STATUS 
    """
    if level <= verbosity:
        _styles[level]()
        _backend.write(text)


def set_term_stream(term_stream):
    """ Set term_stream """
    global _term_stream
    _term_stream = term_stream
    colormode = 'none'
    if _color:
        colormode = 'auto'
    global _backend
    _backend = ColorPrinter(colormode, _term_stream)

def activate_color(color=True):
    """ Turn color output on (or off) """
    global _color
    _color = color
    global _backend
    _backend = ColorPrinter('auto', _term_stream)