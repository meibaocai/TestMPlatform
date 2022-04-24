# -!- coding: utf-8 -!-

# Create your tests here.
# a = {'alg': 'SALT_MD5', 'code': 200, 'data': {'guessTerms': [], 'hotTerms': [], 'defaultTerms': []},
#  'md5': '164ac31d0be8d40096d5d9dfce92a256', 'message': 'Terms  List.'}
# b = 200
# if not(b in a or b in a.values()):
#     print("333333333")
# else:
#     print("44444444444")
import os,sys
a=123
print(f'{a}')

name = '宝元'
age = 18
sex = '男'
msg = F'姓名：{name},性别：{age}，年龄：{sex}'  # 大写字母也可以
msg = f'姓名：{name},性别：{age}，年龄：{sex}'
print(msg)