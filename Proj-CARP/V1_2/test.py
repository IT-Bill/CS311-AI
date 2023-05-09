from getopt import getopt
import sys

print(sys.argv)
opts, args = getopt(sys.argv, "-t :")



print(opts, args)