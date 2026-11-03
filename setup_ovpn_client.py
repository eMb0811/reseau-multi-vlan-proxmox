import paramiko

# 2048-bit OpenVPN static shared key (Base64)
b64_key = "IwojIDIwNDggYml0IE9wZW5WUE4gc3RhdGljIGtleQojCi0tLS0tQkVHSU4gT3BlblZQTiBTdGF0aWMga2V5IFYxLS0tLS0KYTIyYzZlZTMyY2VjYmYwNWU4ODliMGZlZjFjY2JmYmYKZWE4YmE5MDdmM2U2YzgyMWU2ZTlkNjRjZmZiMTZiY2YKM2ZkODIyZThmN2I3ZWFjMjMzZWI1ZDk3ZWQwY2FjMTAKYTJlNDRjYzVlZWU4Mjc0NzUxZDRjZDg1YmQwZDE3YjUKYjE4MmEzODFhOTVlZTAwZjcwNTJjZGZlYTg3MzIwMTEKMzM1ZmRhMTFlNzIwZWZlYWEzNTUzNDhkMzQ1MGJjZTYKMjgzNWFhNGUwNTFkOTJkNTRlYTE3M2VkOTA3ZTM3OWIKYWZkYzE0NjEyMmQ3Njc5YzlkMmRjNDI5NzVjNDY5ZjIKNjU4OTM4NmFlNmIxZmEzYzY3MjNkYjY1NmZlNTIxNzcKNmQxMmZkOWZhMGJmMzFjYzQ5MmMyODU2MjUzMjQ3YmYKZjIxYTg3YjUyNjZhNzgzZjdiZjc5ZDFkM2Q1YjcyYjQKMzRiMTYxMWQ1MzdmNjExZTRmNWY3ODZkY2MxOTk0NDUKYjZiMmNlOTY0ZjU1NDQ5NDdhZGFiN2NiNDU4ZDVlMDAKMjgxMmM4MzI3ODliMmM4MWMxMzI4N2I2MzM3YjY5YmEKNmQ3ZDA3M2MwMDA0ZDE2ZTU0ODNhZjEyMTQ2ZjZhNDYKODRiZjczMDg3NzFkYTNhODU4ZGU2M2QyNjczYzg0ZDAKLS0tLS1FTkQgT3BlblZQTiBTdGF0aWMga2V5IFYxLS0tLS0K"

php_client_script = f"""<?php
require_once('config.inc');
require_once('openvpn.inc');
require_once('filter.inc');

global $config;

init_config_arr(array('openvpn', 'openvpn-client'));

$client = array(
    'vpnid' => 1,
    'mode' => 'p2p_shared_key',
    'protocol' => 'UDP4',
    'dev_mode' => 'tun',
    'interface' => 'wan',
    'server_addr' => '10.153.4.174',
    'server_port' => 1194,
    'description' => 'Site-to-Site VPN to Group 2',
    'shared_key' => '{b64_key}',
    'data_ciphers_fallback' => 'AES-256-CBC',
    'digest' => 'SHA256',
    'tunnel_network' => '10.0.8.0/30'
);

$config['openvpn']['openvpn-client'] = array($client);

// Add firewall rule for OpenVPN interface
init_config_arr(array('filter', 'rule'));
$config['filter']['rule'][] = array(
    'id' => '',
    'tracker' => 1711940003,
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
    'tracker' => 1711940004,
    'type' => 'pass',
    'interface' => 'wan',
    'ipprotocol' => 'inet',
    'statetype' => 'keep state',
    'descr' => 'Allow OpenVPN inbound UDP 1194',
    'protocol' => 'udp',
    'source' => array('any' => ''),
    'destination' => array('any' => '', 'port' => '1194')
);

// Allow SSH and WebGUI on WAN
$config['filter']['rule'][] = array(
    'id' => '',
    'tracker' => 1711940005,
    'type' => 'pass',
    'interface' => 'wan',
    'ipprotocol' => 'inet',
    'statetype' => 'keep state',
    'descr' => 'Allow SSH on WAN',
    'protocol' => 'tcp',
    'source' => array('any' => ''),
    'destination' => array('any' => '', 'port' => '22')
);

$config['filter']['rule'][] = array(
    'id' => '',
    'tracker' => 1711940006,
    'type' => 'pass',
    'interface' => 'wan',
    'ipprotocol' => 'inet',
    'statetype' => 'keep state',
    'descr' => 'Allow WebGUI on WAN',
    'protocol' => 'tcp',
    'source' => array('any' => ''),
    'destination' => array('any' => '', 'port' => '443')
);

write_config('Configured OpenVPN Site-to-Site Client');
openvpn_resync('client', $client);
filter_configure();
echo "OPENVPN_CLIENT_CONFIGURED\\n";
?>"""

if __name__ == '__main__':
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect('10.153.4.173', username='root', password='admin')

    sftp = s.open_sftp()
    with sftp.open('/tmp/setup_ovpn_client.php', 'w') as f:
        f.write(php_client_script)
    sftp.close()

    stdin, stdout, stderr = s.exec_command('php /tmp/setup_ovpn_client.php')
    print("STDOUT:\n", stdout.read().decode())
    print("STDERR:\n", stderr.read().decode())

    stdin, stdout, stderr = s.exec_command('ifconfig ovpnc1')
    print("Tunnel Interface:\n", stdout.read().decode())
    s.close()
