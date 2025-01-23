import argparse
from calendar import isleap
import csv
from datetime import datetime
import logging
from PIL import Image, ImageDraw, ImageFont
import sys


# build a list of workout categories and apply a color
categories = {}

# Set up some defaults
BAND_WIDTH = 50
BAND_HEIGHT = 10
CIRCLE_DIAMETER = 40
MAX_CATEGORIES = 3
DAYS_PER_LINE = 14
IMAGE_WIDTH = 750
IMAGE_HEIGHT = 1500
PEN = 0

colors_dict = {
    'Running': 0xB96C54,
    'Meditation': 0xC0B5B7,
    'Strength': 0x6B796A,
    'Walking': 0x339189,
    'Cardio': 0x35F6A2,
    'Yoga': 0xD8FCFE,
    'Cycling': 0xED6FB9,
    'Stretching': 0x27752B
}

colors = [
    0xA6CEE3,
    0x1F78B4,
    0xB2DF8A,
    0x33A02C,
    0xFB9A99,
    0xE31A1C,
    0xFDBF6F,
    0xFF7F00,
    0xCAB2D6,
    0x6A3D9A,
    0xFFFF99,
    0xB1592b
]

def draw_ledgend(canvas, year, shape):
    x = 0
    y = 0
    myfont = ImageFont.truetype('Arial', 25)
    canvas.text((x+300, y), year, font=myfont, fill=(0,0,0))
    for key in categories:
        if shape.upper() == 'R':
            canvas.rectangle([x, y, x + 25, y + 25], categories[key])
        if shape.upper() == 'C':
            canvas.ellipse([x, y, x + 25, y + 25], categories[key])

        canvas.text((x + CIRCLE_DIAMETER + 10, y), key, font=myfont, fill=(0, 0, 0))
        y+= CIRCLE_DIAMETER
        global PEN
        PEN = y
    return
def draw_days_rectangles(canvas, workouts):
#def draw_day_rectangles(canvas, x, y, day):
    x = 0
    y = PEN
    day = 0
    logging.debug(f'x = {x}, y = {y}')
    
    for day in range(len(workouts)):
        yy = y
        for i in range(len(workouts[day])):
            canvas.rectangle([x, yy, x + BAND_WIDTH - 1, yy + BAND_HEIGHT -1 ], categories[workouts[day][i]])
            yy+= BAND_HEIGHT
        x+= BAND_WIDTH
        if day % DAYS_PER_LINE == 0:
            day = 0
            y += BAND_HEIGHT*MAX_CATEGORIES + BAND_HEIGHT
            x = 0
        
    return

def draw_days_circles(canvas, workouts):
    x = CIRCLE_DIAMETER
    y = PEN
    day = 0
    for day in range(len(workouts)):
        radius =  CIRCLE_DIAMETER/2
        for i in range(len(workouts[day])):
            canvas.ellipse([(x-radius, y-radius), (x+radius, y+radius)], categories[workouts[day][i]])
            radius -= CIRCLE_DIAMETER / len(workouts[day])/2

        x+= CIRCLE_DIAMETER + 10
        if day % DAYS_PER_LINE == 0:
            day = 0
            y += BAND_HEIGHT*MAX_CATEGORIES + BAND_HEIGHT
            x = CIRCLE_DIAMETER
    return

def main():

    # get the current year
    current_year = datetime.now().year

    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument('-f', '--file', help='csv input file', required=True)
    parser.add_argument('-y', '--year', help='year to check (current is default)', default=current_year)
    parser.add_argument('-d', '--debug', help='Log debugging info', action='store_true')
    parser.add_argument('-s', '--shape', help='(C)ircle, (R)ectangle', required=True)
    
    args = parser.parse_args()

    if getattr(args, 'debug') == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)
        
        
    # build the list of the workouts
    with open(getattr(args, 'file'), mode='r') as file:
        csv_reader = csv.DictReader(file)

        workout_data = [
            row for row in csv_reader
            if datetime.strptime(row['Workout Date'], '%m/%d/%y').year == int(getattr(args, 'year'))                
        ]



    for workout in workout_data:
        category = workout['Fitness Discipline']
        if category not in categories:
            categories[category] = ""

    # check to see that we have enough colors
    if len(categories) > len(colors):
        logging.error(f'There are not enough colors, you need {len(categories)}')
        sys.exit()
    else:
        index = 0
        for category in categories:
            categories[category] = colors[index]
            index += 1

    logging.debug(f'categories: {categories}') 

    # Add day of year to each entry
    for entry in workout_data:
        date_obj = datetime.strptime(entry['Workout Date'], "%m/%d/%y")
        entry['day_of_year'] = date_obj.timetuple().tm_yday

    # dump as test
    logging.debug(workout_data)

    workouts = []
    for i in range(367):
        workouts.append([])

    for entry in workout_data:
        if entry['Fitness Discipline'] not in workouts[entry['day_of_year']]:
            workouts[entry['day_of_year']].append(entry['Fitness Discipline'])

        #if not 'Length (minutes)' in workouts[entry['day_of_year']]:
        #    workouts[entry['day_of_year']].append(int(entry['Length (minutes)']))
        #else:
        #    length = workouts[entry['day_of_year']]


    logging.debug(workouts)
    height = IMAGE_HEIGHT
    width = IMAGE_WIDTH

    image = Image.new("RGB", (width, height), (255, 255, 255))
    d = ImageDraw.Draw(image)

    draw_ledgend(d, getattr(args, 'year'), getattr(args, 'shape'))
    for i in range(len(workouts)):
        logging.debug(f'{i}: {workouts[i]}')

    if getattr(args, 'shape').upper() == 'R':
        draw_days_rectangles(d, workouts)
    if getattr(args, 'shape').upper() == 'C':
        draw_days_circles(d, workouts)

    #myfont = ImageFont.truetype('Arial', 25)
    #d.text((0, 50), "bite me", font=myfont, fill=(0, 0, 0))

    image.show()

    return

if __name__ == '__main__':
    main()
