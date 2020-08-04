from django.test import TestCase

# Create your tests here.
a = {'alg': 'SALT_MD5', 'code': 200, 'data': {'guessTerms': [], 'hotTerms': [], 'defaultTerms': []},
 'md5': '164ac31d0be8d40096d5d9dfce92a256', 'message': 'Terms  List.'}
b = 200
if not(b in a or b in a.values()):
    print("333333333")
else:
    print("44444444444")
