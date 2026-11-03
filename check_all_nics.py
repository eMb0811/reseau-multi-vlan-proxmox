import paramiko
import sys

sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.153.4.186', username='root', password='passer2026', timeout=5)

def run(cmd):
    print(f"=== {cmd} ===")
    _, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='replace'))

run("ip -br link")
run("for i in $(ls /sys/class/net); do echo -n \"$i: \"; ethtool $i 2>/dev/null | grep 'Link detected' || echo ''; done")

ssh.close()
