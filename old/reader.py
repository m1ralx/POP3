import time
import ssl


class Reader:
    def __init__(self, sock):
        self.sock = sock

    def recv_timeout(self, the_socket, timeout=2):
        the_socket.setblocking(0)
        total_data = []
        begin = time.time()
        while 1:
            if total_data and time.time() - begin > timeout:
                break
            elif time.time()-begin > timeout*2:
                break
            try:
                data = the_socket.recv(8192)
                if data:
                    total_data.append(data)
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except ssl.SSLWantReadError:
                pass
        return b''.join(total_data).decode()

    def get(self, cmd='', arg1='', arg2=''):
        self.sock.send("{} {}\r\n".format(cmd, arg1, arg2).encode())
        return self.recv_timeout(self.sock)