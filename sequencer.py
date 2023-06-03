#!/usr/bin/python3

"""
VPadSequencer提供一个步进音序器（Step Sequencer）

Key Bindings:
移动光标 : 选择当前按钮位置
hjkl   : 选择当前按钮位置
空格    : 切换当前按钮打开/关闭状态

< : 活动区间左移
> : 活动区间右移
p : 播放/停止
q : 退出

除此之外，该脚本还建立了反向代理服务器，配合VPadClient中提供的`VPadSequencer.preset.json`预设，可以将客户端的消息解析成
音序器的对应操作。

控制消息-Play : 播放/停止
控制消息-Stop : 停止
控制消息-Undo : 活动区间左移
控制消息-Redo : 活动区间右移
MidiOn消息0~63: 当前活动区间中的对应按钮打开（一个区间中正好有64个按钮）
MidiOff消息0~63: 当前活动区间中的对应按钮关闭（一个区间中正好有64个按钮）
"""

import curses
import time
import sys
from lib.main import *
from lib.server import *
from lib.message import *
import threading


COLOR_STATUSBAR_APP_NAME = 1
COLOR_STATUSBAR_ALARM = 2
COLOR_SEQ_ACTIVE_SPAN = 3
COLOR_SEQ_INACTIVE_SPAN = 4
COLOR_SEQ_PROGRESS_COL = 5
COLOR_SEQ_CURSOR = 6

MIDI_NOTE_START = 36

appname = " VPadSequencer "
alarm = " Press 'q' to exit "
log = ""


SEQ_COLS = 64  # Control the columns of the sequencer. It must be the power of the eight
SEQ_LINES = 8  # Control the lines of the sequencer.
span = 0       # Control the active span. A span is 8 consecutive columns.
playing = False# Control playing state. When playing is True, We send midimessage to server, and progress line is moving
cursor_x = 0   # Control user cursor x
cursor_y = 0   # Control user cursor y
playtime = 0   # playtime


# This data structure is the core of sequencer. It indicate wether the sequencer button toggled
# True is light and False is off
matrix = [[False for _ in range(SEQ_COLS)] for _ in range(SEQ_LINES)]
bpm = 130 # The bpm of sequencer
interval = 60 * 1000000000 // bpm // 2
ticks = 0

def get_matrix_char(i, j):
    ch = '▮' if matrix[i][j] else '▯'
    return ch

