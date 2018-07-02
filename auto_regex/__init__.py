import re


class AutoRegex(object):
    def __init__(self):
        self.regex_lines, self.entity_lines = [], {}
        self.regexes, self.entities = [], {}
        self.must_compile = True
        self.i = 0

    def create_regex(self, lines):
        self.must_compile = True
        self.regex_lines.append(lines)

    def _clean_line(self, line):
        # replace double spaces with single "  " -> " "
        line = " ".join(line.split())
        # if {{ found replace with single { : {{word}} -> {word}
        line = line.replace("{{", "{").replace("}}", "}")
        # trim spaces inside {}: { word } -> {word}
        line = line.replace("{ ", "{").replace(" }", "}")
        # replace spaces in keyword
        if "{" in line:
            e = 0
            words = []
            while "{" in line[e:len(line)] and e >= 0:
                i = line[e:len(line)].find("{") + e
                e = line[e:len(line)].find("}") + 1 + e
                words.append(line[i:e].lstrip().rstrip())
            for word in words:
                line = line.replace(word, word.replace(" ", "_"))
        return line

    def get_expressions(self, lines):
        regexes = []
        for line in lines:
            regexes.append(self._create_regex_pattern(line))
        return regexes

    def get_entities(self, query):
        if self.must_compile:
            self._compile_regex()
        for regexes in self.regexes:
            entities = list(self._calc_entities(query, regexes))
            if entities:
                yield min(entities, key=lambda x: sum(map(len, x.values())))

    def get_matches(self, query):
        if self.must_compile:
            self._compile_regex()
        for regexes in self.regexes:
            entities = self._calc_matches(query, regexes)
            regex = [str(r).replace("re.compile('", "") \
                         .replace("', re.IGNORECASE)", "") \
                         .replace("\\\\", "\\") for r in regexes]
            for ent in entities:
                yield {
                    'query': query,
                    'entities': ent,
                    'regexes': regex
                }

    def _create_pattern(self, line):
        for pat, rep in (
                # === Preserve Plain Parentheses ===
                (r'\(([^\|)]*)\)', r'{~(\1)~}'),  # (hi) -> {~(hi)~}

                # === Convert to regex literal ===
                (re.escape, None),  # a b:c -> a\ b\:c
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
                (r'(?<=\s)\\:0(?=\s)', r'\w+'),
                (r'#', r'\d'),
                (r'\d', r'\d'),

                # === Space Word Separations ===
                (r'(?<!\\)(\w)([^\w\s}])', r'\1 \2'),  # a:b -> a :b
                (r'([^\\\w\s{])(\w)', r'\1 \2'),  # a :b -> a : b

                # === Make Symbols Optional ===
                (r'(\\[^\w ])', r'\1?'),

                # === Force 1+ Space Between Words ===
                (r'(?<=\w)(\\\s|\s)+(?=\w)', r'\\W+'),

                # === Force 0+ Space Between Everything Else ===
                (r'\s+', r'\\W*'),
        ):
            if callable(pat):
                line = pat(line)
            else:
                line = re.sub(pat, rep, line)
        return line

    def _create_regex_pattern(self, line):
        line = self._clean_line(line)
        line = self._create_pattern(line)
        replacements = {}
        for ent_name in set(re.findall(r'{([a-z_:]+)}', line)):
            replacements[ent_name] = r'(?P<{}>.*?\w.*?)'.format(ent_name)
        for ent_name, ent in self.entities.items():
            ent_regex = r'(?P<{}>{})'
            replacements[ent_name] = ent_regex.format(
                ent_name.replace(':', '__colon__'), ent)
        for key, value in replacements.items():
            line = line.replace('{' + key + '}', value.format(self.i), 1)
            self.i += 1
        return '^{}$'.format(line)

    def _create_regexes(self, lines):
        return [
            re.compile(self._create_regex_pattern(line), re.IGNORECASE)
            for line in sorted(lines, key=len, reverse=True)
            if line.strip()
        ]

    def _compile_regex(self):
        self.entities = {
            ent_name: r'({})'.format('|'.join(
                self._create_pattern(line) for line in lines if line.strip()
            ))
            for ent_name, lines in self.entity_lines.items()
        }
        self.regexes = [
            self._create_regexes(lines) for lines in self.regex_lines
        ]
        self.must_compile = False

    def _calc_entities(self, query, regexes):
        for regex in regexes:
            match = regex.match(query)
            if match:
                yield {
                    k.rsplit('__', 1)[0].replace('__colon__', ':'): v.strip()
                    for k, v in match.groupdict().items() if v
                }

    def _calc_matches(self, query, regexes):
        for regex in regexes:
            match = regex.match(query)
            if match:
                yield {
                    k.rsplit('__', 1)[0]: v
                    for k, v in match.groupdict().items() if v
                }
