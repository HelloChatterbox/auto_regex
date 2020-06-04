import unittest

from auto_regex import AutoRegex


class TestAutoRegex(unittest.TestCase):

    def test_get_regex(self):
        def _test_get_regex(line, expected):
            a = AutoRegex()
            r = a.get_expressions([line])[0]
            self.assertEqual(r, expected)

        # test positions
        _test_get_regex("say {word}", "^\W*say\W+(?P<word>.*?\w.*?)\W*$")
        _test_get_regex("{word} is the answer",
                        "^\W*(?P<word>.*?\w.*?)\W+is\W+the\W+answer\W*$")
        _test_get_regex("weather in {city} tomorrow",
                        "^\W*weather\W+in\W+(?P<city>.*?\w.*?)\W+tomorrow\W*$")
        # test multiple extractions
        _test_get_regex("{thing} is {attribute}",
                        "^\W*(?P<thing>.*?\w.*?)\W+is\W+(?P<attribute>.*?\w.*?)\W*$")
        _test_get_regex("search {music} by {artist} in {place}",
                        "^\W*search\W+(?P<music>.*?\w.*?)\W+by\W+(?P<artist>.*?\w.*?)\W+in\W+(?P<place>.*?\w.*?)\W*$")
        # test spaces
        _test_get_regex("say { word }", "^\W*say\W+(?P<word>.*?\w.*?)\W*$")
        _test_get_regex("say    {    word }",
                        "^\W*say\W+(?P<word>.*?\w.*?)\W*$")
        _test_get_regex("say {word       }",
                        "^\W*say\W+(?P<word>.*?\w.*?)\W*$")

        # test keyword space cleaning
        _test_get_regex("say {two words}",
                        "^\W*say\W+(?P<two_words>.*?\w.*?)\W*$")

        # test double
        _test_get_regex("say {{word}}", "^\W*say\W+(?P<word>.*?\w.*?)\W*$")

        # test upper case
        _test_get_regex("say { Word }", "^\W*say\W+{Word}\W*$")

    def test_extract(self):
        def _test(query, lines, expected):
            a = AutoRegex()
            a.add_rules(lines)
            for e in a.extract(query):
                self.assertEqual(e, expected)

        _test("say hello",
              "say {word}",
              {"word": "hello"})
        _test("my name is Bond",
              "my name is {name}",
              {"name": "Bond"})
        _test("I a going to a party tomorrow tonight",
              "I am going to {place} tomorrow night",
              {"place": "a party"})
        _test("first choice",
              ["{number} choice", "{number} option"],
              {"number": "first"})
        _test("first option",
              ["{number} choice", "{number} option"],
              {"number": "first"})
        _test("set volume to 100 percent",
              ["set { thing } to { number } percent"],
              {"thing": "volume", "number": "100"})


if __name__ == "__main__":
    unittest.main()
