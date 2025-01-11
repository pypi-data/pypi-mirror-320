#
# Copyright (c) 2023 Jared Crapo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# pylint: disable=protected-access, missing-function-docstring, redefined-outer-name
# pylint: disable=missing-module-docstring, unused-variable

import pytest
import rich.errors
import rich.style

import dye.agents
from dye import Dye


#
# test GeneratorBase functionality
#
def test_agent_classmap():
    classmap = dye.agents.AgentBase.classmap
    assert "environment_variables" in classmap
    assert "bogusagent" not in classmap
    assert classmap["environment_variables"].__name__ == "EnvironmentVariables"


def test_agent_name():
    envgen = dye.agents.EnvironmentVariables(None, None, None)
    assert envgen.agent == "environment_variables"
    fzfgen = dye.agents.Fzf(None, None, None)
    assert fzfgen.agent == "fzf"


#
# test high level generation functions
#
def test_activate_single_scope(dye_cmdline, capsys):
    tomlstr = """
        [styles]
        background =  "#282a36"
        foreground =  "#f8f8f2"
        current_line =  "#f8f8f2 on #44475a"
        comment =  "#6272a4"
        cyan =  "#8be9fd"
        green =  "#50fa7b"
        orange =  "#ffb86c"
        pink =  "#ff79c6"
        purple =  "#bd93f9"
        red =  "#ff5555"
        yellow =  "#f1fa8c"

        [scope.iterm]
        agent = "iterm"
        style.foreground = "foreground"
        style.background = "background"

        [scope.fzf]
        agent = "fzf"

        # attributes specific to fzf
        environment_variable = "FZF_DEFAULT_OPTS"

        # command line options
        opt.--prompt = ">"
        opt.--border = "single"
        opt.--pointer = "•"
        opt.--info = "hidden"
        opt.--no-sort = true
        opt."+i" = true

        # styles
        style.text = "foreground"
        style.label = "green"
        style.border = "orange"
        style.selected = "current_line"
        style.prompt = "green"
        style.indicator = "cyan"
        style.match = "pink"
        style.localstyle = "green on black"
    """
    exit_code = dye_cmdline("activate -s fzf", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert out
    assert not err
    assert out.count("\n") == 1


def test_activate_unknown_scope(dye_cmdline, capsys):
    tomlstr = """
        [styles]
        background =  "#282a36"
        foreground =  "#f8f8f2"

        [scope.iterm]
        agent = "iterm"
        style.foreground = "foreground"
        style.background = "background"

        [scope.ls]
        # set some environment variables
        environment.unset = ["SOMEVAR", "ANOTHERVAR"]
        environment.export.LS_COLORS = "ace ventura"
    """
    exit_code = dye_cmdline("activate -s unknownscope", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert not out
    assert err


def test_activate_no_scopes(dye_cmdline, capsys):
    tomlstr = """
        [styles]
        background =  "#282a36"
        foreground =  "#f8f8f2"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not out
    assert not err


#
# test elements common to all scopes
#
def test_activate_enabled(dye_cmdline, capsys):
    tomlstr = """
        [scope.nolistvar]
        enabled = false
        agent = "environment_variables"
        unset = "NOLISTVAR"

        [scope.somevar]
        enabled = true
        agent = "environment_variables"
        unset = "SOMEVAR"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert "unset SOMEVAR" in out
    assert "unset NOLISTVAR" not in out


def test_activate_enabled_false_enabled_if_ignored(dye_cmdline, capsys):
    tomlstr = """
        [scope.unset]
        enabled = false
        enabled_if = "[[ 1 == 1 ]]"
        agent = "environment_variables"
        unset = "NOLISTVAR"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert not out


def test_activate_enabled_true_enabed_if_ignored(dye_cmdline, capsys):
    tomlstr = """
        [scope.unset]
        enabled = true
        enabled_if = "[[ 0 == 1 ]]"
        agent = "environment_variables"
        unset = "NOLISTVAR"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert "unset NOLISTVAR" in out


def test_activate_enabled_invalid_value(dye_cmdline, capsys):
    tomlstr = """
        [scope.unset]
        enabled = "notaboolean"
        agent = "environment_variables"
        unset = "NOLISTVAR"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert not out
    assert "to be true or false" in err


ENABLED_IFS = [
    ("", True),
    ("echo", True),
    ("[[ 1 == 1 ]]", True),
    ("[[ 1 == 0 ]]", False),
    ("{var:echocmd} hi", True),
    ("{variable:falsetest}", False),
]


@pytest.mark.parametrize("cmd, enabled", ENABLED_IFS)
def test_activate_enabled_if(cmd, enabled, dye_cmdline, capsys):
    tomlstr = f"""
        [variables]
        echocmd = "/bin/echo"
        falsetest = "[[ 1 == 0 ]]"

        [scope.unset]
        enabled_if = "{cmd}"
        agent = "environment_variables"
        unset = "ENVVAR"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    if enabled:
        assert "unset ENVVAR" in out
    else:
        assert not out


def test_activate_comments(dye_cmdline, capsys):
    tomlstr = """
        [scope.nolistvar]
        enabled = false
        agent = "environment_variables"
        unset = "NOLISTVAR"

        [scope.somevar]
        enabled = true
        agent = "environment_variables"
        unset = "SOMEVAR"
    """
    exit_code = dye_cmdline("activate --comment", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert "# [scope.nolistvar]" in out
    assert "# [scope.somevar]" in out
    assert "unset SOMEVAR" in out
    assert "unset NOLISTVAR" not in out


def test_unknown_agent(dye_cmdline, capsys):
    tomlstr = """
        [scope.myprog]
        agent = "mrfusion"
        unset = "SOMEVAR"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    _, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert "unknown agent" in err
    assert "mrfusion" in err


def test_no_agent(dye_cmdline, capsys):
    tomlstr = """
        [scope.myscope]
        enabled = false
    """
    exit_code = dye_cmdline("activate", tomlstr)
    _, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert "does not have an agent" in err
    assert "myscope" in err


#
# test the environment_variables agent
#
ENV_INTERPOLATIONS = [
    ("{style:dark_orange}", "#ff6c1c"),
    ("{style:dark_orange:fghex}", "#ff6c1c"),
    ("{style:dark_orange:fghexnohash}", "ff6c1c"),
    (
        "{style:dark_orange:ansi_on}hello there{style:dark_orange:ansi_off}",
        "\x1b[38;2;255;108;28mhello there\x1b[0m",
    ),
    # we have to have the style keyword, or it all just gets passed through
    ("{dark_orange}", "{dark_orange}"),
    # escaped opening bracket, becasue this is toml, if you want a backslash
    # you have to you \\ because toml strings can contain escape sequences
    (r"\\{style:bright_blue}", "{style:bright_blue}"),
    # if you don't have matched brackets, or are missing the
    # literal 'style:' keyword, don't expect the backslash
    # to be removed. again here we have two backslashes in the first
    # argument so that it will survive toml string escaping
    (r"\\{ some other  things}", r"\{ some other  things}"),
    (r"\\{escaped unmatched bracket", r"\{escaped unmatched bracket"),
    # try a mixed variable and style interpolation
    ("{style:dark_orange} {var:someopts}", "#ff6c1c --option=fred -v"),
]


@pytest.mark.parametrize("phrase, interpolated", ENV_INTERPOLATIONS)
def test_activate_environment_interpolation(dye_cmdline, capsys, phrase, interpolated):
    tomlstr = f"""
        [variables]
        someopts = "--option=fred -v"

        [styles]
        dark_orange = "#ff6c1c"

        [scope.gum]
        agent = "environment_variables"
        export.GUM_OPTS = " --cursor-foreground={phrase}"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert out == f'export GUM_OPTS=" --cursor-foreground={interpolated}"\n'


def test_activate_environment_unset_list(dye_cmdline, capsys):
    tomlstr = """
        [variables]
        thevar = "ANOTHERVAR"

        [scope.ls]
        agent = "environment_variables"
        # set some environment variables
        unset = ["SOMEVAR", "{var:thevar}"]
        export.LS_COLORS = "ace ventura"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert "unset SOMEVAR" in out
    assert "unset ANOTHERVAR" in out
    assert 'export LS_COLORS="ace ventura"' in out


def test_activate_environment_unset_string(dye_cmdline, capsys):
    tomlstr = """
        [scope.unset]
        agent = "environment_variables"
        unset = "NOLISTVAR"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert "unset NOLISTVAR" in out


#
# test the fzf agent
#
ATTRIBS_TO_FZF = [
    ("bold", "regular:bold"),
    ("underline", "regular:underline"),
    ("reverse", "regular:reverse"),
    ("dim", "regular:dim"),
    ("italic", "regular:italic"),
    ("strike", "regular:strikethrough"),
    ("bold underline", "regular:bold:underline"),
    ("underline italic", "regular:underline:italic"),
    ("italic underline", "regular:underline:italic"),
]


@pytest.mark.parametrize("styledef, fzf", ATTRIBS_TO_FZF)
def test_fzf_attribs_from_style(styledef, fzf):
    style = rich.style.Style.parse(styledef)
    genny = dye.agents.Fzf(None, None, None, None, None)
    assert fzf == genny._fzf_attribs_from_style(style)


STYLE_TO_FZF = [
    # text, current-line, selected-line and preview styles have special processing
    # for foreground and background colors
    ("text", "", ""),
    ("text", "default", "fg:-1:regular"),
    ("text", "default on default", "fg:-1:regular,bg:-1"),
    ("text", "bold default on default underline", "fg:-1:regular:bold:underline,bg:-1"),
    ("text", "white on bright_red", "fg:7:regular,bg:9"),
    ("text", "bright_white", "fg:15:regular"),
    ("text", "bright_yellow on color(4)", "fg:11:regular,bg:4"),
    ("text", "green4", "fg:28:regular"),
    ("current-line", "navy_blue dim on grey82", "fg+:17:regular:dim,bg+:252"),
    (
        "selected-line",
        "navy_blue dim on grey82",
        "selected-fg:17:regular:dim,selected-bg:252",
    ),
    ("preview", "#af00ff on bright_white", "preview-fg:#af00ff:regular,preview-bg:15"),
    # other styles do not
    ("border", "magenta", "border:5:regular"),
    ("query", "#2932dc", "query:#2932dc:regular"),
]


@pytest.mark.parametrize("name, styledef, fzf", STYLE_TO_FZF)
def test_fzf_from_style(name, styledef, fzf):
    style = rich.style.Style.parse(styledef)
    genny = dye.agents.Fzf(None, None, None, None, None)
    assert fzf == genny._fzf_from_style(name, style)


def test_fzf(dye_cmdline, capsys):
    tomlstr = """
        [styles]
        purple = "#7060eb"

        [variables]
        bstyle = "rounded"

        [scope.fzf]
        agent = "fzf"
        environment_variable = "QQQ"
        opt."+i" = true
        opt.--border = "{var:bstyle}"
        style.prompt = "magenta3"
        style.info = "purple"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    expected = (
        """export QQQ=" +i --border='rounded'"""
        """ --color='prompt:164:regular,info:#7060eb:regular'"\n"""
    )
    assert out == expected


def test_fzf_no_opts(dye_cmdline, capsys):
    tomlstr = """
        [variables]
        varname = "ZZ"

        [scope.fzf]
        agent = "fzf"
        environment_variable = "Q{var:varname}QQ"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == """export QZZQQ=""\n"""


def test_fzf_no_varname(dye_cmdline, capsys):
    tomlstr = """
        [scope.fzf]
        agent = "fzf"
        opt."+i" = true
        opt.--border = "rounded"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert "FZF_DEFAULT_OPTS" in out


#
# test the ls_colors agent
#
# we only reallly have to test that the style name maps to the right code in ls_colors
# ie directory -> di, or setuid -> su. The ansi codes are created by rich.style
# so we don't really need to test much of that
STYLE_TO_LSCOLORS = [
    ("text", "", ""),
    ("text", "default", "no=0"),
    ("file", "default", "fi=0"),
    ("directory", "#8be9fd", "di=38;2;139;233;253"),
    ("symlink", "green4 bold", "ln=1;38;5;28"),
    ("multi_hard_link", "blue on white", "mh=34;47"),
    ("pipe", "#f8f8f2 on #44475a underline", "pi=4;38;2;248;248;242;48;2;68;71;90"),
    ("so", "bright_white", "so=97"),
    ("door", "bright_white", "do=97"),
    ("block_device", "default", "bd=0"),
    ("character_device", "black", "cd=30"),
    ("broken_symlink", "bright_blue", "or=94"),
    ("missing_symlink_target", "bright_blue", "mi=94"),
    ("setuid", "bright_blue", "su=94"),
    ("setgid", "bright_red", "sg=91"),
    ("sticky", "blue_violet", "st=38;5;57"),
    ("other_writable", "blue_violet italic", "ow=3;38;5;57"),
    ("sticky_other_writable", "deep_pink2 on #ffffaf", "tw=38;5;197;48;2;255;255;175"),
    ("executable_file", "cornflower_blue on grey82", "ex=38;5;69;48;5;252"),
    ("file_with_capability", "red on black", "ca=31;40"),
]


@pytest.mark.parametrize("name, styledef, expected", STYLE_TO_LSCOLORS)
def test_ls_colors_from_style(name, styledef, expected):
    style = rich.style.Style.parse(styledef)
    genny = dye.agents.LsColors(None, None, None, None, None)
    code, render = genny.ls_colors_from_style(
        name,
        style,
        genny.LS_COLORS_MAP,
        allow_unknown=False,
        prog="prog",
        scope="scope",
    )
    assert render == expected
    assert code == expected[0:2]


def test_ls_colors_no_styles(dye_cmdline, capsys):
    tomlstr = """
        [scope.lsc]
        agent = "ls_colors"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export LS_COLORS=""\n'


def test_ls_colors_unknown_style(dye_cmdline, capsys):
    tomlstr = """
        [scope.lsc]
        agent = "ls_colors"
        style.bundleid = "default"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert "unknown style" in err
    assert "lsc" in err


def test_ls_colors_environment_variable(dye_cmdline, capsys):
    tomlstr = """
        [scope.lsc]
        agent = "ls_colors"
        environment_variable = "OTHER_LS_COLOR"
        style.file = "default"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export OTHER_LS_COLOR="fi=0"\n'


def test_ls_colors_styles_variables(dye_cmdline, capsys):
    tomlstr = """
        [variables]
        pinkvar = "magenta3"

        [styles]
        warning = "yellow on red"

        [scope.lsc]
        agent = "ls_colors"
        style.file = "warning"
        style.directory = "{var:pinkvar}"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export LS_COLORS="fi=33;41:di=38;5;164"\n'


def test_ls_colors_clear_builtin(dye_cmdline, capsys):
    tomlstr = """
        [scope.lsc]
        agent = "ls_colors"
        clear_builtin = true
        style.directory = "bright_blue"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    expected = (
        'export LS_COLORS="di=94:no=0:fi=0:ln=0:'
        "mh=0:pi=0:so=0:do=0:bd=0:cd=0:or=0:mi=0:"
        'su=0:sg=0:st=0:ow=0:tw=0:ex=0:ca=0"\n'
    )
    assert out == expected


def test_ls_colors_clear_builtin_not_boolean(dye_cmdline, capsys):
    tomlstr = """
        [scope.lsc]
        agent = "ls_colors"
        clear_builtin = "error"
        style.directory = "bright_blue"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert not out
    assert "'clear_builtin' to be true or false" in err


#
# test the exa_colors agent
#
# we only reallly have to test that the style name maps to the right code in ls_colors
# ie directory -> di, or setuid -> su. The ansi codes are created by rich.style
# so we don't really need to test much of that
STYLE_TO_EXACOLORS = [
    ("text", "", ""),
    ("text", "default", "no=0"),
    ("file", "default", "fi=0"),
    ("directory", "#8be9fd", "di=38;2;139;233;253"),
    ("symlink", "green4 bold", "ln=1;38;5;28"),
    ("multi_hard_link", "blue on white", "mh=34;47"),
    ("pi", "#f8f8f2 on #44475a underline", "pi=4;38;2;248;248;242;48;2;68;71;90"),
    ("socket", "bright_white", "so=97"),
    ("door", "bright_white", "do=97"),
    ("block_device", "default", "bd=0"),
    ("character_device", "black", "cd=30"),
    ("broken_symlink", "bright_blue", "or=94"),
    ("missing_symlink_target", "bright_blue", "mi=94"),
    ("setuid", "bright_blue", "su=94"),
    ("setgid", "bright_red", "sg=91"),
    ("sticky", "blue_violet", "st=38;5;57"),
    ("other_writable", "blue_violet italic", "ow=3;38;5;57"),
    ("sticky_other_writable", "deep_pink2 on #ffffaf", "tw=38;5;197;48;2;255;255;175"),
    ("executable_file", "cornflower_blue on grey82", "ex=38;5;69;48;5;252"),
    ("file_with_capability", "red on black", "ca=31;40"),
    ("sn", "#7060eb", "sn=38;2;112;96;235"),
]


@pytest.mark.parametrize("name, styledef, expected", STYLE_TO_EXACOLORS)
def test_exa_colors_from_style(name, styledef, expected):
    style = rich.style.Style.parse(styledef)
    genny = dye.agents.ExaColors(None, None, None, None, None)
    code, render = genny.ls_colors_from_style(
        name,
        style,
        genny.EXA_COLORS_MAP,
        allow_unknown=False,
        prog="prog",
        scope="scope",
    )
    assert render == expected
    assert code == expected[0:2]


def test_exa_colors_no_styles(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "exa_colors"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export EXA_COLORS=""\n'


def test_exa_colors_unknown_style(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "exa_colors"
        style.bundleid = "default"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert "unknown style" in err
    assert "exac" in err


def test_exa_colors_environment_variable(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "exa_colors"
        environment_variable = "OTHER_EXA_COLOR"
        style.file = "default"
        style.size_number = "#7060eb"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export OTHER_EXA_COLOR="fi=0:sn=38;2;112;96;235"\n'


def test_exa_colors_styles_variables(dye_cmdline, capsys):
    tomlstr = """
        [variables]
        pinkvar = "magenta3"

        [styles]
        warning = "yellow on red"

        [scope.lsc]
        agent = "exa_colors"
        style.file = "warning"
        style.directory = "{var:pinkvar}"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export EXA_COLORS="fi=33;41:di=38;5;164"\n'


def test_exa_colors_clear_builtin(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "exa_colors"
        clear_builtin = true
        style.directory = "bright_blue"
        style.uu = "bright_red"
        style.punctuation = "#555555"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    expected = 'export EXA_COLORS="reset:di=94:uu=91:xx=38;2;85;85;85"\n'
    assert out == expected


def test_exa_colors_clear_builtin_not_boolean(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "exa_colors"
        clear_builtin = "error"
        style.directory = "bright_blue"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert not out
    assert "'clear_builtin' to be true or false" in err


#
# test the eza_colors agent
#
# we only reallly have to test that the style name maps to the right code in ls_colors
# ie directory -> di, or setuid -> su. The ansi codes are created by rich.style
# so we don't really need to test much of that
STYLE_TO_EZACOLORS = [
    ("filekinds:normal", "default", "fi=0"),
    ("filekinds:directory", "#8be9fd", "di=38;2;139;233;253"),
    ("filekinds:symlink", "green4 bold", "ln=1;38;5;28"),
    ("lc", "blue on white", "lc=34;47"),
    ("pi", "#f8f8f2 on #44475a underline", "pi=4;38;2;248;248;242;48;2;68;71;90"),
    ("filekinds:socket", "bright_white", "so=97"),
    ("filekinds:block_device", "default", "bd=0"),
    ("filekinds:char_device", "black", "cd=30"),
    ("broken_symlink", "bright_blue", "or=94"),
    ("perms:special_user_file", "bright_blue", "su=94"),
    ("perms:special_other", "bright_red", "sf=91"),
    ("perms:other_write", "deep_pink2 on #ffffaf", "tw=38;5;197;48;2;255;255;175"),
    ("filekinds:executable", "cornflower_blue on grey82", "ex=38;5;69;48;5;252"),
    ("size:number_style", "#7060eb", "sn=38;2;112;96;235"),
    ("*.toml", "#8be9fd", "*.toml=38;2;139;233;253"),
]


@pytest.mark.parametrize("name, styledef, expected", STYLE_TO_EZACOLORS)
def test_eza_colors_from_style(name, styledef, expected):
    style = rich.style.Style.parse(styledef)
    genny = dye.agents.Eza(None, None, None, None, None)
    code, render = genny.ls_colors_from_style(
        name,
        style,
        genny.EZA_COLORS_MAP,
        allow_unknown=True,
        prog="prog",
        scope="scope",
    )
    assert render == expected
    assert code == expected.split("=", 1)[0]


def test_eza_colors_no_styles(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "eza"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export EZA_COLORS=""\n'


def test_eza_colors_environment_variable(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "eza"
        environment_variable = "OTHER_EZA_COLOR"
        style.'filekinds:normal' = "default"
        style.'size:number_style' = "#7060eb"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export OTHER_EZA_COLOR="fi=0:sn=38;2;112;96;235"\n'


def test_eza_colors_styles_variables(dye_cmdline, capsys):
    tomlstr = """
        [variables]
        pinkvar = "magenta3"

        [styles]
        warning = "yellow on red"

        [scope.lsc]
        agent = "eza"
        style.'filekinds:normal' = "warning"
        style.'filekinds:directory' = "{var:pinkvar}"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == 'export EZA_COLORS="fi=33;41:di=38;5;164"\n'


def test_eza_colors_clear_builtin(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "eza"
        clear_builtin = true
        style.'filekinds:directory' = "bright_blue"
        style.uu = "bright_red"
        style.punctuation = "#555555"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    expected = 'export EZA_COLORS="reset:di=94:uu=91:xx=38;2;85;85;85"\n'
    assert out == expected


def test_eza_colors_clear_builtin_not_boolean(dye_cmdline, capsys):
    tomlstr = """
        [scope.exac]
        agent = "eza"
        clear_builtin = "error"
        style.directory = "bright_blue"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert not out
    assert "'clear_builtin' to be true or false" in err


#
# test the iterm agent
#
def test_iterm_fg_bg(dye_cmdline, capsys):
    tomlstr = """
        [styles]
        foreground = "#ffeebb"
        background = "#221122"

        [scope.iterm]
        agent = "iterm"
        style.foreground = "foreground"
        style.background = "background"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    assert len(lines) == 2
    assert lines[0] == r'builtin echo -en "\e]1337;SetColors=fg=ffeebb\a"'
    assert lines[1] == r'builtin echo -en "\e]1337;SetColors=bg=221122\a"'


def test_iterm_bg(dye_cmdline, capsys):
    tomlstr = """
        [scope.iterm]
        agent = "iterm"
        style.background = "#b2cacd"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    assert len(lines) == 1
    assert lines[0] == r'builtin echo -en "\e]1337;SetColors=bg=b2cacd\a"'


def test_iterm_profile(dye_cmdline, capsys):
    tomlstr = """
        [scope.iterm]
        agent = "iterm"
        cursor = "box"
        style.cursor = "#b2cacd"
        profile = "myprofilename"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    # we have multiple directives in this scope, but the profile directive
    # should always come out first
    assert len(lines) == 3
    assert lines[0] == r'builtin echo -en "\e]1337;SetProfile=myprofilename\a"'


def test_iterm_cursor(dye_cmdline, capsys):
    tomlstr = """
        [scope.iterm]
        agent = "iterm"
        cursor = "underline"
        style.cursor = "#cab2cd"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    assert len(lines) == 2
    assert lines[0] == r'builtin echo -en "\e]1337;CursorShape=2\a"'
    assert lines[1] == r'builtin echo -en "\e]1337;SetColors=curbg=cab2cd\a"'


CURSOR_SHAPES = [
    ("block", "0"),
    ("box", "0"),
    ("vertical_bar", "1"),
    ("vertical", "1"),
    ("bar", "1"),
    ("pipe", "1"),
    ("underline", "2"),
]


@pytest.mark.parametrize("name, code", CURSOR_SHAPES)
def test_iterm_cursor_shape(dye_cmdline, capsys, name, code):
    tomlstr = f"""
        [scope.iterm]
        agent = "iterm"
        cursor = "{name}"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    assert len(lines) == 1
    # fr'...' lets us use f string interpolation, but the r disables
    # escape processing, just what we need for this test
    assert lines[0] == rf'builtin echo -en "\e]1337;CursorShape={code}\a"'


def test_iterm_cursor_profile(dye_cmdline, capsys):
    tomlstr = """
        [scope.iterm]
        agent = "iterm"
        profile = "smoov"
        cursor = "profile"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    assert len(lines) == 2
    # fr'...' lets us use f string interpolation, but the r disables
    # escape processing, just what we need for this test
    assert lines[1] == r'builtin echo -en "\e[0q"'


def test_iterm_cursor_shape_invalid(dye_cmdline, capsys):
    tomlstr = """
        [scope.iterm]
        agent = "iterm"
        cursor = "ibeam"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_ERROR
    assert not out
    assert "unknown cursor" in err


def test_item_tab_default(dye_cmdline, capsys):
    tomlstr = """
        [scope.iterm]
        agent = "iterm"
        style.tab = "default"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    assert len(lines) == 1
    assert lines[0] == r'builtin echo -en "\e]6;1;bg;*;default\a"'


def test_iterm_tab_color(dye_cmdline, capsys):
    tomlstr = """
        [scope.iterm]
        agent = "iterm"
        style.tab = "#337799"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    lines = out.splitlines()
    assert len(lines) == 3
    assert lines[0] == r'builtin echo -en "\e]6;1;bg;red;brightness;51\a"'
    assert lines[1] == r'builtin echo -en "\e]6;1;bg;green;brightness;119\a"'
    assert lines[2] == r'builtin echo -en "\e]6;1;bg;blue;brightness;153\a"'


#
# test the shell agent
#
def test_shell(dye_cmdline, capsys):
    tomlstr = """
        [variables]
        greeting = "hello there"

        [styles]
        purple = "#A020F0"

        [scope.shortcut]
        agent = "shell"
        command.first = "echo {var:greeting}"
        command.next = "echo general kenobi"
        command.last = "echo {style:purple}"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == "echo hello there\necho general kenobi\necho #a020f0\n"


def test_shell_ansi(dye_cmdline, capsys):
    tomlstr = """
        [variables]
        greeting = "hello there"

        [styles]
        purple = "#A020F0"

        [scope.shortcut]
        agent = "shell"
        command.first = "echo {style:purple:ansi_on}{var:greeting}{style:purple:ansi_off}"
    """  # noqa: E501
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert out == "echo \x1b[38;2;160;32;240mhello there\x1b[0m\n"


def test_shell_enabled_if(dye_cmdline, capsys):
    # we have separate tests for enabled_if, but since it's super useful with the
    # shell agent, i'm including another test here
    tomlstr = """
        [scope.shortcut]
        agent = "shell"
        enabled_if = "[[ 1 == 0 ]]"
        command.first = "shortcuts run 'My Shortcut Name'"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert not out


def test_shell_multiline(dye_cmdline, capsys):
    tomlstr = """
        [scope.multiline]
        agent = "shell"
        command.long = '''
echo hello there
echo general kenobi
if [[ 1 == 1 ]]; then
  echo "yes sir"
fi
'''
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    # yes we have two line breaks at the end of what we expect
    # because there are single line commands, we have to output
    # a newline after the command
    # but on multiline commands that might give an extra newline
    # at the end of the day, that makes zero difference in
    # functionality, but it matters for testing, hence this note
    expected = """echo hello there
echo general kenobi
if [[ 1 == 1 ]]; then
  echo "yes sir"
fi

"""
    assert out == expected


def test_shell_no_commands(dye_cmdline, capsys):
    tomlstr = """
        [scope.shortcut]
        agent = "shell"
    """
    exit_code = dye_cmdline("activate", tomlstr)
    out, err = capsys.readouterr()
    assert exit_code == Dye.EXIT_SUCCESS
    assert not err
    assert not out
