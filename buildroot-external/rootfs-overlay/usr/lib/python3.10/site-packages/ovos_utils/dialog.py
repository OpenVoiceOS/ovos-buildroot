import os
import random
import re
from os.path import join
from pathlib import Path

from ovos_utils.bracket_expansion import expand_options
from ovos_config.config import read_mycroft_config
from ovos_utils.file_utils import resolve_resource_file
from ovos_utils.lang import translate_word
from ovos_utils.log import LOG


class MustacheDialogRenderer:
    """A dialog template renderer based on the mustache templating language."""

    def __init__(self):
        self.templates = {}
        self.recent_phrases = []

        # TODO magic numbers are bad!
        self.max_recent_phrases = 3
        # We cycle through lines in .dialog files to keep Mycroft from
        # repeating the same phrase over and over. However, if a .dialog
        # file only contains a few entries, this can cause it to loop.
        #
        # This offset will override max_recent_phrases on very short .dialog
        # files. With the offset at 2, .dialog files with 3 or more lines will
        # be managed to avoid repetition, but .dialog files with only 1 or 2
        # lines will be unaffected. Dialog should never get stuck in a loop.
        self.loop_prevention_offset = 2

    def load_template_file(self, template_name, filename):
        """Load a template by file name into the templates cache.

        Args:
            template_name (str): a unique identifier for a group of templates
            filename (str): a fully qualified filename of a mustache template.
        """
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                template_text = line.strip()
                # Skip all lines starting with '#' and all empty lines
                if (not template_text.startswith('#') and
                        template_text != ''):
                    if template_name not in self.templates:
                        self.templates[template_name] = []

                    # convert to standard python format string syntax. From
                    # double (or more) '{' followed by any number of
                    # whitespace followed by actual key followed by any number
                    # of whitespace followed by double (or more) '}'
                    template_text = re.sub(r'\{\{+\s*(.*?)\s*\}\}+', r'{\1}',
                                           template_text)

                    self.templates[template_name].append(template_text)

    def render(self, template_name, context=None, index=None):
        """
        Given a template name, pick a template and render it using the context.
        If no matching template exists use template_name as template.

        Tries not to let Mycroft say exactly the same thing twice in a row.

        Args:
            template_name (str): the name of a template group.
            context (dict): dictionary representing values to be rendered
            index (int): optional, the specific index in the collection of
                templates

        Returns:
            str: the rendered string
        """
        context = context or {}
        if template_name not in self.templates:
            # When not found, return the name itself as the dialog
            # This allows things like render("record.not.found") to either
            # find a translation file "record.not.found.dialog" or return
            # "record not found" literal.
            return template_name.replace('.', ' ')

        # Get the .dialog file's contents, minus any which have been spoken
        # recently.
        template_functions = self.templates.get(template_name)

        if index is None:
            template_functions = ([t for t in template_functions
                                   if t not in self.recent_phrases] or
                                  template_functions)
            line = random.choice(template_functions)
        else:
            line = template_functions[index % len(template_functions)]
        # Replace {key} in line with matching values from context
        line = line.format(**context)
        line = random.choice(expand_options(line))

        # Here's where we keep track of what we've said recently. Remember,
        # this is by line in the .dialog file, not by exact phrase
        self.recent_phrases.append(line)
        if (len(self.recent_phrases) >
                min(self.max_recent_phrases, len(self.templates.get(
                    template_name)) - self.loop_prevention_offset)):
            self.recent_phrases.pop(0)
        return line


def load_dialogs(dialog_dir, renderer=None):
    """Load all dialog files within the specified directory.

    Args:
        dialog_dir (str): directory that contains dialog files

    Returns:
        a loaded instance of a dialog renderer
    """
    if renderer is None:
        renderer = MustacheDialogRenderer()

    directory = Path(dialog_dir)
    if not directory.exists() or not directory.is_dir():
        LOG.warning('No dialog files found: {}'.format(dialog_dir))
        return renderer

    for path, _, files in os.walk(str(directory)):
        for f in files:
            if f.endswith('.dialog'):
                renderer.load_template_file(f.replace('.dialog', ''),
                                            join(path, f))
    return renderer


def get_dialog(phrase, lang=None, context=None):
    """Looks up a resource file for the given phrase.

    If no file is found, the requested phrase is returned as the string. This
    will use the default language for translations.

    Args:
        phrase (str): resource phrase to retrieve/translate
        lang (str): the language to use
        context (dict): values to be inserted into the string

    Returns:
        str: a randomized and/or translated version of the phrase
    """

    if not lang:
        try:
            conf = read_mycroft_config()
            lang = conf.get('lang')
        except FileNotFoundError:
            lang = "en-us"

    filename = join('text', lang.lower(), phrase + '.dialog')
    template = resolve_resource_file(filename)
    if not template:
        LOG.debug('Resource file not found: {}'.format(filename))
        return phrase

    stache = MustacheDialogRenderer()
    stache.load_template_file('template', template)
    if not context:
        context = {}
    return stache.render('template', context)


def join_list(items, connector, sep=None, lang=''):
    """ Join a list into a phrase using the given connector word
    Examples:
        join_list([1,2,3], "and") ->  "1, 2 and 3"
        join_list([1,2,3], "and", ";") ->  "1; 2 and 3"
    Args:
        items (array): items to be joined
        connector (str): connecting word (resource name), like "and" or "or"
        sep (str, optional): separator character, default = ","
        lang (str, optional): an optional BCP-47 language code, if omitted
                              the default language will be used.
    Returns:
        str: the connected list phrase
    """

    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])

    if not sep:
        sep = ", "
    else:
        sep += " "
    return (sep.join(str(item) for item in items[:-1]) +
            " " + translate_word(connector, lang) +
            " " + items[-1])
