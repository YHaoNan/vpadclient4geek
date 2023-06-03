import curses

scr = curses.initscr()

pad = curses.newpad(100, 100)
pad.addstr("This text is thirty characters");


i=0
while True:
    pad.refresh(0, i, 5, 5, 15, 20)
    curses.napms(100)
    i=(i+1)%30

curses.endwin()