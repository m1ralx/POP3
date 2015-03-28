import unittest
from unittest.mock import MagicMock, Mock
# from unittest.mock import *
import pop3
import email_parser
import socket
import ssl


class Test(unittest.TestCase):
    msg1 = ""
    msg2 = ""
    msg3 = ""
    att = ""
    parsed = list()
    part = ""
    cur = ""
    stat = """+OK Welcome.
+OK 482 9303391"""

    def setUp(self):
        with open('msg1.txt', 'r') as file1, open('msg2.txt', 'r') as file2,\
                open('msg3.txt', 'r') as file3, open('msg3att.txt','r') as f_att:
            def read_all(file, is_msg=True):
                ans = ""
                for line in file:
                    ans += line
                if is_msg:
                    return ans.replace('\n', '\r\n')
                else:
                    return ''.join(ans.split('\n'))
            self.msg1 = read_all(file1)
            self.msg2 = read_all(file2)
            self.msg3 = read_all(file3)
            self.att = read_all(f_att, False)

    def test_pop(self):
        pop = pop3.POP3('pop.gmail.com')
        pop._send_command = MagicMock(return_value=self.msg1)
        self.assertEqual(pop.retr(1), self.msg1)
        pop.type = 'nossl'
        pop.create_socket()
        pop.sock.close()
        self.assertTrue(type(pop.sock) == ssl.SSLSocket)
        pop.type = 'ssl'
        pop.host = 'mail.e1.ru'
        pop.sock = None
        pop.create_socket()
        pop.sock.close()
        self.assertTrue(type(pop.sock) == socket.socket)

    def test_sock(self):
        pop = pop3.POP3('pop.gmail.com')
        pop.create_socket()



        l_msg1 = len(self.msg1)
        part1 = str(self.msg1)[:int(l_msg1/3)]
        itr = iter([b'', self.part.encode(), b''])
        self.part = part1

        def effect(arg):
            self.cur = next(itr)
        pop.sock.recv = MagicMock(side_effect=effect, return_value=self.cur)
        try:
            self.assertEqual(pop.retr(1), part1)
        except StopIteration:
            pop._send_command = MagicMock(return_value=self.stat)
            self.assertEqual(pop.stat(), (482, 9303391))
            pop.sock.close()

    def test_parse(self):
        pop = pop3.POP3('pop.gmail.com')
        itr = iter([self.msg1, self.msg2, self.msg3])
        pop.get_several_messages = MagicMock(return_value=itr)
        for num, msg in enumerate(pop.get_several_messages()):
            parsed_msg = email_parser.Parser(msg, save=True, id_=num)
            self.parsed.append(parsed_msg)
            # self.assertEqual(parsed_msg.from_, 'Алексей Миронов mironov.alexey.fiit.urfu@gmail.com')
            # self.assertEqual(parsed_msg.to, 'pop3-test@rambler.ru Not implemented')

    def test_message_info(self):
        self.test_parse()
        self.assertTrue(self.parsed[-1].attachments)
        self.assertEqual(self.parsed[-1].text, "No text in the message")
        self.assertEqual(self.parsed[-1].subject, 'picture')
        self.assertEqual(self.parsed[0].text, 'Многострочное\r\nПисьмо\r\nLALALA\r\n')
        self.assertEqual(self.parsed[1].text, 'No text in the message')
        self.assertEqual(self.parsed[-1].attachments[0].encoded_data, self.att)
        self.assertEqual(self.parsed[1].from_, 'okulovsky  notifications@github.com')
        self.assertEqual(self.parsed[0].from_, 'Алексей Миронов mironov.alexey.fiit.urfu@gmail.com')
        self.assertEqual(self.parsed[1].to, 'Iwan9544/FoolsGame  FoolsGame@noreply.github.com')
        self.assertEqual(self.parsed[0].to, 'pop3-test@rambler.ru Not implemented')

if __name__ == '__main__':
    unittest.main()
