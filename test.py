import unittest

from auto_regex import AutoRegex


class TestAutoRegex(unittest.TestCase):

    def test_get_regex(self):
        def _test_get_regex(line, expected):
            a = AutoRegex()
            r = a.get_expressions([line])[0]
            self.assertEqual(r, expected)

        # test positions
        _test_get_regex("say {word}", "^\W*say\W*(?P<word>.*?\w.*?)\W*$")
        _test_get_regex("{word} is the answer",
                        "^\W*(?P<word>.*?\w.*?)\W*is\W+the\W+answer\W*$")
        _test_get_regex("weather in {city} tomorrow",
                        "^\W*weather\W+in\W*(?P<city>.*?\w.*?)\W*tomorrow\W*$")
        # test multiple extractions
        _test_get_regex("{thing} is {attribute}",
                        "^\W*(?P<thing>.*?\w.*?)\W*is\W*(?P<attribute>.*?\w.*?)\W*$")
        _test_get_regex("search {music} by {artist} in {place}",
                        "^\W*search\W*(?P<music>.*?\w.*?)\W*by\W*(?P<artist>.*?\w.*?)\W*in\W*(?P<place>.*?\w.*?)\W*$")
        # test spaces
        _test_get_regex("say { word }", "^\W*say\W*(?P<word>.*?\w.*?)\W*$")
        _test_get_regex("say    {    word }",
                        "^\W*say\W*(?P<word>.*?\w.*?)\W*$")
        _test_get_regex("say {word       }",
                        "^\W*say\W*(?P<word>.*?\w.*?)\W*$")

        # test keyword space cleaning
        _test_get_regex("say {two words}",
                        "^\W*say\W*(?P<two_words>.*?\w.*?)\W*$")

        # test double
        _test_get_regex("say {{word}}", "^\W*say\W*(?P<word>.*?\w.*?)\W*$")

        # test upper case
        # TODO FIX ME
        # _test_get_regex("say { Word }", "^\W*say\W*(?P<Word>.*?\w.*?)\W*$")
        _test_get_regex("say { Word }", "^\W*say\W*(?P<word>.*?\w.*?)\W*$")

    def test_get_entities(self):
        def _test_get_entities(query, lines, expected):
            if not isinstance(lines, list):
                lines = [lines]
            a = AutoRegex()
            a.create_regex(lines)
            for e in a.get_entities(query):
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
        _test_get_entities("set volume to 100 percent",
                           ["set { thing } to { number } percent"],
                           {"thing": "volume", "number": "100"})

    def test_get_matches(self):
        def _test_get_matches(query, lines, expected):
            if not isinstance(lines, list):
                lines = [lines]
            a = AutoRegex()
            a.create_regex(lines)
            for e in a.get_matches(query):
                self.assertEqual(e, expected)

        _test_get_matches("say hello", "say {word}",
                          {'entities': {"word": "hello"},
                           'query': 'say hello',
                           'regexes': ['^\W*say\W*(?P<word>.*?\w.*?)\W*$']
                           }
                          )
        _test_get_matches("I a going to a party tomorrow tonight",
                          "I am going to {place} tomorrow night",
                          {'entities': {"place": "a party"},
                           'query': 'I a going to a party tomorrow tonight',
                           'regexes': [
                               '^\W*I\W+am\W+going\W+to\W*(?P<place>.*?\w.*?)\W*tomorrow\W+night\W*$']
                           }
                          )
        _test_get_matches("say blip blop, i am a bot", "say {word}",
                          {'entities': {"word": "blip blop, i am a bot"},
                           'query': 'say blip blop, i am a bot',
                           'regexes': ['^\W*say\W*(?P<word>.*?\w.*?)\W*$']
                           }
                          )
        _test_get_matches("search dragula by rob zombie in youtube",
                          "search {music} by {artist} in {place}",
                          {'entities': {'artist': 'rob zombie',
                                        'music': 'dragula',
                                        'place': 'youtube'},
                           'query': 'search dragula by rob zombie in youtube',
                           'regexes': [
                               '^\W*search\W*(?P<music>.*?\w.*?)\W*by\W*(?P<artist>.*?\w.*?)\W*in\W*(?P<place>.*?\w.*?)\W*$']
                           }
                          )


if __name__ == "__main__":
    unittest.main()
