import codecs
import random

words = codecs.open('words.txt','r','utf-8').readlines()

rates = {'，': 15,
         '。': 10,
         '？': 6,
         '！': 4,
         '……': 1,
         '、': 2}

alphabet = [char for char, rate in rates.items() for i in range(rate)]

count = 500

result = ''

for i in range(count):
    result += random.choice(words).strip()
    if random.random() < 0.23 and result[-1] not in alphabet:
        result += random.choice(alphabet)
    if random.random() < 0.02 and result[-1] not in alphabet:
        result += random.choice('。？！') + '\n\n'

if result[-1] != '\n' and result[-1] not in alphabet:
    result += random.choice('。？！')

print(result)
