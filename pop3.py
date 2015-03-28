import socket
import ssl
import time


class POP3:
    def __init__(self, host, port=995, type_=None):
        self.host = host
        self.port = port
        self.sock = None
        self.type = type_

    def create_socket(self):
        if self.type != 'ssl':
            sock = socket.socket()
            self.port = 110
        else:
            sock = ssl.SSLSocket(socket.socket())
        sock.settimeout(2)
        try:
            sock.connect((self.host, self.port))
        except socket.timeout:
            self.port = 995 if self.port == 110 else 110
            sock.settimeout(1)
            if self.port == 995:
                sock = ssl.SSLSocket(socket.socket())
            else:
                sock = socket.socket()
            sock.settimeout(1)
            try:
                sock.connect((self.host, self.port))
            except socket.timeout:
                print("incorrect host/port. restart program plz")
                return -1
            except socket.gaierror:
                return -1
        except socket.gaierror:
            return -1
        self.sock = sock

    def retr(self, number):
        return self._send_command('RETR', number)

    def user(self, email_addr):
        res = (self._send_command('USER', email_addr))
        return res

    def pass_(self, password):
        request = (self._send_command('PASS', password))
        try:
            number_of_messages = int(request.split()[1])
            print("Number of messages: ", number_of_messages)
        except ValueError:
            pass
        except IndexError:
            pass
        return request

    def reconnect(self):
        print('reconnecting..')
        self.create_socket()
        print('Done')

    def _send_command(self, *command):
        str_command = '{} ' * len(command)
        str_command = str_command[:-1] + '\r\n'
        try:
            self.sock.send(str_command.format(*command).encode())
        except ConnectionAbortedError:
            print('Connection is lost')
            return -1
        d = self.recv_data()
        return d

    def stat(self):
        return_value = self._send_command('STAT')
        # print(repr(return_value))
        if not return_value or return_value == -1:
            return -1
        rets = return_value.split()
        num_messages = -1
        size_messages = -1
        for val in rets:
            if val.isnumeric():
                if num_messages == -1:
                    num_messages = int(val)
                else:
                    size_messages = int(val)
        return num_messages, size_messages

    def list(self, number=None):
        if number:
            return self._send_command('LIST', number)
        return self._send_command('LIST')

    def get_several_messages(self, start, end):
        # res = list()
        for i in range(start, end + 1):
            msg = self.retr(i)
            if not msg or msg == -1:
                print("Connection is lost")
                yield -1
                return
            else:
                yield msg
        # return res

    def dele(self, number):
        if not self._send_command('DELE', number):
            print("Connection is lost")
            quit()

    def rset(self):
        if not self._send_command('RSET'):
            print("Connection is lost")
            quit()

    def top(self, message_num):
        # print(message_num)
        retval = self._send_command('TOP', message_num, 0)
        if not retval or retval == -1:
            print("Connection is lost")
            # quit()
            return -1
        return retval

    def recv_data(self, timeout=2):
        self.sock.setblocking(0)
        total_data = []
        begin = time.time()
        while 1:
            if total_data and time.time() - begin > timeout:
                break
            elif time.time() - begin > timeout * 2:
                break
            self.sock.settimeout(2)
            try:
                data = self.sock.recv(2 ** 20)
                if data:
                    total_data.append(data)
                    begin = time.time()
                else:
                    time.sleep(0.1)
            except ssl.SSLWantReadError:
                pass
            except ConnectionAbortedError:
                return -1
            except socket.timeout:
                break
        total_data = b''.join(total_data)
        try:
            result = total_data.decode()
        except UnicodeDecodeError:
            encoding = total_data.lower().split(b'charset=')[1]
            encoding = encoding[:encoding.find(b'\r')].strip().replace(
                b'"', b'')
            return total_data.decode(encoding=encoding.decode())

        return result
        # return b''.join(total_data).decode()  #  (encoding="ISO-8859-1")  #
        # utf-8???

    def quit(self):
        self._send_command("QUIT")
        self.sock.close()
        print("The session ended")

# if __name__ == "__main__":
#     pop3 = POP3("pop.rambler.ru")
#     user = 'pop3-test@rambler.ru'
#     psw = 'pop3test'
#     pop3.user(user)
#     pop3.pass_(psw)
#     num_messages, total_size = pop3.stat()
#     print(pop3.get_several_messages(6))
    # m = (pop3.retr(1))
    # text_message = ''
    # parts = m.split('\r\n\r\n')
    # for i in range(0, len(parts)):
    #     if "Content-Type: text/" in parts[i-1]:
    #         text_message = parts[i]
    #         info = parts[i-1]
    #         break
    # found = re.search(r"Content-Transfer-Encoding:\s(.*)\r\n"
    #                   r"Content-Type:\s(.*);.*=(.*)\r\n", info)
    # content_transfer_encoding = found.group(1)
    # content_type = found.group(2)
    # charset = found.group(3)
