#!/usr/bin/python
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


"""
Recompile tex-files intelligently in the background whenever they change
and display the resulting pdf. For each tex-file, there is a watchlist
(see below), the file is recompiled whenever a file on the watchlist
changes. The program can be configured via command line options and
via config files.

Usage:
texpreview.py [options] file1.tex file2.tex ...

The files file1.tex, file2.tex, ... are compiled and displayed
independently.

Options are:

  -w file                         Add file to the watchlist:
  --watch=file                    You can use this option more than
                                  once. You can also
                                  use wildcards, which will be
                                  expanded to a list of files. Make
                                  sure to quote a wildcard expression
                                  so that it is not already expanded
                                  by the shell.

  -c pdflatex                     Change the compiler. The default
  --compiler=pdflatex             compiler is 'pdflatex'. You can
                                  switch to standard latex here, or
                                  an equivalent program. Make sure to
                                  also use the --dvi option if you
                                  select 'latex' here.

  --dvi                           Select this if you have a compiler
                                  that produces dvi. The 'dvipdf'
                                  program will be used to convert to
                                  pdf.

  --cleanup='%.dvi ...'           Specify patterns to delete on cleanup.
                                  Patterns are extended as shell globs.
                                  The '%' wildcard can be used.
                                  Consecutive patterns have to be
                                  separated by whitespace. See notes
                                  below for details.

  --dvipdf='dvipdf %.dvi'         Change the command that converts
                                  between dvi and pdf.

  -o ''                           Set additional options passed to the
  --options=''                    compiler.

  -v kpdf                         Change the pdf viewer. The default
  --viewer=kpdf                   viewer is kpdf. Make sure to choose a
                                  viewer that supports automatic
                                  reloading. Set the viewer to '' if you
                                  don't want to use any viewer at all

  --smart                         Turn on 'smart'-mode. Compilers are
                                  run as necessary to produce a complete
                                  pdf. 'smart'-mode is on by default.

  --stupid                        Turn off 'smart'-mode. Only the tex
                                  compiler is run when the texfile or a
                                  watchfile changes. You have to press
                                  CTRL+C for a complete recompile.

  --color                         Activate color output.

  --nocolor                       Deactivate color output (default).

  --verbosity=3                   Set verbosity of output. Values can
                                  range from 0 to 4. At '0', there is
                                  no output except the running message;
                                  at '1', there are only critical error
                                  messages; at '2' there are warning
                                  messages; at '3' there are status
                                  messages; at '4', there is debug
                                  information.

  --debug                         Equivalent to '--verbosity=4'

  --bibtex                        Run the texfile through bibtex.
                                  (Default in smart mode)

  --nobibtex                      Do not run the texfile through bibtex.
                                  (Default in stupid mode)


  --makeindex                     Run the texfile through makeindex.
                                  (Default in smart mode)

  --nomakeindex                   Do not run the texfile through
                                  makeindex. (Default in stupid mode)


  --makeindexbin='makindex %'     Set makindex command

  --bibtexbin='bibtex %'          Set bibtex command

  -e                              Compile only once and then exit, don't
  --exit                          launch viewer.

  --nocleanup                     Don't delete temporary files.

  --config filename               Provide a custom config file

  --noconfig                      Don't use any global or local config
                                  file.

  --noautowatch                   Disable the autowatch capabilities.
                                  You will have to add all watchfiles
                                  manually

  --autowatch                     Override 'autowatch = false' in conf
                                  file

  --dumpconfig                    Print a config file with the
                                  standard options to STDOUT and exit.

  --precommand=''                 Command that is run on program startup

  --postcommand=''                Command that is run on program exit

  --extracompiler=''              Extra compiler command to run at a full
                                  compilation cycle. There is guaranteed
                                  to be one tex-compilation before and
                                  after extracompiler (extracompiler has
                                  the same place as makeindex). You can
                                  use the % wildcard when specifying the
                                  extracompiler.

  -h                              Display this message.
  --help

The '%' wildcard character in the --bibtexbin, --maketexbin --cleanup
--extracompiler, and --dvipdf options is replaced by the filename of
the texfile, without extension.

The default string for the --cleanup option is:
'%.dvi %.backup %.blg %.log %.toc %.bbl %.out %.bak %.snm %.idx %.ilg
 %.ind %.nav %.aux %.lot %.lof %.preview.pdf'


Use of Config Files
===================

The program makes use of config files that allow you to set
default options for the command line switches.

First, there is the global conf file in
$HOME/.texpreview/CONFIGFILENAME

Second, there is a possible local CONFIGFILENAME file in the current
directory.

Third, there can be an additional file given on the command line with
the --config switch

If the --noconfig command line switch is given, global and and local
conf files are ignored, but files given by --config are still parsed.

If the global config file does not exist, it is automatically created
(unless the --noconfig option is given).


Watchlist Cababilities
======================

If any of the files on the watchlist changes, all tex-files are
recompiled. Any files included in the tex-file via the \include or
\input commands will be on the watchlist automatically, unless the
--noautowatch option is specified"

The tex-file that is being compiled is also on the watchlist
automatically.

All additional watchfiles have to be specified either on the command
line or in a config file


Smart and Stupid Mode
============================

By default, the program runs in 'smart' mode. This means that the output
of compilers is parsed to find out what has to be done to produce a
complete pdf file, with all references, citations, index pages, etc.
resolved.

If you use --extracompiler, the program at a minimum runs the tex
compiler twice, with the extracompiler in between at. There is no way
to parse the output of extracompiler, so the program cannot be smart
about what to do in this case.

If the bibtex and makeindex options are set to false, bibtex and
makeindex are never run, even if a full compilation would require
that. A warning will be issued.

If the program is not in smart mode (smart mode set to false in a
config file, or you have used --stupid), only the tex compiler is
run when a tex file or a file on the watchlist changes. This means
that the resulting pdf is not guaranteed to be resolved completely.
If you change the index, the bibliography, etc., you will have to
do an unconditional complete recompile by pressing CTRL+C once.


Compatibility
===================

Note that you can use this program on Windows as well. However, it is
somewhat limited: You cannot open the preview file in a viewer, as an
open file on Windows is locked, and trying to update it would result
in an error. Future versions will address this problem.

This program prints all status messages and errors to STDERR. The
compiler output, including warnings and errors, will be printed on
STDOUT. This gives you the option of using pipes to separate these
two levels of output.
"""


