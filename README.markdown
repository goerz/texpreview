# texpreview

[http://github.com/goerz/texpreview](http://github.com/goerz/texpreview)

Author: [Michael Goerz](http://michaelgoerz.net)

texpreviw.py is a script that monitors a TeX file and its dependents for
changes and recompiles it in the background. It tries to do this intelligently,
although at this time its intelligence is severely lacking. The purpose is to
have a compiled PDF file continuously updated every time you save a TeX file.

This code is licensed under the [GPL](http://www.gnu.org/licenses/gpl.html)

## Install ##

Download and extract the package, then run
    sudo python setup.py install


## Usage ##

    texpreview.py

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
    
      --cverbosity=2                  Like --verbosity, but for compiler ouput
    
      --debug                         Equivalent to '--verbosity=4 --cverbosity=4'
    
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
    $HOME/.texpreview/texpreview.cfg
    
    Second, there is a possible local texpreview.cfg file in the current
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
    
