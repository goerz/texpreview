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


import sys
import re
from os.path import basename
import os
from struct import *
import TexpreviewPrinter as Out
VERB_SILENT = Out.VERB_SILENT
VERB_ERR    = Out.VERB_ERR
VERB_WARN   = Out.VERB_WARN
VERB_STATUS = Out.VERB_STATUS
VERB_DEBUG  = Out.VERB_DEBUG


numRuns = 0

def percent_escape(str):
	return re.sub('[\x80-\xff /&]', lambda x: '%%%02X' % unpack('B', x.group(0))[0], str)

def make_link(file, line):
	return 'file: ' + percent_escape(file) + '; line=' + line

def shell_quote(string):
	return '"' + re.sub(r'([`$\\"])', r'\\\1', string) + '"'

class TexParser(object):
    """Master Class for Parsing Tex Typesetting Streams"""
    def __init__(self, input_stream, verbose=True):
        super(TexParser, self).__init__()
        self.input_stream = input_stream
        self.done = False
        self.verbose = verbose
        self.numErrs = 0
        self.numWarns = 0
        self.isFatal = False
        self.patterns = {}
        
    def parseStream(self):
        """docstring for parseStream"""
        line = self.input_stream.readline()

        while line and not self.done:
            line = line
            foundMatch = False

            # process matching patterns until we find one
            for pat in self.patterns.keys():
                myMatch = pat.match(line)
                if myMatch:
                    self.patterns[pat](myMatch,line)
                    foundMatch = True
                    break
            
            if self.verbose and not foundMatch:
                Out.write("DEBUG: writing 'verbose' line\n", VERB_STATUS, stream='sub')
                Out.write(line, VERB_STATUS, stream='sub')
            
            line = self.input_stream.readline()

        return self.isFatal, self.numErrs, self.numWarns

    def info(self,m,line):
        Out.write("DEBUG: Texparser.info()\n", VERB_STATUS, stream='sub')
        Out.write(line, VERB_STATUS, stream='sub')
    
    def error(self,m,line):
        Out.write("DEBUG: Texparser.error()\n", VERB_STATUS, stream='sub')
        Out.write(line, VERB_ERR, stream='sub')
        self.numErrs += 1

    def warning(self,m,line):
        Out.write("DEBUG: Texparser.warning()\n", VERB_STATUS, stream='sub')
        Out.write(line, VERB_WARN, stream='sub')
        self.numWarns += 1

class BibTexParser(TexParser):
    """Parse and format Error Messages from bibtex"""
    def __init__(self, btex, verbose=True):
        super(BibTexParser, self).__init__(btex,verbose)
        self.patterns = { 
            re.compile("Warning--I didn't find a database entry") : self.warning,
            re.compile(r'I found no \\\w+ command') : self.error,            
            re.compile('---') : self.finishRun
        }
    
    def finishRun(self,m,line):
        self.done = True

