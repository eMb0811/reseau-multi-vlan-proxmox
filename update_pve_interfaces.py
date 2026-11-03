import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.153.4.186', username='root', password='passer2026', timeout=5)

ssh.exec_command("sed -i 's/bridge-ports enp3s0f0$/bridge-ports enp3s0f0 enp3s0f1/' /etc/network/interfaces")
_, stdout, _ = ssh.exec_command("grep -A 5 'auto vmbr2' /etc/network/interfaces")
print(stdout.read().decode())
ssh.close()
