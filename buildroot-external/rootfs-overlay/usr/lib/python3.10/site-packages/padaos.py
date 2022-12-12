import re
import sre_constants
import logging
from threading import Lock


LOG = logging.getLogger('padaos')

class IntentContainer:
    def __init__(self):
        self.intent_lines, self.entity_lines = {}, {}
        self.intents, self.entities = {}, {}
        self.must_compile = True
        self.i = 0
        self.compile_lock = Lock()

    def add_intent(self, name, lines):
        with self.compile_lock:
            self.must_compile = True
            self.intent_lines[name] = lines

    def remove_intent(self, name):
        with self.compile_lock:
            self.must_compile = True
            if name in self.intent_lines:
                del self.intent_lines[name]

    def add_entity(self, name, lines):
        with self.compile_lock:
            self.must_compile = True
            self.entity_lines[name] = lines

    def remove_entity(self, name):
        with self.compile_lock:
            self.must_compile = True
            if name in self.entity_lines:
                del self.entity_lines[name]

    def _create_pattern(self, line):
        for pat, rep in (
                # === Preserve Plain Parentheses ===
                (r'\(([^\|)]*)\)', r'{~(\1)~}'),  # (hi) -> {~(hi)~}

                # === Convert to regex literal ===
                (r'(\W)', r'\\\1'),
                (r' {} '.format, None),  # 'abc' -> ' abc '

                # === Unescape Chars for Convenience ===
                (r'\\ ', r' '),  # "\ " -> " "
                (r'\\{', r'{'),  # \{ -> {
                (r'\\}', r'}'),  # \} -> }
                (r'\\#', r'#'),  # \# -> #

                # === Support Parentheses Expansion ===
                (r'(?<!\\{\\~)\\\(', r'(?:'),  # \( -> (  ignoring  \{\~\(
                (r'\\\)(?!\\~\\})', r')'),  # \) -> )  ignoring  \)\~\}
                (r'\\{\\~\\\(', r'\\('),  # \{\~\( -> \(
                (r'\\\)\\~\\}', r'\\)'),  # \)\~\}  -> \)
                (r'\\\|', r'|'),  # \| -> |

                # === Support Special Symbols ===
                (r'(?<=\s)\\:0(?=\s)', r'\\w+'),
                (r'#', r'\\d'),
                (r'\d', r'\\d'),

                # === Space Word Separations ===
                (r'(?<!\\)(\w)([^\w\s}])', r'\1 \2'),  # a:b -> a :b
                (r'([^\\\w\s{])(\w)', r'\1 \2'),  # a :b -> a : b

                # === Make Symbols Optional ===
                (r'(\\[^\w ])', r'\1?'),

                # === Force 1+ Space Between Words ===
                (r'(?<=\w)(\\\s|\s)+', r'\\W+'),

                # === Force 0+ Space Between Everything Else ===
                (r'\s+', r'\\W*'),
        ):
            if callable(pat):
                line = pat(line)
            else:
                line = re.sub(pat, rep, line)
        return line

    def _create_intent_pattern(self, line, intent_name):
        namespace = intent_name.split(':')[0] + ':'
        line = self._create_pattern(line)
        replacements = {}
        for ent_name in set(re.findall(r'{([a-z_:]+)}', line)):
            replacements[ent_name] = r'(?P<{}__{{}}>.*?\w.*?)'.format(ent_name)
        for ent_name, ent in self.entities.items():
            ent_regex = r'(?P<{}__{{}}>{})'
            if ent_name.startswith(namespace):
                replacements[ent_name[len(namespace):]] = ent_regex.format(
                    ent_name[len(namespace):], ent
                )
            else:
                replacements[ent_name] = ent_regex.format(ent_name.replace(':', '__colon__'), ent)
        for key, value in replacements.items():
            line = line.replace('{' + key + '}', value.format(self.i), 1)
            self.i += 1
        return '^{}$'.format(line)

    def _create_regex(self, line, intent_name):
        """ Create regex and return. If error occurs returns None. """
        try:
            return re.compile(self._create_intent_pattern(line, intent_name),
                              re.IGNORECASE)
        except sre_constants.error as e:
            LOG.warning('Failed to parse the line "{}" '
                        'for {}'.format(line, intent_name))
            return None
            
    def create_regexes(self, lines, intent_name):
        regexes = [self._create_regex(line, intent_name)
                  for line in sorted(lines, key=len, reverse=True)
                  if line.strip()]
        # Filter out all regexes that fails
        return [r for r in regexes if r is not None]

    def compile(self):
        with self.compile_lock:
            self._compile()

    def _compile(self):
        self.entities = {
            ent_name: r'({})'.format('|'.join(
                self._create_pattern(line) for line in lines if line.strip()
            ))
            for ent_name, lines in self.entity_lines.items()
        }
        self.intents = {
            intent_name: self.create_regexes(lines, intent_name)
            for intent_name, lines in self.intent_lines.items()
        }
        self.must_compile = False

    def _calc_entities(self, query, regexes):
        for regex in regexes:
            match = regex.match(query)
            if match:
                yield {
                    k.rsplit('__', 1)[0].replace('__colon__', ':'): v.strip()
                    for k, v in match.groupdict().items() if v
                }

    def calc_intents(self, query):
        query = ' ' + query + ' '
        if self.must_compile:
            self.compile()
        for intent_name, regexes in self.intents.items():
            entities = list(self._calc_entities(query, regexes))
            if entities:
                yield {
                    'name': intent_name,
                    'entities': min(entities, key=lambda x: sum(map(len, x.values())))
                }

    def calc_intent(self, query):
        return min(
            self.calc_intents(query),
            key=lambda x: sum(map(len, x['entities'].values())),
            default={'name': None, 'entities': {}}
        )
