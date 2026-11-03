import paramiko
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.153.4.186', username='root', password='passer2026', timeout=5)

def qm_sh(vmid, bash_cmd):
    cmd_str = f"qm guest exec {vmid} -- bash -c \"{bash_cmd}\""
    _, stdout, stderr = ssh.exec_command(cmd_str)
    res_str = stdout.read().decode('utf-8', errors='replace')
    try:
        res = json.loads(res_str)
        out = res.get('out-data', '')
        print(f"=== {bash_cmd} ===")
        print(out.strip())
        return out
    except Exception as e:
        print("ERR:", res_str)
        return ""

qm_sh(312, "journalctl -u isc-dhcp-server -n 50 --no-pager")
qm_sh(312, "cat /etc/default/isc-dhcp-server")
qm_sh(312, "cat /etc/dhcp/dhcpd.conf")
qm_sh(312, "ip link show")

ssh.close()
