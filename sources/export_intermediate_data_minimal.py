import sys
import os
import glob
import argparse

import json
import codecs
import re
import sys
import logging
import copy
import collections

class LogData(object):
    log_instance = logging.Logger('default')


def getlog():
    """Get the global log setup by the __main__ script"""

    if LogData.log_instance is None:
        setuplog()

    return LogData.log_instance


def setuplog(output_file=None):
    """Setup the global log. Add more specific settings as you please."""

    log = LogData.log_instance
    if LogData.log_instance is None:
        log = logging.Logger()
    log.name = 'main'

    # Format
    formatter = logging.Formatter('%(asctime)s %(levelname)8s %(module)10s.py@%(lineno)-3d   %(message)s')

    # Output to std out
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.formatter = formatter
    log.addHandler(stdout_handler)

    # Output to file
    if output_file is not None:
        file_handler = logging.FileHandler(output_file, 'w')
        file_handler.formatter = formatter
        log.addHandler(file_handler)

    LogData.log_instance = log
    return LogData.log_instance

log = getlog()

# Utility path vars to common directories
DIR_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

DIR_SOURCES = os.path.normpath(os.path.join(DIR_ROOT, "sources"))
DIR_CONTENT_GENERATED = os.path.normpath(os.path.join(DIR_ROOT, "content", "generated"))
DIR_CONTENT_KEYBOARDS = os.path.normpath(os.path.join(DIR_ROOT, "content", "keyboards"))

CONTENT_APPS_JS_FILE = os.path.normpath(os.path.join(DIR_ROOT, "content", "generated", "apps.js"))

OS_WINDOWS = 'windows'
OS_MAC = 'mac'
OS_LINUX = 'linux'

VALID_OS_NAMES = [OS_WINDOWS, OS_MAC, OS_LINUX]