# TODO: maybe it's possible to add an option to kill and restart the viewer
#       on each recompile. This would be helpful on windows, where you can't
#       overwrite a file that's open.
#       Note: this can be done with some special programs for Windows
#       (openpdf, closepdf). Add a command line option to use these.
# TODO: parse output of latex commands, and display a "Compiled with warnings"
#       or "did not compile" message
# TODO: try to make main() shorter.
# TODO: maybe: allow to filter the output of latex, e.g. show only errors
# TODO: add color
# TODO: maybe: add debug option that lists options and other info as program
#       runs. Alternatively: allow verbosity levels by command line switches
# TODO: allow precommand and postcommand to use % wildcard.
# TODO: prevent a file from being on the compile list more than once
# TODO: maybe --bibtex and --makeindex should just have no effect in smart
#       mode, except that they are used as option for an unconditional new
#       compile --- actually, I think it's fine the way it is: it would make
#       no sense to have --bibtex off in a full compile and on in a smart
#       compile: the two states should be in sync, which is enforced by the
#       warning smartcompile gives. But, there probably should not be
#       different default for --bibtex and --makeindex in smart and stupid
#       mode
# TODO: bibtex fails even though it shouldn't
# TODO: piping into /dev/null causes the program to fail.

import sys
import getopt
import os
import time
import ConfigParser
from Texpreview.Texfile import Texfile
import Texpreview.TexpreviewPrinter as Out
VERB_SILENT = Out.VERB_SILENT
VERB_ERR    = Out.VERB_ERR
VERB_WARN   = Out.VERB_WARN
VERB_STATUS = Out.VERB_STATUS
VERB_DEBUG  = Out.VERB_DEBUG


