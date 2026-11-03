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

run("ip link show enp3s0f0")
run("ip link show enp3s0f1")
run("ip link show enp4s0f1")
run("ethtool enp3s0f0 | grep -E 'Speed|Duplex|Link detected'")
run("ethtool enp3s0f1 | grep -E 'Speed|Duplex|Link detected'")
run("ethtool enp4s0f1 | grep -E 'Speed|Duplex|Link detected'")

ssh.close()