class DataContainer(object):
    VALID_NAME_LOOKUP = {
        u'§': ['SECTION'],
        u'!': ['EXCLAMATION'],
        u'@': ['AT'],
        u'£': ['POUND'],
        u'$': ['DOLLAR'],
        u'%': ['PERCENT'],
        u'^': ['CARET'],
        u'&': ['AMPERSAND'],
        u'(': ['LEFT_PARENTHESIS'],
        u')': ['RIGHT_PARENTHESIS'],
        u'_': ['UNDERSCORE'],
        u'[': ['LEFT_BRACKET'],
        u']': ['RIGHT_BRACKET'],
        u'{': ['LEFT_BRACE'],
        u'}': ['RIGHT_BRACE'],
        u';': ['SEMICOLON'],
        u':': ['COLON'],
        u'\'': ['SINGLE_QUOTE'],
        u'‘': ['SINGLE_QUOTE'],
        u'"': ['DOUBLE_QUOTE'],
        u'\\': ['BACKSLASH'],
        u'|': ['VERTICAL_BAR'],
        u'?': ['QUESTION_MARK'],
        u'<': ['LESSTHAN'],
        u'>': ['MORETHAN'],
        u',': ['COMMA'],
        u'`': ['ACCENT_GRAVE'],
        u'~': ['TILDE'],
        u'#': ['HASH'],
        u'±': ['PLUSMINUS'],

        # Numbers and maths
        u'number': ['ONE', 'NUMPAD_ONE', 'TWO', 'NUMPAD_TWO', 'THREE', 'NUMPAD_THREE', 'FOUR', 'NUMPAD_FOUR',
                    'FIVE', 'NUMPAD_FIVE', 'SIX', 'NUMPAD_SIX', 'SEVEN', 'NUMPAD_SEVEN', 'EIGHT', 'NUMPAD_EIGHT',
                    'NINE', 'NUMPAD_NINE','ZERO', 'NUMPAD_ZERO'],
        u'number keys': ['ONE', 'NUMPAD_ONE', 'TWO', 'NUMPAD_TWO', 'THREE', 'NUMPAD_THREE', 'FOUR', 'NUMPAD_FOUR',
                         'FIVE', 'NUMPAD_FIVE', 'SIX', 'NUMPAD_SIX', 'SEVEN', 'NUMPAD_SEVEN', 'EIGHT', 'NUMPAD_EIGHT',
                         'NINE', 'NUMPAD_NINE','ZERO', 'NUMPAD_ZERO'],
        u'1': ['ONE', 'NUMPAD_ONE'],
        u'2': ['TWO', 'NUMPAD_TWO'],
        u'3': ['THREE', 'NUMPAD_THREE'],
        u'4': ['FOUR', 'NUMPAD_FOUR'],
        u'5': ['FIVE', 'NUMPAD_FIVE'],
        u'6': ['SIX', 'NUMPAD_SIX'],
        u'7': ['SEVEN', 'NUMPAD_SEVEN'],
        u'8': ['EIGHT', 'NUMPAD_EIGHT'],
        u'9': ['NINE', 'NUMPAD_NINE'],
        u'0': ['ZERO', 'NUMPAD_ZERO'],
        u'-': ['MINUS', 'NUMPAD_MINUS'],
        u'–': ['MINUS', 'NUMPAD_MINUS'],
        u'+': ['PLUS', 'NUMPAD_PLUS'],
        u'=': ['EQUAL', 'NUMPAD_EQUAL'],
        u'*': ['ASTERISK', 'NUMPAD_ASTERISK'],
        u'/': ['SLASH', 'NUMPAD_SLASH'],
        u'.': ['PERIOD', 'NUMPAD_PERIOD'],
        u'numpad_0': ['NUMPAD_ZERO'],
        u'numpad_1': ['NUMPAD_ONE'],
        u'numpad_2': ['NUMPAD_TWO'],
        u'numpad_3': ['NUMPAD_THREE'],
        u'numpad_4': ['NUMPAD_FOUR'],
        u'numpad_5': ['NUMPAD_FIVE'],
        u'numpad_6': ['NUMPAD_SIX'],
        u'numpad_7': ['NUMPAD_SEVEN'],
        u'numpad_8': ['NUMPAD_EIGHT'],
        u'numpad_9': ['NUMPAD_NINE'],
        u'numpad 0': ['NUMPAD_ZERO'],
        u'numpad 1': ['NUMPAD_ONE'],
        u'numpad 2': ['NUMPAD_TWO'],
        u'numpad 3': ['NUMPAD_THREE'],
        u'numpad 4': ['NUMPAD_FOUR'],
        u'numpad 5': ['NUMPAD_FIVE'],
        u'numpad 6': ['NUMPAD_SIX'],
        u'numpad 7': ['NUMPAD_SEVEN'],
        u'numpad 8': ['NUMPAD_EIGHT'],
        u'numpad 9': ['NUMPAD_NINE'],
        u'numpad -': ['NUMPAD_MINUS'],
        u'numpad +': ['NUMPAD_PLUS'],
        u'numpad =': ['NUMPAD_EQUAL'],
        u'numpad *': ['NUMPAD_ASTERISK'],
        u'numpad /': ['NUMPAD_SLASH'],
        u'numpad .': ['NUMPAD_PERIOD'],
        u'numpad enter': ['NUMPAD_ENTER'],
        u'numpad return': ['NUMPAD_ENTER'],

        # Non-English keyboard characters
        # Reference used: http://www.ascii.cl/htmlcodes.htm

        u'¡': ['INVERTED_EXCLAMATION'],
        u'¢': ['CENT'],
        u'¤': ['CURRENCY'],
        u'¥': ['YEN'],
        u'¦': ['BROKEN_VBAR'],
        u'¨': ['UMLAUT'],
        u'©': ['COPYRIGHT'],
        u'ª': ['FEMININ_ORDINAL'],
        u'«': ['LEFT_DOUBLE_ANGLE_QUOTES'],
        u'¬': ['NOT_SIGN'],
        u'®': ['TRADEMARK'],
        u'¯': ['OVERLINE'],

        u'°': ['DEGREE_SIGN'],
        u'²': ['SQUARED_SIGN'],
        u'³': ['CUBED_SIGN'],
        u'´': ['ACCENT_ACUTE'],
        u'µ': ['MICRO_SIGN'],
        u'¶': ['PARAGRAPH_SIGN'],
        u'·': ['GEORGIAN_COMMA'],
        u'¸': ['CEDILLA_SIGN'],
        u'¹': ['SUPERSCRIPT_ONE'],
        u'º': ['MASCULIN_ORDINAL_SIGN'],
        u'»': ['RIGHT_DOUBLE_ANGLE_QUOTES'],
        u'¼': ['ONE_QUARTER_SIGN'],
        u'½': ['ONE_HALF_SIGN'],
        u'¾': ['ONE_THIRD_SIGN'],
        u'¿': ['INVERTED_QUESTION_MARK'],

        u'À': ['CAP_A_GRAVE'],
        u'Á': ['CAP_A_ACUTE'],
        u'Â': ['CAP_A_CIRC'],
        u'Ã': ['CAP_A_TILDE'],
        u'Ä': ['CAP_A_UML'],
        u'Å': ['CAP_A_RING'],
        u'Æ': ['CAP_AE'],
        u'Ç': ['CAP_C_CEDIL'],
        u'È': ['CAP_E_GRAVE'],
        u'É': ['CAP_E_ACUTE'],
        u'Ê': ['CAP_E_CIRC'],
        u'Ë': ['CAP_E_UML'],
        u'Ì': ['CAP_I_GRAVE'],
        u'Í': ['CAP_I_ACUTE'],
        u'Î': ['CAP_I_CIRC'],
        u'Ï': ['CAP_I_UML'],

        u'Ð': ['CAP_ETH'],
        u'Ñ': ['CAP_N_TILDE'],
        u'Ò': ['CAP_O_GRAVE'],
        u'Ó': ['CAP_O_ACUTE'],
        u'Ô': ['CAP_O_CIRC'],
        u'Õ': ['CAP_O_TILDE'],
        u'Ö': ['CAP_O_UML'],
        u'×': ['TIMES'],
        u'Ø': ['CAP_O_SLASH'],
        u'Ù': ['CAP_U_GRAVE'],
        u'Ú': ['CAP_U_ACUTE'],
        u'Û': ['CAP_U_CIRC'],
        u'Ü': ['CAP_U_UML'],
        u'Ý': ['CAP_Y_ACUTE'],
        u'Þ': ['CAP_THORN'],
        u'ß': ['SZLIG'],

        u'à': ['A_GRAVE'],
        u'á': ['A_ACUTE'],
        u'â': ['A_CIRC'],
        u'ã': ['A_TILDE'],
        u'ä': ['A_UML'],
        u'å': ['A_RING'],
        u'æ': ['AE'],
        u'ç': ['C_CEDIL'],
        u'è': ['E_GRAVE'],
        u'é': ['E_ACUTE'],
        u'ê': ['E_CIRC'],
        u'ë': ['E_UML'],
        u'ì': ['I_GRAVE'],
        u'í': ['I_ACUTE'],
        u'î': ['I_CIRC'],
        u'ï': ['I_UML'],

        u'ð': ['ETH'],
        u'ñ': ['N_TILDE'],
        u'ò': ['O_GRAVE'],
        u'ó': ['O_ACUTE'],
        u'ô': ['O_CIRC'],
        u'õ': ['O_TILDE'],
        u'ö': ['O_UML'],
        u'÷': ['DIVIDE'],
        u'ø': ['O_SLASH'],
        u'ù': ['U_GRAVE'],
        u'ú': ['U_ACUTE'],
        u'û': ['U_CIRC'],
        u'ü': ['U_UML'],
        u'ý': ['Y_ACUTE'],
        u'þ': ['THORN'],
        u'ÿ': ['Y_UML'],

        u'Œ': ['CAP_OE'],
        u'œ': ['OE'],
        u'Š': ['CAP_S_CARON'],
        u'š': ['S_CARON'],
        u'Ÿ': ['CAP_Y_UML'],
        u'ƒ': ['FUNCTION'],

        u'—': ['MINUS'],
        u'’': ['SINGLE_QUOTE_RIGHT'],
        u'“': ['DOUBLE_QUOTE'],  # this is usually what is meant
        u'”': ['DOUBLE_QUOTE_RIGHT'],
        u'„': ['DOUBLE_QUOTE_LOW'],
        u'†': ['DAGGER'],
        u'‡': ['DOUBLE_DAGGER'],
        u'•': ['BULLET'],
        u'…': ['ELLIPSIS'],
        u'‰': ['PER_THOUSAND'],
        u'€': ['EURO'],
        u'™': ['TRADEMARK'],

        # Other non-character names

        u'shift': ['SHIFT'],
        u'left_shift': ['SHIFT'],
        u'right_shift': ['SHIFT'],
        u'ctrl': ['CONTROL'],
        u'left_ctrl': ['CONTROL'],
        u'right_ctrl': ['CONTROL'],
        u'alt': ['ALT'],
        u'left_alt': ['ALT'],
        u'right_alt': ['ALT'],
        u'option': ['ALT'],
        u'opt': ['ALT'],
        u'left_opt': ['ALT'],
        u'right_opt': ['ALT'],
        u'cmd': ['COMMAND'],
        u'command': ['COMMAND'],
        u'left_cmd': ['COMMAND'],
        u'right_cmd': ['COMMAND'],
        u'win': ['OSKEY'],

        u'esc': ['ESCAPE'],
        u'caps lock': ['CAPSLOCK'],
        u'space': ['SPACE'],
        u'spacebar': ['SPACE'],
        u'back_space': ['BACKSPACE'],
        u'back space': ['BACKSPACE'],
        u'return': ['ENTER'],
        u'ret': ['ENTER'],
        u'del': ['DELETE'],
        u'ins': ['INSERT'],
        u'hom': ['HOME'],
        u'pgup': ['PAGE_UP'],
        u'pgdn': ['PAGE_DOWN'],
        u'pageup': ['PAGE_UP'],
        u'pagedown': ['PAGE_DOWN'],
        u'pagedn': ['PAGE_DOWN'],
        u'page up': ['PAGE_UP'],
        u'page down': ['PAGE_DOWN'],

        u'arrow keys': ['UP_ARROW', 'DOWN_ARROW', 'LEFT_ARROW', 'RIGHT_ARROW'],
        u'arrows': ['UP_ARROW', 'DOWN_ARROW', 'LEFT_ARROW', 'RIGHT_ARROW'],
        u'up': ['UP_ARROW'],
        u'up arrow': ['UP_ARROW'],
        u'uparrow': ['UP_ARROW'],
        u'up arrow key': ['UP_ARROW'],
        u'down': ['DOWN_ARROW'],
        u'down arrow': ['DOWN_ARROW'],
        u'downarrow': ['DOWN_ARROW'],
        u'down arrow key': ['DOWN_ARROW'],
        u'left': ['LEFT_ARROW'],
        u'left arrow': ['LEFT_ARROW'],
        u'leftarrow': ['LEFT_ARROW'],
        u'left arrow key': ['LEFT_ARROW'],
        u'right': ['RIGHT_ARROW'],
        u'right arrow': ['RIGHT_ARROW'],
        u'rightarrow': ['RIGHT_ARROW'],
        u'right arrow key': ['RIGHT_ARROW'],

        u'prtscr': ['PRINT_SCREEN'],
        u'break': ['PAUSE_BREAK'],
        u'pause': ['PAUSE_BREAK'],

        u'media_first': ['MEDIA_PREVIOUS'],
        u'media_last': ['MEDIA_NEXT']
    }

    VALID_KEYNAMES = None


