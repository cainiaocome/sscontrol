#!/usr/bin/env python2.7
#encoding: utf-8

import os
import time
import signal
import socket
import psutil as ps
from IPy import IP

total_mem = 0
ip = ''
start_ss = "ssserver -c {} >/dev/null 2>&1 &"
def init():

    # init global var
    global total_mem
    total_mem = ps.virtual_memory()[0]/1024/1024   # use MB
    print 'total_mem:',total_mem

    global ip
    for nic,addrs in ps.net_if_addrs().items():
        for addr in addrs:
            if addr.family==socket.AF_INET:
                _ip = IP(addr.address)
                if _ip.iptype()=='PUBLIC':
                    ip = str(_ip)
    print 'public ip:', ip

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
        time.sleep(1)
        for each_config_file in os.listdir("/etc/shadowsocks/"):
            this_config_file_process_exists = False
            for proc in ps.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'memory_percent'])
                except:
                    pass
                else:
                    if pinfo['name']=='ssserver' and pinfo['cmdline'][3]==each_config_file:
                        this_config_file_process_exists = True
                        break
            if this_config_file_process_exists==False:
                os.system(start_ss.format('/etc/shadowsocks/{}'.format(each_config_file)))
        for proc in ps.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'memory_percent'])
            except:
                pass
            else:
                if pinfo['name']=='ssserver':
                    print pinfo['pid'], pinfo['memory_info'][0]/1024/1024, pinfo['memory_percent']
                    if pinfo['memory_percent']>5:
                        # kill and start a new one
                        proc.kill()
        print '-'*90

if __name__=='__main__':
    main()
