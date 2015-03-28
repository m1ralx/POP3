import unittest
import attachment
import email_parser
import pop3
import threading
import socket
import ssl


def create_server():
    def create_sock():
        # server = ssl.SSLSocket(socket.socket())  # socket.AF_INET, socket.SOCK_STREAM
        # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server = socket.socket()
        # server = ssl.SSLSocket(server)
        server.bind(('', 995))
        server.listen(1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return server
    server = create_sock()
    conn, addr = server.accept()
    # print('Connected with ' + addr[0] + ':' + str(addr[1]))
    # conn = ssl.SSLSocket(conn)

    def recv_data():
        data = b''
        block = 1024
        while True:
            conn.settimeout(0.5)
            try:
                current = conn.recv(block)
            except socket.timeout:
                current = b''
            data += current
            if current == b'':
                break
        return data

    while 1:
        # data = conn.recv(1024)
        data = recv_data()
        print('server:', data)
        if not data or data == b'QUIT':
            break
        conn.send(data)
    conn.close()
    server.close()


# class Tests(unittest.TestCase):
#     def setUp(self):
#         threading.Thread(target=create_server).start()

try:
    threading.Thread(target=create_server).start()
    sock = socket.socket()
    sock.connect(('localhost', 995))

    def recv_data():
        data = b''
        block = 1024
        while True:
            sock.settimeout(0.5)
            try:
                current = sock.recv(block)
            except socket.timeout:
                current = b''
            # except ConnectionAbortedError:
            #     pass
            data += current
            if current == b'':
                break
        return data.decode()

    def client():
        try:
            for i in range(6):
                print('client sended')
                sock.send(b'QUIT1')
                import time
                # time.sleep(1)
                print('client', recv_data())
        except ConnectionAbortedError:
            pass
        finally:
            sock.close()
    threading.Thread(target=client).start()

    # create_server()
except ConnectionAbortedError:
    print("Closed")