from lib.client import *
import lib.message as message
from threading import Lock
import time

# we have 128 connection channel
_conns = [None for _ in range(128)]

_conns_lock = Lock()

"""
在channel通道上（0~127）尝试与host建立连接
"""
def Connect(host, channel=0):
    assert channel >=0 and channel <= 127 , "channel must in [0, 127]"

    # first check
    if _conns[channel] != None:
        raise "There is already have a connection [%s] in channel {}" % (_conns[channel], channel)

    cli = Client(host)
    if cli.connect():
        _conns_lock.acquire()
        # double check
        if _conns[channel] != None:
            _conns_lock.release()
            raise "There is already have a connection [%s] in channel {}" % (_conns[channel], channel)
        _conns[channel] = cli
        _conns_lock.release()
    else:
        raise "Cannot create connection"

def Close(channel=0):
    assert channel >=0 and channel <= 127 , "channel must in [0, 127]"

    _conns_lock.acquire()
    if _conns[channel] == None:
        _conns_lock.release()
        raise "There is no connection in channel {}" % (channel)
    _conns[channel].close()
    _conns[channel] = None
    _conns_lock.release()
    
    

def _get_ch_conn(channel):
    assert channel >=0 and channel <= 127 , "channel must in [0, 127]"
    _conns_lock.acquire()
    if _conns[channel] == None:
        _conns_lock.release()
        raise "There is no connection in channel %d, please call Connnect(host, %d)" % (channel, channel)
    conn = _conns[channel]
    _conns_lock.release()
    return conn

"""
Send a midi message to server in specific connchannel
"""
def MidiMessage(note, velocity, state, channel=1, connchannel=0):
    _get_ch_conn(connchannel).send(
        message.MidiMessage(note, velocity, state, channel)
    )

"""
Send a midi on message to server in specific connchannel
"""
def MidiMessageOn(note, velocity, channel=1, connchannel=0):
    MidiMessage(note, velocity, state=1, channel=channel, connchannel=connchannel)
"""
Send a midi off message to server in specific connchannel
"""
def MidiMessageOff(note, velocity, channel=1, connchannel=0):
    MidiMessage(note, velocity, state=0, channel=channel, connchannel=connchannel)

"""
Send a midi on message and a midi off message continously
If interval is None(by default), send midi off immediately after midi on.
Otherwise, we send midi on and sleep interval seconds, then midi off.
This function will block when interval is not None;
"""
def MidiMessageToggle(note, velocity, channel=1, connchannel=0, interval=None):
    MidiMessageOn(note, velocity, channel, connchannel)
    if interval != None:
        time.sleep(interval)
    MidiMessageOff(note, velocity, channel, connchannel)

"""
Send a arp message to server in specific connchannel
"""
def ArpMessage(note, velocity, state, method=M_UP, rate=R_1_8, swing_pct=0, up_note_cnt=4, velocity_automation=V_UP, dynamic_pct=20, bpm=130, channel=1, connchannel=0):
    _get_ch_conn(connchannel).send(
        message.ArpMessage(note, velocity, state, method, rate, swing_pct, up_note_cnt, velocity_automation, dynamic_pct, bpm, channel)
    )
"""
Send a arp message with state on to server in specific connchannel
"""
def ArpMessageOn(note, velocity, method=M_UP, rate=R_1_8, swing_pct=0, up_note_cnt=4, velocity_automation=V_UP, dynamic_pct=20, bpm=130, channel=1, connchannel=0):
    ArpMessage(note, velocity, 1, method, rate, swing_pct, up_note_cnt, velocity_automation, dynamic_pct, bpm, channel, connchannel=connchannel)
"""
Send a arp message with state off to server in specific connchannel
"""
def ArpMessageOff(note, velocity, method=M_UP, rate=R_1_8, swing_pct=0, up_note_cnt=4, velocity_automation=V_UP, dynamic_pct=20, bpm=130, channel=1, connchannel=0):
    ArpMessage(note, velocity, 0, method, rate, swing_pct, up_note_cnt, velocity_automation, dynamic_pct, bpm, channel, connchannel=connchannel)
"""
Send a arp on message and a arp off message continously
If interval is None(by default), send arp off immediately after arp on.
Otherwise, we send arp on and sleep interval seconds, then arp off.
This function will block when interval is not None;
"""
def ArpMessageToggle(note, velocity, method=M_UP, rate=R_1_8, swing_pct=0, up_note_cnt=4, velocity_automation=V_UP, dynamic_pct=20, bpm=130, channel=1, connchannel=0, interval=None):
    ArpMessageOn(note, velocity, method, rate, swing_pct, up_note_cnt, velocity_automation, dynamic_pct, bpm, channel, connchannel=connchannel)
    if interval != None:
        time.sleep(interval)
    ArpMessageOff(note, velocity, method, rate, swing_pct, up_note_cnt, velocity_automation, dynamic_pct, bpm, channel, connchannel=connchannel)

"""
Send a chord message to server in specific connchannel
"""
def ChordMessage(note, velocity, state, bpm=130, chord_type=CT_MAJOR, chord_level=CL_L7, transpose=0, arp_delay=20, channel=1, connchannel=0):
    _get_ch_conn(connchannel).send(
        message.ChordMessage(note, velocity, state, bpm, chord_type, chord_level, transpose, arp_delay, channel)
    )
"""
Send a chord message with state on to server in specific connchannel
"""
def ChordMessageOn(note, velocity, bpm=130, chord_type=CT_MAJOR, chord_level=CL_L7, transpose=0, arp_delay=20, channel=1, connchannel=0):
    ChordMessage(note, velocity, 1, bpm, chord_type, chord_level, transpose, arp_delay, channel, connchannel)
"""
Send a chord message with state off to server in specific connchannel
"""
def ChordMessageOff(note, velocity, bpm=130, chord_type=CT_MAJOR, chord_level=CL_L7, transpose=0, arp_delay=20, channel=1, connchannel=0):
    ChordMessage(note, velocity, 0, bpm, chord_type, chord_level, transpose, arp_delay, channel, connchannel)

"""
Send a chord on message and a chord off message continously
If interval is None(by default), send chord off immediately after chord on.
Otherwise, we send chord on and sleep interval seconds, then chord off.
This function will block when interval is not None;
"""
def ChordMessageToggle(note, velocity, bpm=130, chord_type=CT_MAJOR, chord_level=CL_L7, transpose=0, arp_delay=20, channel=1, connchannel=0, interval=None):
    ChordMessageOn(note, velocity, bpm, chord_type, chord_level, transpose, arp_delay, channel, connchannel)
    if interval != None:
        time.sleep(interval)
    ChordMessageOff(note, velocity, bpm, chord_type, chord_level, transpose, arp_delay, channel, connchannel)

def SendMessage(message, connchannel=0):
    _get_ch_conn(connchannel).send(message)