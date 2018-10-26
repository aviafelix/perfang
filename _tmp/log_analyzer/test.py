import simplejson as json
from jsoncomment import JsonComment

parser = JsonComment(json)

config = parser.load(open('test.config', 'r', encoding='utf-8'))
print(config)

