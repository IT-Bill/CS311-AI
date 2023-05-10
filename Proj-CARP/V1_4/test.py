from getopt import getopt
import sys

opts, args = getopt(sys.argv, "-t-s:")
print(opts, args)