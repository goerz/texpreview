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
    the texpreview program for all output.

    The module can handle printing messages to several streams (e.g. stdout,
    stderr, a file, etc). A message consists of a string and a verbosity 
    level. Each stream is defined by a maximum verbosity and a handle. 
    The stream verbosity specifies which messages are printed (messages with
    a higher verbosity level than the maximum verbosity of the stream are 
    dropped).

    The module has the following attributes:
        streams         Dictionary of stream names. By default, the following 
                        streams are defined:
                        
                        streams = {
                            'direct' : { 
                                'verbosity'  : DEFAULT_VERBOSITY,
                                'handle' : sys.stderr,
                                'styles' : { 
                                    VERB_SILENT : ...
                                    VERB_ERR    : ...
                                    VERB_WARN   : ...
                                    VERB_STATUS : ...
                                    VERB_DEBUG  : ...
                                            }
                                        },
                            'sub'    : { 
                                'verbosity'  : VERB_STATUS,
                                'handle' : sys.stdout,
                                'styles' : { 
                                    VERB_SILENT : ...
                                    VERB_ERR    : ...
                                    VERB_WARN   : ...
                                    VERB_STATUS : ...
                                    VERB_DEBUG  : ...
                                            }
                                    }
                                }
                    
       default_stream   The name of the stream that is used when no explicit 
                        stream is given with a call to the print method.
    
    The module also defines a number of constants for the levels. While the
    levels are just integers internally, you should only use the defined
    constants.
    
    The levels are:
    VERB_SILENT: No output
    VERB_ERR: Critical Errors
    VERB_WARN: Noncritical Warnings
    VERB_STATUS: Status Messages
    VERB_DEBUG: Debug Info

    Additionally, there is on more constant:
    DEFAULT_VERBOSITY = VERB_STATUS

    An example usage:

    >>> import TexpreviewPrinter as Out
    >>> Out.activate_color()
    >>> Out.write("Hello World in Blue on STDERR", level=Out.VERB_WARN)
    Hello World in Blue on STDERR
    >>> Out.write("Hello World in Red on STDERR", stream='direct', level=Out.VERB_ERR)
    Hello World in Red on STDERR
    >>> Out.write("Hello World in Red on STDOUT", stream='sub', level=Out.VERB_ERR)
    Hello World in Red on STDOUT
    >>> Out.activate_color(color=False)
    >>> Out.write("Hello World without color on STDOUT", stream='sub', level=Out.VERB_ERR)
    Hello World without color on STDOUT
    >>> Out.streams['direct']['verbosity'] = Out.VERB_ERR
    >>> Out.write("Hello World, below threshold, no output", level=Out.VERB_ERR)
"""


import sys

def nocolored(text, color=None, on_color=None, attrs=None):
    return text

try:
    from termcolor import colored as termcolored
    _colors_available = True
except ImportError:
    print "Color not available!"
    print "You need to install the termcolor module from"
    print "http://pypi.python.org/pypi/termcolor/0.1\n"
    termcolored = nocolored
    _colors_available = False

colored = nocolored # the 'colored' function should point to either 
                    # 'nocolored' or 'termcolored', depending on
                    # whether or not color is activated.

# Verbosity constants
VERB_SILENT = 0
VERB_ERR    = 1
VERB_WARN   = 2
VERB_STATUS = 3
VERB_DEBUG  = 4

DEFAULT_VERBOSITY = VERB_STATUS



streams = {
    'direct' : { 
        'verbosity'  : DEFAULT_VERBOSITY,
        'handle' : sys.stderr,
        'styles' : { 
            VERB_SILENT : lambda text: colored(text, attrs=['bold']),
            VERB_ERR    : lambda text: colored(text, 'red', attrs=['bold']),
            VERB_WARN   : lambda text: colored(text, 'blue', attrs=['bold']),
            VERB_STATUS : lambda text: colored(text, attrs=['bold']),
            VERB_DEBUG  : lambda text: colored(text, attrs=['bold'])
                    }
                },
    'sub'    : { 
        'verbosity'  : VERB_STATUS,
        'handle' : sys.stdout,
        'styles' : { 
            VERB_SILENT : lambda text: colored(text),
            VERB_ERR    : lambda text: colored(text, 'red'),
            VERB_WARN   : lambda text: colored(text, 'blue'),
            VERB_STATUS : lambda text: colored(text),
            VERB_DEBUG  : lambda text: colored(text)
                    }
               }
          }

default_stream = 'direct'



def write(text, level=DEFAULT_VERBOSITY, stream=None):
    """ If VERB_STATUS is below the verbosity threshold, print text to the 
        handle associated with stream, with the formatting belonging to 
        VERB_STATUS.
    """
    if stream is None:
        stream = default_stream
    if stream not in streams.keys():
        raise KeyError("%s is not a registered name for a stream" % stream)
    verbosity = streams[stream]['verbosity']
    if level <= verbosity:
        streams[stream]['handle'].write(streams[stream]['styles'][level](text))

def activate_color(color=True):
    """ Turn color output on (or off)
        Turning color on means that formatting takes effect. Colors are
        done with ANSI codes. If your terminal sucks, don't turn on colors.
    """
    global colored
    if color:
        if _colors_available:
            colored = termcolored
        else:
            sys.stderr.write("Module 'termcolor' is missing, color " \
                            + "capabilities are not available")
            colored = nocolored
    else:
        colored = nocolored
