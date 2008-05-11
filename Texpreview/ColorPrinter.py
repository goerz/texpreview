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

""" This module contains the ColorPrinter class, which implements colored
    output"""

import sys
import re

COLORS = ['BLACK', 'BLUE', 'GREEN', 'CYAN', 'RED', 
          'MAGENTA', 'YELLOW', 'WHITE']

class CursesNotAvailable(Exception):
    """ Raised by ColorPrinter if mode was set to 'curses', but curses is 
        not available """
    pass

class WinNotAvailable(Exception):
    """ Raised by ColorPrinter if mode was set to 'win', but win is not 
        available """
    pass

class UnknownColor(Exception):
    """ Raised if the ColorPrinter or any of the TerminalControllers is set
        to an unknown color
    """ 
    pass



class ColorPrinter(object):
    """ Class that provides an interface to color printing """
    def __init__(self, mode='auto', term_stream=sys.stdout):
        """ Initialize the color printer """
        self._requested_mode = mode
        self._backend = None
        self._color = None
        self._background = None
        self.handle = term_stream
        self.bold = None
        self.bgbold = None
        self._used_mode = self.set_mode(mode)
    
    def write(self, text):
        """ print text in color to handle"""
        if self._used_mode == "none":
            self.handle.write(text)
        else:
            backend = self._backend
            if self.color is not None:
                backend.set_color(self.color)
            if self.background is not None:
                backend.set_background(self.background)
            if self.bold is not None:
                backend.bold = self.bold
            if self.bgbold is not None:
                backend.bgbold = self.bgbold
            backend.write(text)
    
    def warn(self, text):
        """ print text in color to sys.stderr"""
        handle = self.handle
        self.handle = sys.stderr
        self.write(text)
        self.handle = handle
    
    def set_color(self, color):
        """ Set foreground color """
        color = color.upper()
        if color not in COLORS:
            raise UnknownColor, color
        self._color = color
    color = property(lambda self: self._color, set_color)
    
    def set_background(self, color):
        """ Set background color """
        color = color.upper()
        if color not in COLORS:
            raise UnknownColor, color
        self._background = color
    background = property(lambda self: self._background, set_background )
    
    def set_mode(self, mode):
        """ Try to set mode. Return mode that was actually set """
        if mode == "auto":
            try:
                self._backend = CursesTerminalController()
                return 'curses'
            except CursesNotAvailable:
                try:
                    self._backend = WinTerminalController()
                    return 'win'
                except WinNotAvailable:
                    self._backend = None # TODO: AnsiTerminalController()
                    return 'ansi'
        if mode == "curses":
            self._backend = CursesTerminalController()
            return 'curses'
        if mode == "win":
            self._backend = WinTerminalController()
            return 'curses'
        if mode == "ansi":
            self._backend = None # TODO: AnsiTerminalController()
            return 'ansi'
        return 'none'

    def get_mode(self):
        """ Return a tuple that consists of the set mode and the 
            mode actually used """
        return (self._requested_mode, self._used_mode)


class AnsiTerminalController(object):
    """
    bla
    """
    def __init__(self, term_stream=sys.stdout):
        """ bla """
        raise NotImplementedError
        
    def set_color(self, color):
        """ Set foreground color """
        raise NotImplementedError
    def set_background(self, color):
        """ Set background color """
        raise NotImplementedError
    def set_bold(self, value=True):
        """ Switch on or off foreground bold """
        raise NotImplementedError
    def set_bgbold(self, value=True):
        """ Switch on or off background bold """
        raise NotImplementedError
    
    def write(self, text):
        raise NotImplementedError


