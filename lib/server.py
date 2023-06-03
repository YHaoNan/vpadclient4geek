import lib.message as message
import lib.constants as constants
import lib.bytes as b
import socketserver
"""
This is an easy vpad server framework
can receive vpad message and pass it to you

You can use this to build a full vpad server
or make a reverse proxy to the real vpad server

An example of reverse proxy is ../sequencer.py
"""

_BUFFER_SIZE = 1024

_MESSAGE_OBJ = {
    1: message.HandShakeMessage,
    2: message.MidiMessage,
    3: message.ArpMessage,
    4: message.ChordMessage,
    8: message.ControlMessage
}

class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        while True:
            self.data = self.request.recv(_BUFFER_SIZE)
            # 如果没有数据了 跳出循环
            if len(self.data) == 0: break
            self.offset = 0
            while self.offset < len(self.data):
                message_bytes = self.read_an_message_bytes()
                op = message_bytes[0]
                if op not in _MESSAGE_OBJ:
                    print(f"UNKNOWN MESSAGE {message_bytes}")
                else:
                    ret = self.server.callback(_MESSAGE_OBJ[op].build(message_bytes[1:]))
                    if ret != None:
                        self.request.send(bytes(ret.bytes()))


    def skip_bytes(self, n):
        self.offset += n

    def read_an_message_bytes(self):
        # 读取一个消息的首两个字节，这个字节代表消息的长度
        length, n = b.read_int2(self.data, self.offset)
        # 跳过读取的字节
        self.skip_bytes(n)

        # 读取消息体，这个消息体已经不包含代表长度两个字节了
        message_bytes = b.slice(self.data, self.offset, length)
        # 跳过该消息，执行完这行，self.offset应该在下一条消息首部
        self.skip_bytes(length)
        return message_bytes

class Server:

    """
    listening on port 1236
    when received an message, call callbackfn with message
    you can return an other message to indicate you wanna reply the client
    """
    def listen(self, callbackfn):
        #self.usercallback = callbackfn
        _server = socketserver.ThreadingTCPServer(('0.0.0.0', constants.SERVER_PORT), ServerHandler)
        _server.allow_reuse_address = True
        _server.daemon_threads = True
        _server.callback = callbackfn
        _server.serve_forever()
