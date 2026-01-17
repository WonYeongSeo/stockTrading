
from datetime import datetime
from helper.constants import CONST_JUMP_START_TIME
from helper import util
from kiwoom.stock import Stock

list_2 = []
s1 = Stock('11', 'AA', 1000, 0)
list_2.append(s1)
s2 = Stock('33', 'bbb', 2000, 0)
list_2.append(s2)
s3 = Stock('44', 'AA', 3000, 0)
list_2.append(s3)

list_1 = []
c2 = Stock('22', 'ddd', 4000, 0)
list_1.append(c2)

c1 = Stock('11', 'AA', 900, 0)
list_1.append(c1)

c1 = Stock('11', 'AA', 1100, 0)
list_1.append(c1)

for c in list_1 :
    print(c.code, c.name, c.price)
print('====')
for c in list_2 :
    l = list(filter(lambda x: x.code == c.code, list_1))
    if l :
        a = l[0]
        list_1.remove(a)
print('----')
for c in list_1 :
    print(c.code, c.name, c.price)


#__delay_time = CONST_JUMP_START_TIME - datetime.now()
# __delay_time = (CONST_JUMP_START_TIME - datetime.now()).total_seconds()
# print(f'### {__delay_time} 후에 시작!!')