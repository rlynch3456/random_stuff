from PIL import Image
from random import randint

#points = [(0, 0), (150, 300), (300, 0)]
points = [(0, 299), (150, 0), (299, 299)]

image = Image.new("RGB", (400,400), (0, 0, 0))

x = y = 300

for _ in range(1_000_000):
	point = randint(0,2)
	x = int((x + points[point][0]) /2)
	y = int((y + points[point][1]) /2)
	image.putpixel((x,y), (255, 255, 255))

image.show()