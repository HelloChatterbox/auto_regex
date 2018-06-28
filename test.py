import unittest

from autoregex import AutoRegex


class TestAutoRegex(unittest.TestCase):

    def test_get_regex(self):
        def _test_get_regex(line, expected):
            a = AutoRegex()
            r = a.get_regexes([line])[0]
            self.assertEqual(r, expected)

        _test_get_regex("say {word}", "^\W*say\W*(?P<word>.*?\w.*?)\W*$")
        _test_get_regex("{word} is the answer",
                        "^\W*(?P<word>.*?\w.*?)\W*is\W+the\W+answer\W*$")
        _test_get_regex("weather in {city} tomorrow",
                        "^\W*weather\W+in\W*(?P<city>.*?\w.*?)\W*tomorrow\W*$")

    def test_get_entities(self):
        def _test_get_entities(query, lines, expected):
            if not isinstance(lines, list):
                lines = [lines]
            a = AutoRegex()
            a.create_regex(lines)
            for e in a.calc_entities(query):
                self.assertEqual(e, expected)

        _test_get_entities("say hello", "say {word}",
                           {"word": "hello"})
        _test_get_entities("my name is Bond", "my name is {name}",
                           {"name": "Bond"})
        _test_get_entities("I a going to a party tomorrow tonight",
                           "I am going to {place} tomorrow night",
                           {"place": "a party"})
        _test_get_entities("first choice",
                           ["{number} choice", "{number} option"],
                           {"number": "first"})
        _test_get_entities("first option",
                           ["{number} choice", "{number} option"],
                           {"number": "first"})

    def test_get_matches(self):
        def _test_get_matches(query, lines, expected):
            if not isinstance(lines, list):
                lines = [lines]
            a = AutoRegex()
            a.create_regex(lines)
            for e in a.calc_matches(query):
                self.assertEqual(e, expected)

        _test_get_matches("say hello", "say {word}",
                          {'entities': {"word": "hello"},
                           'query': 'say hello',
                           'regex': '^\W*say\W*(?P<word>.*?\w.*?)\W*$'
                           }
                          )
        _test_get_matches("I a going to a party tomorrow tonight",
                          "I am going to {place} tomorrow night",
                          {'entities': {"place": "a party"},
                           'query': 'I a going to a party tomorrow tonight',
                           'regex': '^\W*I\W+am\W+going\W+to\W*(?P<place>.*?\w.*?)\W*tomorrow\W+night\W*$'
                           }
                          )
        _test_get_matches("say blip blop, i am a bot", "say {word}",
                          {'entities': {"word": "blip blop, i am a bot"},
                           'query': 'say blip blop, i am a bot',
                           'regex': '^\W*say\W*(?P<word>.*?\w.*?)\W*$'
                           }
                          )


if __name__ == "__main__":
    unittest.main()
