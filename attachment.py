import base64
import os
import quopri
import re


class Attachment:
    def __init__(self, part, id_, save, parent=None):
        self.data = part
        self.save = save
        self.parent = parent
        self.id_ = id_
        # print(part)
        self.info = dict()
        Attachment.header_parse(self.data, self.info)
        # self.parent.header_parse(self.data, self.info)
        self.filename, self.encoded_data = self.parse_att()
        if self.save:
            self.save_attachment()

    def parse_att(self):
        encoded_att = self.data.split('\r\n\r\n')[1]
        content_dispos_ = "Content-Disposition"
        # print(self.part)
        content_dispos = (self.info[content_dispos_]
                          if content_dispos_ in self.info else
                          self.info[content_dispos_.lower()])
        if "filename" not in content_dispos:
            return "noname.html", encoded_att
        filename_ind = content_dispos.find("filename") + len('filename')
        while content_dispos[filename_ind] in ' =':
            filename_ind += 1
        if '"' in content_dispos[filename_ind:]:
            filename_ind += 1
        content_dispos = content_dispos[filename_ind:]
        filename = content_dispos
        if '"' in filename:
            filename = filename[:content_dispos.find('"')]
        return filename, encoded_att

    @staticmethod
    def filling_dictionary(header, info):
        for i, line in enumerate(header):
            if re.match(r'\w', line):
                line = line.split(':')
                key = line[0]
                value = ':'.join(line[1:])
                j = 1 if i < len(header) - 1 else 0
                if i + j == len(header):
                    break
                while re.match(r'\s', header[i + j]):
                    value += header[i + j]
                    j += 1
                    if i + j == len(header):
                        break
                info[key] = value

    @staticmethod
    def header_parse(message, info):
        header = message.split('\r\n\r\n')[0].split('\r\n')
        if message.startswith('+OK'):
            header = header[1:]
        Attachment.filling_dictionary(header, info)
        keys = list(info.keys()).copy()
        for key in keys:
            info[key.lower()] = info[key]

    def save_attachment(self, address=None):
        self.encoded_data = self.encoded_data.replace('\r\n', '')
        if 'base64' in self.info["Content-Transfer-Encoding"]:
            decoded = base64.b64decode(self.encoded_data)
        if 'quoted-printable' in self.info['Content-Transfer-Encoding']:
            decoded = quopri.decodestring(self.encoded_data)
        if not address:
            path = os.path.abspath(os.curdir)
            path += '/' + "Messages"
            if not os.path.exists(path):
                os.mkdir(path)
            path += '/' + str(self.id_)
            if not os.path.exists(path):
                os.mkdir(path)

            path += '/Attachments/'
            if not os.path.exists(path):
                os.mkdir(path)
        else:
            path = address
        if not path.endswith('/'):
            path += '/'
        with open(path + self.filename.replace('/', '-'), 'wb') as file_object:
            file_object.write(decoded)