def _populate_valid_keynames():
    valid_keynames = []
    for char_or_name, names in DataContainer.VALID_NAME_LOOKUP.items():
        valid_keynames.extend(names)

    # Valid keynames that aren't in the VALID_NAME_LOOKUP values
    valid_keynames.extend([
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11',
        'F12', 'F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19',
        'TAB', 'END', 'NUMLOCK', 'EJECT', 'FN_KEY', 'CLEAR',
        'MEDIA_PLAY', 'MEDIA_STOP', 'SCROLL_LOCK', 'CAPSLOCK'
    ])

    # Filter out duplicates & set
    DataContainer.VALID_KEYNAMES = list(set(valid_keynames))


def get_all_valid_keynames():
    """Gets a list of all valid keynames used"""

    if DataContainer.VALID_KEYNAMES is None:
        _populate_valid_keynames()

    return DataContainer.VALID_KEYNAMES


def is_valid_keyname(name):
    """Checks if the given name is a valid keyname used in keyboard layouts"""

    if DataContainer.VALID_KEYNAMES is None:
        _populate_valid_keynames()

    return name in DataContainer.VALID_KEYNAMES


def get_valid_keynames(char_or_name, treat_numpad_keys_explicitly=False):
    """Checks if the given name is a valid keyname used in keyboard layouts
    returns a list of uppercased valid key names.

    If the given name couldn't be converted, an empty list is returned.

    /:param treat_numpad_keys_explicitly    if true, will not expand ambiguous keys to numpad keys (0 and Numpad 0 have different functions)
    """

    valid_keynames = []

    if is_valid_keyname(char_or_name.upper()):
        valid_keynames =  [char_or_name.upper()]
    elif char_or_name.lower() in DataContainer.VALID_NAME_LOOKUP.keys():
        valid_keynames =  DataContainer.VALID_NAME_LOOKUP[char_or_name.lower()]

    # Remove numpad keys
    if treat_numpad_keys_explicitly and 'numpad' not in char_or_name.lower():
        valid_keynames = [n for n in valid_keynames if 'numpad' not in n.lower()]

    return valid_keynames


