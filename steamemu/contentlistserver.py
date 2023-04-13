# uncompyle6 version 3.8.0
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:25:05) [MSC v.1500 64 bit (AMD64)]
# Warning: this version of Python has problems handling the Python 3 byte type in constants properly.

# Embedded file name: Y:\source\Server\steamemu\contentlistserver.py
import threading, logging, struct, binascii, os, steam, config, globalvars

class contentlistserver(threading.Thread):

    def __init__(self, (socket, address), config):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.config = config

    def run(self):
        log = logging.getLogger('clstsrv')
        clientid = str(self.address) + ': '
        log.info(clientid + 'Connected to Content List Server ')
        if self.config['public_ip'] != '0.0.0.0':
            if clientid.startswith(globalvars.servernet):
                bin_ip = steam.encodeIP((self.config['server_ip'], self.config['file_server_port']))
            else:
                bin_ip = steam.encodeIP((self.config['public_ip'], self.config['file_server_port']))
        else:
            bin_ip = steam.encodeIP((self.config['server_ip'], self.config['file_server_port']))
        msg = self.socket.recv(4)
        if msg == '\x00\x00\x00\x02':
            self.socket.send('\x01')
            msg = self.socket.recv_withlen()
            command = msg[0]
            if command == '\x00':
                if msg[2] == '\x00' and len(msg) == 21:
                    log.info(clientid + 'Sending out file servers with packages')
                    reply = struct.pack('>H', 1) + '\x00\x00\x00\x00' + bin_ip + bin_ip
                elif msg[2] == '\x01' and len(msg) == 25:
                    appnum, version, numservers, region = struct.unpack('>xxxLLHLxxxxxxxx', msg)
                    log.info('%ssend which server has content for app %s %s %s %s' % (clientid, appnum, version, numservers, region))
                    if os.path.isfile('files/cache/' + str(appnum) + '_' + str(version) + '/' + str(appnum) + '_' + str(version) + '.manifest'):
                        reply = struct.pack('>H', 1) + '\x00\x00\x00\x00' + bin_ip + bin_ip
                    elif os.path.isfile(self.config['v2manifestdir'] + str(appnum) + '_' + str(version) + '.manifest'):
                        reply = struct.pack('>H', 1) + '\x00\x00\x00\x00' + bin_ip + bin_ip
                    elif os.path.isfile(self.config['manifestdir'] + str(appnum) + '_' + str(version) + '.manifest'):
                        reply = struct.pack('>H', 1) + '\x00\x00\x00\x00' + bin_ip + bin_ip
                    else:
                        log.warning('%sNo servers found for app %s %s %s %s' % (clientid, appnum, version, numservers, region))
                        reply = '\x00\x00'
                else:
                    log.warning('Invalid message! ' + binascii.b2a_hex(msg))
                    reply = '\x00\x00'
            elif command == '\x03':
                log.info(clientid + 'Sending out file servers with packages')
                reply = struct.pack('>H', 1) + bin_ip
            else:
                log.warning('Invalid message! ' + binascii.b2a_hex(msg))
                reply = ''
            self.socket.send_withlen(reply)
        else:
            log.warning('Invalid message! ' + binascii.b2a_hex(msg))
        self.socket.close()
        log.info(clientid + 'Disconnected from Content List Server')