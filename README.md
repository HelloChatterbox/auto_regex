# auto_regex

regex automated

# install

install from pip
```bash
pip install auto_regex
```
  
or just bundle the python file with your project, it is standalone
        
# usage
```python
from auto_regex import AutoRegex
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
for query in test:
    matches = list(rx.extract(query))
    print(matches)
    """
    [{'something': 'hello'}]
    [{'user': 'Jarbas'}]
    """
```

# Caveats and known bugs

- extra spaces will be removed

- spaces in entities will be replaced with _ ```say {two words}```  -> ``` say {two_words}``` 
    
# Credits

JarbasAI

Heavily borrowed from [Padaos](https://github.com/MatthewScholefield/padaos)
