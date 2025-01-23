'''
Fun program to plot 3n+1
'''

import sys

def main():

    peaks = []
    line = []
    x = 0

    if(len(sys.argv) < 2):
        print('Whoops, you need to supply a seed number')
        sys.exit()

    # Move import of plotly here, after the commandline argument check for performance.
    import plotly.express as px

    start = int(sys.argv[1])
    num = start
    count = 0
    while num > 1:
        if num % 2 != 0:
            num = num * 3 + 1
        else:
            num = num / 2
           
        count +=1
        #print(count, int(num))
        peaks.append(num)
        line.append(x)
        x = x + 1

    for peak in peaks:
        print(peak)

    fig = px.line(x=line, y=peaks)
    fig.update_layout(
        title={
            'text':f"3n+1 for {start:,}",
            'x': .5})
    fig.show()

if __name__ == '__main__':
    main()
