import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.153.4.186', username='root', password='passer2026')

remote_cmd = """cat << 'EOF' > /tmp/send_easyrule.py
import subprocess, time

def send(s):
    mapping = {' ': 'spc', '-': 'minus', '/': 'slash', '.': 'dot', '_': 'shift-minus'}
    for c in s:
        key = mapping.get(c, c)
        subprocess.run(['qm', 'sendkey', '313', key], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.04)
    subprocess.run(['qm', 'sendkey', '313', 'ret'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

print('Applying easyrules...')
send('pfctl -d')
send('easyrule pass wan tcp any any 443')
send('easyrule pass wan tcp any any 80')
send('easyrule pass wan icmp any any')
print('Rules executed!')
EOF
python3 /tmp/send_easyrule.py
"""

stdin, stdout, stderr = ssh.exec_command(remote_cmd)
print("STDOUT:", stdout.read().decode())
print("STDERR:", stderr.read().decode())
ssh.close()
