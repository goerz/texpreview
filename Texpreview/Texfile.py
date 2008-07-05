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

""" This module contains the Texfile class and the CompilerOutputPrinter
    that is needed by it."""

import os
import sys
import re
import subprocess
import time
import shutil
from glob import glob
from CompilerOutputPrinter import CompilerOutputPrinter
import TexpreviewPrinter as Out
VERB_SILENT = Out.VERB_SILENT
VERB_ERR    = Out.VERB_ERR
VERB_WARN   = Out.VERB_WARN
VERB_STATUS = Out.VERB_STATUS
VERB_DEBUG  = Out.VERB_DEBUG


 # File extensions that should never be parsed as text.
BINARYEXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg', '.eps',
                    '.tif', '.tiff', '.dvi', '.ps',]

# File extensions that belong to bibtex. When these files change, it is
# treated like a changed citation
BIBEXTENSIONS = ['.bib', '.bst']



class Texfile:
    """ Class that represents a tex file and all it's compile options

        Additionally, a list of watchfiles is kept.

        A Texfile has the following attributes:
        filename                         Name of the texfile
        options                          Dict of options
        changed                          Dict of changes, set by
                                         the has_changed method

        The 'options' dict had the following keys:
        smart           [True]           Smart mode on/off
        texcompiler     [pdflatex]       Program used for compilation
        compileroptions []               Options passed to the compiler
        makeindex       [True]           Should makeindex be called?
        bibtex          [True]           Should bibtex be called?
        makeindexbin    [makeindex %]    path/name of makeindex program
        bibtexbin       [bibtex %]       path/name of bibtex program
        extracompiler   []               additional compiler
        dvi             [False]          Does compiler yield dvi?
        viewer          [kpdf]           PDF file viewer
        no_cleanup      [False]          Should temp files be kept?
        cleanup         [[]]             List of files to be deleted.
        color           [False]          Color output

        The items of cleanupfiles are expanded with glob, and the '%'
        wildcard is replaced by filename (without extension)

        extracompiler is executed between two runs of the tex compiler.


        The 'changed' dict has the following keys:
        citations, labels, references, index

        After has_changed is called. All the flags in 'changed' are
        set.
    """

    def __init__(self, filename):
        """ Create a Texfile object wrapping the filename"""
        self.filename = filename
        self.changed = {'citations':False, 'labels':False,
                        'references':False, 'index':False}
        self.options = {}
        self.options['smart'] = True
        self.options['makeindex'] = True
        self.options['texcompiler'] = 'pdflatex'
        self.options['compileroptions'] = ''
        self.options['bibtex'] = True
        self.options['bibtexbin'] = 'bibtex %'
        self.options['makeindexbin'] = 'makeindex %'
        self.options['extracompiler'] = ''
        self.options['color'] = False
        self.options['dvi'] = False
        self.options['dvipdf'] = 'dvipdf %.dvi'
        self.options['no_cleanup'] = False
        self.options['viewer'] = 'kpdf'
        self.options['cleanup'] = []
        self._basename = self.filename # filename without ending
        if self._basename.endswith('.tex'):
            self._basename = self._basename.replace('.tex', '')
            if not os.path.isfile(self._basename + ".tex"):
                Out.write("The file %s that " % (self.options['filename'])\
                          + "you want to compile doesn't exist.\n", VERB_ERR)
        self._printer = CompilerOutputPrinter() # pretty printer
        self._references = {} # These four dicts map filenames to
        self._labels = {}     # lists of references, labels,
        self._citations = {}  # citations, and index items that
        self._indexitems = {} # occur in these files.
        self._watchfiletimes = {} # dict of filenames to change times
        self._patterns = {
            'citations'  : re.compile(r'\\cite[a-z*]{,3}\{'),
            'labels'     : re.compile(r'\\label\{'),
            'references' : re.compile(r'\\ref\{'),
            'index'      : re.compile(r'\\index\{')
        }
        self.add_watchfile(self._basename + '.tex')

    def _get_elements_from_file(self, filename):
        """ Return a dict with the following four elements:
            - a list of 'labels' defined in the file
            - a list of 'references' defined in the file
            - a list of 'citations' defined in the file
            - a list of 'index' items defined in the file
        """
        result = {'labels'    :[],
                  'references':[],
                  'citations' :[],
                  'index'     :[]}
        for extension in BINARYEXTENSIONS:
            if (filename.lower()).endswith(extension):
                return result
        try:
            afile = open(filename)
            filecontents = afile.read()
            afile.close()
        except IOError, data:
            Out.write("Couldn't read %s for analysis:\n" % filename, VERB_WARN)
            Out.write(data + "\n", VERB_WARN)
            return None
        for element in result.keys(): # elements are labels, references, ...
            position = 0
            while True:
                element_match = \
                         self._patterns[element].search(filecontents, position)
                if element_match:
                    position = element_match.start() + 1
                    result[element].append( \
                                       extract_element(filecontents, position))
                else:
                    break # next element
        return result

    def run_bibtex(self):
        """ Run bibtex on the texfile """
        Out.write("Running bibtex %s\n" % self._basename)
        bibtex_command = \
                      self.options['bibtexbin'].replace('%', self._basename)
        try:
            bibtexprocess = subprocess.Popen( \
                    bibtex_command + " 2>&1", \
                    shell=True, \
                    cwd=os.getcwd(), \
                    env=os.environ, \
                    stdout=subprocess.PIPE, \
                    stdin=open(os.devnull)
                )
            self._printer.mode = 'bibtex'
            self._printer.write(bibtexprocess.stdout)
            while True:
                time.sleep(1)
                exitcode = bibtexprocess.poll()
                if exitcode is not None:
                    break
                Out.write("Waiting for bibtex to finish.\n", VERB_DEBUG)
            if exitcode != 0:
                Out.write("bibtex returned with error (exit code %s).\n" \
                     % exitcode, VERB_WARN)
                return False #Failure
            return True
        except OSError, data:
            Out.write("bibtex failed to run:\n", VERB_WARN)
            Out.write(data + "\n", VERB_WARN)

    def get_includes(self):
        """Return a list of all files that are included (with \include
            or \input) in the texfile """
        # TODO: move includepattern and inputtpattern to self._patterns
        includepattern = re.compile(r'\\include\{(?P<filename>.*?)\}')
        inputpattern = re.compile(r'\\input\{(?P<filename>.*?)\}')
        result = []
        try:
            texfile = open(self._basename + ".tex")
            for line in texfile:
                includematch = includepattern.search(line)
                inputmatch = inputpattern.search(line)
                if includematch:
                    filename = includematch.group('filename') + ".tex"
                    if os.path.isfile(filename):
                        result.append(filename)
                if inputmatch:
                    filename = inputmatch.group('filename')
                    if os.path.isfile(filename):
                        result.append(filename)
            texfile.close()
        except IOError, data:
            Out.write("Couldn't get included files from %s:\n" \
                                           % self._basename + ".tex", VERB_WARN)
            Out.write(data + "\n", VERB_WARN)
        return result


    def run_makeindex(self):
        """ Run makeindex on the texfile """
        Out.write("Running makeindex %s\n" % self._basename)
        makeindex_command = \
                      self.options['makeindexbin'].replace('%', self._basename)
        try:
            makeindexprocess = subprocess.Popen( \
                    makeindex_command + " 2>&1" , \
                    shell=True, \
                    cwd=os.getcwd(), \
                    env=os.environ, \
                    stdout=subprocess.PIPE, \
                    stdin=open(os.devnull)
                )
            self._printer.mode = 'makeindex'
            self._printer.write(makeindexprocess.stdout)
            while True:
                time.sleep(1)
                exitcode = makeindexprocess.poll()
                if exitcode is not None:
                    break
                print "Waiting for makeindex to finish"
            if exitcode != 0:
                Out.write("'%s' returned with error (exit code %s).\n" \
                     % (makeindex_command, exitcode), VERB_WARN)
                return False #Failure
            return True
        except OSError, data:
            Out.write("makeindex failed to run:\n", VERB_WARN)
            Out.write(data + "\n", VERB_WARN)

    def firstcompile(self):
        """ Make the first complete compilation of the texfile """
        Out.write("Start Initial Compilation\n")
        if os.path.isfile(self._basename + ".pdf"):
            Out.write("There was an old pdf file %s. It will be deleted.\n" \
                 % (self._basename + ".pdf"))
            os.remove(self._basename + ".pdf")
        if self.options['smart']:
            for watchfile in self.watchfilelist():
                elements = self._get_elements_from_file(watchfile)
                self._references[watchfile] = elements['references']
                self._labels[watchfile] = elements['labels']
                self._citations[watchfile] = elements['citations']
                self._indexitems[watchfile] = elements['index']
        return self.fullcompile()

    def fullcompile(self):
        """ Make a complete unconditional compilation of the texfile

            This is guaranteed to produce a working pdf with all
            references, bibliographies, etc. complete. The file is
            processed several times, the steps are:
            - compile (just pdflatex, or whatever is set as texcompiler)
            - bibtex (if bibtex attribute is set)
            - recompile (like compile)
            - makeindex (if the makeindex attribute is set)
            - extracompiler (if set)
            - recompile
        """
        Out.write("Start Full Compilation.\n")
        if not self.run_latex():
            return False # Failure
        if self.options['bibtex']:
            if not self.run_bibtex():
                Out.write("bibtex failed.\n", VERB_WARN)
            if not self.run_latex():
                return False # Failure
        if self.options['makeindex']:
            if not self.run_makeindex():
                Out.write("makeindex failed.\n", VERB_WARN)
            self.run_latex()
        if not self.run_extracompiler():
            Out.write("'%s' failed.\n" % self.options['extracompiler'], \
                                                                      VERB_WARN)
        if not self.run_latex():
            return False # Failure
        if self.options['dvi']:
            if not self.convert_dvi():
                return False #Failure
        if not self.create_previewfile():
            return False # Failure
        return True # Success

    def smartcompile(self):
        """ Run whatever compilers are necessary to create a complete
            pdf with all references etc. resolved.

            At a minimum, the texcompiler is run once. If an
            extracompiler is set, texompiler -> extracompiler
            -> texcompiler is run at minimum.

            Bibtex and Makeindex are skipped if they are set to
            False in the options.
        """
        Out.write("Start Smart Compilation.\n")
        if not self.run_latex():
            return False # Failure
        if self.changed['citations']:
            if self.options['bibtex']:
                if not self.run_bibtex():
                    Out.write("bibtex failed.\n", VERB_WARN)
            else:
                Out.write("There were changes in the citations, but bibtex is "\
                     + "disabled. You should enable bibtex.\n", VERB_WARN)
            if not self.run_latex():
                return False # Failure
        if self.changed['index']:
            if self.options['makeindex']:
                if not self.run_makeindex():
                    Out.write("makeindex failed\n", VERB_WARN)
                self.run_latex()
            else:
                Out.write("There were changes in the index, but makeindex is "\
                     + "disabled. You should enable makeindex.\n", VERB_WARN)
        if not self.run_extracompiler():
            Out.write("'%s' failed.\n" % self.options['extracompiler'], \
                                                                      VERB_WARN)
        if self.changed['citations'] or self.changed['labels'] \
        or self.changed['references'] or self.changed['index'] \
        or self.options['extracompiler'] != '':
            if not self.run_latex():
                return False # Failure
        if self.options['dvi']:
            self.convert_dvi()
        self.create_previewfile()
        return True # Success


    def run_extracompiler(self):
        """ Run the compiler set in the extracompiler attribute """
        if self.options['extracompiler'] is not None:
            self.options['extracompiler'] = \
                                          self.options['extracompiler'].strip()
        else:
            self.options['extracompiler'] = ''
        extracompiler = self.options['extracompiler']
        if extracompiler != '':
            extracompiler = extracompiler.replace("%", self._basename)
            try:
                Out.write("Running extracompiler '%s'\n" % extracompiler)
                extracompilerprocess = subprocess.Popen( \
                        extracompiler + " 2>&1" , \
                        shell=True, \
                        cwd=os.getcwd(), \
                        env=os.environ, \
                        stdout=subprocess.PIPE, \
                        stdin=open(os.devnull)
                    )
                self._printer.mode = 'extracompiler'
                self._printer.write(extracompilerprocess.stdout)
                while True:
                    time.sleep(1)
                    exitcode = extracompilerprocess.poll()
                    if exitcode is not None:
                        break
                    print "Waiting for '%s' to finish" % extracompiler
                if exitcode != 0:
                    Out.write("'%s' returned with error (exit code %s).\n" \
                         % (extracompiler, exitcode), VERB_WARN)
                    return False #Failure
                return True
            except OSError, data:
                Out.write("'%s' failed to run:\n" % extracompiler, VERB_WARN)
                Out.write(data + "\n", VERB_WARN)
        return True

    def run_latex(self):
        """ This runs pdflatex (or whatever is given as
            texcompiler). If dvi is set, it is assumed that the compiler
            produced a dvi file, which is then converted to pdf via
            'dvipdf'.
        """
        Out.write("Running %s %s on %s\n" % (self.options['texcompiler'],
                                       self.options['compileroptions'],
                                       self._basename + ".tex"))
        try:
            latexprocess = subprocess.Popen( \
                    self.options['texcompiler'] + " " \
                     + self.options['compileroptions'] + " " \
                     + self._basename + " 2>&1", \
                    shell=True, \
                    cwd=os.getcwd(), \
                    env=os.environ, \
                    stdout=subprocess.PIPE, \
                    stdin=open(os.devnull)
                )
            self._printer.mode = 'latex'
            self._printer.write(latexprocess.stdout)
            while True:
                time.sleep(1)
                exitcode = latexprocess.poll()
                if exitcode is not None:
                    break
                print "Waiting for %s to finish" \
                       % self.options['texcompiler']
            if exitcode != 0:
                Out.write(self._basename + \
                     ".tex failed to compile (exit code %s).\n" \
                     % exitcode, VERB_WARN)
                return False #Failure
        except OSError, data:
            Out.write(self._basename + ".tex failed to compile:\n", VERB_WARN)
            Out.write(data + "\n", VERB_WARN)
            return False # Failure
        return True # Success

    def launch_viewer(self):
        """ Launch the pdf viewer for the preview pdf
        """
        if self.options['viewer'] != '' \
        and self.options['viewer'] is not None:
            Out.write("Launching viewer '" + self.options['viewer']+ "' for " \
                + self._basename + ".preview.pdf\n")
            os.system(self.options['viewer'] + " " + self._basename \
                      + ".preview.pdf & ")

    def cleanup(self):
        """ Delete the temporary files that are generated during the
            compilation of texfilebase.tex.
        """
        if not self.options['no_cleanup']:
            Out.write("Deleting temporary files for %s" \
                      % self._basename + '.tex\n')
            files_to_delete = []
            for element in self.options['cleanup']:
                element = element.replace('%', self._basename)
                files_to_delete += glob(element)
            for filename in files_to_delete:
                if os.path.isfile(filename):
                    try:
                        Out.write("    Deleting %s" % filename, VERB_DEBUG)
                        os.remove(filename)
                    except OSError, data:
                        Out.write(data + "\n", VERB_WARN)

    def has_changed(self):
        """ Check if the texfile or any of the watchfiles have
            changed
        """
        changed = False
        for watchfile in self._watchfiletimes.keys():
            if self._watchfiletimes[watchfile] < os.path.getmtime(watchfile):
                changed = True
                Out.write("%s has changed.\n" % watchfile)
                if self.options['smart']:
                    elements = self._get_elements_from_file(watchfile)
                    # references
                    if self._references[watchfile] != elements['references']:
                        Out.write("Changed references in %s\n" % watchfile)
                        self.changed['references'] = True
                        self._references[watchfile] = elements['references']
                    else:
                        self.changed['references'] = False
                    # labels
                    if self._labels[watchfile] != elements['labels']:
                        Out.write("Changed labels in %s\n" % watchfile)
                        self.changed['labels'] = True
                        self._labels[watchfile] = elements['labels']
                    else:
                        self.changed['labels'] = False
                    # citations
                    if self._citations[watchfile] != elements['citations']:
                        Out.write("Changed citations in %s\n" % watchfile)
                        self.changed['citations'] = True
                        self._citations[watchfile] = elements['citations']
                    else:
                        self.changed['citations'] = False
                    for extension in BIBEXTENSIONS:
                        if (watchfile.lower()).endswith(extension):
                            Out.write("Bibliography file %s has changed\n" \
                                      % watchfile)
                            self.changed['citations'] = False
                    # index
                    if self._indexitems[watchfile] != elements['index']:
                        Out.write("Changed index in %s\n" % watchfile)
                        self.changed['index'] = True
                        self._indexitems[watchfile] = elements['index']
                    else:
                        self.changed['index'] = False
            self._watchfiletimes[watchfile] = os.path.getmtime(watchfile)
        return changed

    def convert_dvi(self):
        """ Convert file.dvi to file.pdf """
        # TODO: check if dvi file actually exists
        dvipdf_command = \
                     self.options['dvipdf'].replace('%', self._basename)
        Out.write("Running '%s' to convert %s to %s\n" \
                                            % (dvipdf_command, \
                                               self._basename + ".dvi", \
                                               self._basename + ".pdf"))
        try:
            if subprocess.call( \
                dvipdf_command + " 2>&1", \
                cwd=os.getcwd(), \
                env=os.environ, \
                shell=True, \
            ) != 0:
                Out.write("Failed to convert " + self._basename \
                          + ".dvi to pdf.\n", VERB_WARN)
                self.cleanup()
                Out.write("Is '%s' available?\n" % dvipdf_command, VERB_ERR)
        except OSError, data:
            Out.write("'%s' failed:\n" % dvipdf_command, VERB_WARN)
            Out.write(data + "\n", VERB_WARN)
            return False
        return True


    def create_previewfile(self):
        """ Copy the file.pdf resulting from a compilation to
            file.preview.pdf
        """
        compiledpdf = self._basename + ".pdf"
        previewpdf = self._basename + ".preview.pdf"
        if not os.path.isfile(compiledpdf):
            Out.write("pdf file %s does not exist.\n" % compiledpdf, VERB_ERR)
            if self.options['texcompiler'] != 'pdflatex':
                self.cleanup()
                Out.write("Did you forget to select --dvi?\n", VERB_ERR)
            sys.exit(2)
        try:
            Out.write("Copying %s to %s\n" % (compiledpdf, previewpdf))
            shutil.copy(compiledpdf, previewpdf)
        except IOError, data:
            Out.write(data + "\n", VERB_WARN)
            Out.write("Could not copy %s to %s.\n" \
                      % (compiledpdf, previewpdf), VERB_WARN)
            return False
        return True # Success


    def add_watchfile(self, watchfile_wc):
        """ Add a watchfile or wildcard expression to the list of
            watchfiles
        """
        class WatchFileExistsException(Exception):
            """Raised internally if a watchfile is already on the watchlist"""
            pass
        for watchfile in glob(watchfile_wc):
            try:
                if os.path.isfile(watchfile):
                    for existing_file in self._watchfiletimes.keys():
                        if os.path.samefile(existing_file, watchfile):
                            raise WatchFileExistsException(watchfile)
                    self._watchfiletimes[watchfile] = \
                                                    os.path.getmtime(watchfile)
                else:
                    Out.write("The file %s that you want " % watchfile \
                              + "to watch does not exist.\n", VERB_ERR)
                    sys.exit(2)
            except WatchFileExistsException, data:
                Out.write("The file %s is already being watched" \
                          % data, VERB_DEBUG)

    def clear_watchfilelist(self):
        """ Delete all watchfiles, except the texfile itself """
        self._watchfiletimes = {}
        self.add_watchfile(self._basename + '.tex')

    def watchfilelist(self):
        """ Return the list of watchfiles """
        return self._watchfiletimes.keys()


def extract_element(fullstring, position):
    """ Extract the contents of the first {...} block found after
        position in fullstring """
    Out.write("Extracting element from fullstring at position %s\n" \
              % position, VERB_DEBUG)
    try:
        startposition = fullstring.index("{", position) + 1
        endposition = startposition
        open_brackets = 1
        while open_brackets > 0:
            endposition += 1
            if fullstring[endposition] == '{':
                open_brackets += 1
            elif fullstring[endposition] == '}':
                open_brackets -= 1
        return fullstring[startposition:endposition]
    except (ValueError, IndexError):
        Out.write("Internal Error extracting element: " \
             + "string has invalid brackets.\n", VERB_WARN)
    return None

