#!/usr/bin/env python3
import argparse
import socket
import getpass
import os

import email_parser
import pop3


def handle_args():
    parser = argparse.ArgumentParser(usage="main.py\nFollow instructions")
    parser.add_argument('--config', '-c', help='path to config file with login,'
                                               ' password and host')
    parser.add_argument('--type', '-t', help='type of socket')
    parser.add_argument('--host', '-ho', help='host')
    parser.add_argument('--user', '-u', help='email address')
    parser.add_argument('--pswd', '-p', help='password')
    parser.add_argument('--save', '-s', action='store_true', help=
                        'true/false argument for saving attachments '
                        'and text of message')
    return parser.parse_args()


def handle_msgs(current, res, save):
    try:
        for msg in res:
            if msg == -1:
                return -1
            if not msg:
                print("something went wrong")
                continue
            if "-ERR" in msg or "no such message" in msg:
                print("No such message")
                return -2
            current += 1
            try:
                # print(msg)
                print(email_parser.Parser(msg, current, save))
            except UnicodeEncodeError:
                print("I can't print this message, cuz fcking retard "
                      "console doesn't support these characters")
    except UnicodeDecodeError:
        # print(e)
        # import sys, traceback
        # print(traceback.print_tb(sys.exc_info()[2]))
        # print(sys.exc_traceback)
        # traceback.print_stack()
        print("INCORRECT ENCODING IN MESSAGE")


def get_host_value(args, get_host, user):
    if not args.host:
        host = input("Please enter domain your email or grant "
                     "this built-in function:\n")
        if not host:
            while "@" not in user:
                print('incorrect username. Enter correct username plz')
                user = input()
            host = get_host(user)
    else:
        host = args.host
    return host


def get_pswd_value(args):
    pswd = ''
    if not args.pswd:
        while not pswd:
            print("Please enter your password:\n")
            pswd = getpass.getpass()
            if pswd:
                break
    else:
        pswd = args.pswd
    return pswd


def get_user_value(args):
    user = ''
    while not args.user or user:
        user = input('Please enter your login:\r\n')
        if user:
            break
    else:
        user = args.user
    return user


def fill_commands_dict(change, change_save, commands, connect, get_stat,
                       get_subject_list, pop, list_, save_to):
    commands['connect'] = connect
    commands['get'] = pop.get_several_messages
    commands['delete'] = pop.dele
    commands['quit'] = pop.quit
    commands['list'] = list_
    commands['change'] = change
    commands['saving'] = change_save
    commands['stat'] = get_stat
    commands['top'] = pop.top
    commands['saveto'] = save_to
    keys = list(commands.keys())
    for key in keys:
        commands[key.upper()] = commands[key]


