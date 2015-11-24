#!/usr/bin/env python2.7
#encoding: utf-8

import os
import time
import signal
import socket
import psutil as ps
from IPy import IP

def main():
    for proc in ps.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'create_time', 'memory_info', 'memory_percent'])
        except:
            pass
        else:
            print pinfo['name'], pinfo['cmdline']
            if pinfo['name']=='ssserver':
                pass
                #print pinfo['pid'], pinfo['cmdline'][3], pinfo['memory_info'][0]/1024/1024, pinfo['memory_percent']

if __name__=='__main__':
    main()
