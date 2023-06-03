import lib.bytes as b

class Message:
    def build(bytes):
        pass

class MidiMessage:
    def __init__(self, note, velocity, state, channel=1):
        self.note = note
        self.velocity = velocity
        self.state = state
        self.channel = channel
    
    def bytes(self):
        return b.message([
            b.int1(2),
            b.int1(self.note),
            b.int1(self.velocity),
            b.int1(self.state),
            b.int1(self.channel)
        ])

    def build(bytes):
        msg = MidiMessage(0, 0, 0, 0)
        msg.note, _ = b.read_int1(bytes, 0)
        msg.velocity, _ = b.read_int1(bytes, 1)
        msg.state, _ = b.read_int1(bytes, 2)
        msg.state, _ = b.read_int1(bytes, 3)
        return msg

class ArpMessage:
    def __init__(self, note, velocity, state, method, rate, swing_pct, up_note_cnt, velocity_automation, dynamic_pct, bpm, channel=1):
        self.note = note
        self.velocity = velocity
        self.state = state
        self.method = method
        self.rate = rate
        self.swing_pct = swing_pct
        self.up_note_cnt = up_note_cnt
        self.velocity_automation = velocity_automation
        self.dynamic_pct = dynamic_pct
        self.bpm = bpm
        self.channel = channel
    
    def bytes(self):
        return b.message([
            b.int1(3),
            b.int1(self.note),
            b.int1(self.velocity),
            b.int1(self.state),
            b.int1(self.method),
            b.int1(self.rate),
            b.int1(self.swing_pct),
            b.int1(self.up_note_cnt),
            b.int1(self.velocity_automation),
            b.int2(self.dynamic_pct),
            b.int2(self.bpm),
            b.int1(self.channel),
        ])
    
    def build(bytes):
        pass
    
class ChordMessage:
    def __init__(self, note, velocity, state, bpm, chord_type, chord_level, transpose, arp_delay, channel=1):
        self.note = note
        self.velocity = velocity
        self.state = state
        self.bpm = bpm
        self.chord_type = chord_type
        self.chord_level = chord_level
        self.transpose = transpose
        self.arp_delay = arp_delay
        self.channel = channel
    
    
    def bytes(self):
        return b.message([
            b.int1(4),
            b.int1(self.note),
            b.int1(self.velocity),
            b.int1(self.state),
            b.int1(self.chord_type),
            b.int1(self.chord_level),
            b.int1(self.transpose),
            b.int1(self.arp_delay),
            b.int2(self.bpm),
            b.int1(self.channel),
        ])

    def build(bytes):
        pass