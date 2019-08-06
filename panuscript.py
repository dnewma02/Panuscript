import sys
from src.cli import *

def main():
    print('add gui stuff as main function')

if __name__ == '__main__':
    # run command line, else script
    if len(sys.argv) > 1: run(sys.argv)
    else: main()
