#!/usr/bin/env python3
import sys

for i in range(1, len(sys.argv)):
    print(chr(int(sys.argv[i])), end="")