class Shortcut(object):
    def __init__(self, name, key, mods=list(), anymod=False):
        self.name = name
        self.key = key
        self.mods = mods
        self.anymod = anymod

    def serialize(self):
        mods = list(set(self.mods))
        mods.sort()
        mods_str = json.dumps(mods)

        return '{"name":"%s", "mods":%s}' % (self.name, mods_str)

    def __str__(self):
        return self.serialize()


class ShortcutContext(object):
    def __init__(self, name):
        self.name = name
        self.shortcuts = []
        self.added_shortcuts_lookup = []
        self.added_keycombos_lookup = []
        self.added_keycombo_to_shortcuts_lookup = {}

    def add_shortcut(self, s, check_for_duplicates=True, explicit_numpad_mode=False):
        log.debug("adding shortcut %s", self._get_shortcut_str(s))

        # Validate modifier names
        # Modifier keys cannot be ambiguous (ctrl -> left_ctrl, right_ctrl), but can be added later if needed
        valid_mod_names = []
        for mod in s.mods:
            valid_mod_keys = get_valid_keynames(mod, explicit_numpad_mode)
            if len(valid_mod_keys) == 0:
                log.warning('...skipping add shortcut because it has an invalid modifier key name (%s)', mod)
                return
            assert len(valid_mod_keys) == 1, "Ambiguous modifier keys not supported yet"
            valid_mod_names.append(valid_mod_keys[0])
        s.mods = valid_mod_names

        # Split up ambiguous keys into multiple shortcuts
        #  a simple example is +, which can be PLUS or NUMPAD_PLUS
        expanded_shortcuts = []
        keys = get_valid_keynames(s.key, explicit_numpad_mode)
        if len(keys) == 0:
            log.warning('...skipping add shortcut because it has an invalid key name (%s)', s.key)
            return

        for key in keys:
            # if anymod can be used, split it up into individual shortcuts
            if s.anymod:
                for mod in s.mods:
                    s_expanded = Shortcut(s.name, key, [mod])
                    expanded_shortcuts.append(s_expanded)
            else:
                s_expanded = copy.deepcopy(s)
                s_expanded.key = key
                expanded_shortcuts.append(s_expanded)

        # Add all expanded shortcuts
        for shortcut in expanded_shortcuts:
            shortcut_str = self._get_shortcut_str(shortcut)
            keycombo_str = self._get_keycombo_str(shortcut)

            if not check_for_duplicates:
                self.shortcuts.append(shortcut)
                self.added_shortcuts_lookup.append(shortcut_str)
                self.added_keycombo_to_shortcuts_lookup[keycombo_str] = shortcut_str
                continue

            # Don't Add Duplicates
            if keycombo_str in self.added_keycombo_to_shortcuts_lookup.keys():
                existing_shortcut = self.added_keycombo_to_shortcuts_lookup[keycombo_str]
                log.warning('Warning: shortcut with keycombo %s already exists in context\n' +
                         '   ...existing shortcut is: %s\n   ...skipping add shorcut: "%s"',
                         keycombo_str, existing_shortcut, shortcut.name)
                continue

            if len(expanded_shortcuts) > 1:
                log.debug('   ...expanding into %s', shortcut_str)
            self.shortcuts.append(shortcut)
            self.added_shortcuts_lookup.append(shortcut_str)
            self.added_keycombo_to_shortcuts_lookup[keycombo_str] = shortcut_str

    def _get_shortcut_str(self, shortcut):
        keys = list(shortcut.mods)
        keys.sort()
        keys.append(shortcut.key)

        anymod = ''
        if shortcut.anymod:
            anymod = ' (Any Mod)'

        return ('"' + shortcut.name + '"').ljust(45) + '+'.join(keys) + anymod

    def _get_keycombo_str(self, shortcut):
        keys = list(shortcut.mods)
        keys.sort()
        keys.append(shortcut.key)
        return '+'.join(keys)

    def serialize(self):
        # todo: check for duplicates somewhere else!
        lookup_table = {}
        for shortcut in self.shortcuts:
            if shortcut.key not in lookup_table.keys():
                lookup_table[shortcut.key] = []
            lookup_table[shortcut.key].append(shortcut)

        output_str = '"%s" : {\n' % self.name

        sorted_shortcuts = collections.OrderedDict(sorted(lookup_table.items()))
        for key, shortcuts in sorted_shortcuts.items():
            output_str += '    "%s" : [\n' % key

            # Important to sort shortcuts alphabetically, this improves the quality of repo diffs
            serialized_shortcuts = [s.serialize() for s in shortcuts]
            serialized_shortcuts.sort()
            for shortcut_str in serialized_shortcuts:
                output_str += '        %s,\n' % shortcut_str

            output_str = output_str.rstrip(',\n')
            output_str += '\n    ],\n'
        output_str = output_str.rstrip(',\n')

        output_str += '\n}'

        return output_str