# Setting the following to False will cause the program to
# not use a global config file in any way (or create one if it's missing).
# Local config files or config files specified via --config are still
# used.
USE_GLOBAL_CONFIG = True

# Standard filename of the config file. You'll have to adapt the documentation
# if you change this.
CONFIGFILENAME = 'texpreview.cfg'


def samefile(file1, file2):
    """ Fallback replacement for os.path.samefile (e.g. on Windows) """
    return ( os.path.abspath(file1.lower()) == \
                                           os.path.abspath(file2.lower()) )
if not hasattr(os.path, 'samefile'):
    Out.write("Using fallback function for os.path.samefile.\n", VERB_DEBUG)
    os.path.samefile = samefile


def cmdline_to_dict():
    """ Parse the command line options into a dictionary
    """
    Out.write("Entering cmdline_to_dict\n", VERB_DEBUG)
    try:
        opts, files = getopt.getopt(sys.argv[1:], "hw:c:v:o:e",
                      ["help", "watch=", "compiler=","viewer=", "makeindex",
                       "dvi", "options=", "exit", "nocleanup",
                       "dvipdf=", "config=", "noconfig", "dumpconfig",
                       "bibtex", "bibtexbin=", "makeindexbin=", "nomakeindex",
                       "nobibtex", "precommand=", "postcommand=",
                       'cleanup=', "noautowatch", "autowatch", "smart",
                       "stupid", "extracompiler=", "verbosity=", "debug",
                       "color", "nocolor"])
    except getopt.GetoptError, details:
        Out.write(details + "\n", VERB_ERR)
        sys.exit(2)
    cmdlineoptions = {}
    # TODO: check that 'value' is never another option, i.e. that the second
    # option wasn't in fact missed
    value_options = {'-c'              : 'texcompiler',
                     '--compiler'      : 'texcompiler',
                     '-o'              : 'compileroptions',
                     '--options'       : 'compileroptions',
                     '-v'              : 'viewer',
                     '--viewer'        : 'viewer',
                     '--bibtexbin'     : 'bibtexbin',
                     '--makeindexbin'  : 'makeindexbin',
                     '--dvipdf'        : 'dvipdf',
                     '--precommand'    : 'precommand',
                     '--postcommand'   : 'postcommand',
                     '--config'        : 'config',
                     '--extracompiler' : 'extracompiler'
                    }
    boolean_options = { '--dvi'          : ('dvi', True),
                        '--makeindex'    : ('makeindex', True),
                        '--nomakeindex'  : ('makeindex', False),
                        '--bibtex'       : ('bibtex', True),
                        '--nobibtex'     : ('bibtex', False),
                        '--noconfig'     : ('no_config', True),
                        '--nocleanup'    : ('no_cleanup', True),
                        '-e'             : ('exit_after_compile', True),
                        '--exit'         : ('exit_after_compile', True),
                        '--dumpconfig'   : ('dumpconfig', True),
                        '--autowatch'    : ('autowatch', True),
                        '--noautowatch'  : ('autowatch', False),
                        '-h'             : ('help', True),
                        '--help'         : ('help', True),
                        '--color'        : ('color', True),
                        '--nocolor'      : ('color', False)
                      }
    for opt, value in opts:
        if value.startswith('-'):
            Out.write("The value '%s' that was supplied " %  value \
                      + "with the option '%s' " % opt \
                      + "looks like an option itself.\n", VERB_WARN)
        if value_options.has_key(opt):
            key = value_options[opt]
            cmdlineoptions[key] = value
            continue
        if boolean_options.has_key(opt):
            (key, bvalue) = boolean_options[opt]
            cmdlineoptions[key] = bvalue
            continue
        if opt in ("-w", "--watch"):
            if cmdlineoptions.has_key('watchfiles'):
                (cmdlineoptions['watchfiles']).append(value)
            else:
                cmdlineoptions['watchfiles'] = [value]
            continue
        if opt == "--cleanup":
            cmdlineoptions['cleanup'] = value
            cmdlineoptions['no_cleanup'] = False
            continue
        if opt == "--verbosity":
            try:
                verbosity = int(value)
                cmdlineoptions['verbosity'] = verbosity
                if verbosity < VERB_SILENT or verbosity > VERB_DEBUG:
                    raise ValueError
            except ValueError:
                Out.write("verbosity has to be an integer between %i and %i" \
                          % (VERB_SILENT, VERB_DEBUG), VERB_WARN)
            continue
        if opt == "--smart":
            cmdlineoptions['smart'] = True
            if not cmdlineoptions.has_key('bibtex'):
                cmdlineoptions['bibtex'] = True
            if not cmdlineoptions.has_key('makeindex'):
                cmdlineoptions['makeindex'] = True
            continue
        if opt == "--stupid":
            cmdlineoptions['smart'] = False
            if not cmdlineoptions.has_key('bibtex'):
                cmdlineoptions['bibtex'] = False
            if not cmdlineoptions.has_key('makeindex'):
                cmdlineoptions['makeindex'] = False
            continue
        if opt == "--debug":
            cmdlineoptions['verbosity'] = VERB_DEBUG
            continue
    cmdlineoptions['files'] = files
    return cmdlineoptions


