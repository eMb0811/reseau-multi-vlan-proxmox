import paramiko
import time

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('10.153.4.186', username='root', password='passer2026')

# 1. Stop VM 311 cleanly
print("Stopping VM 311...")
stdin, stdout, stderr = s.exec_command('qm shutdown 311 && sleep 2 && qm status 311')
print(stdout.read().decode())

# 2. Set link_down=0 on VM 314
print("Enabling link on VM 314 net0...")
stdin, stdout, stderr = s.exec_command('qm set 314 -net0 virtio=BC:24:11:68:AC:C3,bridge=vmbr0,link_down=0')
print(stdout.read().decode())

# 3. Clean up temporary IP from vmbr1 on Proxmox
stdin, stdout, stderr = s.exec_command('ip addr del 192.168.1.2/24 dev vmbr1 2>/dev/null')
stdout.read()

# 4. Reboot VM 314 cleanly to boot with full new config
print("Rebooting VM 314 to apply fresh network config...")
stdin, stdout, stderr = s.exec_command('qm reboot 314')
print(stdout.read().decode())

s.close()
print("Cutover commands executed successfully.")
