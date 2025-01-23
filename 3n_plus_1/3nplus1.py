import sys

max = 0
for n in range(10000):
    num = n
    max = 0
    n = num
    count = 0
    while num > 1:
        if num % 2 != 0:
            num = num * 3 + 1
        else:
            num = num / 2
        
        if num > max:
            max = num
        count +=1
    print(n, " max: ", int(max), " count: ", count)