def set_home_env():
    """ Try to make sure the $HOME environment variable is set, even
        on a Windows system.
    """
    if  os.environ.get("HOME") is None:
        Out.write("HOME is not set, we will try to set it.\n", VERB_DEBUG)
        # We're probably on a Windows system.
        # Set HOME as HOMEDRIVE + HOMEPATH
        if  os.environ.get("HOMEDRIVE") is not None \
            and os.environ.get("HOMEPATH") is not None:
            os.environ.setdefault("HOME", \
                os.path.normpath( \
                    os.path.join(os.environ.get("HOMEDRIVE"), \
                                    os.environ.get("HOMEPATH")) ))
            Out.write("Set HOME to '%s'.\n" \
                      % os.environ.get("HOME") , VERB_DEBUG)



def run_compile_loop(texfileobjects):
    """ Run the compile loop for an array of Texfile objects
    """
    Out.write("Going into compile loop.\n", VERB_DEBUG)
    print_running_message()
    while True:
        try:
            time.sleep(1)
            for texfileobject in texfileobjects:
                if texfileobject.has_changed():
                    if texfileobject.options['smart']:
                        texfileobject.smartcompile()
                    else:
                        Out.write("Recompiling in stupid mode\n")
                        texfileobject.run_latex()
                        if texfileobject.options['dvi']:
                            texfileobject.convert_dvi()
                        texfileobject.create_previewfile()
                    print_running_message()
        except KeyboardInterrupt:
            try:
                Out.write("Hit Ctrl+C again to quit\n", VERB_SILENT)
                time.sleep(1)
                for texfileobject in texfileobjects:
                    texfileobject.fullcompile()
                print_running_message()
            except KeyboardInterrupt:
                for texfileobject in texfileobjects:
                    texfileobject.cleanup()
                return True # Success


def clean_exit(texfileobjects, postcommand):
    """Cleanup, postcommand, exit"""
    Out.write("\n\ntexpreview.py is finishing ...\n")
    cleanup(texfileobjects)
    run_command(postcommand, description = 'postcommand')
    Out.write("\nDone\n")
    sys.exit(0)