class ApplicationConfig(object):
    def __init__(self, app_name, app_version, app_os, default_context_name):
        super(ApplicationConfig, self).__init__()
        self.name = app_name
        self.version = app_version
        self.os = app_os
        self.default_context_name = default_context_name
        self.contexts = {}

    def get_or_create_new_context(self, name):
        """Gets an existing context by name, or adds a new one to the application"""

        if name in self.contexts.keys():
            return self.contexts[name]

        context = ShortcutContext(name)
        self.contexts[context.name] = context
        return context

    def get_mods_used(self):
        mods_used = []
        for context in self.contexts.values():
            for shortcut in context.shortcuts:
                for mod in shortcut.mods:
                    if mod not in mods_used:
                        mods_used.append(mod)
        return sorted(mods_used)

    def is_empty(self):
        """Returns true if all contexts are empty or AppConfig has no contexts"""
        for context in self.contexts.values():
            if len(context.shortcuts) > 0:
                return False
        return True

    def serialize(self, output_dir):
        """Serialize this class into a .json file with name: 'APP-NAME_VERSION_OS.json'
        Returns True for succes, False for failure"""

        assert os.path.isdir(output_dir), "The output dir is not a directory"
        assert self.os in VALID_OS_NAMES, "The application Operating system must be one of these: " + str(VALID_OS_NAMES)
        assert self.version is not None and len(self.version) > 0, "The application version must be assigned"

        # Check for empty
        if self.is_empty():
            log.warning("Cannot export ApplicationConfig because it is empty")
            return False

        # todo: handle colons in name
        appname_for_file = self.name.lower().replace(' ', '-')
        output_path = os.path.join(output_dir, "{0}_{1}_{2}.json".format(appname_for_file, self.version, self.os).lower())
        log.info('serializing ApplicationConfig to %s', output_path)

        mods_used = self.get_mods_used()

        output_str = u'{\n'
        output_str += u'    "name" : "%s",\n' % self.name
        output_str += u'    "version" : "%s",\n' % self.version
        output_str += u'    "os" : "%s",\n' % self.os
        output_str += u'    "mods_used" : %s,\n' % json.dumps(mods_used)
        output_str += u'    "default_context" : "%s",\n' % self.default_context_name
        output_str += u'    "contexts" : {\n'

        contexts_str = u""

        contexts = list(self.contexts.values())
        contexts.sort(key=lambda c: c.name)
        for context in contexts:
            # don't serialize empty contexts
            if len(context.shortcuts) == 0:
                continue

            ctx_str = u'        ' + context.serialize()
            ctx_str = ctx_str.replace(u'\n', u'\n        ')

            contexts_str += ctx_str + u',\n'
        contexts_str = contexts_str.rstrip(u',\n')

        output_str += contexts_str + u'\n'
        output_str += u'    }\n'
        output_str += u'}\n'

        # Write to file
        f = codecs.open(output_path, encoding='utf-8', mode='w+')
        f.write(output_str)
        f.close()

        # Regenerate apps.js file, this file has a list of all application json files
        #  so the web application knows what apps exist
        regenerate_site_apps_js()