span_counter = [0 for _ in range(SEQ_COLS//8)]
max_span = 0
def turn_on(x, y):
    global max_span
    span = y // 8
    if max_span < span: max_span = span
    span_counter[span] += 1
    matrix[x][y] = True

def turn_off(x, y):
    global max_span
    span = y // 8
    span_counter[span] -= 1
    matrix[x][y] = False
    if max_span == span:
        # 找到下一个max_span
        for c in reversed(range(0, span)):
            if span_counter[c] != 0:
                max_span = c
                return
        # 没找到
        max_span = 0
  
def toggle_light(x, y):
    if matrix[x][y]:
        turn_off(x,y)
    else: 
        turn_on(x,y)

def toggle_playing():
    global playing, playtime, ticks
    playing = not playing
    if playing:
        ticks = -1
        playtime = time.perf_counter_ns()

def incr_bpm(newbpm):
    global bpm, interval
    bpm+=newbpm
    interval = 60 * 1000000000 // bpm // 4
  

def print_ui(msg):
    global log
    log = str(msg)

def init_basic():
    curses.curs_set(0) # This call made the cursor invisable
    # curses.use_default_colors() # Use default color 
    curses.init_pair(COLOR_STATUSBAR_APP_NAME, curses.COLOR_MAGENTA, curses.COLOR_GREEN)
    curses.init_pair(COLOR_STATUSBAR_ALARM, curses.COLOR_RED, curses.COLOR_GREEN)
    curses.init_pair(COLOR_SEQ_ACTIVE_SPAN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_SEQ_INACTIVE_SPAN, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(COLOR_SEQ_PROGRESS_COL, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_SEQ_CURSOR, curses.COLOR_RED, curses.COLOR_BLACK)

def status_bar(scr):
    line = curses.LINES-1; col = 0; bpm_chars = 11

    bemoji = ' '
  
    if bpm < 60:
        bemoji = '🥱'
    elif bpm < 100: 
        bemoji = '😀'
    elif bpm < 180:
        bemoji = '😁'
    elif bpm < 250:
        bemoji = '😆'
    else:
        bemoji = '😇'

    scr.addstr(line, col, appname, curses.color_pair(COLOR_STATUSBAR_APP_NAME) | curses.A_BOLD); col += len(appname)
    scr.addstr(line, col, alarm, curses.color_pair(COLOR_STATUSBAR_ALARM)); col += len(alarm)
    spaces = ' ' * (curses.COLS-bpm_chars-col-1)
    scr.addstr(line, col, spaces, curses.color_pair(COLOR_STATUSBAR_APP_NAME)); col += len(spaces)
    scr.addstr(line, col, "%s[BPM:%3d]"%(bemoji, bpm), curses.color_pair(COLOR_STATUSBAR_APP_NAME))

def sequencer(scr):
    top   = (curses.LINES // 2) - (SEQ_LINES // 2)
    left  = (curses.COLS // 2) - (SEQ_COLS // 2)

    spanstart = span * 8
    spanend   = spanstart + 8 - 1
    for l in range(SEQ_LINES):
        for c in range(SEQ_COLS):
            if l == cursor_x and c == cursor_y:
                scr.addstr(top+l, left+c, get_matrix_char(l, c), curses.color_pair(COLOR_SEQ_CURSOR))
            elif ticks % (max_span * 8 + 8) == c and playing:
                scr.addstr(top+l, left+c, get_matrix_char(l, c), curses.color_pair(COLOR_SEQ_PROGRESS_COL))
            elif c>=spanstart and c<=spanend:
                scr.addstr(top+l, left+c, get_matrix_char(l, c), curses.color_pair(COLOR_SEQ_ACTIVE_SPAN))
            else:
                scr.addstr(top+l, left+c, get_matrix_char(l, c), curses.color_pair(COLOR_SEQ_INACTIVE_SPAN))

def logmessage(scr):
    scr.addstr(curses.LINES-2, 0, log)

def draw_ui(scr):
    scr.erase()
    status_bar(scr)
    sequencer(scr)
    logmessage(scr)
    scr.refresh()

def send_message():
    y = ticks % (max_span * 8 + 8)
    for x in range(SEQ_LINES):
        if matrix[x][y]:
            MidiMessageToggle(x+MIDI_NOTE_START, 90)

def handle_ticks():
    global ticks
    if playing:
        if time.perf_counter_ns() - playtime >= (ticks * interval):
            ticks+=1
            send_message()
def incrspan():
    global span
    if span+1 < SEQ_COLS // 8:
        span+=1
def decrspan():
    global span
    if span > 0:
        span-=1
def handle_keypress(key):
    if key == None: return
    print_ui(f'current pressed key {key}, maxspan {max_span}')
    global span, cursor_x, cursor_y, matrix, playing, bpm 
    if key == '>': incrspan()
    elif key == '<': decrspan()
    elif key == 'KEY_UP' or key == 'k': cursor_x = (cursor_x - 1) % SEQ_LINES
    elif key == 'KEY_DOWN' or key == 'j': cursor_x = (cursor_x + 1) % SEQ_LINES
    elif key == 'KEY_LEFT' or key == 'h': cursor_y = (cursor_y - 1) % SEQ_COLS
    elif key == 'KEY_RIGHT' or key == 'l': cursor_y = (cursor_y + 1) % SEQ_COLS
    elif key == ' ': toggle_light(cursor_x, cursor_y)
    elif key == 'p': toggle_playing()
    elif key == '=': 
        if bpm < 999: incr_bpm(1)
    elif key == '+':
        if bpm < 990: incr_bpm(10)
    elif key == '-':
        if bpm > 1: incr_bpm(-1)
    elif key == '_': 
        if bpm > 10: incr_bpm(-10)

def get_key(scr):
    try: 
        return scr.getkey()
    except:
        return None
  
def tui(scr):
    init_basic()
    scr.nodelay(True)
    draw_ui(scr)
    key = get_key(scr)
    while key != 'q':
        handle_ticks()
        handle_keypress(key)
        draw_ui(scr)
        key = get_key(scr)
        #curses.napms(1) # sleep 1ms to avoid busy cpu spin
        time.sleep(0.001)
def main():
    if len(sys.argv) < 2:
        print("Usage: sequencer.py <vpad server host>")
        sys.exit(1)

    # init client
    Connect(sys.argv[1])

    # init reverse server
    def start_server():
        def message_handler(message):
            if isinstance(message, HandShakeMessage):
                print_ui(f'Handshake from [{message.name}]')
                return HandShakeMessage('VPadSequencer', 'Python')
            elif isinstance(message, MidiMessage):
                print_ui(f'MidiMsg {message.note} state {message.state}')
                if message.state == 1:
                    turn_on(message.note // 8, span*8 + message.note % 8)
                else:
                    turn_off(message.note // 8, span*8 + message.note % 8)
            elif isinstance(message, ControlMessage):
                print_ui(f'ControlMessage op {message.operation}')
                if message.op == COP_PLAY: toggle_playing()
                elif message.op == COP_STOP and playing: toggle_playing()
                elif message.op == COP_UNDO: decrspan()
                elif message.op == COP_REDO: incrspan()
            return None
        Server().listen(message_handler)
    threading.Thread(target=start_server).start()
    curses.wrapper(tui)
if __name__ == '__main__':
    main()
