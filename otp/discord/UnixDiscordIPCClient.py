import os
import socket

from otp.discord.DiscordIPCClient import DiscordIPCClient


class UnixDiscordIPCClient(DiscordIPCClient):

    def _connect(self):
        self._f = socket.socket(socket.AF_UNIX)
        pipePattern = self._getPipePattern()
        for i in range(10):
            path = pipePattern.format(i)
            if not os.path.exists(path):
                continue

            try:
                self._f.connect(path)
                break
            except:
                continue
        else:
            self._close()

    def _write(self, data):
        if self._closed:
            return

        self._f.sendall(data)

    @staticmethod
    def _getPipePattern():
        envKeys = ('XDG_RUNTIME_DIR', 'TMPDIR', 'TMP', 'TEMP')
        for envKey in envKeys:
            dirPath = os.environ.get(envKey)
            if dirPath:
                break
        else:
            dirPath = '/tmp'

        return os.path.join(dirPath, 'discord-ipc-{}')
