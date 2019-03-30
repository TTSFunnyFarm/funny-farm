import json
import os
import struct
import sys
import uuid

from direct.directnotify import DirectNotifyGlobal

from otp.discord.DiscordIPCGlobals import *


class DiscordIPCClient:
    """
    DiscordIPCClient is the base class used for implementing the Discord Rich
    Presence API by communicating with an open Discord instance via its JSON IPC.

    To properly use this class, call DiscordIPCClient.forPlatform with your clientId
    and (optionally) your platform. This will resolve to either WinDiscordIPCClient or
    UnixDiscordIPCClient, depending on the current platform. Supports context handler protocol.
    """
    notify = DirectNotifyGlobal.directNotify.newCategory('DiscordIPCClient')

    def __init__(self, clientId):
        self.clientId = clientId
        self._closed = False
        self._f = None  # Must be overridden by subclass.
        try:
            self._connect()
            self._doHandshake()
            self.notify.debug('Connected via ID %s' % clientId)
        except:
            self.notify.debug('No connection or handshake')
            self._close()

    @classmethod
    def forPlatform(cls, clientId, platform=sys.platform):
        if platform == 'win32':
            from otp.discord.WinDiscordIPCClient import WinDiscordIPCClient
            return WinDiscordIPCClient(clientId)
        else:
            from otp.discord.UnixDiscordIPCClient import UnixDiscordIPCClient
            return UnixDiscordIPCClient(clientId)

    def _doHandshake(self):
        retOp, retData = self.sendRecv({'v': 1, 'client_id': self.clientId}, op=OP_HANDSHAKE)
        if retOp == OP_FRAME and retData['cmd'] == 'DISPATCH' and retData['evt'] == 'READY':
            return
        else:
            raise RuntimeError(retData)

    def _recvExactly(self, size):
        buf = b''
        sizeRemaining = size
        while sizeRemaining:
            chunk = self._recv(sizeRemaining)
            buf += chunk
            sizeRemaining -= len(chunk)

        return buf

    def close(self):
        if self._closed:
            return

        try:
            self.send({}, op=OP_CLOSE)
        except:
            pass

        self._close()

    def sendRecv(self, data, op=OP_FRAME):
        if self._closed:
            self.notify.debug('Closed')
            return None, None

        try:
            nonce = data.get('nonce')
            self.send(data, op=op)
        except:
            self.notify.debug('Send failed')
            return None, None

        try:
            header = self._recvExactly(8)
            op, length = struct.unpack('<II', header)
            payload = self._recvExactly(length)
            data = json.loads(payload.decode('utf-8'))
        except:
            self.notify.debug('Recv failed')
            return None, None

        if data.get('nonce') == nonce:
            return op, data
        else:
            self.notify.debug('Unexpected reply')
            return None, None

    def send(self, data, op=OP_FRAME):
        dataStr = json.dumps(data, separators=(',', ':'))
        dataBytes = dataStr.encode('utf-8')
        header = struct.pack('<II', op, len(dataBytes))
        self._write(header)
        self._write(dataBytes)

    def _recv(self, size):
        if hasattr(self._f, 'recv'):
            _method = self._f.recv
        else:
            _method = self._f.read

        return _method(int(bytes(size)))

    def _close(self):
        self._closed = True
        try:
            self._f.close()
            del self._f
        except:
            pass

    def setActivity(self, activity):
        data = {
            'cmd': 'SET_ACTIVITY',
            'args': {'pid': os.getpid(),
                     'activity': activity},
            'nonce': str(uuid.uuid4())
        }
        return self.sendRecv(data)

    def _connect(self):
        pass  # Must be overridden by subclass.

    def _write(self, data):
        pass  # Must be overridden by subclass.
