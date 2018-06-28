# auto_regex
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

    
# Credits

JarbasAI


Heavily borrowed from [Padaos](https://github.com/MatthewScholefield/padaos)
