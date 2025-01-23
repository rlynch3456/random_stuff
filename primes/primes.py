'''
Some fun plotting prime numbers after watching this video: https://www.youtube.com/watch?v=EK32jo7i5LQ&t=505s.

Next step will be to use some python plotting library directly.
'''

import math
import sys

def isPrime(n):
    if n % 2 == 0 and n > 2:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True
number = 0
count = 0
maximum = 100
args = sys.argv

if len(args) < 2:
    print("Did not supply input number, try again...")
    sys.exit()

try:
    number = int(args[1])
except:
    print("You did not supply a number, try again...")

if len(args) == 3:
    try:
        maximum = int(args[2])
    except:
        print("You did not enter a number for maximum, default is 100")

print "maximum = ", maximum

for i in range(2, number):
    if count > maximum:
        break
    if isPrime(i):
        print i*math.sin(i), i*math.cos(i)
        count += 1
