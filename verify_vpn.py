import paramiko

def test_vpn():
    print("=== Testing Tunnel VM 314 -> VM 313 (10.0.8.2 -> 10.0.8.1) ===")
    s314 = paramiko.SSHClient()
    s314.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s314.connect('10.153.4.173', username='root', password='admin')
    _, out, _ = s314.exec_command('ping -c 3 10.0.8.1')
    print(out.read().decode())
    s314.close()

    print("=== Testing Tunnel VM 313 -> VM 314 (10.0.8.1 -> 10.0.8.2) ===")
    s313 = paramiko.SSHClient()
    s313.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s313.connect('10.153.4.174', username='root', password='pfsense')
    _, out, _ = s313.exec_command('ping -c 3 10.0.8.2')
    print(out.read().decode())
    s313.close()

if __name__ == '__main__':
    test_vpn()
