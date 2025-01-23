'''
Utility program to merge multiple PDFs into a sinlge PDF.

Input can be a list of PDFs, or a folder.  In the case of a folder, all PDFs found within
this folder will be merged.

Output will be named result.pdf
'''

from pypdf import PdfWriter
import sys
import os

def generateList(args):

    # Look at the first arg.  If it is a file, then we have a list of files
    # Otherwise if it is a folder, we will loop through the files in that folder.

    pdfs = []
    changed = False
    if os.path.isfile(args[1]):
        for file in args[1:]:
            pdfs.append(file)
    else:

        # This is a folder
        cwd = os.getcwd()

        if not (cwd == args[1]) and not (args[1] == "."):
            os.chdir(args[1])
            changed = True

        for files in os.listdir():
            if os.path.splitext(files)[1][1:].upper() == 'PDF':
                pdfs.append(files)

        # in this case, sort the array of pdfs
        pdfs.sort()

        if changed == True:
            os.chdir(cwd)

    return pdfs

def merge(pdfs):

    merger = PdfWriter()
    number = len(pdfs)
    for pdf in pdfs:
        merger.append(pdf)

    merger.write('result.pdf')
    merger.close()
    for pdf in pdfs:
        print(f'{pdf}')
    print('merged into result.pdf')


def main():
    
    args = sys.argv

    if len(args) < 2:
        print("Did you forget something...?")
        print("pdfmerg <file1, file2,... | folder name>")
        sys.exit()

    pdfs = generateList(args)

    merge(pdfs)

    return

if __name__ == "__main__":
    main()