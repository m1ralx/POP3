import socket
import poplib
import time
import quopri
import ssl
import sys
import email
from email.parser import Parser as Parser_msg
import base64
import re
import reader
import getpass

"""mail.split('\r\n\r\n', maxsplit=1)"""
# Обработка аргументов, интерфейс, класc

class Head_parser:
    def __init__(self):
        self.fromexp = r"^From:.*\s*?<(?P<FROM>.*?)>"
        self.toexp = r"^To:\s(?P<TO>.*)\s+"
        self.subjectexp = r"^Subject:\s*(?P<SUBJECT>(.*\s*)*?)^\w"
        self.dateexp = r"^Date:\s(?P<DATE>.*)\s+"
        self.exps = {'From': self.fromexp, 'To': self.toexp,
                     'Subject': self.subjectexp, 'Date': self.dateexp}

    @staticmethod
    def decode_subj_from_quopri(found):
        subject = ""
        for f in found:
            subject += f[2]
        if found[0][1].upper() == 'B':
            subject = (base64.b64decode(subject)
                       .decode(found[0][0], 'replace'))
        else:
            subject = (quopri.decodestring(subject)
                       .decode(found[0][0], 'replace'))
        subjects.write(subject)

    @staticmethod
    def decode_subj_from_base64(found):
        try:
            for f in found:
                subject = base64.b64decode(f[2]).decode()
                subjects.write(subject)
        except UnicodeDecodeError:
            text = ''.join([x[2] for x in found])
            subject = (base64.b64decode(text)
                       .decode(found[0][0], errors='replace'))
            subjects.write(subject)

    def get_info_for_message(self, msg):
        info = dict()
        for exp in self.exps:
            match = re.search(self.exps[exp], msg, re.MULTILINE)
            recived_info = ""
            if match:
                recv_dict = match.groupdict()
                data = recv_dict[exp.upper()].strip()
                if exp == "Subject":
                    found = re.findall(
                        r'=\?([a-zA-z0-9-]+)\?([bqBQ])'
                        r'\?([a-zA-Z0-9/_:,!+=]{4,})={0,2}\?',
                        data)
                    if found:
                        if not 'B' in [x[1].upper() for x in found]:
                            self.decode_subj_from_quopri(found)
                        else:
                            self.decode_subj_from_base64(found)
                        subjects.write('\n')
                    else:
                        subjects.write(recv_dict[exp.upper()].strip() + '\n')
                recived_info = recv_dict[exp.upper()].strip()
            info[exp] = recived_info

        return info

sock = poplib.POP3_SSL('pop.rambler.ru', port=995)._create_socket(1000)
# print(1)
socket_reader = reader.Reader(sock)

# # print(get('USER', 'pop3-test@rambler.ru'))
# # print(get('PASS', 'pop3test'))

# print(socket_reader.get('USER', 'lyceum0960@yandex.ru'))
# request = socket_reader.get('PASS', 'vbauvbui')
user = "pop3-test@rambler.ru"
psw = "pop3test"
# user = input()
# psw = getpass.getpass(prompt="Password: ")
print(socket_reader.get("USER", user))
request = socket_reader.get("PASS", psw)
print(request)
parser = Head_parser()
p = Parser_msg()
number_of_messages = int(request.split()[1])
count = 1


def handle():
    global part, content_type, msg, encoding
    for part in email.message_from_string(msg).walk():
        content_type = part.get_content_type()
        if content_type == "text/plain" or content_type == "text/html":
            msg = ''.join(
                re.split(r'\n\n([.\n]*)', str(part), re.DOTALL)[1:]).replace(
                '=\n', '')
            if part['Content-Transfer-Encoding'] == 'base64':
                encoding = 'base64'
                msg = msg.replace('\n', '')
                if len(msg) % 4 == 3:
                    msg += "="
                msg = base64.b64decode(msg).decode(part.get_content_charset(),
                                                   'replace')
                msgs.write(msg)
                break
            elif part["Content-Transfer-Encoding"] == 'quoted-printable':
                encoding = "quoted-printable"
                msg = quopri.decodestring(msg).decode(
                    part.get_content_charset(), 'replace')
                msgs.write(msg)
                break
            else:
                msgs.write(msg)
                break

                # break
                # elif "text/html" in part.get_content_type():
                #     msg = ''.join(re.split(r'\n\n([.\n]*)', str(part), re.DOTALL)[1:]).replace('=\n', '')
                #     if part['Content-Transfer-Encoding'] == 'quoted-printable':
                #         msg = quopri.decodestring(msg).decode(part.get_content_charset(), 'replace')
                #         msg = msg.replace("<br>", '\n')
                #         msg = msg.replace("</p>", '\n')
                #         msg = re.sub("<.*?>", "", msg)
                #         # msgs.write(msg)
                #         # print(msg)
                # else:
                #     msgs.write(msg)


with open('letters.txt', 'w') as file, open('msgs.txt', 'w') as msgs, \
        open('subjects.txt', 'w') as subjects:
    for i in range(4, number_of_messages + 1):
        msg = socket_reader.get('RETR', i)
        file.write(str(parser.get_info_for_message(msg)))
        file.write('\r\n----------------------------------\r\n\r\n')
        msg = '\n'.join(msg.split('\n')[1:])
        print(msg)
        encoding = ""
        parts = msg.split('\r\n\r\n')
        for i in range(1, len(parts)):
            if "Content-Type: text/" in parts[i-1]:
                text_message = parts[i]
                info = parts[i-1]
                break
        # encoding = msg.
        print(info)
        # break
        content_type_index = info.index('Content-Type: ')
        types = info[content_type_index:].split(';')
        content_type = types[0].split()[1]
        charset = types[1].split("=")[1].replace('"', '')
        # print(content_type, charset)
        # print(text_message.split('--')[0])
        # break
        # print(msg.split('\r\n\r\n', maxsplit=1)[1])
        # handle()
# print(recv_timeout(sock))
# user = 'pop3-test@rambler.ru'
# psw = 'pop3test'
# sock.close()