def regenerate_site_apps_js():
    log.debug("REGENERATING FILE " + CONTENT_APPS_JS_FILE)

    class SiteAppDatas:
        def __init__(self):
            self.apps = {}

        def add_app(self, filename, app_name, version, os_name):
            if app_name not in self.apps.keys():
                self.apps[app_name] = {}

            if version not in self.apps[app_name].keys():
                self.apps[app_name][version] = {}

            if os_name not in self.apps[app_name][version].keys():
                self.apps[app_name][version][os_name] = filename

        def to_json(self):
            json_str = '[\n'
            for appname in sorted(self.apps.keys()):
                version_dict = self.apps[appname]
                json_str += '    {\n'
                json_str += '        name: "%s",\n' % appname
                json_str += '        data: {\n'
                for version in reversed(sorted(version_dict.keys())):
                    os_dict = version_dict[version]
                    json_str += '            "%s": {\n' % version
                    for os_name in sorted(os_dict.keys()):
                        filename = os_dict[os_name]
                        json_str += '                "%s": "%s",\n' % (os_name, filename)
                    json_str += '            },\n'
                json_str += '        }\n'
                json_str += '    },\n'
            json_str += ']'

            return json_str

    apps_js_file = open(CONTENT_APPS_JS_FILE, 'w')
    apps_js_file.write("// DO NOT EDIT THIS FILE\n")
    apps_js_file.write("// This file is automatically generated when new ApplicationConfigs are serialized\n")
    apps_js_file.write("// look in /shmaplib/appdata.py at regenerate_site_apps_js()\n\n")

    # Generate JSON for all applications in the specific format we want it
    app_sitedata = SiteAppDatas()
    for path in glob.glob(os.path.join(DIR_CONTENT_GENERATED, "*.json")):
        with open(path, encoding="utf8") as appdata_file:
            log.debug('...adding %s', path)
            appdata = json.load(appdata_file)

            app_name = appdata["name"]
            app_version = appdata["version"]
            app_os = appdata["os"]

            filename = os.path.basename(path)
            app_sitedata.add_app(filename, app_name, app_version, app_os)

    # Write json for all application data
    apps_json = app_sitedata.to_json()
    apps_js_file.write("var sitedata_apps = " + apps_json + ";\n")
    apps_js_file.close()