class WinTerminalController(object):
    """
    bla
    """
    STD_INPUT_HANDLE  = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE  = -12
    
    FOREGROUND_BLUE  = 0x01 # text color contains blue.
    FOREGROUND_GREEN = 0x02 # text color contains green.
    FOREGROUND_RED   = 0x04 # text color contains red.
    FOREGROUND_INTENSITY = 0x08 # text color is intensified.
    BACKGROUND_BLUE  = 0x10 # background color contains blue.
    BACKGROUND_GREEN = 0x20 # background color contains green.
    BACKGROUND_RED   = 0x40 # background color contains red.
    BACKGROUND_INTENSITY = 0x80 # background color is intensified.
    
    def __init__(self, term_stream=sys.stdout):
        # See http://msdn.microsoft.com/library/default.asp?url=/library/
        #  en-us/winprog/winprog/windows_api_reference.asp
        # for information on Windows APIs.
        
        try:
            import ctypes
        except:
            raise WinNotAvailable
        
        std_handle = None
        if term_stream is sys.stdout:
            std_handle = self.STD_OUTPUT_HANDLE
        if term_stream is sys.stderr:
            std_handle = self.STD_ERROR_HANDLE
        if std_handle is None:
            # only the standard terminals are supported
            raise WinNotAvailable
        
        self.handle = ctypes.windll.kernel32.GetStdHandle(std_handle)
        
    def _internal_set_color(self, color):
        """(color) -> BOOL
        
        Example: 
        _internal_set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        """
        handle = self.handle
        result = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return result
    
    def set_color(self, color):
        """ Set foreground color """
        raise NotImplementedError
    def set_background(self, color):
        """ Set background color """
        raise NotImplementedError
    def set_bold(self, value=True):
        """ Switch on or off foreground bold """
        raise NotImplementedError
    def set_bgbold(self, value=True):
        """ Switch on or off background bold """
        raise NotImplementedError
    
    def write(self, text):
        raise NotImplementedError



