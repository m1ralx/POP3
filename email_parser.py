import re
import quopri
import base64
import os
from encodings.aliases import aliases

import attachment


class Parser:
    def __init__(self, email, id_, save=False):
        self.message = email
        self.id_ = id_ - 1
        self.save = save
        # print(email)
        # return
        # self.subject = self.get_subject()
        self.info = {}
        # self.header_parse(self.message, self.info)
        self.get_info(self.message, self.info)

        # self.header_parse(self.message, self.info)
        # self.to = self.info["To"]
        self.subject = (Parser.get_decoded_string(self.info["subject"],
                                                  info=self.info)
                        if "subject" in self.info else "No subject")
        self.from_ = self.get_from_to("From").strip()
        self.to = self.get_from_to("To").strip()
        self.date = self.info["date"] if "date" in self.info else "No date"
        self.text = "\r\n\r\n".join(self.message.split("\r\n\r\n")[1:]).strip()
        # print(self.message)
        self.parts = [x.strip() for x in self.get_parts(self.message)[1:]]
        # print(len(self.parts))
        if not self.parts:
            self.handle_singlepart()
        self.parts[-1] = '\r\n'.join(self.parts[-1].split("\r\n")[:-2]).strip()
        self.text = self.get_text()
        self.attachments = self.get_attachments()
        self.attacments_names = '\r\n'.join([att.filename for att in self.attachments])
        if self.save:
            self.save_message()

    @staticmethod
    def get_info(message, info):
        return attachment.Attachment.header_parse(message, info)

    @staticmethod
    def find(headers_value):
        return re.findall(
            r'=\?([a-zA-Z0-9-]+)\?([bqBQ])'
            r'\?([a-zA-Z0-9\[/_:,\."\]!+=#-]{4,})={0,2}\?', headers_value,
            re.MULTILINE)

    def get_from_to(self, param):
        param = param.lower()
        if param not in self.info:
            return "Not implemented field"

        pair = [x for x in self.info[param].split('<') if len(x) > 0]
        name = pair[0]
        addr = pair[1][:-1] if len(pair) > 1 else ""
        name = self.get_decoded_string(name, subject=False, info=self.info)
        return " ".join((name, addr))

    @staticmethod
    def get_decoded_string(input_string, subject=True, info=None):
        found = Parser.find(input_string)
        # print("----------------------------")
        # print(found)
        if not found:
            if subject:
                return info['subject'].strip()
            return input_string
        res = ''
        if found[0][1].upper() == "B":
            try:
                res = ''.join([base64.b64decode(found[i][2]).decode(found[i][0])
                               for i in range(len(found))])
                return res
            except UnicodeDecodeError:
                for part in found:
                    if part[1].upper() == "B":
                        res += (part[2].strip())
                res = Parser.decode_b64(res, found[0][0])
        else:
            for part in found:
                res += Parser.decode_quopri(part[2].strip(), part[0])
        return res

    @staticmethod
    def header_parse(message, info):
        header = message.split('\r\n\r\n')[0].split('\r\n')[1:]
        attachment.Attachment.filling_dictionary(header, info)

    def get_text(self):
        for num, part in enumerate(self.parts):
            if "content-type: text/" in part.lower():
                break
        text = self.parse_part(part)
        # print(text)
        # print("PART!:", part)
        if not text:
            # import pprint
            # pprint.pprint(self.parts)
            return "No text in the message"
        encoding, charset = self.get_text_info()
        # print(text)
        # print(encoding, charset)
        if encoding != "None":
            if encoding.lower() == 'base64':
                text = text.replace('\r\n', '')
                return self.decode_b64(text, charset)
            elif encoding.lower() == 'quoted-printable':
                # text = text.replace('\r\n', '')  #
                # print(text)
                try:
                    return self.decode_quopri(text, charset)
                except ValueError:
                    return text
            else:
                return text
        else:
            return text

    def parse_part(self, part):
        return '\r\n\r\n'.join(part.split('\r\n\r\n')[1:])

    def get_text_info(self):
        for part in self.parts:
            if "content-type: text/" in part.lower():
                # print("PART!:", part)
                info = dict()
                attachment.Attachment.header_parse(part, info)
                ctype = "Content-Type"
                if 'content-type' in info:
                    ctype = 'content-type'
                elif ctype not in info:
                    ctype = "Content-type"
                charset_index = info[ctype].find('charset=') + len(
                    'charset=')
                info[ctype] = info[ctype][charset_index:]
                index_end = info[ctype].find(';')
                if index_end == -1:
                    index_end = len(info[ctype])
                charset = info[ctype][:index_end].replace('"', '')
                cde = "Content-Transfer-Encoding"
                if cde in info:
                    content_transfer_encoding = info[cde].strip()
                elif cde.lower() in info:
                    content_transfer_encoding = info[cde.lower()].strip()
                elif cde in self.info:
                    content_transfer_encoding = self.info[cde].strip()
                elif cde.lower() in self.info:
                    content_transfer_encoding = self.info[cde.lower()].strip()
                else:
                    content_transfer_encoding = "None"
                # print("ENCODING:", content_transfer_encoding)
                return content_transfer_encoding, charset

    def get_parts(self, text):
        # print(text)
        b = "boundary="
        index_of_bound = text.find(b) + len(b)
        text = text[index_of_bound:]
        index_of_bound_end = text.find('\r\n')
        boundary = text[:index_of_bound_end].replace('"', '')\
            .strip()\
            .replace(';', '')
        # print('BOUND', repr(boundary))
        parts = re.split(r"--" + boundary + r"[^-]", text)
        # pprint(parts)
        # print('-------------------------------------------------------')

        # if 'multipart' in parts[0]:
        #     parts[1] = parts[0] + parts[1]
        #     parts = parts[1:]
        # print('here:', len(parts))
        result = []
        for part in parts:
            if "multipart" not in part:
                result.append(part)
            else:
                result += self.get_parts(part)
                # print("!!!!!!", len(result))
                # print(result)
        # print('PARTS:', len(result))
        return result

    def handle_singlepart(self):
        bound = "Content-Type:"
        bound2 = "Content-type:"
        if bound not in self.message:
            bound = bound.lower()
        if bound not in self.message:
            bound = bound2
        text = bound + bound.join(self.message.split(bound)[1:])
        self.parts.append(text)

    def get_attachments(self):
        att = "Content-Disposition: attachment"
        parts_with_att = list()
        for part in self.parts:
            if att in part or att.lower() in part:
                parts_with_att.append(part)
        attchmts = list()
        for part in parts_with_att:
            attchmts.append(attachment.Attachment(part, self.id_, self.save))
        return attchmts

    @staticmethod
    def decode_b64(string, charset):
        return base64.b64decode(string).decode(charset, 'replace')

    @staticmethod
    def decode_quopri(string, charset):
        # print(list(aliases.items()))
        # if charset.lower() != 'koi8-r':
        charset = charset.replace('-', '_').lower()
        if charset not in aliases.keys() and charset not in aliases.values():
            # print(1111111)
            return quopri.decodestring(string).decode(errors='replace')
        return quopri.decodestring(string).decode(charset, 'replace')

    def save_message(self):
        path = os.path.abspath(os.curdir)
        path += '/' + "Messages"
        if not os.path.exists(path):
            os.mkdir(path)
        path += '/' + str(self.id_) + '/'
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + str(self.id_) + ".txt", 'w') as file_object:
            file_object.write(str(self))

    def __str__(self):
        string = "Number: " + str(self.id_) + '\r\n'
        if not self.attachments:
            string += ("From: " + self.from_ + '\nTo: ' + self.to +
                      '\nDate: ' + self.date + '\nSubject: '
                      + self.subject + '\nMessage:\n' + self.text + '\r\n\r\n')
        else:
            string += ("From: " + self.from_ + '\nTo: ' + self.to +
                      '\nDate: ' + self.date + '\nSubject: ' +
                      self.subject + '\nMessage:\n' + self.text +
                      "\r\n\r\nAttachments:\r\n" +
                      self.attacments_names + '\r\n\r\n')
        return string

# if __name__ == "__main__":
#     # pop = pop3.POP3("pop.rambler.ru")
#     pop = pop3.POP3("pop.yandex.ru")
#     # user = 'pop3-test@rambler.ru'
#     # psw = 'pop3test'
#     user = 'lyceum0960@yandex.ru'
#     psw = 'vbauvbui'
#
#     pop.user(user)
#     pop.pass_(psw)
#     print(Parser(pop.retr()))
#     # pop.dele(36)
#     pop.quit()
#     # for msg in pop.get_several_messages(1, 36):
#     #     p = Parser(msg)
#     #     print(p)
#         # print(p.subject)
