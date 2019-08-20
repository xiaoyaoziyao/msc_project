
n = int(input())
list = list(range(1,n+1))
b = []
while(len(list)>1):
    list.pop(0)
    b.append(list[0])
    a = list[0]
    list.pop(0)
    list.append(a)
print(b)



