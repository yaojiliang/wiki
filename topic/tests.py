from django.test import TestCase

# Create your tests here.

l=[
    {'id':1,'parent_id':0},
    {'id':2,'parent_id':1},
    {'id':3,'parent_id':0},
    {'id':4,'parent_id':3},
]

l2=[]

for i in range(len(l)):
    dic = {}
    _list=[]
    dic['id']=l[i]['parent_id']
    for j in range(len(l2)):
        if dic['id'] == l2[j]['id']:
            continue
    dic['children']=l[i]['id']

    l2.append(dic)
print(l2)