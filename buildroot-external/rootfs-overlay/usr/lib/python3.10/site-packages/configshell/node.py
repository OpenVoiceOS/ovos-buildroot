'''
This file is part of ConfigShell.
Copyright (c) 2011-2013 by Datera, Inc

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
'''

import inspect
import re
import six

class ExecutionError(Exception):
    pass

class ConfigNode(object):
    '''
    The ConfigNode class defines a common skeleton to be used by specific
    implementation. It is "purely virtual" (sorry for using non-pythonic
    vocabulary there ;-) ).
    '''
    _path_separator = '/'
    _path_current = '.'
    _path_previous = '..'

    ui_type_method_prefix = "ui_type_"
    ui_command_method_prefix = "ui_command_"
    ui_complete_method_prefix = "ui_complete_"
    ui_setgroup_method_prefix = "ui_setgroup_"
    ui_getgroup_method_prefix = "ui_getgroup_"

    help_intro = '''
                 GENERALITIES
                 ============
                 This is a shell in which you can create, delete and configure
                 configuration objects.

                 The available commands depend on the current path or target
                 path you want to run a command in: different path have
                 different sets of available commands, i.e. a path pointing at
                 an iSCSI target will not have the same available commands as,
                 say, a path pointing at a storage object.

                 The prompt that starts each command line indicates your
                 current path. Alternatively (useful if the prompt displays
                 an abbreviated path to save space), you can run the
                 `pwd` command to display the complete current path.

                 Navigating the tree is done using the `cd` command. Without
                 any argument, `cd` presents you with the full objects
                 tree. Just use arrows to select the destination path, and
                 enter will get you there. Please try `help cd` for navigation
                 tips.

                 COMMAND SYNTAX
                 ==============
                 Commands are built using the following syntax:

                 [TARGET_PATH] COMMAND_NAME [OPTIONS]

                 TARGET_PATH indicates the path to run the command from.
                 If omitted, the command is run from your current path.

                 OPTIONS depend on the command. Please use `help` to
                 get more information.
                 '''

    def __init__(self, name, parent=None, shell=None):
        '''
        @param parent: The parent ConfigNode of the new object. If None, then
        the ConfigNode will be a root node.
        @type parent: ConfigNode or None
        @param shell: The shell to attach a root node to.
        @type shell: ConfigShell
        '''
        self._name = name
        self._children = set([])
        if parent is None:
            if shell is None:
                raise ValueError("A root ConfigNode must have a shell.")
            else:
                self._parent = None
                self._shell = shell
                shell.attach_root_node(self)
        else:
            if shell is None:
                self._parent = parent
                self._shell = None
            else:
                raise ValueError("A non-root ConfigNode can't have a shell.")

        if self._parent is not None:
            for sibling in self._parent._children:
                if sibling.name == name:
                    raise ValueError("Name '%s' already used by a sibling."
                                     % self._name)
            self._parent._children.add(self)

        self._configuration_groups = {}

        self.define_config_group_param(
            'global', 'tree_round_nodes', 'bool',
            'Tree node display style.')
        self.define_config_group_param(
            'global', 'tree_status_mode', 'bool',
            'Whether or not to display status in tree.')
        self.define_config_group_param(
            'global', 'tree_max_depth', 'number',
            'Maximum depth of displayed node tree.')
        self.define_config_group_param(
            'global', 'tree_show_root', 'bool',
            'Whether or not to display tree root.')
        self.define_config_group_param(
            'global', 'color_mode', 'bool',
            'Console color display mode.')
        self.define_config_group_param(
            'global', 'loglevel_console', 'loglevel',
            'Log level for messages going to the console.')
        self.define_config_group_param(
            'global', 'loglevel_file', 'loglevel',
            'Log level for messages going to the log file.')
        self.define_config_group_param(
            'global', 'logfile', 'string',
            'Logfile to use.')
        self.define_config_group_param(
            'global', 'color_default', 'colordefault',
            'Default text display color.')
        self.define_config_group_param(
            'global', 'color_path', 'color',
            'Color to use for path completions')
        self.define_config_group_param(
            'global', 'color_command', 'color',
            'Color to use for command completions.')
        self.define_config_group_param(
            'global', 'color_parameter', 'color',
            'Color to use for parameter completions.')
        self.define_config_group_param(
            'global', 'color_keyword', 'color',
            'Color to use for keyword completions.')
        self.define_config_group_param(
            'global', 'prompt_length', 'number',
            'Max length of the shell prompt path, 0 for infinite.')

        if self.shell.prefs['bookmarks'] is None:
            self.shell.prefs['bookmarks'] = {}

    # User interface types

    def ui_type_number(self, value=None, enum=False, reverse=False):
        '''
        UI parameter type helper for number parameter type.
        @param value: Value to check against the type.
        @type value: anything
        @param enum: Has a meaning only if value is omitted. If set, returns
        a list of the possible values for the type, or [] if this is not
        possible. If not set, returns a text description of the type format.
        @type enum: bool
        @param reverse: If set, translates an internal value to its UI
        string representation.
        @type reverse: bool
        @return: c.f. parameter enum description.
        @rtype: str|list|None
        @raise ValueError: If the value does not check ok against the type.
        '''
        if reverse:
            if value is not None:
                return str(value)
            else:
                return 'n/a'

        type_enum = []
        syntax = "NUMBER"
        if value is None:
            if enum:
                return type_enum
            else:
                return syntax
        elif not value:
            return None
        else:
            try:
                value = int(value)
            except ValueError:
                raise ValueError("Syntax error, '%s' is not a %s."
                                 % (value, syntax))
            else:
                return value

    def ui_type_string(self, value=None, enum=False, reverse=False):
        '''
        UI parameter type helper for string parameter type.
        @param value: Value to check against the type.
        @type value: anything
        @param enum: Has a meaning only if value is omitted. If set, returns
        a list of the possible values for the type, or [] if this is not
        possible. If not set, returns a text description of the type format.
        @type enum: bool
        @param reverse: If set, translates an internal value to its UI
        string representation.
        @type reverse: bool
        @return: c.f. parameter enum description.
        @rtype: str|list|None
        @raise ValueError: If the value does not check ok against the type.
        '''
        if reverse:
            if value is not None:
                return value
            else:
                return 'n/a'

        type_enum = []
        syntax = "STRING_OF_TEXT"
        if value is None:
            if enum:
                return type_enum
            else:
                return syntax
        elif not value:
            return None
        else:
            try:
                value = str(value)
            except ValueError:
                raise ValueError("Syntax error, '%s' is not a %s."
                                 % (value, syntax))
            else:
                return value

    def ui_type_bool(self, value=None, enum=False, reverse=False):
        '''
        UI parameter type helper for boolean parameter type. Valid values are
        either 'true' or 'false'.
        @param value: Value to check against the type.
        @type value: anything
        @param enum: Has a meaning only if value is omitted. If set, returns
        a list of the possible values for the type, or None if this is not
        possible. If not set, returns a text description of the type format.
        @type enum: bool
        @param reverse: If set, translates an internal value to its UI
        string representation.
        @type reverse: bool
        @return: c.f. parameter enum description.
        @rtype: str|list|None
        @raise ValueError: If the value does not check ok againts the type.
        '''
        if reverse:
            if value:
                return 'true'
            else:
                return 'false'
        type_enum = ['true', 'false']
        syntax = '|'.join(type_enum)
        if value is None:
            if enum:
                return type_enum
            else:
                return syntax
        elif value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise ValueError("Syntax error, '%s' is not %s."
                             % (value, syntax))

    def ui_type_loglevel(self, value=None, enum=False, reverse=False):
        '''
        UI parameter type helper for log level parameter type.
        @param value: Value to check against the type.
        @type value: anything
        @param enum: Has a meaning only if value is omitted. If set, returns
        a list of the possible values for the type, or None if this is not
        possible. If not set, returns a text description of the type format.
        @type enum: bool
        @param reverse: If set, translates an internal value to its UI
        string representation.
        @type reverse: bool
        @return: c.f. parameter enum description.
        @rtype: str|list|None
        @raise ValueError: If the value does not check ok againts the type.
        '''
        if reverse:
            if value is not None:
                return value
            else:
                return 'n/a'

        type_enum = self.shell.log.levels
        syntax = '|'.join(type_enum)
        if value is None:
            if enum:
                return type_enum
            else:
                return syntax
        elif value in type_enum:
            return value
        else:
            raise ValueError("Syntax error, '%s' is not %s"
                             % (value, syntax))

    def ui_type_color(self, value=None, enum=False, reverse=False):
        '''
        UI parameter type helper for color parameter type.
        @param value: Value to check against the type.
        @type value: anything
        @param enum: Has a meaning only if value is omitted. If set, returns
        a list of the possible values for the type, or None if this is not
        possible. If not set, returns a text description of the type format.
        @type enum: bool
        @param reverse: If set, translates an internal value to its UI
        string representation.
        @type reverse: bool
        @return: c.f. parameter enum description.
        @rtype: str|list|None
        @raise ValueError: If the value does not check ok againts the type.
        '''
        if reverse:
            if value is not None:
                return value
            else:
                return 'default'

        type_enum = self.shell.con.colors + ['default']
        syntax = '|'.join(type_enum)
        if value is None:
            if enum:
                return type_enum
            else:
                return syntax
        elif not value or value == 'default':
            return None
        elif value in type_enum:
            return value
        else:
            raise ValueError("Syntax error, '%s' is not %s"
                             % (value, syntax))

    def ui_type_colordefault(self, value=None, enum=False, reverse=False):
        '''
        UI parameter type helper for default color parameter type.
        @param value: Value to check against the type.
        @type value: anything
        @param enum: Has a meaning only if value is omitted. If set, returns
        a list of the possible values for the type, or None if this is not
        possible. If not set, returns a text description of the type format.
        @type enum: bool
        @param reverse: If set, translates an internal value to its UI
        string representation.
        @type reverse: bool
        @return: c.f. parameter enum description.
        @rtype: str|list|None
        @raise ValueError: If the value does not check ok againts the type.
        '''
        if reverse:
            if value is not None:
                return value
            else:
                return 'none'

        type_enum = self.shell.con.colors + ['none']
        syntax = '|'.join(type_enum)
        if value is None:
            if enum:
                return type_enum
            else:
                return syntax
        elif not value or value == 'none':
            return None
        elif value in type_enum:
            return value
        else:
            raise ValueError("Syntax error, '%s' is not %s"
                             % (value, syntax))


    # User interface get/set methods

    def ui_setgroup_global(self, parameter, value):
        '''
        This is the backend method for setting parameters in configuration
        group 'global'. It simply uses the Prefs() backend to store the global
        preferences for the shell. Some of these group parameters are shared
        using the same Prefs() object by the Log() and Console() classes, so
        this backend should not be changed without taking this into
        consideration.

        The parameters getting to us have already been type-checked and casted
        by the type-check methods registered in the config group via the ui set
        command, and their existence in the group has also been checked. Thus
        our job is minimal here. Also, it means that overhead when called with
        generated arguments (as opposed to user-supplied) gets minimal
        overhead, and allows setting new parameters without error.

        @param parameter: The parameter to set.
        @type parameter: str
        @param value: The value
        @type value: arbitrary
        '''
        self.shell.prefs[parameter] = value

    def ui_getgroup_global(self, parameter):
        '''
        This is the backend method for getting configuration parameters out of
        the global configuration group. It gets the values from the Prefs()
        backend. Eventual casting to str for UI display is handled by the ui
        get command, for symmetry with the pendant ui_setgroup method.
        Existence of the parameter in the group should have already been
        checked by the ui get command, so we go blindly about this. This might
        allow internal client code to get a None value if the parameter does
        not exist, as supported by Prefs().

        @param parameter: The parameter to get the value of.
        @type parameter: str
        @return: The parameter's value
        @rtype: arbitrary
        '''
        return self.shell.prefs[parameter]

    def ui_eval_param(self, ui_value, type, default):
        '''
        Evaluates a user-provided parameter value using a given type helper.
        If the parameter value is None, the default will be returned. If the
        ui_value does not check out with the type helper, and execution error
        will be raised.

        @param ui_value: The user provided parameter value.
        @type ui_value: str
        @param type: The ui_type to be used
        @type type: str
        @param default: The default value to return.
        @type default: any
        @return: The evaluated parameter value.
        @rtype: depends on type
        @raise ExecutionError: If evaluation fails.
        '''
        type_method = self.get_type_method(type)
        if ui_value is None:
            return default
        else:
            try:
                value = type_method(ui_value)
            except ValueError as msg:
                raise ExecutionError(msg)
            else:
                return value

    def get_type_method(self, type):
        '''
        Returns the type helper method matching the type name.
        '''
        return getattr(self, "%s%s" % (self.ui_type_method_prefix, type))

    # User interface commands

    def ui_command_set(self, group=None, **parameter):
        '''
        Sets one or more configuration parameters in the given group.
        The "global" group contains all global CLI preferences.
        Other groups are specific to the current path.

        Run with no parameter nor group to list all available groups, or
        with just a group name to list all available parameters within that
        group.

        Example: set global color_mode=true loglevel_console=info

        SEE ALSO
        ========
        get
        '''
        if group is None:
            self.shell.con.epy_write('''
                                     AVAILABLE CONFIGURATION GROUPS
                                     ==============================
                                     %s
                                     ''' % ' '.join(self.list_config_groups()))
        elif not parameter:
            if group not in self.list_config_groups():
                raise ExecutionError("Unknown configuration group: %s" % group)

            section = "%s CONFIG GROUP" % group.upper()
            underline1 = ''.ljust(len(section), '=')
            parameters = ''
            for p_name in self.list_group_params(group, writable=True):
                p_def = self.get_group_param(group, p_name)
                type_method = self.get_type_method(p_def['type'])
                p_name = "%s=%s" % (p_def['name'], p_def['type'])
                underline2 = ''.ljust(len(p_name), '-')
                parameters += '%s\n%s\n%s\n\n' \
                        % (p_name, underline2, p_def['description'])
            self.shell.con.epy_write('''%s\n%s\n%s\n'''
                                     % (section, underline1, parameters))

        elif group not in self.list_config_groups():
            raise ExecutionError("Unknown configuration group: %s" % group)

        for param, value in six.iteritems(parameter):
            if param not in self.list_group_params(group):
                raise ExecutionError("Unknown parameter %s in group '%s'."
                                     % (param, group))

            p_def = self.get_group_param(group, param)
            type_method = self.get_type_method(p_def['type'])
            if not p_def['writable']:
                raise ExecutionError("Parameter %s is read-only." % param)

            try:
                value = type_method(value)
            except ValueError as msg:
                raise ExecutionError("Not setting %s! %s" % (param, msg))

            group_setter = self.get_group_setter(group)
            group_setter(param, value)
            group_getter = self.get_group_getter(group)
            value = group_getter(param)
            value = type_method(value, reverse=True)
            self.shell.con.display("Parameter %s is now '%s'." % (param, value))

    def ui_complete_set(self, parameters, text, current_param):
        '''
        Parameter auto-completion method for user command set.
        @param parameters: Parameters on the command line.
        @type parameters: dict
        @param text: Current text of parameter being typed by the user.
        @type text: str
        @param current_param: Name of parameter to complete.
        @type current_param: str
        @return: Possible completions
        @rtype: list of str
        '''
        completions = []

        self.shell.log.debug("Called with params=%s, text='%s', current='%s'"
                             % (str(parameters), text, current_param))

        if current_param == 'group':
            completions = [group for group in self.list_config_groups()
                           if group.startswith(text)]
        elif 'group' in parameters:
            group = parameters['group']
            if group in self.list_config_groups():
                group_params = self.list_group_params(group, writable=True)
                if current_param in group_params:
                    p_def = self.get_group_param(group, current_param)
                    type_method = self.get_type_method(p_def['type'])
                    type_enum = type_method(enum=True)
                    if type_enum is not None:
                        type_enum = [item for item in type_enum
                                     if item.startswith(text)]
                        completions.extend(type_enum)
                else:
                    group_params = ([param + '=' for param in group_params
                                     if param.startswith(text)
                                     if param not in parameters])
                    if group_params:
                        completions.extend(group_params)

        if len(completions) == 1 and not completions[0].endswith('='):
            completions = [completions[0] + ' ']

        self.shell.log.debug("Returning completions %s." % str(completions))
        return completions

    def ui_command_get(self, group=None, *parameter):
        '''
        Gets the value of one or more configuration parameters in the given
        group.

        Run with no parameter nor group to list all available groups, or
        with just a group name to list all available parameters within that
        group.

        Example: get global color_mode loglevel_console

        SEE ALSO
        ========
        set
        '''
        if group is None:
            self.shell.con.epy_write('''
                                     AVAILABLE CONFIGURATION GROUPS
                                     ==============================
                                     %s
                                     ''' % ' '.join(self.list_config_groups()))
        elif not parameter:
            if group not in self.list_config_groups():
                raise ExecutionError("Unknown configuration group: %s" % group)

            section = "%s CONFIG GROUP" % group.upper()
            underline1 = ''.ljust(len(section), '=')
            parameters = ''
            params = [self.get_group_param(group, p_name)
                      for p_name in self.list_group_params(group)]
            for p_def in params:
                group_getter = self.get_group_getter(group)
                value = group_getter(p_def['name'])
                type_method = self.get_type_method(p_def['type'])
                value = type_method(value, reverse=True)
                param = "%s=%s" % (p_def['name'], value)
                if p_def['writable'] is False:
                    param += " [ro]"
                underline2 = ''.ljust(len(param), '-')
                parameters += '%s\n%s\n%s\n\n' \
                        % (param, underline2, p_def['description'])

            self.shell.con.epy_write('''%s\n%s\n%s\n'''
                                     % (section, underline1, parameters))

        elif group not in self.list_config_groups():
            raise ExecutionError("Unknown configuration group: %s" % group)

        for param in parameter:
            if param not in self.list_group_params(group):
                raise ExecutionError("No parameter '%s' in group '%s'."
                                     % (param, group))

            self.shell.log.debug("About to get the parameter's value.")
            group_getter = self.get_group_getter(group)
            value = group_getter(param)
            p_def = self.get_group_param(group, param)
            type_method = self.get_type_method(p_def['type'])
            value = type_method(value, reverse=True)
            if p_def['writable']:
                writable = ""
            else:
                writable = "[ro]"
            self.shell.con.display("%s=%s %s"
                                   % (param, value, writable))

    def ui_complete_get(self, parameters, text, current_param):
        '''
        Parameter auto-completion method for user command get.
        @param parameters: Parameters on the command line.
        @type parameters: dict
        @param text: Current text of parameter being typed by the user.
        @type text: str
        @param current_param: Name of parameter to complete.
        @type current_param: str
        @return: Possible completions
        @rtype: list of str
        '''
        completions = []

        self.shell.log.debug("Called with params=%s, text='%s', current='%s'"
                             % (str(parameters), text, current_param))

        if current_param == 'group':
            completions = [group for group in self.list_config_groups()
                           if group.startswith(text)]
        elif 'group' in parameters:
            group = parameters['group']
            if group in self.list_config_groups():
                group_params = ([param
                                 for param in self.list_group_params(group)
                                 if param.startswith(text)
                                 if param not in parameters])
                if group_params:
                    completions.extend(group_params)

        if len(completions) == 1 and not completions[0].endswith('='):
            completions = [completions[0] + ' ']

        self.shell.log.debug("Returning completions %s." % str(completions))
        return completions

    def ui_command_ls(self, path=None, depth=None):
        '''
        Display either the nodes tree relative to path or to the current node.

        PARAMETERS
        ==========

        path
        ----
        The path to display the nodes tree of. Can be an absolute path, a
        relative path or a bookmark.

        depth
        -----
        The depth parameter limits the maximum depth of the tree to display.
        If set to 0, then the complete tree will be displayed (the default).

        SEE ALSO
        ========
        cd bookmarks
        '''
        try:
            target = self.get_node(path)
        except ValueError as msg:
            raise ExecutionError(str(msg))

        if depth is None:
            depth = self.shell.prefs['tree_max_depth']
        try:
            depth = int(depth)
        except ValueError:
            raise ExecutionError('The tree depth must be a number.')

        if depth == 0:
            depth = None
        tree = self._render_tree(target, depth=depth)
        self.shell.con.display(tree)

    def _render_tree(self, root, margin=None, depth=None, do_list=False):
        '''
        Renders an ascii representation of a tree of ConfigNodes.
        @param root: The root node of the tree
        @type root: ConfigNode
        @param margin: Format of the left margin to use for children.
        True results in a pipe, and False results in no pipe.
        Used for recursion only.
        @type margin: list
        @param depth: The maximum depth of nodes to display, None means
        infinite.
        @type depth: None or int
        @param do_list: Return two lists, one with each line text
        representation, the other with the corresponding paths.
        @type do_list: bool
        @return: An ascii tree representation or (lines, paths).
        @rtype: str
        '''
        lines = []
        paths = []

        node_length = 2
        node_shift = 2
        level = root.path.rstrip('/').count('/')
        if margin is None:
            margin = [0]
            root_call = True
        else:
            root_call = False

        if do_list:
            color = None
        elif not level % 3:
            color = None
        elif not (level - 1) % 3:
            color = 'blue'
        else:
            color = 'magenta'

        if do_list:
            styles = None
        elif root_call:
            styles = ['bold', 'underline']
        else:
            styles = ['bold']

        if do_list:
            name = root.name
        else:
            name = self.shell.con.render_text(root.name, color, styles=styles)
        name_len = len(root.name)

        (description, is_healthy) = root.summary()
        if not description:
            if is_healthy is True:
                description = "OK"
            elif is_healthy is False:
                description = "ERROR"
            else:
                description = "..."

        description_len = len(description) + 3

        if do_list:
            summary = '['
        else:
            summary = self.shell.con.render_text(' [', styles=['bold'])

        if is_healthy is True:
            if do_list:
                summary += description
            else:
                summary += self.shell.con.render_text(description, 'green')
        elif is_healthy is False:
            if do_list:
                summary += description
            else:
                summary += self.shell.con.render_text(description, 'red',
                                                styles=['bold'])
        else:
            summary += description

        if do_list:
            summary += ']'
        else:
            summary += self.shell.con.render_text(']', styles=['bold'])

        def sorting_keys(s):
            m = re.search(r'(.*?)(\d+$)', str(s))
            if m:
                return (m.group(1), int(m.group(2)))
            else:
                return (str(s), 0)

        # Sort ending numbers numerically, so we get e.g. "lun1, lun2, lun10"
        # instead of "lun1, lun10, lun2".
        children = sorted(root.children, key=sorting_keys)
        line = ""

        for pipe in margin[:-1]:
            if pipe:
                line = line + "|".ljust(node_shift)
            else:
                line = line + ''.ljust(node_shift)

        if self.shell.prefs['tree_round_nodes']:
            node_char = 'o'
        else:
            node_char = '+'
        line += node_char.ljust(node_length, '-')
        line += ' '
        margin_len = len(line)

        pad = (self.shell.con.get_width() - 1
               - description_len
               - margin_len
               - name_len) * '.'
        if not do_list:
            pad = self.shell.con.render_text(pad, color)

        line += name
        if self.shell.prefs['tree_status_mode']:
            line += ' %s%s' % (pad, summary)

        lines.append(line)
        paths.append(root.path)

        if root_call \
           and not self.shell.prefs['tree_show_root'] \
           and not do_list:
            tree = ''
            for child in children:
                tree = tree + self._render_tree(child, [False], depth)
        else:
            tree = line + '\n'
            if depth is None or depth > 0:
                if depth is not None:
                    depth = depth - 1
                for i in range(len(children)):
                    margin.append(i<len(children)-1)
                    if do_list:
                        new_lines, new_paths = \
                                self._render_tree(children[i], margin, depth,
                                                  do_list=True)
                        lines.extend(new_lines)
                        paths.extend(new_paths)
                    else:
                        tree = tree \
                                + self._render_tree(children[i], margin, depth)
                    margin.pop()

        if root_call:
            if do_list:
                return (lines, paths)
            else:
                return tree[:-1]
        else:
            if do_list:
                return (lines, paths)
            else:
                return tree


    def ui_complete_ls(self, parameters, text, current_param):
        '''
        Parameter auto-completion method for user command ls.
        @param parameters: Parameters on the command line.
        @type parameters: dict
        @param text: Current text of parameter being typed by the user.
        @type text: str
        @param current_param: Name of parameter to complete.
        @type current_param: str
        @return: Possible completions
        @rtype: list of str
        '''
        if current_param == 'path':
            (basedir, slash, partial_name) = text.rpartition('/')
            basedir = basedir + slash
            target = self.get_node(basedir)
            names = [child.name for child in target.children]
            completions = []
            for name in names:
                num_matches = 0
                if name.startswith(partial_name):
                    num_matches += 1
                    if num_matches == 1:
                        completions.append("%s%s/" % (basedir, name))
                    else:
                        completions.append("%s%s" % (basedir, name))
            if len(completions) == 1:
                if not self.get_node(completions[0]).children:
                    completions[0] = completions[0].rstrip('/') + ' '

            # Bookmarks
            bookmarks = ['@' + bookmark for bookmark
                         in self.shell.prefs['bookmarks']
                         if ('@' + bookmark).startswith(text)]
            self.shell.log.debug("Found bookmarks %s." % str(bookmarks))
            if bookmarks:
                completions.extend(bookmarks)

            self.shell.log.debug("Completions are %s." % str(completions))
            return completions

        elif current_param == 'depth':
            if text:
                try:
                    int(text.strip())
                except ValueError:
                    self.shell.log.debug("Text is not a number.")
                    return []
            return [ text + number for number
                    in [str(num) for num in range(10)]
                    if (text + number).startswith(text)]

    def ui_command_cd(self, path=None):
        '''
        Change current path to path.

        The path is constructed just like a unix path, with "/" as separator
        character, "." for the current node, ".." for the parent node.

        Suppose the nodes tree looks like this:
           +-/
           +-a0      (1)
           | +-b0    (*)
           |  +-c0
           +-a1      (3)
             +-b0
              +-c0
               +-d0  (2)

        Suppose the current node is the one marked (*) at the beginning of all
        the following examples:
            - `cd ..` takes you to the node marked (1)
            - `cd .` makes you stay in (*)
            - `cd /a1/b0/c0/d0` takes you to the node marked (2)
            - `cd ../../a1` takes you to the node marked (3)
            - `cd /a1` also takes you to the node marked (3)
            - `cd /` takes you to the root node "/"
            - `cd /a0/b0/./c0/../../../a1/.` takes you to the node marked (3)

        You can also navigate the path history with "<" and ">":
            - `cd <` takes you back one step in the path history
            - `cd >` takes you one step forward in the path history

        SEE ALSO
        ========
        ls cd
        '''
        self.shell.log.debug("Changing current node to '%s'." % path)

        if self.shell.prefs['path_history'] is None:
            self.shell.prefs['path_history'] = [self.path]
            self.shell.prefs['path_history_index'] = 0

        # Go back in history to the last existing path
        if path == '<':
            if self.shell.prefs['path_history_index'] == 0:
                self.shell.log.info("Reached begining of path history.")
                return self
            exists = False
            while not exists:
                if self.shell.prefs['path_history_index'] > 0:
                    self.shell.prefs['path_history_index'] = \
                            self.shell.prefs['path_history_index'] - 1
                    index = self.shell.prefs['path_history_index']
                    path = self.shell.prefs['path_history'][index]
                    try:
                        target_node = self.get_node(path)
                    except ValueError:
                        pass
                    else:
                        exists = True
                else:
                    path = '/'
                    self.shell.prefs['path_history_index'] = 0
                    self.shell.prefs['path_history'][0] = '/'
                    exists = True
            self.shell.log.info('Taking you back to %s.' % path)
            return self.get_node(path)

        # Go forward in history
        if path == '>':
            if self.shell.prefs['path_history_index'] == \
               len(self.shell.prefs['path_history']) - 1:
                self.shell.log.info("Reached the end of path history.")
                return self
            exists = False
            while not exists:
                if self.shell.prefs['path_history_index'] \
                   < len(self.shell.prefs['path_history']) - 1:
                    self.shell.prefs['path_history_index'] = \
                            self.shell.prefs['path_history_index'] + 1
                    index = self.shell.prefs['path_history_index']
                    path = self.shell.prefs['path_history'][index]
                    try:
                        target_node = self.get_node(path)
                    except ValueError:
                        pass
                    else:
                        exists = True
                else:
                    path = self.path
                    self.shell.prefs['path_history_index'] \
                            = len(self.shell.prefs['path_history'])
                    self.shell.prefs['path_history'].append(path)
                    exists = True
            self.shell.log.info('Taking you back to %s.' % path)
            return self.get_node(path)

        # Use an urwid walker to select the path
        if path is None:
            lines, paths = self._render_tree(self.get_root(), do_list=True)
            start_pos = paths.index(self.path)
            selected = self._lines_walker(lines, start_pos=start_pos)
            path = paths[selected]

        # Normal path
        try:
            target_node = self.get_node(path)
        except ValueError as msg:
            raise ExecutionError(str(msg))

        index = self.shell.prefs['path_history_index']
        if target_node.path != self.shell.prefs['path_history'][index]:
            # Truncate the hostory to retain current path as last one
            self.shell.prefs['path_history'] = \
                    self.shell.prefs['path_history'][:index+1]
            # Append the new path and update the index
            self.shell.prefs['path_history'].append(target_node.path)
            self.shell.prefs['path_history_index'] = index + 1
        self.shell.log.debug("After cd, path history is: %s, index is %d"
                             % (str(self.shell.prefs['path_history']),
                                self.shell.prefs['path_history_index']))
        return target_node

    def _lines_walker(self, lines, start_pos):
        '''
        Using the curses urwid library, displays all lines passed as argument,
        and after allowing selection of one line using up, down and enter keys,
        returns its index.
        @param lines: The lines to display and select from.
        @type lines: list of str
        @param start_pos: The index of the line to select initially.
        @type start_pos: int
        @return: the index of the selected line.
        @rtype: int
        '''
        import urwid

        palette = [('header', 'white', 'black'),
                   ('reveal focus', 'black', 'yellow', 'standout')]

        content = urwid.SimpleListWalker(
            [urwid.AttrMap(w, None, 'reveal focus')
             for w in [urwid.Text(line) for line in lines]])

        listbox = urwid.ListBox(content)
        frame = urwid.Frame(listbox)

        def handle_input(input, raw):
            for key in input:
                widget, pos = content.get_focus()
                if key == 'up':
                    if pos > 0:
                        content.set_focus(pos-1)
                elif key == 'down':
                    try:
                        content.set_focus(pos+1)
                    except IndexError:
                        pass
                elif key == 'enter':
                    raise urwid.ExitMainLoop()

        content.set_focus(start_pos)
        loop = urwid.MainLoop(frame, palette, input_filter=handle_input)
        loop.run()
        return listbox.focus_position

    def ui_complete_cd(self, parameters, text, current_param):
        '''
        Parameter auto-completion method for user command cd.
        @param parameters: Parameters on the command line.
        @type parameters: dict
        @param text: Current text of parameter being typed by the user.
        @type text: str
        @param current_param: Name of parameter to complete.
        @type current_param: str
        @return: Possible completions
        @rtype: list of str
        '''
        if current_param == 'path':
            completions = self.ui_complete_ls(parameters, text, current_param)
            completions.extend([nav for nav in ['<', '>']
                                if nav.startswith(text)])
            return completions

    def ui_command_help(self, topic=None):
        '''
        Displays the manual page for a topic, or list available topics.
        '''
        commands = self.list_commands()
        if topic is None:
            msg = self.shell.con.dedent(self.help_intro)
            msg += self.shell.con.dedent('''

                                   AVAILABLE COMMANDS
                                   ==================
                                   The following commands are available in the
                                   current path:

                                   ''')
            for command in commands:
                msg += "  - %s\n" % self.get_command_syntax(command)[0]
            self.shell.con.epy_write(msg)
            return

        if topic not in commands:
            raise ExecutionError("Cannot find help topic %s." % topic)

        syntax, comments, defaults = self.get_command_syntax(topic)
        msg = self.shell.con.dedent('''
                             SYNTAX
                             ======
                             %s

                             ''' % syntax)
        for comment in comments:
            msg += comment + '\n'

        if defaults:
            msg += self.shell.con.dedent('''
                                  DEFAULT VALUES
                                  ==============
                                  %s

                                  ''' % defaults)
        msg += self.shell.con.dedent('''
                              DESCRIPTION
                              ===========
                              ''')
        msg += self.get_command_description(topic)
        msg += "\n"
        self.shell.con.epy_write(msg)

    def ui_complete_help(self, parameters, text, current_param):
        '''
        Parameter auto-completion method for user command help.
        @param parameters: Parameters on the command line.
        @type parameters: dict
        @param text: Current text of parameter being typed by the user.
        @type text: str
        @param current_param: Name of parameter to complete.
        @type current_param: str
        @return: Possible completions
        @rtype: list of str
        '''
        if current_param == 'topic':
            # TODO Add other types of topics
            topics = self.list_commands()
            completions = [topic for topic in topics
                           if topic.startswith(text)]
        else:
            completions = []

        if len(completions) == 1:
            return [completions[0] + ' ']
        else:
            return completions

    def ui_command_exit(self):
        '''
        Exits the command line interface.
        '''
        return 'EXIT'

    def ui_command_bookmarks(self, action, bookmark=None):
        '''
        Manage your bookmarks.

        Note that you can also access your bookmarks with the
        `cd` command. For instance, the following commands
        are equivalent:
            - `cd @mybookmark`
            - `bookmarks go mybookmark``

        You can also use bookmarks anywhere where you would use
        a normal path:
            - `@mybookmark ls` performs the `ls` command
            in the bookmarked path.
            - `ls @mybookmark` shows you the objects tree from
            the bookmarked path.


        PARAMETERS
        ==========

        action
        ------
        The "action" parameter is one of:
            - `add` adds the current path to your bookmarks.
            - `del` deletes a bookmark.
            - `go` takes you to a bookmarked path.
            - `show` shows you all your bookmarks.

        bookmark
        --------
        This is the name of the bookmark.

        SEE ALSO
        ========
        ls cd
        '''
        if action == 'add' and bookmark:
            if bookmark in self.shell.prefs['bookmarks']:
                raise ExecutionError("Bookmark %s already exists." % bookmark)

            self.shell.prefs['bookmarks'][bookmark] = self.path
            # No way Prefs is going to account for that :-(
            self.shell.prefs.save()
            self.shell.log.info("Bookmarked %s as %s."
                                % (self.path, bookmark))
        elif action == 'del' and bookmark:
            if bookmark not in self.shell.prefs['bookmarks']:
                raise ExecutionError("No such bookmark %s." % bookmark)

            del self.shell.prefs['bookmarks'][bookmark]
            # No way Prefs is going to account for that deletion
            self.shell.prefs.save()
            self.shell.log.info("Deleted bookmark %s." % bookmark)
        elif action == 'go' and bookmark:
            if bookmark not in self.shell.prefs['bookmarks']:
                raise ExecutionError("No such bookmark %s." % bookmark)
            return self.ui_command_cd(
                self.shell.prefs['bookmarks'][bookmark])
        elif action == 'show':
            bookmarks = self.shell.con.dedent('''
                                              BOOKMARKS
                                              =========

                                              ''')
            if not self.shell.prefs['bookmarks']:
                bookmarks += "No bookmarks yet.\n"
            else:
                for (bookmark, path) \
                        in six.iteritems(self.shell.prefs['bookmarks']):
                    if len(bookmark) == 1:
                        bookmark += '\0'
                    underline = ''.ljust(len(bookmark), '-')
                    bookmarks += "%s\n%s\n%s\n\n" % (bookmark, underline, path)
            self.shell.con.epy_write(bookmarks)
        else:
            raise ExecutionError("Syntax error, see 'help bookmarks'.")

    def ui_complete_bookmarks(self, parameters, text, current_param):
        '''
        Parameter auto-completion method for user command bookmarks.
        @param parameters: Parameters on the command line.
        @type parameters: dict
        @param text: Current text of parameter being typed by the user.
        @type text: str
        @param current_param: Name of parameter to complete.
        @type current_param: str
        @return: Possible completions
        @rtype: list of str
        '''
        if current_param == 'action':
            completions = [action for action in ['add', 'del', 'go', 'show']
                           if action.startswith(text)]
        elif current_param == 'bookmark':
            if 'action' in parameters:
                if parameters['action'] not in ['show', 'add']:
                    completions = [mark for mark
                                   in self.shell.prefs['bookmarks']
                                   if mark.startswith(text)]
        else:
            completions = []

        if len(completions) == 1:
            return [completions[0] + ' ']
        else:
            return completions

    def ui_command_pwd(self):
        '''
        Displays the current path.

        SEE ALSO
        ========
        ls cd
        '''
        self.shell.con.display(self.path)

    # Private methods

    def __str__(self):
        if self.is_root():
            return '/'
        else:
            return self.name

    def _get_parent(self):
        '''
        Get this node's parent.
        @return: The node's parent.
        @rtype: ConfigNode
        '''
        return self._parent

    def _get_name(self):
        '''
        @return: The node's name.
        @rtype: str
        '''
        return self._name

    def _set_name(self, name):
        '''
        Sets the node's name.
        '''
        self._name = name

    def _get_path(self):
        '''
        @returns: The absolute path for this node.
        @rtype: str
        '''
        subpath = self._path_separator + self.name
        if self.is_root():
            return self._path_separator
        elif self._parent.is_root():
            return subpath
        else:
            return self._parent.path + subpath

    def _list_children(self):
        '''
        Lists the children of this node.
        @return: The set of children nodes.
        @rtype: set of ConfigNode
        '''
        return self._children

    def _get_shell(self):
        '''
        Gets the shell attached to ConfigNode tree.
        '''
        if self.is_root():
            return self._shell
        else:
            return self.get_root().shell

    # Public methods

    def summary(self):
        '''
        Returns a tuple with a status/description string for this node and a
        health flag, to be displayed along the node's name in object trees,
        etc.
        @returns: (description, is_healthy)
        @rtype: (str, bool or None)
        '''
        return ('', None)

    def execute_command(self, command, pparams=[], kparams={}):
        '''
        Execute a user command on the node. This works by finding out which is
        the support command method, using ConfigNode naming convention:
        The support method's name is 'PREFIX_COMMAND', where PREFIX is defined
        by ConfigNode.ui_command_method_prefix and COMMAND is the commands's
        name as seen by the user.
        @param command: Name of the command.
        @type command: str
        @param pparams: The positional parameters to use.
        @type pparams: list
        @param kparams: The keyword=value parameters to use.
        @type kparams: dict
        @return: The support method's return value.
        See ConfigShell._execute_command() for expected return values and how
        they are interpreted by ConfigShell.
        @rtype: str or ConfigNode or None
        '''
        self.shell.log.debug("Executing command %s " % command
                             + "with pparams %s " % pparams
                             + "and kparams %s." % kparams)

        if command in self.list_commands():
            method = self.get_command_method(command)
        else:
            raise ExecutionError("Command not found %s" % command)

        self.assert_params(method, pparams, kparams)
        return method(*pparams, **kparams)

    def assert_params(self, method, pparams, kparams):
        '''
        Checks that positional and keyword parameters match a method
        definition, or raise an ExecutionError.
        @param method: The method to check call signature against.
        @type method: method
        @param pparams: The positional parameters.
        @type pparams: list
        @param kparams: The keyword parameters.
        @type kparams: dict
        @raise ExecutionError: When the check fails.
        '''
        spec = inspect.getargspec(method)
        args = spec.args[1:]
        pp = spec.varargs
        kw = spec.keywords

        if spec.defaults is None:
            nb_opt_params = 0
        else:
            nb_opt_params = len(spec.defaults)
        nb_max_params = len(args)
        nb_min_params = nb_max_params - nb_opt_params

        req_params = args[:nb_min_params]
        opt_params = args[nb_min_params:]

        unexpected_keywords = sorted(set(kparams) - set(args))
        missing_params = sorted(set(args[len(pparams):])
                                - set(opt_params)
                                - set(kparams.keys()))

        nb_params = len(pparams) + len(kparams)
        nb_standard_params = len(pparams) \
                + len([param for param in kparams if param in args])
        nb_extended_params = nb_params - nb_standard_params

        self.shell.log.debug("Min params: %d" % nb_min_params)
        self.shell.log.debug("Max params: %d" % nb_max_params)
        self.shell.log.debug("Required params: %s" % ", ".join(req_params))
        self.shell.log.debug("Optional params: %s" % ", ".join(opt_params))
        self.shell.log.debug("Got %s standard params." % nb_standard_params)
        self.shell.log.debug("Got %s extended params." %  nb_extended_params)
        self.shell.log.debug("Variable positional params: %s" % pp)
        self.shell.log.debug("Variable keyword params: %s" % kw)

        if len(missing_params) == 1:
            raise ExecutionError(
                "Missing required parameter %s"
                % missing_params[0])
        elif missing_params:
            raise ExecutionError(
                "Missing required parameters %s"
                % ", ".join("'%s'" % missing for missing in missing_params))

        if spec.keywords is None:
            if len(unexpected_keywords) == 1:
                raise ExecutionError(
                    "Unexpected keyword parameter '%s'."
                    % unexpected_keywords[0])
            elif unexpected_keywords:
                raise ExecutionError(
                    "Unexpected keyword parameters %s."
                    % ", ".join("'%s'" % kw for kw in unexpected_keywords))
        all_params = args[:len(pparams)]
        all_params.extend(kparams.keys())
        for param in all_params:
            if all_params.count(param) > 1:
                raise ExecutionError(
                    "Duplicate parameter %s."
                    % param)

        if nb_opt_params == 0 \
           and nb_standard_params != nb_min_params \
           and pp is None:
            raise ExecutionError(
                "Got %d positionnal parameters, expected exactly %d."
                % (nb_standard_params, nb_min_params))

        if nb_standard_params > nb_max_params and pp is None:
            raise ExecutionError(
                "Got %d positionnal parameters, expected at most %d."
                % (nb_standard_params, nb_max_params))

    def list_commands(self):
        '''
        @return: The list of user commands available for this node.
        @rtype: list of str
        '''
        prefix = self.ui_command_method_prefix
        prefix_len = len(prefix)
        return tuple([name[prefix_len:] for name in dir(self)
                if name.startswith(prefix) and name != prefix
                and inspect.ismethod(getattr(self, name))])

    def get_group_getter(self, group):
        '''
        @param group: A valid configuration group
        @type group: str
        @return: The getter method for the configuration group.
        @rtype: method object
        '''
        prefix = self.ui_getgroup_method_prefix
        return getattr(self, '%s%s' % (prefix, group))

    def get_group_setter(self, group):
        '''
        @param group: A valid configuration group
        @type group: str
        @return: The setter method for the configuration group.
        @rtype: method object
        '''
        prefix = self.ui_setgroup_method_prefix
        return getattr(self, '%s%s' % (prefix, group))

    def get_command_method(self, command):
        '''
        @param command: The command to get the method for.
        @type command: str
        @return: The user command support method.
        @rtype: method
        @raise ValueError: If the command is not found.
        '''
        prefix = self.ui_command_method_prefix
        if command in self.list_commands():
            return getattr(self, '%s%s' % (prefix, command))
        else:
            self.shell.log.debug('No command named %s in %s (%s)'
                                 % (command, self.name, self.path))
            raise ValueError('No command named "%s".' % command)

    def get_completion_method(self, command):
        '''
        @return: A user command's completion method or None.
        @rtype: method or None
        @param command: The command to get the completion method for.
        @type command: str
        '''
        prefix = self.ui_complete_method_prefix
        try:
            method = getattr(self, '%s%s' % (prefix, command))
        except AttributeError:
            return None
        else:
            return method

    def get_command_description(self, command):
        '''
        @return: An description string for a user command.
        @rtype: str
        @param command: The command to describe.
        @type command: str
        '''
        doc = self.get_command_method(command).__doc__
        if not doc:
            doc = "No description available."
        return self.shell.con.dedent(doc)

    def get_command_syntax(self, command):
        '''
        @return: A list of formatted syntax descriptions for the command:
            - (syntax, comments, default_values)
            - syntax is the syntax definition line.
            - comments is a list of additionnal comments about the syntax.
            - default_values is a string with the default parameters values.
        @rtype: (str, [str...], str)
        @param command: The command to document.
        @type command: str
        '''
        method = self.get_command_method(command)
        parameters, args, kwargs, default = inspect.getargspec(method)
        parameters = parameters[1:]
        if default is None:
            num_defaults = 0
        else:
            num_defaults = len(default)

        if num_defaults != 0:
            required_parameters = parameters[:-num_defaults]
            optional_parameters = parameters[-num_defaults:]
        else:
            required_parameters = parameters
            optional_parameters = []

        self.shell.log.debug("Required: %s" % str(required_parameters))
        self.shell.log.debug("Optional: %s" % str(optional_parameters))

        syntax = "%s " % command

        required_parameters_str = ''
        for param in required_parameters:
            required_parameters_str += "%s " % param
        syntax += required_parameters_str

        optional_parameters_str = ''
        for param in optional_parameters:
            optional_parameters_str += "[%s] " % param
        syntax += optional_parameters_str

        comments = []
        if args is not None:
            syntax += "[%s...] " % args
        if kwargs is not None:
            syntax += "[%s=value...] " % (kwargs)

        default_values = ''
        if num_defaults > 0:
            for index, param in enumerate(optional_parameters):
                if default[index] is not None:
                    default_values += "%s=%s " % (param, str(default[index]))

        return syntax, comments, default_values

    def get_command_signature(self, command):
        '''
        Get a command's signature.
        @param command: The command to get the signature of.
        @type command: str
        @return: (parameters, free_pparams, free_kparams) where parameters is a
        list of all the command's parameters and free_pparams and free_kparams
        booleans set to True is the command accepts an arbitrary number of,
        respectively, pparams and kparams.
        @rtype: ([str...], bool, bool)
        '''
        method = self.get_command_method(command)
        parameters, args, kwargs, default = inspect.getargspec(method)
        parameters = parameters[1:]
        if args is not None:
            free_pparams = args
        else:
            free_pparams = False
        if kwargs is not None:
            free_kparams = kwargs
        else:
            free_kparams = False
        self.shell.log.debug("Signature is %s, %s, %s."
                             % (str(parameters),
                                str(free_pparams),
                                str(free_kparams)))
        return parameters, free_pparams, free_kparams

    def get_root(self):
        '''
        @return: The root node of the nodes tree.
        @rtype: ConfigNode
        '''
        if self.is_root():
            return self
        else:
            return self.parent.get_root()

    def define_config_group_param(self, group, param, type,
                                  description=None, writable=True):
        '''
        Helper to define configuration group parameters.
        @param group: The configuration group to add the parameter to.
        @type group: str
        @param param: The new parameter name.
        @type param: str
        @param description: Optional description string.
        @type description: str
        @param writable: Whether or not this would be a rw or ro parameter.
        @type writable: bool
        '''
        if group not in self._configuration_groups:
            self._configuration_groups[group] = {}

        if description is None:
            description = "The %s %s parameter." % (param, group)

        # Fail early if the type and set/get helpers don't exist
        self.get_type_method(type)
        self.get_group_getter(group)
        if writable:
            self.get_group_setter(group)

        self._configuration_groups[group][param] = \
                [type, description, writable]

    def list_config_groups(self):
        '''
        Lists the configuration group names.
        '''
        return self._configuration_groups.keys()

    def list_group_params(self, group, writable=None):
        '''
        Lists the parameters from group matching the optional param, writable
        and type supplied (if none is supplied, returns all group parameters.
        @param group: The group to list parameters of.
        @type group: str
        @param writable: Optional writable flag filter.
        @type writable: bool
        '''
        if group not in self.list_config_groups():
            return []
        else:
            params = []
            for p_name, p_def in six.iteritems(self._configuration_groups[group]):
                (p_type, p_description, p_writable) = p_def
                if writable is not None and p_writable != writable:
                    continue
                params.append(p_name)

            params.sort()
            return params

    def get_group_param(self, group, param):
        '''
        @param group: The configuration group to retreive the parameter from.
        @type group: str
        @param param: The parameter name.
        @type param: str
        @return: A dictionnary for the requested group parameter, with
        name, writable, description, group and type fields.
        @rtype: dict
        @raise ValueError: If the parameter or group does not exist.
        '''
        if group not in self.list_config_groups():
            raise ValueError("Not such configuration group %s" % group)
        if param not in self.list_group_params(group):
            raise ValueError("Not such parameter %s in configuration group %s"
                             % (param, group))
        (p_type, p_description, p_writable) = \
                self._configuration_groups[group][param]

        return dict(name=param, group=group, type=p_type,
                    description=p_description, writable=p_writable)

    shell = property(_get_shell,
                     doc="Gets the shell attached to ConfigNode tree.")

    name = property(_get_name, _set_name,
                    doc="Gets or sets the node's name.")

    path = property(_get_path,
                   doc="Gets the node's path.")

    children = property(_list_children,
                        doc="Lists the node's children.")

    parent = property(_get_parent,
                      doc="Gets the node's parent.")

    def is_root(self):
        '''
        @return: Wether or not we are a root node.
        @rtype: bool
        '''
        if self._parent is None:
            return True
        else:
            return False

    def get_child(self, name):
        '''
        @param name: The child's name.
        @type name: str
        @return: Our child named by name.
        @rtype: ConfigNode
        @raise ValueError: If there is no child named by name.
        '''
        for child in self._children:
            if child.name == name:
                return child
        else:
            raise ValueError("No such path %s/%s"
                             % (self.path.rstrip('/'), name))

    def remove_child(self, child):
        '''
        Removes a child from our children's list.
        @param child: The child to remove.
        @type child: ConfigNode
        '''
        self._children.remove(child)

    def get_node(self, path):
        '''
        Looks up a node by path in the nodes tree.
        @param path: The node's path.
        @type path: str
        @return: The node that has the given path.
        @rtype: ConfigNode
        @raise ValueError: If there is no node with that path.
        '''
        def adjacent_node(name):
            '''
            Returns an adjacent node or ourself.
            '''
            if name == self._path_current:
                return self
            elif name == self._path_previous:
                if self._parent is not None:
                    return self._parent
                else:
                    return self
            else:
                return self.get_child(name)


        # Cleanup the path
        if path is None or path == '':
            path = '.'

        # Is it a bookmark ?
        if path.startswith('@'):
            bookmark = path.lstrip('@').strip()
            if bookmark in self.shell.prefs['bookmarks']:
                path = self.shell.prefs['bookmarks'][bookmark]
            else:
                raise ValueError("No such bookmark %s" % bookmark)

        # More cleanup
        path = re.sub('%s+' % self._path_separator, self._path_separator, path)
        if len(path) > 1:
            path = path.rstrip(self._path_separator)
        self.shell.log.debug("Looking for path '%s'" % path)


        # Absolute path - make relative and pass on to root node
        if path.startswith(self._path_separator):
            next_node = self.get_root()
            next_path = path.lstrip(self._path_separator)
            if next_path:
                return next_node.get_node(next_path)
            else:
                return next_node

        # Relative path
        if self._path_separator in path:
            next_node_name, next_path = path.split(self._path_separator, 1)
            next_node = adjacent_node(next_node_name)
            return next_node.get_node(next_path)

        # Path is just one of our children
        return adjacent_node(path)
