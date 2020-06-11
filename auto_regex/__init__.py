import re
import string


class AutoRegex:
    def __init__(self):
        self.rules = []
        self.regexes  = []
        self.must_compile = True

    @staticmethod
    def _partition(line):
        t = line.partition("{")[2].partition("}")
        matches = []
        if t[0] and t[1]:
            matches.append(t[0])
        leftover = t[2]
        if leftover:
            matches += AutoRegex._partition(leftover)
        return matches

    @staticmethod
    def clean_line(line,
                   whitelist=string.ascii_letters + string.digits + "#{} "):
        line = ''.join(c for c in line if c in whitelist)
        # make lower case
        line = line.lower()
        # replace double spaces with single space : "  " -> " "
        line = " ".join(line.split())
        # if {{ found replace with single { : {{word}} -> {word}
        line = line.replace("{{", "{").replace("}}", "}")
        line = line.replace("{ {", "{").replace("} }", "}")
        # trim spaces inside {}: { word } -> {word}
        line = line.replace("{ ", "{").replace(" }", "}")
        kw = AutoRegex._partition(line)
        for word in kw:
            # replace spaces inside {}: {word two} -> {word_two}
            line = line.replace("{" + word + "}",
                                "{" + word.replace(" ", "_") + "}")
            # tag kw
            line = line.replace("{" + word + "}", "$" + word.replace(" ", "_"))
        # balance parentheses
        for word in kw:
            wlist = string.ascii_letters + string.digits + " $_#{}"
            new_line = ""
            for c in line:
                if c in wlist:
                    new_line += c
                else:
                    new_line += " "
            line = new_line.replace("$" + word.replace(" ", "_"),
                                    "{" + word.replace(" ", "_") + "}")
        return line

    @staticmethod
    def get_expressions(lines):
        if not isinstance(lines, list):
            lines = [lines]
        lines = [AutoRegex.clean_line(line) for line in lines]
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
        lines = [AutoRegex.clean_line(line) for line in lines]
        self.must_compile = True
        self.rules.append(lines)

    def extract(self, query):
        if self.must_compile:
            self._compile()
        for regexes in self.regexes:
            entities = list(self.match(query, regexes))
            if entities:
                yield min(entities, key=lambda x: sum(map(len, x.values())))

    def _compile_rx(self, lines):
        return [
            re.compile(self.create_regex_pattern(line), re.IGNORECASE)
            for line in sorted(lines, key=len, reverse=True)
            if line.strip()
        ]

    def _compile(self):
        self.regexes = [
            self._compile_rx(lines) for lines in self.rules
        ]
        self.must_compile = False

    @staticmethod
    def match(query, regexes):
        for regex in regexes:
            match = regex.match(query)
            if match:
                yield {
                    k.rsplit('__', 1)[0].replace('__colon__', ':'): v.strip()
                    for k, v in match.groupdict().items() if v
                }


if __name__ == "__main__":
    rules = [
        "{track} from {album}",
        "{track} by {artist}",
        "say {{something}} about {topic}",
        "number #",

        "track ## from {album}",
        "## track from {album}",
        "track # from {album}",
        "# track from {album}",

        "say {{something}} please",
        "{{user}} is}}[]{_ my name",  # unbalanced are ignored
        '''!""""#$%&/()=???|AS*+ºª-_.:,;^~'`*«»}][{§£@|''', # symbols ignored
        "test as}{a}}}{      { jihugf }"
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

    test = ["something from badass album",
            "number 42",
            "track 10 from foo",
            "6 track from bar",
            "At The Center Of All Infinity by yuri gagarin",
           # "Jarbas is my name"
    ]
    for t in test:
        matches = list(rx.extract(t))
        print(matches)
        """
        [{'something': 'hello'}]
        [{'user': 'Jarbas'}]
        """