def configure_output(options_dict):
    """ Set color and verbosity of Out depending on what is set in
        options_dict
    """
    Out.write("Entering configure_output\n", VERB_DEBUG)
    if options_dict.has_key('color'):
        if options_dict['color']:
            Out.activate_color()
    if options_dict.has_key('verbosity'):
        try:
            Out.streams['direct']['verbosity'] = int(options_dict['verbosity'])
            Out.write("Set verbosity to %s\n" \
                               % Out.streams['direct']['verbosity'], VERB_DEBUG)
        except ValueError:
            Out.write("Verbosity was not an integer in configure_output\n", \
                      VERB_WARN)
    # TODO: do the same thing with a compiler-verbosity

def main():
    """Command line program for compiling tex files """

    # command line parsing
    cmdlineoptions = cmdline_to_dict()
    configure_output(cmdlineoptions)

    # display help before dealing with config files etc.
    if cmdlineoptions.has_key('help'):
        usage()
        sys.exit()
    # dump config file if that is asked for
    if cmdlineoptions.has_key('dumpconfig'):
        create_configfile()
        sys.exit()

    # hard coded default options
    options = hard_defaults()
    # merge the hard coded defaults with options from the configfiles
    options = read_configfiles(options, get_configfilelist(cmdlineoptions))
    # add options from the  command line
    options = transfer_options(cmdlineoptions, options)
    configure_output(options)


    # Exit if there is no file to compile
    if len(options['files']) == 0:
        Out.write("You have not provided any file to compile. " \
                  "Nothing to do. Exit.\n", VERB_ERR)
        sys.exit(2)

    # Generate Texfile objects
    texfileobjects = []
    for texfile in options['files']:
        if not texfile.endswith('.tex'):
            texfile = texfile + '.tex'
        if os.path.isfile(texfile):
            texfileobject = Texfile(texfile)
            texfileobject.options = options.copy()
            if options['exit_after_compile']:
                texfileobject.options['viewer'] = None
            for watchfile in options['watchfiles']:
                texfileobject.add_watchfile(watchfile)
            texfileobject.options['cleanup'] \
                = options['cleanup'].split()
            texfileobjects.append(texfileobject)
        else:
            Out.write("The file %s that you want to compile does not exist.\n" \
                      % texfile, VERB_ERR)

    # autowatch
    if options['autowatch']:
        for texfileobject in texfileobjects:
            includefiles = texfileobject.get_includes()
            for includefile in includefiles:
                if includefile not in texfileobject.watchfilelist():
                    Out.write("autowatch: Adding %s to %s watchfilelist\n" \
                         % (includefile, texfileobject.filename), VERB_DEBUG)
                    texfileobject.add_watchfile(includefile)

    # Precommand
    run_command(options['precommand'], description = 'precommand')

    # Initial compilation
    for texfileobject in texfileobjects:
        if not texfileobject.firstcompile():
            cleanup(texfileobjects)
            Out.write("Initial compilation failed\n", VERB_ERR)
            exit(2)
        # open viewer
        texfileobject.launch_viewer()

    # exit if --exit
    if options['exit_after_compile']:
        clean_exit(texfileobjects, options['postcommand'])
    # Go into compile loop
    run_compile_loop(texfileobjects)

    # Finish
    clean_exit(texfileobjects, options['postcommand'])


def print_running_message():
    """ Print a message informing the user that the program is running,
        and how it can be controlled
    """
    Out.write("\n\ntexpreview.py is running ... \n\t" \
      + "Press CTRL+C to do a complete unconditional "\
      + "recompile of all files.\n\t" \
      + "Press CTRL+C twice to exit the program\n", VERB_SILENT)


def hard_defaults():
    """ Return an options dict with the hard coded default options """
    Out.write("Setting hard default options\n", VERB_DEBUG)
    options = {}
    options['smart'] = True
    options['noconfig'] = False
    options['watchfiles'] = []
    options['texcompiler'] = 'pdflatex'
    options['compileroptions'] = ''
    options['viewer'] = 'kpdf'
    options['makeindex'] = True
    options['bibtex'] = True
    options['makeindexbin'] = 'makeindex %'
    options['bibtexbin'] = 'makeindex %'
    options['dvi'] = False
    options['exit_after_compile'] = False
    options['dvipdf'] = 'dvipdf %.dvi'
    options['no_cleanup'] = False
    options['extracompiler'] = ''
    options['precommand'] = ''
    options['postcommand'] = ''
    options['verbosity'] = VERB_STATUS
    options['color'] = False
    options['cleanup'] = '%.dvi %.backup %.blg %.log %.toc %.bbl %.out ' \
                              + '%.bak %.snm %.idx %.ilg %.ind %.nav %.aux ' \
                              + '%.lot %.lof %.preview.pdf'
    options['autowatch'] = True
    return options

