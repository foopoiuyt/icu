# Copyright (C) 2018 and later: Unicode, Inc. and others.
# License & terms of use: http://www.unicode.org/copyright.html

# Python 2/3 Compatibility (ICU-20299)
# TODO(ICU-20301): Remove this.
from __future__ import print_function

from . import *
from .. import *
from .. import utils
from ..request_types import *
import re
import os

CMakeRule = namedtuple("CMakeRule", ["name", "dep_literals", "dep_files", "output_files", "cmds"])
CMakeWriteFileVariableCommand = namedtuple("CMakeWriteFileCommand", ["file", "var_name"])

def get_cmake_rules(build_dirs, requests, **kwargs):
    cmake_string = ""

    # Common Variables
    common_vars = kwargs["common_vars"]

    # Generate Rules
    cmake_rules = []
    dir_dep = name_to_cmake("{TMP_DIR}_dirs", common_vars)
    cmake_string += "add_custom_target({DIR_DEP}\nCOMMAND ${{CMAKE_COMMAND}} -E make_directory {ALL_DIRS})\n".format(
        DIR_DEP = dir_dep,
        ALL_DIRS = " ".join(build_dirs).format(**common_vars)
    )

    for request in requests:
        cmake_rules += get_cmake_rules_helper(request, **kwargs)

    for rule in cmake_rules:
        if isinstance(rule, MakeStringVar):
            if "\n" in rule.content:
                content = "[==[" + rule.content + "]==]"
            else:
                content = "\"" + rule.content + "\""
            cmake_string += "set({NAME} {CONTENT})\n\n".format(
                NAME = rule.name,
                CONTENT = content
            )
            continue
        if isinstance(rule, CMakeWriteFileVariableCommand):
            cmake_string += "file(WRITE {FILE} ${{{VAR_NAME}}} )\n\n".format(
                FILE = rule.file,
                VAR_NAME = rule.var_name
            )
            continue
        if isinstance(rule, CMakeRule):
            # Workaround for directory separator issue in commands
            if os.name == "nt":
                cmds = map(lambda c: c.replace("/", "\\\\"), rule.cmds)
            else:
                cmds = rule.cmds

            cmake_string += "add_custom_command(OUTPUT {OUTPUT}\n\tDEPENDS {DIR_DEP} {DEP_LITERALS} {DEP_FILES}\n\tCOMMAND {CMDS})\n".format(
                OUTPUT = files_to_cmake(rule.output_files, common_vars),
                DIR_DEP = dir_dep,
                DEP_LITERALS = " ".join(rule.dep_literals),
                DEP_FILES = files_to_cmake(rule.dep_files, common_vars),
                CMDS = "\n\t".join(cmds)
            )
            cmake_string += "add_custom_target({NAME} DEPENDS {OUTPUT})\n\n".format(
                NAME = name_to_cmake(rule.name, common_vars),
                OUTPUT = files_to_cmake(rule.output_files, common_vars)
            )
        if isinstance(rule, MakeFilesVar):
            cmake_string += "set({NAME} {FILE_LIST})\n\n".format(
                NAME = rule.name,
                FILE_LIST = files_to_cmake(rule.files, common_vars, wrap=True)
            )

    return cmake_string

def get_cmake_rules_helper(request, common_vars, **kwargs):
    if isinstance(request, PrintFileRequest):
        var_name = "%s_CONTENT" % request.name.upper()
        return [
            MakeStringVar(
                name = var_name,
                content = request.content
            ),
            CMakeWriteFileVariableCommand(
                file = files_to_cmake([request.output_file], common_vars),
                var_name = var_name
            )
        ]

    if isinstance(request, CopyRequest):
        return [
            CMakeRule(
                name = request.name,
                dep_literals = [],
                dep_files = [request.input_file],
                output_files = [request.output_file],
                cmds = ["${CMAKE_COMMAND} -E copy %s %s" % (
                    files_to_cmake([request.input_file], common_vars),
                    files_to_cmake([request.output_file], common_vars))
                ]
            )
        ]

    if isinstance(request, VariableRequest):
        return [
            MakeFilesVar(
                name = request.name.upper(),
                files = request.input_files
            )
        ]

    #TODO what to do with make and gentest?
    if request.tool.name == "make":
        cmd_template = "echo \"[unsupported]\""
        cmd_dep = ""
    elif request.tool.name == "gentest":
        cmd_template = "${{GENTEST}} {ARGS}"
        cmd_dep = "gentest"
    else:
        assert isinstance(request.tool, IcuTool)
        cmd_template = "${{{{TOOLBINDIR}}}}/{TOOL} {{ARGS}}".format(
            TOOL = request.tool.name
        )
        cmd_dep = request.tool.name

    if isinstance(request, SingleExecutionRequest):
        cmd = utils.format_single_request_command(request, cmd_template, common_vars)
        dep_files = request.all_input_files()

        if len(dep_files) > 5:
            # For nicer printing, for long input lists, use a helper variable.
            dep_var_name = "%s_DEPS" % request.name.upper()
            return [
                MakeFilesVar(
                    name = dep_var_name,
                    files = dep_files
                ),
                CMakeRule(
                    name = request.name,
                    dep_literals = ["${%s}" % dep_var_name, cmd_dep],
                    dep_files = [],
                    output_files = request.output_files,
                    cmds = [cmd]
                )
            ]

        else:
            return [
                CMakeRule(
                    name = request.name,
                    dep_literals = [cmd_dep],
                    dep_files = dep_files,
                    output_files = request.output_files,
                    cmds = [cmd]
                )
            ]

    if isinstance(request, RepeatedExecutionRequest):
        rules = []
        dep_literals = [cmd_dep]
        # To keep from repeating the same dep files many times, make a variable.
        if len(request.common_dep_files) > 0:
            dep_var_name = "%s_DEPS" % request.name.upper()
            dep_literals += ["${%s}" % dep_var_name]
            rules += [
                MakeFilesVar(
                    name = dep_var_name,
                    files = request.common_dep_files
                )
            ]
        # Add a rule for each individual file.
        for loop_vars in utils.repeated_execution_request_looper(request):
            (_, specific_dep_files, input_file, output_file) = loop_vars
            name_suffix = input_file.filename[input_file.filename.rfind("/")+1:input_file.filename.rfind(".")]
            cmd = utils.format_repeated_request_command(
                request,
                cmd_template,
                loop_vars,
                common_vars
            )
            rules += [
                CMakeRule(
                    name = "%s_%s" % (request.name, name_suffix),
                    dep_literals = dep_literals,
                    dep_files = specific_dep_files + [input_file],
                    output_files = [output_file],
                    cmds = [cmd]
                )
            ]
        return rules

def files_to_cmake(files, common_vars, wrap = False, **kwargs):
    if len(files) == 0:
        return ""
    dirnames = [utils.dir_for(file).format(**common_vars) for file in files]
    join_str = " \n\t\t" if wrap and len(files) > 2 else " "
    if len(files) == 1:
        return "%s/%s" % (dirnames[0], files[0].filename)
    else:
        return join_str.join("%s/%s" % (d, f.filename) for d,f in zip(dirnames, files))


def name_to_cmake(name, common_vars, **kwargs):
    return re.sub(r'[^-a-zA-Z0-9_.+]', '_', name.format(**common_vars))
