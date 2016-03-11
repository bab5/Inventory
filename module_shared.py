import sys
import os
import ast
import ConfigParser
import util_locator as ul

APP_DIR = ul.module_path()
CONFIGFILE = os.path.join(APP_DIR, 'inventory.cfg')


def get_settings():
    cc = ConfigParser.RawConfigParser()
    if os.path.isfile(CONFIGFILE):
        cc.readfp(open(CONFIGFILE, "r"))
    else:
        print '\n[!] Cannot find config file. Exiting...'
        sys.exit()

    # modules
    mod_linux = cc.getboolean('modules', 'linux')

    # targets  ------------------------------------------------------------------------
    targets = cc.get('targets', 'targets')
    exclude_ips = cc.get('targets', 'exclude_ips')
    # credentials  --------------------------------------------------------------------
    use_key_file = cc.getboolean('credentials', 'use_key_file')
    key_file = cc.get('credentials', 'key_file')
    credentials = cc.get('credentials', 'credentials')
    # ssh settings   ------------------------------------------------------------------
    ssh_port = cc.get('ssh_settings', 'ssh_port')
    timeout = cc.get('ssh_settings', 'timeout')
    # options   ------------------------------------------------------------------------
    get_serial_info = cc.getboolean('options', 'get_serial_info')
    get_hardware_info = cc.getboolean('options', 'get_hardware_info')
    get_os_details = cc.getboolean('options', 'get_os_details')
    get_cpu_info = cc.getboolean('options', 'get_cpu_info')
    get_memory_info = cc.getboolean('options', 'get_memory_info')
    ignore_domain = cc.getboolean('options', 'ignore_domain')
    upload_ipv6 = cc.getboolean('options', 'upload_ipv6')
    duplicate_serials = cc.getboolean('options', 'duplicate_serials')
    remove_stale_ips = cc.getboolean('options', 'remove_stale_ips')
    add_hdd_as_device_properties = cc.getboolean('options', 'add_hdd_as_device_properties')
    add_hdd_as_parts = cc.getboolean('options', 'add_hdd_as_parts')
    give_hostname_precedence = cc.getboolean('options', 'give_hostname_precedence')
    debug = cc.getboolean('options', 'debug')
    threads = cc.get('options', 'threads')
    dict_output = cc.getboolean('options', 'dict_output')
    get_dv_install_info = cc.getboolean('options', 'get_dv_install_info')

    return mod_linux, targets, exclude_ips,\
        use_key_file, key_file, credentials, ssh_port, timeout, get_serial_info, duplicate_serials,\
        add_hdd_as_device_properties, add_hdd_as_parts, get_hardware_info, get_os_details, get_cpu_info,\
        get_memory_info, ignore_domain, upload_ipv6, debug, threads, dict_output, give_hostname_precedence,\
        remove_stale_ips, get_dv_install_info


# noinspection PyProtectedMember
caller = os.path.basename(sys._getframe().f_back.f_code.co_filename)

if caller == 'main.py':
    mod_linux, targets, exclude_ips, use_key_file,\
        key_file, credentials, ssh_port, timeout, get_serial_info, duplicate_serials, add_hdd_as_device_properties,\
        add_hdd_as_parts, get_hardware_info, get_os_details, get_cpu_info, get_memory_info, ignore_domain,\
        upload_ipv6, debug, THREADS, DICT_OUTPUT, give_hostname_precedence, get_dv_install_info, REMOVE_STALE_IPS = get_settings()

    ssh_port = int(ssh_port)
    timeout = int(timeout)

else:
    if len(sys.argv) == 5:
        mod_linux, xtargets, xexclude_ips,\
            xuse_key_file, xkey_file, xcredentials, ssh_port, timeout, get_serial_info, duplicate_serials,\
            add_hdd_as_device_properties, add_hdd_as_parts, get_hardware_info, get_os_details, get_cpu_info,\
            get_memory_info, ignore_domain, upload_ipv6, debug, THREADS, DICT_OUTPUT, get_dv_install_info, give_hostname_precedence,\
            REMOVE_STALE_IPS = get_settings()

        ssh_port = int(ssh_port)
        timeout = int(timeout)
        targets = sys.argv[1].strip()
        use_key_file = ast.literal_eval(sys.argv[2].strip().capitalize())
        KF = sys.argv[3].strip()
        if KF.lower() in ('none', 'false', 'true'):
            key_file = ast.literal_eval(KF.capitalize())
        else:
            key_file = KF
            if not os.path.exists(key_file):
                print '[!] Cannot find key file: "%s"' % key_file
                print '[!] Exiting...'
                sys.exit()
        CR = sys.argv[4].strip()
        if CR.lower() in ('none', 'false', 'true'):
            credentials = ast.literal_eval(CR)
        else:
            credentials = CR

    else:
        print '\n[!] Wrong number of args. '
        print ' '.join(sys.argv[1:])
        print '[-] main.py TARGET use_key_file key_file credentials'
        sys.exit()
