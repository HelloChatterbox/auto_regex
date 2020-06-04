import re
import string


class AutoRegex:
    def __init__(self):
        self.regex_lines, self.entity_lines = [], {}
        self.regexes, self.entities = [], {}
        self.must_compile = True
        self.i = 0

    @staticmethod
    def _partition(line):
        t = line.partition("{")[2].partition("}")
        matches = []
        if t[0]:
            matches.append(t[0])
        leftover = t[2]
        if leftover:
            matches += AutoRegex._partition(leftover)
        return matches

    @staticmethod
    def clean_line(line,
                   whitelist=string.ascii_letters + string.digits + "{}() _"):
        line = ''.join(c for c in line if c in whitelist)
        # make lower case
        # line = line.lower()
        # replace double spaces with single space : "  " -> " "
        line = " ".join(line.split())
        # if {{ found replace with single { : {{word}} -> {word}
        line = line.replace("{{", "{").replace("}}", "}")
        line = line.replace("{ {", "{").replace("} }", "}")
        # trim spaces inside {}: { word } -> {word}
        line = line.replace("{ ", "{").replace(" }", "}")

        for word in AutoRegex._partition(line):
            line = line.replace("{" + word + "}",
                                "{" + word.replace(" ", "_") + "}")
        return line

    @staticmethod
    def get_expressions(lines):
        if not isinstance(lines, list):
            lines = [lines]
        return [AutoRegex.create_regex_pattern(line) for line in lines]

    @staticmethod
    def get_kwords(lines):
        if not isinstance(lines, list):
            lines = [lines]
        for line in lines:
            line = AutoRegex.clean_line(line)
            yield AutoRegex._partition(line)

    @staticmethod
    def get_unique_kwords(lines):
        flatten = lambda l: [item for sublist in l for item in sublist]
        flat_list = flatten(list(AutoRegex.get_kwords(lines)))
        return list(set(flat_list))

    @staticmethod
    def _create_pattern(line):
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
                (r'(?<=(\w|\}))(\\\s|\s)+(?=\S)', r'\\W+'),

                # === Force 0+ Space Between Everything Else ===
                (r'\s+', r'\\W*'),
        ):
            if callable(pat):
                line = pat(line)
            else:
                line = re.sub(pat, rep, line)
        return line

    @staticmethod
    def create_regex_pattern(line):
        line = AutoRegex.clean_line(line)
        line = AutoRegex._create_pattern(line)
        replacements = {}
        for ent_name in set(re.findall(r'{([a-z_:]+)}', line)):
            replacements[ent_name] = r'(?P<{}>.*?\w.*?)'.format(ent_name)

        for key, value in replacements.items():
            line = line.replace('{' + key + '}', value)
        return '^{}$'.format(line)

    def add_rules(self, lines):
        if not isinstance(lines, list):
            lines = [lines]
        self.must_compile = True
        self.regex_lines.append(lines)

    def extract(self, query):
        if self.must_compile:
            self._compile()
        for regexes in self.regexes:
            entities = list(self._match(query, regexes))
            if entities:
                yield min(entities, key=lambda x: sum(map(len, x.values())))

    def _compile_rx(self, lines):
        return [
            re.compile(self.create_regex_pattern(line), re.IGNORECASE)
            for line in sorted(lines, key=len, reverse=True)
            if line.strip()
        ]

    def _compile(self):
        self.entities = {
            ent_name: r'({})'.format('|'.join(
                self._create_pattern(line) for line in lines if line.strip()
            ))
            for ent_name, lines in self.entity_lines.items()
        }
        self.regexes = [
            self._compile_rx(lines) for lines in self.regex_lines
        ]
        self.must_compile = False

    def _match(self, query, regexes):
        for regex in regexes:
            match = regex.match(query)
            if match:
                yield {
                    k.rsplit('__', 1)[0].replace('__colon__', ':'): v.strip()
                    for k, v in match.groupdict().items() if v
                }


if __name__ == "__main__":
    rules = [
        "say {{something}} about {topic}",
        "say {{something}} please",
        "{{user}} is my name"
    ]

    for r in AutoRegex.get_expressions(rules):
        print(r)
        """
        ^\W*say\W+(?P<something>.*?\w.*?)\W+about\W+(?P<topic>.*?\w.*?)\W*$
        ^\W*say\W+(?P<something>.*?\w.*?)\W+please\W*$
        ^\W*(?P<user>.*?\w.*?)\W+is\W+my\W+name\W*$
        """
    for kw in AutoRegex.get_kwords(rules):
        print(kw)
        """
        ['something', 'topic']
        ['something']
        ['user']
        """

    rx = AutoRegex()
    rx.add_rules(rules)

    test = ["say hello please",
            "Jarbas is my name"]
    for t in test:
        matches = list(rx.extract(t))
        print(matches)
        """
        [{'something': 'hello'}]
        [{'user': 'Jarbas'}]
        """

