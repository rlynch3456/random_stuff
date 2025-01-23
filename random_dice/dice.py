'''
Having some fun plotting random dice rolls.
'''
from PIL import Image, ImageDraw
from random import randint

#colors = [(0,0,0), (0,0,0), (255, 255, 255), (227, 227, 227), (204, 204, 204), (181, 181, 181), (158, 158, 158), 
#		(135, 135, 135), (112, 112, 112), (89, 89, 89), (66, 66, 66), (43, 43, 43), (0, 0, 0)]

colors = [(0,0,0), (255, 255, 255), (204, 204, 204), (158, 158, 158), (112, 112, 112), (66, 66, 66), (0, 0, 0)]

height = 500
width = 500

image = Image.new("RGB", (width, height), (0, 0, 0))

# get a drawing context
d = ImageDraw.Draw(image)
for x in range(0, height-1, 2):
	for y in range(0, width-1, 2):
		roll = randint(1, 6)
		print(roll)
		d.rectangle([x,y, x+1, y+1], colors[roll])

image.show()
image.save("dice.png", "PNG")