def create_configfile(configfilename=None):
    """ Create a new config file with default options at the location
        configfilname, or STDOUT if configfilename is None
    """
    try:
        if configfilename is None:
            configfilename = 'STDOUT'
            configfile = sys.stdout
        else:
            try:
                Out.write("Creating new configfile at %s\n" % configfilename)
                configfile = open(configfilename, "w")
            except IOError, data:
                Out.write("Can't write to %s:%s\n" % (configfilename, data), \
                                                                      VERB_WARN)
                return None
        try:
            configfile.write("[options]\n")
            configfile.write("smart = True\n")
            configfile.write("texcompiler = pdflatex\n")
            configfile.write("compileroptions = \n")
            configfile.write("viewer = kpdf\n")
            configfile.write("bibtex = True\n")
            configfile.write("makeindex = True\n")
            configfile.write("dvi = False\n")
            configfile.write("autowatch = True\n")
            configfile.write("color = False\n")
            configfile.write("verbosity = %s\n" % VERB_STATUS)
            configfile.write("exit_after_compile = False\n")
            configfile.write("cleanup = %.dvi %.backup %.blg %.log " \
                             + "%.bbl %.out %.bak %.snm %.idx %.ilg %.ind " \
                             +  "%.nav %.aux %.lot %.lof %.toc "
                             +  "%.preview.pdf\n")
            configfile.write("dvipdf = dvipdf %.dvi\n")
            configfile.write("makeindexbin = makeindex %\n")
            configfile.write("bibtexbin = bibtex %\n")
            configfile.write("no_cleanup = False\n")
            configfile.write("precommand = \n")
            configfile.write("postcommand = \n")
            configfile.write("extracompiler = \n")
            configfile.write("\n")
            configfile.write("[files]\n")
            configfile.write("# You can enter the files that you want to " \
                                + "compile in this section.\n")
            configfile.write("#   1 = main1.tex\n")
            configfile.write("#   2 = main2.tex\n")
            configfile.write("#   ...\n")
            configfile.write("\n")
            configfile.write("[watchfiles]\n")
            configfile.write("# You can enter the files that you want " \
                                + "to watch for changes in this section\n")
            configfile.write("#   1 = file1.tex\n")
            configfile.write("#   2 = includes/*.tex\n")
            configfile.write("#   ...\n")
        except IOError, data:
            Out.write("Error writing to %s:%s\n" % (configfilename, data), \
                                                                      VERB_WARN)
        if configfile is not sys.stdout:
            configfile.close()
    except IOError, data:
        Out.write(data + "\n", VERB_WARN)


