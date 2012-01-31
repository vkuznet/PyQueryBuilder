#!/usr/bin/env python
"""module for print"""
#-*- coding: ISO-8859-1 -*-
##########################################################################
#  Copyright (C) 2008 Valentin Kuznetsov <vkuznet@gmail.com>
#  All rights reserved.
#  Distributed under the terms of the BSD License.  The full license is in
#  the file doc/LICENSE, distributed as part of this software.
##########################################################################

import sys
import re
import time
from pyquerybuilder.utils.Errors import Error

class PrintOutput:
    """Print output with color RGB and
       print output with format TXT XML HTML CSV"""
    def __init__(self):
        """initialize a internal TerminalController"""
        self.term = TerminalController()

    def print_red(self, msg):
        """print in red"""
        print self.msg_red(msg)

    def print_green(self, msg):
        """print in green"""
        print self.msg_green(msg)

    def print_blue(self, msg):
        """print in blue"""
        print self.msg_blue(msg)

    def msg_red(self, msg):
        """print in red using termcontroller"""
        return self.term.RED + msg + self.term.NORMAL

    def msg_green(self, msg):
        """print in greeen using termcontroller"""
        return self.term.GREEN + msg + self.term.NORMAL

    def msg_blue(self, msg):
        """print in blue using termcontroller"""
        return self.term.BLUE + msg + self.term.NORMAL

    def print_txt(self, t_list, o_list, l_list, msg=None):
        """
        Print text in a form of table
        --------------
        title1  title2
        --------------
        val     value
        """
        sep = ""
        for item in l_list:
            sep += "-" * (item + 2) # add 2 char space for wrap
        print sep
        for idx in xrange(0, len(t_list)):
            title  = t_list[idx]
            length = l_list[idx]
            print "%s%s " % (title," " * abs(length - len(title))),
        print
        print sep
        for item in o_list:
            for idx in xrange(0, len(item)):
                elem = str(item[idx])
                length = l_list[idx]
                print "%s%s " % (elem, " "*abs(length - len(elem))),
            print
        print sep

    def print_xml(self, t_list, o_list, l_list, msg=None):
        """
        print in format of XML file
        <query> <sql>msg</sql> 
        <table>
             <row>
                 <title>value</title>
                 <title>value</title>
             </row>
        </table>
        </query>
        """
        sep = """<?xml version="1.0" encoding="utf-8"?>\n"""
        sep += "<query>\n"
        sep += "  <sql>%s</sql>\n" % msg
        sep += "  <table>\n"
        for item in o_list:
            sep += "    <row>\n"
            for idx in xrange(0, len(item)):
                value = item[idx]
                sep += "      <%s>%s</%s>\n" % (t_list[idx], value, t_list[idx])
            sep += "    </row>\n"
        sep += "  </table>\n"
        sep += "</query>\n"
        print sep

    def print_html(self, t_list, o_list, l_list, msg=None):
        """
        print in format of HTML file
        <table class="dbsh_table">
        <th>
           <td>title</td>
           <td>title></td>
        </th>
        <tr>
           <td>value</td>
           <td>value</td>
        <tr>
        </table>
        """
        sep = "<table class=\"dbsh_table\">\n"
        sep += "<th>\n"
        for title in t_list:
            sep += "<td>%s</td>\n" % title
        sep += "</th>\n"
        for item in o_list:
            sep += "<tr>\n"
            for value in item:
                sep += "<td>%s</td>\n" % value
            sep += "</tr>\n"
        sep += "</table>\n"
        print sep

    def print_csv(self, t_list, o_list, l_list, msg=None):
        """
        print in format of CSV
        title,title
        value,value
        value,value
        """
        for title in t_list:
            if title != t_list[:-1]:
                print "%s," % title
            else:
                print title
        print
        for item in o_list:
            for value in item:
                if value != o_list[:-1]:
                    print "%s," % value
                else:
                    print value