def main():

    def get_host(user):
        return 'pop.'+user[user.index('@') + 1:]

    args = handle_args()
    CONFIG = ''
    if args.config:
        CONFIG = args.config

    def get_value(line):
        if len(line.split()) < 2:
            return
        return line.split()[1]

    def get_info_from_config():
        user = host = pswd = ''
        if not os.path.exists(CONFIG):
            user, pswd, host = get_info()
        else:
            with open(CONFIG, 'r') as config_file:
                for line in config_file:
                    if line.upper().startswith('USER'):
                        user = get_value(line)
                        if not user:
                            user = get_user_value(args)
                    if line.upper().startswith('PSWD'):
                        pswd = get_value(line)
                        if not pswd:
                            pswd = get_pswd_value(args)
                    if line.upper().startswith('HOST'):
                        host = get_value(line)
                        if not host:
                            host = get_host_value(args, get_host, user)
        if not user:
            user = get_user_value(args)
        if not pswd:
            pswd = get_pswd_value(args)
        if not host:
            host = get_host_value(args, get_host, user)
        return user, pswd, host

    def get_info():
        user = get_user_value(args)
        pswd = get_pswd_value(args)
        host = get_host_value(args, get_host, user)
        return user, pswd, host

    if args.config:
        user, pswd, host = get_info_from_config()
    else:
        user, pswd, host = get_info()


    save = False
    if args.save:
        save = True
    type_ = args.type
    pop = pop3.POP3(host, type_=type_)
    commands = {}

    def connect():
        nonlocal host, user, pswd
        pop.host = host
        created = pop.create_socket()
        while created == -1:
            print('incorrect host')
            user, pswd, host = change()
            pop.host = host
            created = pop.create_socket()
        ans = pop.user(user)
        ps = pop.pass_(pswd)
        ans += ps
        stat = pop.stat()
        if '-ERR' in ans or stat == -1 or stat == (-1, -1):
            return -1

    def change():
        args.host = ''
        args.user = ''
        args.pswd = ''
        return get_info()

    def save_to(message_num, address):
        msg = next(commands['get'](message_num, message_num))
        if msg == -1:
            return -1
        if not msg or (msg.startswith('-ERR') and 'no such' in msg):
            print('No such message')
            return
        if not os.path.exists(address):
            os.mkdir(address)
        parsed_message = email_parser.Parser(msg, message_num)
        if not address.endswith('/'):
            address += '/'
        with open(address + str(message_num) + '.txt', 'w') as tfile:
            tfile.write(msg)
        for att in parsed_message.attachments:
            att.save_attachment(address)

    def get_subject_list(*args):
        if not args:
            current_ind = 1
            while True:
                msg = commands['top'](current_ind)
                if msg == -1:
                    print('Connection is lost')
                    yield -1
                    return
                if not msg or '-ERR' in msg or 'no such message' in msg:
                    # print('No such message')
                    yield -2
                    break
                try:
                    info = dict()
                    email_parser.Parser.get_info(msg, info)
                    subj = (email_parser.Parser.get_decoded_string(
                        info['subject'], info=info)
                        if "subject" in info else "No subject")
                    yield (current_ind, subj)
                except UnicodeDecodeError:
                    yield "Incorrect encoding in message"
                current_ind += 1
        elif len(args) == 1:
            index = int(args[0])
            msg = commands['top'](index)
            if msg == -1:
                yield -1
                return
            if not msg or '-ERR' in msg or 'no such message' in msg:
                    print('No such message')
                    yield -2
                    return
                    # break
            try:
                info = dict()
                email_parser.Parser.get_info(msg, info)
                subj = (email_parser.Parser.get_decoded_string(
                    info['subject'], info=info)
                    if "subject" in info else "No subject")
                yield (index, subj)
            except UnicodeDecodeError:
                yield "Incorrect encoding in message"
        else:
            for i in range(int(args[0]), int(args[1]) + 1):
                msg = commands['top'](i)
                if msg == -1:
                    yield -1
                    return
                if not msg or '-ERR' in msg or 'no such message' in msg:
                    print('No such message')
                    yield -2
                    break
                try:
                    info = dict()
                    email_parser.Parser.get_info(msg, info)
                    subj = (email_parser.Parser.get_decoded_string(
                        info['subject'], info=info)
                        if "subject" in info else "No subject")
                    yield (i, subj)
                except UnicodeDecodeError:
                    yield "Incorrect encoding in message"

    def list_(*args):
        msg = pop.list(*args)
        if msg == -1:
            return -1
        if msg.startswith('-ERR') and 'no such' in msg:
            print('No such message')
            return
        print(msg)

    def get_stat():
        num_messages, size_messages = pop.stat()
        print("Messages:", num_messages)
        print("Total size:", size_messages)

    def change_save():
        nonlocal save
        print("state", save)
        if save:
            save = False
            print("save emails and attachments are disabled")
        else:
            save = True
            print("save emails and attachments are enabled")

    fill_commands_dict(change, change_save, commands, connect, get_stat,
                       get_subject_list, pop, list_, save_to)
    help_dict = dict()
    help_dict['get'] = ("usage:  get iLeft [iRight]"
                       "displays a message (the message list of the interval)")

    def help_():
        print("COMMANDS:")
        for command in {x.lower() for x in commands}:
            print(command)
    help_()
    commands['help'] = help_
    connected = False
    while True:
        if not connected:
            print("Connecting..")
            while connect() == -1:
                print("incorrect login/pswd/host")
                print("try with the correct data")
                user, pswd, host = change()
            print("DONE.")
            connected = True
        line = input("Your command: ").split()
        if not line:
            continue
        command = line[0]
        if command.lower() == 'quit':
            break
        if command.lower() == 'change':
            user, pswd, host = change()
            connect()
            connected = True
            continue
        if not connected and command != 'connect':
            # print('The first command must be \"connect\"')
            connect()
            connected = True
            continue
        # if command.lower() == 'list':

        if command.lower() == 'top':
            subj_list = get_subject_list(*line[1:])
            for subj in subj_list:
                if subj == -1:
                    connected = False
                    continue
                if subj == -2:
                    break
                try:
                    print(subj[0], "Subject: ", subj[1])
                except UnicodeEncodeError:
                    print("I can't print this subj, cuz fcking retard "
                          "console doesn't support these characters")
            continue
        if command.lower() not in commands:
            print("INCORRECT COMMAND")
            continue
        if command.lower() == 'saveto':
            if len(line[1:]) < 2 or len(line) > 3:
                print('USE: saveto message_number path_to_save')
                print('INCORRECT COMMAND')
                continue
            try:
                msg_num = int(line[1:][0])
            except ValueError:
                print("INCORRECT COMMAND")
                continue
            addr = line[2]
            res = commands['saveto'](msg_num, addr)
            if res == -1:
                connected = False
                continue
            continue
        try:
            command_args = tuple(int(arg) for arg in line[1:])
        except ValueError:
            print('INCORRECT COMMAND')
            continue

        if command.lower() == 'stat' and len(command_args) > 0:
            print('INCORRECT COMMAND')
            continue
        if (command.lower() == 'get' or command.lower() == 'delete') and\
                not len(command_args):
            print('INCORRECT COMMAND')
            continue
        # if command == ''
        if command.lower() == 'get' and len(command_args) == 1:
            command_args += (command_args[0],)
        if command.lower() == 'connect':
            if connected:
                continue
            else:
                try:
                    if connect() == -1:
                        connected = False
                        print('INCORRECT USERNAME/PASSWORD')
                        exit()
                    else:
                        connected = True
                        continue
                except socket.gaierror:
                    print("INCORRECT HOST")
                    pop.host = input('plz enter correct host:\n')
                    connected = False
                    continue

        if not pop.sock._closed:
            if command != 'connect':
                res = commands[command.lower()](*command_args)
                if res == -1:
                    print("DISCONNECTED")
                    connected = False
                    continue
        else:
            print('try to restart')
            commands['quit']()
        if command.lower() == 'get':
            current = command_args[0]
            error = handle_msgs(current, res, save)
            if error == -1:
                connected = False
                continue


if __name__ == "__main__":
    # try:
    main()
    # except Exception as e:
    #     print(e.args)
    #     print("Уважаемые котики-наркотики, прошу вас перестать вводить всякую "
    #           "фигню")


    # host = 'pop.e1.ru'
    # user = 'sadsad@e1.ru'
    # pswd = 'asdasds'
    # pop = pop3.POP3(host)
    # pop.create_socket()
    # # print(pop._send_command("sasdd"))
    # print(pop.user('pop3test1@e1.ru'))
    # # print(pop.user('pop3test1@e1.ru'))
    # # print(pop.user(user))
    # # print(pop.pass_(pswd))
    # print(pop.pass_('pop3test1'))
    # print(repr(pop.retr(2)))
    # # print(pop.retr(2))