class LaTexParser(TexParser):
    """Parse Output From Latex"""
    def __init__(self, input_stream, verbose=True):
        super(LaTexParser, self).__init__(input_stream,verbose)
        self.patterns = {
            re.compile('^This is') : self.info,
            re.compile('^Document Class') : self.info,
            re.compile('^Latexmk') : self.info,
            re.compile('Run number') : self.newRun,
            re.compile('.*\((\.\/.*\.tex)') : self.detectNewFile,
            re.compile('^\s+file:line:error style messages enabled') : self.detectFileLineErr,
            re.compile('.*\<use (.*?)\>') : self.detectInclude,
            re.compile('^Output written') : self.info,
            re.compile('LaTeX Warning.*?input line (\d+).$') : self.handleWarning,
            re.compile('LaTeX Warning:.*') : self.warning,
            re.compile('^([\.\/\w\x7f-\xff ]+\.tex):(\d+):(.*)') : self.handleError,
            re.compile('([^:]*):(\d+): LaTeX Error:(.*)') : self.handleError,
            re.compile('([^:]*):(\d+): (Emergency stop)') : self.handleError,
            re.compile('Transcript written on (.*).$') : self.linkToLog,
            re.compile("Running 'bibtex") : self.startBibtex,
            re.compile('This is BibTeX,') : self.startBibtex,            
            re.compile("Running 'makeindex") : self.startBibtex,    # TODO: implement real MakeIndexParser
            re.compile("This is makeindex") : self.startBibtex,            
            re.compile('^Error: pdflatex') : self.pdfLatexError,
            re.compile('\!.*') : self.handleOldStyleErrors
        }
                

    def newRun(self,m,line):
        Out.write("DEBUG: LaTexparser.newRun()\n", VERB_STATUS, stream='sub')
        global numRuns
        text =  self.numErrs + ' Errors ' + self.numWarns + " Warnings in this run.\n"
        Out.write(text, VERB_STATUS, stream='sub')
        self.numWarns = 0
        self.numErrs = 0
        numRuns += 1

    def detectNewFile(self,m,line):
        Out.write("DEBUG: LaTexparser.detectNewFile()\n", VERB_STATUS, stream='sub')
        self.currentFile = m.group(1)
        text = "\nTypesetting: " + self.currentFile + "\n\n"
        Out.write(text, VERB_STATUS, stream='sub')

    def detectFileLineErr(self,m,line):
        Out.write("DEBUG: LaTexparser.detectFileLineErr()\n", VERB_STATUS, stream='sub')
        self.fileLineErrors = True

    def detectInclude(self,m,line):
        Out.write("DEBUG: LaTexparser.detectInclude()\n", VERB_STATUS, stream='sub')
        text =  "    Including: " + m.group(1) + "\n"
        Out.write(text, VERB_STATUS, stream='sub')

    def handleWarning(self,m,line):
        Out.write("DEBUG: LaTexparser.handleWarning()\n", VERB_STATUS, stream='sub')
        text = '[' + make_link(os.getcwd()+self.currentFile[1:], m.group(1)) + '] '+line
        Out.write(text, VERB_WARN, stream='sub')
        self.numWarns += 1
    
    def handleError(self,m,line):
        Out.write("DEBUG: LaTexparser.handleError()\n", VERB_STATUS, stream='sub')
        latexErrorMsg = 'Latex Error: [' + make_link(os.getcwd()+'/'+m.group(1),m.group(2)) +  '] ' + m.group(1)+":"+m.group(2) + m.group(3) + "\n"
        line = self.input_stream.readline()
        while len(line) > 1:
            latexErrorMsg = latexErrorMsg+line
            line = self.input_stream.readline()
        Out.write(latexErrorMsg, VERB_WARN, stream='sub')
        self.numErrs += 1

    def linkToLog(self,m,line):
        Out.write("DEBUG: LaTexparser.linkToLog)\n", VERB_STATUS, stream='sub')
        text = 'logfile: ' + m.group(1) + "\n"
        Out.write(text, VERB_STATUS, stream='sub')

    def startBibtex(self,m,line):
        Out.write("DEBUG: LaTexparser.startBibtex()\n", VERB_STATUS, stream='sub')
        text = "\n" + line[:-1] + "\n"
        Out.write(text, VERB_STATUS, stream='sub')
        bp = BibTexParser(self.input_stream,self.verbose)
        self.input_stream.readline() # swallow the following line of '---'
        f,e,w = bp.parseStream()
        self.numErrs += e
        self.numWarns += w

    def handleOldStyleErrors(self,m,line):
        Out.write("DEBUG: LaTexparser.handleOldStyleErrors()\n", VERB_STATUS, stream='sub')
        if re.match('\! LaTeX Error:', line):
            Out.write(text, VERB_ERR, stream='sub')
            self.numErrs += 1
        else:
            Out.write(text, VERB_WARN, stream='sub')
            self.numWarns += 1

    def pdfLatexError(self,m,line):
        """docstring for pdfLatexError"""
        Out.write("DEBUG: LaTexparser.pdfLatexError()\n", VERB_STATUS, stream='sub')
        self.numErrs += 1
        Out.write(line, VERB_ERR, stream='sub')
        line = self.input_stream.readline()
        if line and re.match('^ ==> Fatal error occurred', line):
            Out.write(line, VERB_ERR, stream='sub')
            self.isFatal = True
        else:
            pass

