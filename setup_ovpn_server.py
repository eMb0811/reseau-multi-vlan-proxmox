import paramiko
import base64

shared_key_raw = """#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
a22c6ee32cecbf05e889b0fef1ccbfbf
ea8ba907f3e6c821e6e9d64cffb16bcf
3fd822e8f7b7eac233eb5d97ed0cac10
a2e44cc5eee8274751d4cd85bd0d17b5
b182a381a95ee00f7052cdfea8732011
335fda11e720efeaa355348d3450bce6
2835aa4e051d92d54ea173ed907e379b
afdc146122d7679c9d2dc42975c469f2
6589386ae6b1fa3c6723db656fe52177
6d12fd9fa0bf31cc492c2856253247bf
f21a87b5266a783f7bf79d1d3d5b72b4
34b1611d537f611e4f5f786dcc199445
b6b2ce964f5544947adab7cb458d5e00
2812c832789b2c81c13287b6337b69ba
6d7d073c0004d16e5483af12146f6a46
84bf7308771da3a858de63d2673c84d0
-----END OpenVPN Static key V1-----
"""

b64_key = base64.b64encode(shared_key_raw.encode('utf-8')).decode('utf-8')

php_server_script = f"""<?php
require_once('config.inc');
require_once('openvpn.inc');
require_once('filter.inc');

global $config;

init_config_arr(array('openvpn', 'openvpn-server'));

$server = array(
    'vpnid' => 1,
    'mode' => 'p2p_shared_key',
    'protocol' => 'UDP4',
    'dev_mode' => 'tun',
    'interface' => 'wan',
    'local_port' => 1194,
    'description' => 'Site-to-Site VPN to Group 1',
    'shared_key' => '{b64_key}',
    'data_ciphers_fallback' => 'AES-256-CBC',
    'digest' => 'SHA256',
    'tunnel_network' => '10.0.8.0/30'
);

$config['openvpn']['openvpn-server'] = array($server);

// Add firewall rule for OpenVPN interface
init_config_arr(array('filter', 'rule'));
$config['filter']['rule'][] = array(
    'id' => '',
    'tracker' => 1711940001,
    'type' => 'pass',
    'interface' => 'openvpn',
    'ipprotocol' => 'inet',
    'descr' => 'Allow all traffic through OpenVPN tunnel',
    'source' => array('any' => ''),
    'destination' => array('any' => '')
);

// Add firewall rule for WAN UDP 1194
$config['filter']['rule'][] = array(
    'id' => '',
    'tracker' => 1711940002,
    'type' => 'pass',
    'interface' => 'wan',
    'ipprotocol' => 'inet',
    'statetype' => 'keep state',
    'descr' => 'Allow OpenVPN inbound UDP 1194',
    'protocol' => 'udp',
    'source' => array('any' => ''),
    'destination' => array('any' => '', 'port' => '1194')
);

write_config('Configured OpenVPN Site-to-Site Server');
openvpn_resync('server', $server);
filter_configure();
echo "OPENVPN_SERVER_CONFIGURED\\n";
?>"""

s = paramiko.SSHClient()
s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
s.connect('10.153.4.174', username='root', password='pfsense')
sftp = s.open_sftp()
with sftp.open('/tmp/setup_ovpn_server.php', 'w') as f:
    f.write(php_server_script)
sftp.close()

stdin, stdout, stderr = s.exec_command('php /tmp/setup_ovpn_server.php')
print('Server stdout:', stdout.read().decode())
print('Server stderr:', stderr.read().decode())
s.close()
