# auto_regex
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/micro/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)](https://en.cryptobadges.io/donate/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/jarbasai)
<span class="badge-patreon"><a href="https://www.patreon.com/jarbasAI" title="Donate to this project using Patreon"><img src="https://img.shields.io/badge/patreon-donate-yellow.svg" alt="Patreon donate button" /></a></span>
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/JarbasAl)

regex automated

# install

install from pip

       pip install auto_regex
    
or install from github with pip

        pip install git+https://github.com/JarbasAl/auto_regex
           
or install from source

        git clone https://github.com/JarbasAl/auto_regex
        cd auto_regex
        python setup.py install
        
or just bundle the python file with your project, it is standalone
        
# usage

importing the module

    from autoregex import AutoRegex

    a = AutoRegex()
  
generating a regex expression

    texts = ["say {word}", "repeat {word}"]
    for regex_expression in a.get_expressions(texts):
      print(regex_expression)
 
 outputs
 
    ^\W*say\W*(?P<word>.*?\w.*?)\W*$
    ^\W*repeat\W*(?P<word>.*?\w.*?)\W*$


extracting entities from regex

      lines= ["say {word}", "repeat {word}"]
      query = "say hello"
      a.create_regex(lines)
      for ent in a.get_entities(query):
          print(ent)
          
outputs

      {'word': 'hello'}
      
      
matching regexes
      
      lines= ["say {word}", "repeat {word}"]
      query = "say i am a bot, blip blop"
      a.create_regex(lines)
          for e in a.get_matches(query):
              print(e)
              
outputs

      {
        'query': 'say i am a bot, blip blop', 
        'entities': {'word': 'i am a bot, blip blop'}, 
        'regexes': ['^\\W*repeat\\W*(?P<word>.*?\\w.*?)\\W*$']
      }


while there is no documentation take a look at the [unittests](test.py) to have an idea of expected behaviour and use cases


# Caveats and known bugs

- extra spaces will be removed

- spaces in entities will be replaced with _

    say {two words} -> say {two_words}
    
- sentences become lower case

# Credits

JarbasAI


Heavily borrowed from [Padaos](https://github.com/MatthewScholefield/padaos)