def read_configfiles(options, configfiles):
    """ Return an options dict that consists of the original options
        combined with the options set in the config files.

        Declaration of an option in a config file overrides that same
        option in any earlier config file.
    """
    Out.write("Reading options from configfiles: %s\n" \
              % configfiles, VERB_DEBUG)
    result = {}
    # copy original options
    for key in options.keys():
        Out.write("read_configfiles: option '%s' to '%s' " \
                  % (key, options[key]) + "from original options\n", VERB_DEBUG)
        result[key] = options[key]
    # go through the config files
    for configfile in configfiles:
        Out.write("Reading config file from %s\n" % configfile)
        parser = ConfigParser.ConfigParser()
        try:
            parser.read(configfile)
            # get regular options
            fields = {
                'texcompiler' : parser.get,
                'compileroptions' : parser.get,
                'viewer' : parser.get,
                'makeindex' : parser.getboolean,
                'bibtex' : parser.getboolean,
                'makeindexbin' : parser.get,
                'bibtexbin' : parser.get,
                'dvi' : parser.getboolean,
                'exit_after_compile' : parser.getboolean,
                'dvipdf' : parser.get,
                'precommand' : parser.get,
                'postcommand' : parser.get,
                'extracompiler' : parser.get,
                'autowatch' : parser.getboolean,
                'cleanup' : parser.get,
                'smart' : parser.get,
                'no_cleanup' : parser.getboolean,
                'verbosity' : parser.getint,
                'color' : parser.getboolean
            }
            for field in fields:
                if parser.has_option('options', field):
                    getter = fields[field]
                    result[field] = getter('options', field)
                    Out.write("read_configfiles: Set option " \
                              + "'%s' to '%s' " % (field, result[field]) \
                              +"from config file\n", VERB_DEBUG)
            # get compilation files
            try:
                if parser.has_section('files'):
                    for (field, value) in parser.items('files'):
                        if os.path.isfile(value):
                            try:
                                result['files'].append(value)
                                Out.write("read_configfiles: Appended " \
                                          + "%s to 'files' list.\n" \
                                          % value, VERB_DEBUG)
                            except (IndexError, KeyError):
                                result['files'] = [value]
                                Out.write("read_configfiles: Started 'files' " \
                                          +"list with %s.\n"
                                          % value, VERB_DEBUG)
                        else:
                            Out.write("The file %s " % value \
                                      + "that you want to compile does " \
                                      + "not exist.\n", VERB_ERR)
                else:
                    Out.write("There is no files section in %s\n"
                              % configfile, VERB_DEBUG)
            except:
                Out.write("Error getting compilation files from %s\n" \
                          % configfile, VERB_WARN)
            # get watch files
            try:
                if parser.has_section('watchfiles'):
                    for (field, value) in parser.items('watchfiles'):
                        try:
                            result['watchfiles'].append(value)
                            Out.write("read_configfiles: " \
                                      + "Appended %s to 'watchfiles' list.\n" \
                                      % value, VERB_DEBUG)
                        except (IndexError, KeyError):
                            result['watchfiles'] = [value]
                            Out.write("read_configfiles: Started " \
                                      + "'watchfiles' list with %s.\n" \
                                      % value, VERB_DEBUG)
                else:
                    Out.write("There is no watchfiles section in %s\n" \
                              % configfile, VERB_DEBUG)
            except:
                Out.write("Error getting watch files from %s\n" \
                          % configfile, VERB_WARN)
        except:
            Out.write("Error parsing %s\n" % configfile, VERB_WARN)
    return result


def run_command(cmd, description=""):
    """ Run cmd in shell """
    if cmd is not None:
        cmd = str(cmd).strip()
        if cmd != '':
            if description != '':
                Out.write("Running %s: %s\n" % (description, cmd))
            else:
                Out.write("Running %s\n" % cmd)
            os.system(cmd + " 2>&1")


def get_configfilelist(cmdlineoptions):
    """ Return a list of configfiles to be used in this run.

        First, there is the global conf file in
            $HOME/.texpreview/texpreview.cfg
        Second, there is a possible local config texpreview.cfg file
            in the current directory.
        Third, there can be an additional file given on the command
            line with the --config switch

       If the --noconfig command line switch is given, global and
       and local conf files are ignored, but files given by --config
       are still parsed
    """
    # Global conf, local conf, take --config from cmdlineoptions
    Out.write("Getting list of configfiles.\n", VERB_DEBUG)
    result = []
    if not cmdlineoptions.has_key('no_config'):
        # add the global and the local config file
        # first, the global config file
        if USE_GLOBAL_CONFIG:
            globalconfigfilename = get_globalconfigfilename()
            if globalconfigfilename is not None:
                result.append(globalconfigfilename)
        # second, the local config file
        localconfigfilename = None
        if os.path.isfile("./" + CONFIGFILENAME):
            localconfigfilename = "./" + CONFIGFILENAME
            result.append(localconfigfilename)
    else:
        Out.write("no_config option is set. No global or local " \
                  + "config file used.\n", VERB_DEBUG)
    # beyond the global and local config file, an additional config file can
    # be given on the command line with the --config option.
    if cmdlineoptions.has_key('config'):
        configfilename = cmdlineoptions['config']
        Out.write("Taking config file %s from command line\n" \
                  % configfilename, VERB_DEBUG)
        if os.path.isfile(configfilename):
            result.append(configfilename)
        else:
            Out.write("Couldn't find the config file %s" % configfilename + \
                " that you provided with --config\n", VERB_WARN)
    Out.write("Returning list of config files: %s\n" % str(result), VERB_DEBUG)
    return result


