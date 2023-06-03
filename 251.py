#!/usr/bin/python3
from lib.main import *
import sys

Connect(sys.argv[1])
ChordMessageToggle(D_3, 90, chord_type=CT_MINOR, chord_level=CL_L13, interval=2)
ChordMessageToggle(G_3, 90, chord_type=CT_MAJOR, chord_level=CL_L11, transpose=1, interval= 2)
ChordMessageToggle(C_3, 90, chord_type=CT_MAJOR, chord_level=CL_L9, interval= 2)
ChordMessageToggle(C_3, 90, chord_type=CT_MAJOR, chord_level=CL_L11, interval=1)
ChordMessageToggle(C_3, 90, chord_type=CT_MAJOR, chord_level=CL_L9, interval=1)