class CursesTerminalController(object):
    """
    A class that can be used to portably generate formatted output to
    a terminal.  
    
    `CursesTerminalController` defines a set of instance variables 
    whose values are initialized to the control sequence necessary to
    perform a given action.  These can be simply included in normal
    output to the terminal:

        >>> term = CursesTerminalController()
        >>> print 'This is '+term.GREEN+'green'+term.NORMAL

    Alternatively, the `render()` method can used, which replaces
    '${action}' with the string required to perform 'action':

        >>> term = CursesTerminalController()
        >>> print term.render('This is ${GREEN}green${NORMAL}')

    If the terminal doesn't support a given action, then the value of
    the corresponding instance variable will be set to ''.  As a
    result, the above code will still work on terminals that do not
    support color, except that their output will not be colored.
    Also, this means that you can test whether the terminal supports a
    given action by simply testing the truth value of the
    corresponding instance variable:

        >>> term = CursesTerminalController()
        >>> if term.CLEAR_SCREEN:
        ...     print 'This terminal supports clearning the screen.'

    Finally, if the width and height of the terminal are known, then
    they will be stored in the `COLS` and `LINES` attributes.
    
    If there's a problem during initialization that implies the terminal
    can't print color with curses, CursesNotAvailable is raised.
    
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/475116
    """
    # Cursor movement:
    BOL = ''             #: Move the cursor to the beginning of the line
    UP = ''              #: Move the cursor up one line
    DOWN = ''            #: Move the cursor down one line
    LEFT = ''            #: Move the cursor left one char
    RIGHT = ''           #: Move the cursor right one char

    # Deletion:
    CLEAR_SCREEN = ''    #: Clear the screen and move to home position
    CLEAR_EOL = ''       #: Clear to the end of the line.
    CLEAR_BOL = ''       #: Clear to the beginning of the line.
    CLEAR_EOS = ''       #: Clear to the end of the screen

    # Output modes:
    BOLD = ''            #: Turn on bold mode
    BLINK = ''           #: Turn on blink mode
    DIM = ''             #: Turn on half-bright mode
    REVERSE = ''         #: Turn on reverse-video mode
    NORMAL = ''          #: Turn off all modes

    # Cursor display:
    HIDE_CURSOR = ''     #: Make the cursor invisible
    SHOW_CURSOR = ''     #: Make the cursor visible

    # Terminal size:
    COLS = None          #: Width of the terminal (None for unknown)
    LINES = None         #: Height of the terminal (None for unknown)

    # Foreground colors:
    BLACK = BLUE = GREEN = CYAN = RED = MAGENTA = YELLOW = WHITE = ''
    
    # Background colors:
    BG_BLACK = BG_BLUE = BG_GREEN = BG_CYAN = ''
    BG_RED = BG_MAGENTA = BG_YELLOW = BG_WHITE = ''
    
    _STRING_CAPABILITIES = """
    BOL=cr UP=cuu1 DOWN=cud1 LEFT=cub1 RIGHT=cuf1
    CLEAR_SCREEN=clear CLEAR_EOL=el CLEAR_BOL=el1 CLEAR_EOS=ed BOLD=bold
    BLINK=blink DIM=dim REVERSE=rev UNDERLINE=smul NORMAL=sgr0
    HIDE_CURSOR=cinvis SHOW_CURSOR=cnorm""".split()
    _COLORS = """BLACK BLUE GREEN CYAN RED MAGENTA YELLOW WHITE""".split()
    _ANSICOLORS = "BLACK RED GREEN YELLOW BLUE MAGENTA CYAN WHITE".split()

    def __init__(self, term_stream=sys.stdout):
        """
        Create a `CursesTerminalController` and initialize its attributes
        with appropriate values for the current terminal.
        `term_stream` is the stream that will be used for terminal
        output; if this stream is not a tty, then the terminal is
        assumed to be a dumb terminal (i.e., have no capabilities).
        
        If there's a problem doing color output with curses (curses not
        available or terminal has no capabilities, CursesNotAvailable is
        raised.
        """
        self.term_stream = term_stream
        self._color = None
        self._background = None
        self.bold = None
        self.bgbold = None
        try: 
            import curses
        except:
            raise CursesNotAvailable

        # If the stream isn't a tty, then assume it has no capabilities.
        try:
            if not term_stream.isatty(): 
                raise CursesNotAvailable
        except:
            raise CursesNotAvailable

        # Check the terminal type.  If we fail, then assume that the
        # terminal has no capabilities.
        try: 
            curses.setupterm()
        except: 
            raise CursesNotAvailable

        # Look up numeric capabilities.
        self.COLS = curses.tigetnum('cols')
        self.LINES = curses.tigetnum('lines')
        
        # Look up string capabilities.
        for capability in self._STRING_CAPABILITIES:
            (attrib, cap_name) = capability.split('=')
            setattr(self, attrib, self._tigetstr(cap_name) or '')

        # Colors
        set_fg = self._tigetstr('setf')
        if set_fg:
            for i, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, color, curses.tparm(set_fg, i) or '')
        set_fg_ansi = self._tigetstr('setaf')
        if set_fg_ansi:
            for i, color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                setattr(self, color, curses.tparm(set_fg_ansi, i) or '')
        set_bg = self._tigetstr('setb')
        if set_bg:
            for i, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, 'BG_'+color, curses.tparm(set_bg, i) or '')
        set_bg_ansi = self._tigetstr('setab')
        if set_bg_ansi:
            for i, color in zip(range(len(self._ANSICOLORS)), self._ANSICOLORS):
                setattr(self, 'BG_'+color, curses.tparm(set_bg_ansi, i) or '')

    def _tigetstr(self, cap_name):
        # String capabilities can include "delays" of the form "$<2>".
        # For any modern terminal, we should be able to just ignore
        # these, so strip them out.
        import curses
        cap = curses.tigetstr(cap_name) or ''
        return re.sub(r'\$<\d+>[/*]?', '', cap)

    def render(self, template):
        """
        Replace each $-substitutions in the given template string with
        the corresponding terminal control string (if it's defined) or
        '' (if it's not).
        """
        return re.sub(r'\$\$|\${\w+}', self._render_sub, template)
    
    
    def set_color(self, color):
        """ Set foreground color """
        color = color.upper()
        if color not in COLORS:
            raise UnknownColor, color
        self._color = color
    color = property(lambda self: self._color, set_color)
    
    def set_background(self, color):
        """ Set background color """
        color = color.upper()
        if color not in COLORS:
            raise UnknownColor, color
        self._background = color
    background = property(lambda self: self._background, set_background)

    def write(self, text):
        """
        Write text to self.term_stream
        """
        if self.color is not None:
            self.term_stream.write(getattr(self, self._color.upper()))
        if self.background is not None:
            self.term_stream.write(getattr(self, 'BG_' \
                                                    + self._background.upper()))
        if self.bold is not None:
            if self.bold:
                self.term_stream.write(self.BOLD)
        # TODO: what about bold background?
        self.term_stream.write(self.render(text))


    def _render_sub(self, match):
        """ Internal function used by _render """
        s = match.group()
        if s == '$$': 
            return s
        else: 
            return getattr(self, s[2:-1])
