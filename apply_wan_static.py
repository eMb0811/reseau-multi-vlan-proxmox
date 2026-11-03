import paramiko
import time

php_script = """<?php
require_once('config.inc');
require_once('interfaces.inc');
require_once('filter.inc');

global $config;

$config['interfaces']['wan']['ipaddr'] = '10.153.4.174';
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

init_config_arr(array('virtualip', 'vip'));
$config['virtualip']['vip'] = array(
    array(
        'mode' => 'ipalias',
        'interface' => 'wan',
        'descr' => 'Secondary WAN IP',
        'type' => 'single',
        'subnet_bits' => '24',
        'subnet' => '10.153.4.197'
    ),
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

write_config('Set WAN static IP 10.153.4.174 and VIP aliases');
echo "CONFIG_SAVED\n";
?>"""

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('10.153.4.197', username='root', password='pfsense', timeout=10)
sftp = s.open_sftp()
with sftp.open('/tmp/set_wan_static.php', 'w') as f:
    f.write(php_script)
sftp.close()

stdin, stdout, stderr = s.exec_command('php /tmp/set_wan_static.php')
print('PHP output:', stdout.read().decode())
print('PHP error:', stderr.read().decode())

# Now trigger interface and filter reconfiguration in background
stdin, stdout, stderr = s.exec_command('nohup /etc/rc.reload_all > /tmp/reload.log 2>&1 &')
s.close()
print('Reconfiguration triggered!')
