import curses

screen = curses.initscr()

subwin = curses.newwin(15, 20, 0, 0)
subwin.addstr(4, 4, "Hello from 4,4")
subwin.addstr(5, 15, "Hello from 5,15 with a long string")

subwin.refresh()
curses.napms(2000)

screen.clear()
screen.refresh()

subwin.mvwin(10, 10)
subwin.refresh()

curses.napms(1000)

subwin.clear()
subwin.refresh()
curses.napms(1000)
curses.endwin()