def get_globalconfigfilename():
    """ Return the complete path of the global config file, or None if that
        that is not possible. The config file will be created if it does
        not exist.
    """
    globalconfigfilename = None
    try:
        # make sure $HOME environment variable is set
        set_home_env()
        # set config file name as the default:
        # $HOME/.texpreview/CONFIGFILENAME
        if os.path.isdir(os.environ.get("HOME")):
            globalconfigfiledir = os.path.normpath(\
                                    os.path.join(os.environ.get("HOME"), \
                                                ".texpreview"))
            globalconfigfilename = os.path.normpath(\
                                    os.path.join(globalconfigfiledir, \
                                                CONFIGFILENAME))
            if not os.path.isdir(globalconfigfiledir):
                # create new globalconfigdir
                try:
                    Out.write("Creating %s\n" % globalconfigfiledir, \
                                                                VERB_DEBUG)
                    os.mkdir(globalconfigfiledir)
                except OSError, data:
                    Out.write(data + "\n", VERB_WARN)
            if not os.path.isfile(globalconfigfilename):
                create_configfile(globalconfigfilename)
        else:
            Out.write("Home directory not found. " \
                    + "Can't read global config file.\n")
    except Exception, message:
        Out.write("Accessing global config file failed: ", VERB_WARN)
        Out.write(message + "\n", VERB_WARN)
    return globalconfigfilename


def transfer_options(cmdlineoptions, options):
    """ Transfer the values set in the cmdlineoptions dict into the
        options dict
    """
    Out.write("Entering transfer_options\n", VERB_DEBUG)
    keys = ['watchfiles', 'texcompiler', 'compileroptions', 'dvi',
            'makeindex', 'bibtex', 'makeindexbin', 'bibtexbin',
            'no_cleanup', 'exit_after_compile', 'viewer', 'precommand',
            'postcommand', 'cleanup', 'autowatch', 'extracompiler', 'smart',
            'verbosity', 'color']
    for key in keys:
        if cmdlineoptions.has_key(key):
            options[key] = cmdlineoptions[key]
            Out.write("Transferred option '%s' (value '%s') " \
                      % (key, options[key]) \
                      + "from cmdlineoptions to options.\n", VERB_DEBUG)
    if cmdlineoptions.has_key('files'):
        if options.has_key('files'):
            options['files'] += cmdlineoptions['files']
            Out.write("Added files from cmdlineoptions:\n", VERB_DEBUG)
            Out.write("files are now: %s\n" % options['files'], VERB_DEBUG)
        else:
            options['files'] = cmdlineoptions['files']
            Out.write("Set files from cmdlineoptions:\n", VERB_DEBUG)
            Out.write("files are now: %s\n" % options['files'], VERB_DEBUG)
    return options


def cleanup(texfileobjects):
    """ Clean up all texfiles before exiting """
    Out.write("Cleaning up\n")
    for texfileobject in texfileobjects:
        texfileobject.cleanup()
    Out.write("Finished Cleanup\n")


def usage():
    """ print usage for main program """
    print __doc__

if __name__ == "__main__":
    main()