class IntermediateShortcutData(object):
    """Intermediate shortcut data format for applications.

    This can be used as output from various shortcut document parsers and can be merged together at the end.

    A serialized IntermediateShortcutData document can then be hand-edited to ensure the data going exported
    to the web application is clean and clear.

    The data format for intermediate data (JSON) is as follows:
    {
        "name": "Application Name",
        "version": "v1.2.3",
        "default_context": "Global Context",
        "os": ["windows", "mac"],
        "contexts": {
            "CONTEXT NAME": {
                "SHORTCUT NAME": ["WINDOWS SHORTCUT KEYS", "MAC SHORTCUT KEYS"],
                ...
            },
            ...
        }
    }

    Linux is usually the same as windows shortcuts, so we conveniently ignore that for now.

    The shortcut keys can be in the following formats:
    - "T"               Just one key
    - "Ctrl + T"        Short form allowed
    - "Control + T"
    - "Alt + +"         Special cases handled correctly
    - "Shift + 0-9"     Range of numbers (Equivalent to having the same shortcut name on all buttons)
    - "Space / Z"       '/' is used as a separator if shortcut has multiple options
    """

    class Shortcut:
        """Intermediate Shortcut structure"""
        def __init__(self, name, win_keys, mac_keys):
            self.name = name
            self.win_keys = win_keys
            self.mac_keys = mac_keys

        def _escape(self, text):
            text = text.replace('\\', '\\\\')
            text = text.replace('"', '\\"')
            return text

        def serialize(self):
            return u'            "{0}": ["{1}", "{2}"],\n'.format(self._escape(self.name),
                                                                  self._escape(self.win_keys),
                                                                  self._escape(self.mac_keys))

    class Context(object):
        """Intermediate application context structure that contains a list of shortcuts"""
        def __init__(self, name):
            self.name = name
            self.shortcuts = []
            self._shortcut_lookup = {}

        def add_shortcut(self, name, win_keys, mac_keys):
            # Add keys to existing shortcut
            existing_shortcut = self.get_shortcut(name)
            if existing_shortcut is not None:
                if len(win_keys) and win_keys not in existing_shortcut.win_keys:
                    existing_shortcut.win_keys += " / " + win_keys
                if len(mac_keys) and mac_keys not in existing_shortcut.mac_keys:
                    existing_shortcut.mac_keys += " / " + mac_keys

                return

            # Create new
            s = IntermediateShortcutData.Shortcut(name, win_keys, mac_keys)
            self._shortcut_lookup[name] = s
            self.shortcuts.append(s)

        def get_shortcut(self, name):
            if name not in self._shortcut_lookup:
                return None

            return self._shortcut_lookup[name]

        def serialize(self):
            ctx_str = u'        "{0}": {{\n'.format(self.name)
            for s in self.shortcuts:
                ctx_str += s.serialize()
            ctx_str = ctx_str.strip(",\n")
            ctx_str += u'\n        },\n'
            return ctx_str

    def __init__(self, app_name="", version="", default_context="", os_supported=None):
        """
        IntermediateShortcutData is a json format that can be easily hand-edited to fix shortcut errors.

        :param app_name: display name of the application (Adobe Photoshop)
        :param version: string format of the version (eg: 2015, v1.2, v1.6a)
        :param default_context: the name of the context that will be active by default on the website
        :param os_supported: list of supported os names as a list
        """
        super(IntermediateShortcutData, self).__init__()

        # Validation
        if os_supported:
            assert isinstance(os_supported, list), "the os_supported parameter must be a list"
            assert len(os_supported) > 0, "the os_supported parameter cannot be empty"
            assert len([o for o in os_supported if o in VALID_OS_NAMES]) > 0, \
                "the os_supported param contains invalid os names. Valid names are: " + str(VALID_OS_NAMES)
        else:
            os_supported = list(VALID_OS_NAMES)

        # Properties
        self.name = app_name
        self.version = version
        self.default_context = default_context
        self.os = os_supported
        self.contexts = []
        self._context_lookup = {}

    def add_shortcut(self, context_name, shortcut_name, win_keys, mac_keys):
        if context_name not in self._context_lookup.keys():
            context = IntermediateShortcutData.Context(context_name)
            self._context_lookup[context_name] = context
            self.contexts.append(context)
            print('Adding Context: ' + context.name)

        self._context_lookup[context_name].add_shortcut(shortcut_name, win_keys, mac_keys)

    def extend(self, idata):
        """Merges the data from one intermediate data object into this one"""
        assert isinstance(idata, IntermediateShortcutData), "Can only extend (merge) with IntermediateShortcutData type"

        for source_context in idata.contexts:
            for source_shortcut in source_context.shortcuts:
                self.add_shortcut(source_context.name, source_shortcut.name, source_shortcut.win_keys, source_shortcut.mac_keys)

                # Merge key contents
                if source_context.name in self._context_lookup.keys():
                    shortcut = self._context_lookup[source_context.name].get_shortcut(source_shortcut.name)
                    if shortcut.win_keys is None or len(shortcut.win_keys) == 0:
                        shortcut.win_keys = source_shortcut.win_keys
                    if shortcut.mac_keys is None or len(shortcut.mac_keys) == 0:
                        shortcut.mac_keys = source_shortcut.mac_keys

    def load(self, file_path):
        """Load the intermediate data from a json file"""
        self.contexts = []
        self._context_lookup = {}

        with codecs.open(file_path, encoding='utf-8') as idata_file:
            json_idata = json.load(idata_file)

            self.name = json_idata["name"]
            self.version = json_idata["version"]
            self.default_context = json_idata["default_context"]
            self.os = json_idata["os"]

            for context_name, shortcuts in json_idata["contexts"].items():
                for shortcut_name, os_keys in shortcuts.items():
                    self.add_shortcut(context_name, shortcut_name, os_keys[0], os_keys[1])

    def serialize(self, output_filepath):
        """Save the intermediate data to a json file"""
        json_str = "{\n"

        # Config
        json_str += u'    "name": "{0}",\n'.format(self.name)
        json_str += u'    "version": "{0}",\n'.format(self.version)
        json_str += u'    "default_context": "{0}",\n'.format(self.default_context)
        json_str += u'    "os": {0},\n'.format(json.dumps(self.os))

        # Contexts
        json_str += u'    "contexts": {\n'
        for context in sorted(self.contexts, key=lambda c: c.name):
            json_str += context.serialize()
        json_str = json_str.strip(",\n")
        json_str += "\n    }\n"

        json_str += "}\n"

        f = codecs.open(output_filepath, encoding='utf-8', mode='w+')
        f.write(json_str)
        f.close()


