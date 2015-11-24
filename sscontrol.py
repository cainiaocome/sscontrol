#!/usr/bin/env python2.7
#encoding: utf-8

import os
import time
import signal
import socket
import logging
import psutil as ps
from IPy import IP

logging.basicConfig(filename='log.sscontrol', format='%(asctime)s %(message)s', level=logging.DEBUG)

total_mem = 0
ip = ''
start_ss = "/usr/bin/python /usr/local/bin/ssserver -c {} >/dev/null 2>&1 &"
def init():

    # init global var
    global total_mem
    total_mem = ps.virtual_memory()[0]/1024/1024   # use MB
    logging.debug('total_mem: {}'.format(total_mem))

    global ip
    for nic,addrs in ps.net_if_addrs().items():
        for addr in addrs:
            if addr.family==socket.AF_INET:
                _ip = IP(addr.address)
                if _ip.iptype()=='PUBLIC':
                    ip = str(_ip)
    logging.debug('public ip: {}'.format(ip))

    #singleton
    for proc in ps.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'memory_percent'])
        except:
            pass
        else:
            for x in pinfo['cmdline']:
                if 'sscontrol' in x and pinfo['pid']!=os.getpid():
                    proc.kill()

def main():
    os.system('ulimit -n 51200')
    init()
    while True:
        time.sleep(3)
        for each_config_file in os.listdir("/etc/shadowsocks/"):
            cmd_3 = '/etc/shadowsocks/{}'.format(each_config_file)
            logging.debug('checking {} ......'.format(each_config_file))
            this_config_file_process_exists = False
            for proc in ps.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'memory_percent'])
                except:
                    pass
                else:
                    if len(pinfo['cmdline'])==4 and pinfo['cmdline'][1]=='/usr/local/bin/ssserver' and pinfo['cmdline'][3]==cmd_3:
                        logging.debug('{} ok'.format(each_config_file))
                        this_config_file_process_exists = True
                        break
            if this_config_file_process_exists==False:
                logging.debug('starting {}'.format(each_config_file))
                os.system(start_ss.format(cmd_3))
        for proc in ps.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'memory_percent'])
            except:
                pass
            else:
                if len(pinfo['cmdline'])==4 and pinfo['cmdline'][1]=='/usr/local/bin/ssserver':
                    logging.debug('{} {} {} {}'.format(pinfo['pid'], pinfo['cmdline'][3], 
                                       pinfo['memory_info'][0]/1024/1024, pinfo['memory_percent']))
                    if pinfo['memory_percent']>5:
                        # kill and start a new one
                        logging.info('going to kill {} {} since its memory_percent: {}'.format(
                                                pinfo['pid'], pinfo['cmdline'][3], pinfo['memory_percent']))
                        proc.kill()
        logging.debug('-'*90)

if __name__=='__main__':
    main()
