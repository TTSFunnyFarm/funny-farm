from otp.discord.DiscordIPCClient import DiscordIPCClient


class WinDiscordIPCClient(DiscordIPCClient):
    _pipePattern = R'\\?\pipe\discord-ipc-{}'

    def _connect(self):
        for i in xrange(10):
            path = self._pipePattern.format(i)
            try:
                self._f = open(path, 'w+b')
            except:
                self._close()
            else:
                break
        else:
            self._close()

    def _write(self, data):
        if self._closed:
            return

        data = bytes(data)
        self._f.seek(0, 2)
        self._f.write(data)
        self._f.flush()