#
# http://code.activestate.com/recipes/475116/
#
class TerminalController:
    """
    A class that can be used to portably generate formatted output to
    a terminal.

    `TerminalController` defines a set of instance variables whose
    values are initialized to the control sequence necessary to
    perform a given action.  These can be simply included in normal
    output to the terminal:

        >>> term = TerminalController()
        >>> print 'This is '+term.GREEN+'green'+term.NORMAL

    Alternatively, the `render()` method can used, which replaces
    '${action}' with the string required to perform 'action':

        >>> term = TerminalController()
        >>> print term.render('This is ${GREEN}green${NORMAL}')

    If the terminal doesn't support a given action, then the value of
    the corresponding instance variable will be set to ''.  As a
    result, the above code will still work on terminals that do not
    support color, except that their output will not be colored.
    Also, this means that you can test whether the terminal supports a
    given action by simply testing the truth value of the
    corresponding instance variable:

        >>> term = TerminalController()
        >>> if term.CLEAR_SCREEN:
        ...     print 'This terminal supports clearning the screen.'

    Finally, if the width and height of the terminal are known, then
    they will be stored in the `COLS` and `LINES` attributes.
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
        Create a `TerminalController` and initialize its attributes
        with appropriate values for the current terminal.
        `term_stream` is the stream that will be used for terminal
        output; if this stream is not a tty, then the terminal is
        assumed to be a dumb terminal (i.e., have no capabilities).
        """
        # Curses isn't available on all platforms
        try:
            import curses
        except Error:
            return

        # If the stream isn't a tty, then assume it has no capabilities.
        if not term_stream.isatty():
            return

        # Check the terminal type.  If we fail, then assume that the
        # terminal has no capabilities.
        try:
            curses.setupterm()
        except Error:
            return

        # Look up numeric capabilities. 
        # return -2 if capname is not a numberic capability
        # return -1 if it is canceled or absent from terminal description
        self.COLS = curses.tigetnum('cols')
        self.LINES = curses.tigetnum('lines')

        # Look up string capabilities.
        for capability in self._STRING_CAPABILITIES:
            (attrib, cap_name) = capability.split('=')
            setattr(self, attrib, self._tigetstr(cap_name) or '')

        # Colors
        set_fg = self._tigetstr('setf')
        # curses.tparm instantiates the string with the supplied parameters, 
        # where str should be a parameterized string obtained from the terminfo
        # database. E.g tparm(tigetstr("cup", 5, 3) could result in 
        # '\033[6;4H', the exact result depending on terminal type
        if set_fg:
            for index, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, color, curses.tparm(set_fg, index) or '')
        set_fg_ansi = self._tigetstr('setaf')
        if set_fg_ansi:
            for index, color in zip(range(len(self._ANSICOLORS)),
                                               self._ANSICOLORS):
                setattr(self, color, curses.tparm(set_fg_ansi, index) or '')
        set_bg = self._tigetstr('setb')
        if set_bg:
            for index, color in zip(range(len(self._COLORS)), self._COLORS):
                setattr(self, 'BG_'+color, curses.tparm(set_bg, index) or '')
        set_bg_ansi = self._tigetstr('setab')
        if set_bg_ansi:
            for index, color in zip(range(len(self._ANSICOLORS)),
                                               self._ANSICOLORS):
                setattr(self, 'BG_'+color,
                        curses.tparm(set_bg_ansi, index) or '')

    def _tigetstr(self, cap_name):
        """
        # String capabilities can include "delays" of the form "$<2>".
        # For any modern terminal, we should be able to just ignore
        # these, so strip them out.
        """
        import curses
        # curses.tigetstr return value of the string capability corresponding 
        # to the terminfo capability name capname.
        cap = curses.tigetstr(cap_name) or ''
        return re.sub(r'\$<\d+>[/*]?', '', cap)

    def render(self, template):
        """
        Replace each $-substitutions in the given template string with
        the corresponding terminal control string (if it's defined) or
        '' (if it's not).
        """
        return re.sub(r'\$\$|\${\w+}', self._render_sub, template)

    def _render_sub(self, match):
        """
        replace ${color} with self.color
        if it is $$ just return $$
        """
        rep = match.group()
        if rep == '$$':
            return rep
        else:
            return getattr(self, rep[2:-1])

#######################################################################
# Example use case: progress bar
#######################################################################

class ProgressBar:
    """
    A 3-line progress bar, which looks like::

                                Header
        20% [===========----------------------------------]
                           progress message

    The progress bar is colored, if the terminal supports color
    output; and adjusts to the width of the terminal.
    """
    BAR = '%3d%% ${GREEN}[${BOLD}%s%s${NORMAL}${GREEN}]${NORMAL}\n'
    HEADER = '${BOLD}${CYAN}%s${NORMAL}\n\n'

    def __init__(self, term, header):
        """initialize term, in case Terminal is capable:
           set width bar header
           cleared 0%
           update ?%
        """
        self.term = term
        if not (self.term.CLEAR_EOL and self.term.UP and self.term.BOL):
            raise ValueError("Terminal isn't capable enough -- you "
                             "should use a simpler progress dispaly.")
        self.width = self.term.COLS or 75
        self.barline = term.render(self.BAR)
        self.header = self.term.render(self.HEADER % header.center(self.width))
        self.cleared = 1 #: true if we haven't drawn the bar yet.
        self.update(0, '')

    def update(self, percent, message):
        """move the bar to percent%, with message display"""
        if self.cleared:
            sys.stdout.write(self.header)
            self.cleared = 0
        num = int((self.width - 10)*percent)
        sys.stdout.write(
            self.term.BOL + self.term.UP + self.term.CLEAR_EOL +
            (self.barline % (100*percent, '='*num, '-'*(self.width - 10 - num)))
            + self.term.CLEAR_EOL + message.center(self.width))

    def clear(self):
        """clear bar setup"""
        if not self.cleared:
            sys.stdout.write(self.term.BOL + self.term.CLEAR_EOL +
                             self.term.UP + self.term.CLEAR_EOL +
                             self.term.UP + self.term.CLEAR_EOL)
            self.cleared = 1

if __name__ == "__main__":
    TERM = TerminalController()
    print 'This is ' + TERM.RED + 'red' + TERM.NORMAL

    MYPB = ProgressBar(TERM, "Test progress")
    #MYPB.update(0.1, "doing...")
    for ind in range(0, 30):
        time.sleep(1)
        MYPB.update((ind+1)/30.0, "doing...")
