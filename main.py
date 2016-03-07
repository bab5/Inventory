#!/usr/bin/env python

import Queue
import socket
import threading
import time
import paramiko

# import custom modules
import util_uploader as uploader
import util_ip_operations as ipop
import module_linux as ml
import module_mac as mc


__version__ = "3.4"

# environment and other stuff
lock = threading.Lock()
q = Queue.Queue()



def remove_stale_ips(ips, name):
    rest = uploader.Rest(base_url, username, secret, debug)
    fetched_ips = rest.get_device_by_name(name)
    ips_to_remove = set(fetched_ips) - set(ips)
    if ips_to_remove:
        print '\n[*] IPs to remove: %s' % ips_to_remove
        for ip in ips_to_remove:
            rest.delete_ip(ip)


def get_linux_data(ip, usr, pwd):
    if mod_linux:
        lock.acquire()
        print '[+] Collecting data from: %s' % ip
        lock.release()
        linux = ml.GetLinuxData(base_url, username, secret, ip, ssh_port, timeout, usr, pwd, use_key_file, key_file,
                                get_serial_info, add_hdd_as_device_properties, add_hdd_as_parts,
                                get_hardware_info, get_os_details, get_cpu_info, get_memory_info,
                                ignore_domain, upload_ipv6, give_hostname_precedence, get_dv_install_info, debug)

        data = linux.main()
        print "value debug: %s" % debug
        if debug:
            lock.acquire()
            #print '\nLinux data: '
            for rec in data:
                print rec
            lock.release()
        if DICT_OUTPUT:
            return data
        else:
            # Upload -----------
            # upload(data)
	        print data


def process_data(data_out, ip, usr, pwd):
    msg = str(data_out).lower()
    if 'linux' in msg:
        lock.acquire()
        print '[+] Linux running @ %s ' % ip
        lock.release()
        data = get_linux_data(ip, usr, pwd)
        return data

    else:
        lock.acquire()
        print '[!] Connected to SSH @ %s, but the OS cannot be determined.' % ip
        print '\tInfo: %s\n\tSkipping... ' % str(msg)
        lock.release()
        return


def check_os(ip):
    # global success
    usr = None
    success = False
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if not use_key_file:
        creds = credentials.split(',')
        for cred in creds:
            if cred not in ('', ' ', '\n'):
                try:
                    usr, pwd = cred.split(':')
                except ValueError:
                    print '\n[!] Error. \n\tPlease check credentials formatting. It should look like user:password\n'
                    sys.exit()
            if not success:
                try:
                    lock.acquire()
                    print '[*] Connecting to %s:%s as "%s"' % (ip, ssh_port, usr)
                    lock.release()
                    ssh.connect(ip, username=usr, password=pwd, timeout=timeout, allow_agent=False, look_for_keys=False)
                    stdin, stdout, stderr = ssh.exec_command("uname -a")
                    data_out = stdout.readlines()
                    if data_out:
                        success = True
                        data = process_data(data_out, ip, usr, pwd)
                        return data
                    else:
                        lock.acquire()
                        print '[!] Connected to SSH @ %s, but the OS cannot be determined. ' % ip
                        lock.release()

                except paramiko.AuthenticationException:
                    lock.acquire()
                    print '[!] Could not authenticate to %s as user "%s"' % (ip, usr)
                    lock.release()

                except socket.error:
                    lock.acquire()
                    print '[!] timeout %s ' % ip
                    lock.release()

                except Exception, e:
                    print e
    else:
        if credentials.lower() in ('none', 'false', 'true'):
            print '\n[!] Error!. You must specify user name!'
            print '[-] starter.py 192.168.3.102  True ./id_rsa root'
            print '[!] Exiting...'
            sys.exit()
        try:
            if ':' in credentials:
                usr, pwd = credentials.split(':')
            else:
                usr = credentials
                pwd = None
            print '[*] Connecting to %s:%s as "%s" using key file.' % (ip, ssh_port, usr)
            ssh.connect(ip, username=usr, key_filename=key_file, timeout=timeout)
            stdin, stdout, stderr = ssh.exec_command("uname -a")
            data_out = stdout.readlines()
            if data_out:
                data = process_data(data_out, ip, usr, pwd)
                return data

            else:
                lock.acquire()
                print '[!] Connected to SSH @ %s, but the OS cannot be determined. ' % ip
                lock.release()

        except paramiko.AuthenticationException:
            lock.acquire()
            print '[!] Could not authenticate to %s as user "%s"' % (ip, usr)
            lock.release()

        except socket.error:
            lock.acquire()
            print '[!] timeout %s ' % ip
            lock.release()

        except Exception, e:
            if str(e) == 'not a valid EC private key file':
                print '\n[!] Error: Could not login probably due to the wrong username or key file.'
            else:
                print e


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(float(timeout))
    msg = '\r\n[!] Running %s threads.' % THREADS
    print msg
    print targets
    # parse IP address [single, range or CIDR]
    if targets:
        ipops = ipop.IPOperations(targets)
        scope = ipops.sort_ip()

        # exclude IPs from scope
        if exclude_ips:
            xops = ipop.IPOperations(exclude_ips)
            xscope = xops.sort_ip()
            ip_scope = set(scope) - set(xscope)
        else:
            ip_scope = scope

        if not ip_scope:
            msg = '[!] Empty IP address scope! Please, check target IP address[es].'
            print msg
            sys.exit()
        else:
            if len(ip_scope) == 1:
                q.put(ip_scope[0])
            else:
                for ip in ip_scope:
                    q.put(ip)
            while not q.empty():
                tcount = threading.active_count()
                if tcount < int(THREADS):
                    ip = q.get()
                    p = threading.Thread(target=check_os, args=(str(ip),))
                    p.setDaemon(True)
                    p.start()
                else:
                    time.sleep(0.5)
            else:
                tcount = threading.active_count()
                while tcount > 1:
                    time.sleep(2)
                    tcount = threading.active_count()
                    msg = '[_] Waiting for threads to finish. Current thread count: %s' % str(tcount)
                    lock.acquire()
                    print msg
                    lock.release()

                msg = '\n[!] Done!'
                print msg
    else:
        print "some Error"


if __name__ == '__main__':
    from module_shared import *

    main()
    sys.exit()
else:
    # you can use dict_output if called from external script (starter.py)
    from module_shared import *