class IntermediateDataExporter(object):
    """Exports an intermediate .json file to the contents/generated directory in the correct file format."""

    def __init__(self, source, explicit_numpad_mode=False):
        super(IntermediateDataExporter, self).__init__()
        assert os.path.exists(source), "Source file '%s' does not exist" % source

        self.explicit_numpad_mode = explicit_numpad_mode

        # Load intermediate data
        self.idata = IntermediateShortcutData()
        self.idata.load(source)

        # Get app prefs from intermediate data format
        self.app_name = self.idata.name
        self.app_version = self.idata.version
        self.default_context_name = self.idata.default_context

        # Windows and Mac app configs
        self.data_windows = None
        self.data_mac = None
        if OS_WINDOWS in self.idata.os:
            self.data_windows = ApplicationConfig(self.app_name, self.app_version, OS_WINDOWS, self.default_context_name)
        if OS_MAC in self.idata.os:
            self.data_mac = ApplicationConfig(self.app_name, self.app_version, OS_MAC, self.default_context_name)

    def _parse_shortcut(self, name, keys):
        if len(keys) == 0:
            return []

        # All cases we need to handle:
        #  "A"
        #  "Shift + A"
        #  "Ctrl + 0 - 8"     this is a range of keys from 0 to 8
        #  "Shift + ] / Shift + ["
        #  ". (period) / , (comma)"
        #  "Spacebar or Z"
        #  "Up Arrow / Down Arrow or + / -"
        #  "Shift + Up Arrow / Shift + Down Arrow or Shift + + / Shift + -"

        # Cleanup the string and replace edge cases
        keys = re.sub("numpad \+", "NUMPAD_PLUS", keys, flags=re.IGNORECASE)
        keys = re.sub("numpad /", "NUMPAD_SLASH", keys, flags=re.IGNORECASE)
        keys = keys.replace(" or +", " or TEMP_PLUS")
        keys = keys.replace(" or /", " or TEMP_SLASH")
        keys = keys.replace(" + +", " + TEMP_PLUS")
        keys = keys.replace(" + /", " + TEMP_SLASH")
        keys = keys.strip(" ")
        if keys == '/':
            keys = "TEMP_SLASH"
        if keys == '+':
            keys = "TEMP_PLUS"

        # If we split by ' or ' and then ' / ' we can parse each combo separately
        combo_parts = []
        for parts1 in keys.split(' or '):
            for parts2 in parts1.split('/'):
                combo_parts.append(parts2)

        # Parse each combo
        shortcuts = []
        for combo in combo_parts:
            # TODO: skip mouse shortcuts for now
            if 'click' in combo.lower() or 'drag' in combo.lower():
                continue

            parts = combo.split("+")

            # Parse main key
            key = parts[-1]  # last element
            key = key.strip(' ')
            if key == 'TEMP_SLASH':
                key = '/'
            elif key == 'TEMP_PLUS':
                key = '+'

            # Has no key
            if len(key) == 0:
                continue

            # Parse modifiers
            mods = [m.strip(u' ') for m in parts[:-1]]  # all but last

            # Handle a range of keys (Example: "Ctrl + 0-9" or "Ctrl + Numpad 0-9")
            #  which will result in multiple shortcuts with the same label
            results = re.findall(".*?([0-9])-([0-9])", key)
            if results:
                start = int(results[0][0])
                end = int(results[0][1])
                is_numpad_key = 'numpad' in key.lower()

                for i in range(start, end+1):
                    key_name = str(i)
                    if is_numpad_key:
                        key_name = 'Numpad ' + key_name
                    shortcut = Shortcut(name, key_name, mods)
                    shortcuts.append(shortcut)

            # Result is just one shortcut
            else:
                shortcut = Shortcut(name, key, mods)
                shortcuts.append(shortcut)

        return shortcuts

    def parse(self):
        # WINDOWS: Iterate contexts and shortcuts
        if self.data_windows:
            log.info("Parsing intermediate data for Windows shortcuts")
            for context in self.idata.contexts:
                context_win = self.data_windows.get_or_create_new_context(context.name)
                for shortcut in context.shortcuts:
                    for s in self._parse_shortcut(shortcut.name, shortcut.win_keys):
                        context_win.add_shortcut(s, True, self.explicit_numpad_mode)
            log.info("...DONE\n")

        # MAC: Iterate contexts and shortcuts
        if self.data_mac:
            log.info("Parsing intermediate data for MacOS shortcuts")
            for context in self.idata.contexts:
                context_mac = self.data_mac.get_or_create_new_context(context.name)
                for shortcut in context.shortcuts:
                    for s in self._parse_shortcut(shortcut.name, shortcut.mac_keys):
                        context_mac.add_shortcut(s, True, self.explicit_numpad_mode)
            log.info("...DONE\n")

    def export(self):
        if self.data_windows:
            self.data_windows.serialize(DIR_CONTENT_GENERATED)
        if self.data_mac:
            self.data_mac.serialize(DIR_CONTENT_GENERATED)


def export_intermediate_file(file_path, explicit_numpad_mode):
    exporter = IntermediateDataExporter(file_path, explicit_numpad_mode)
    exporter.parse()
    exporter.export()


def main():
    parser = argparse.ArgumentParser(description="Converts intermediate json data files to the web application data format.")
    parser.add_argument('-e', '--explicit-numpad-keys', action='store_true', required=False, help="Numpad keys don't have the same action as main keys")
    parser.add_argument('file', nargs='?', help="File to convert (Ignored if -a flag is set)", default=".\CheeseBerry_2023-10-19_js.json")

    args = parser.parse_args()
    if args.file is not None:
        args.file = os.path.abspath(args.file)

    export_intermediate_file(args.file, args.explicit_numpad_keys)


if __name__ == '__main__':
    main()
