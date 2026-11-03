import paramiko

php_script = """<?php
require_once('config.inc');
require_once('interfaces.inc');
require_once('filter.inc');

global $config;

// 1. WAN Configuration for Group 1
$config['interfaces']['wan']['ipaddr'] = '10.153.4.173';
$config['interfaces']['wan']['subnet'] = '24';
$config['interfaces']['wan']['gateway'] = 'WANGW';

init_config_arr(array('gateways', 'gateway_item'));
$config['gateways']['gateway_item'] = array(
    array(
        'interface' => 'wan',
        'gateway' => '10.153.4.254',
        'name' => 'WANGW',
        'weight' => 1,
        'ipprotocol' => 'inet',
        'descr' => 'Campus WAN Gateway',
        'defaultgw' => true
    )
);

// 2. DHCP Pools (100 to 200 as on VM 311)
$config['dhcpd']['opt1']['range']['from'] = '192.168.10.100';
$config['dhcpd']['opt1']['range']['to'] = '192.168.10.200';

$config['dhcpd']['opt2']['range']['from'] = '192.168.20.100';
$config['dhcpd']['opt2']['range']['to'] = '192.168.20.200';

$config['dhcpd']['opt3']['range']['from'] = '192.168.30.100';
$config['dhcpd']['opt3']['range']['to'] = '192.168.30.200';

// 3. Virtual IP Aliases (.254 legacy gateways)
init_config_arr(array('virtualip', 'vip'));
$config['virtualip']['vip'] = array(
    array(
        'mode' => 'ipalias',
        'interface' => 'opt1',
        'descr' => 'Legacy VLAN10 Gateway',
        'type' => 'single',
        'subnet_bits' => '24',
        'subnet' => '192.168.10.254'
    ),
    array(
        'mode' => 'ipalias',
        'interface' => 'opt2',
        'descr' => 'Legacy VLAN20 Gateway',
        'type' => 'single',
        'subnet_bits' => '24',
        'subnet' => '192.168.20.254'
    ),
    array(
        'mode' => 'ipalias',
        'interface' => 'opt3',
        'descr' => 'Legacy VLAN30 Gateway',
        'type' => 'single',
        'subnet_bits' => '24',
        'subnet' => '192.168.30.254'
    )
);

// 4. Hostname
$config['system']['hostname'] = 'pfsense-autre-groupe';

write_config('Configured pfSense for Group 1 (10.153.4.173)');
echo "CONFIG_SAVED_GROUP1\n";
?>"""

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('10.153.4.186', username='root', password='passer2026')

sftp = s.open_sftp()
with sftp.open('/tmp/config_group1.php', 'w') as f:
    f.write(php_script)
sftp.close()

stdin, stdout, stderr = s.exec_command('''
sshpass -p pfsense scp -o StrictHostKeyChecking=no /tmp/config_group1.php root@192.168.1.1:/tmp/config_group1.php
sshpass -p pfsense ssh -o StrictHostKeyChecking=no root@192.168.1.1 php /tmp/config_group1.php
''')
print('Output:\n', stdout.read().decode())
print('Error:\n', stderr.read().decode())
s.close()
