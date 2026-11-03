#!/usr/bin/env bash
# ==============================================================================
# Script : install_ntopng.sh
# Description : Installation de Redis, NTOPng, configuration du port 3000
#               et supervision exclusive du LAN (VLANs 10, 20 et 30)
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " [1/4] Installation des dépendances et de Redis Server..."
echo "=========================================================="

sudo apt-get update -y
sudo apt-get install -y redis-server curl wget gnupg software-properties-common lsb-release

# Démarrer et activer Redis
sudo systemctl enable redis-server
sudo systemctl restart redis-server

echo "=========================================================="
echo " [2/4] Configuration du dépôt NTOPng et installation..."
echo "=========================================================="

if apt-cache show ntopng >/dev/null 2>&1; then
    echo "Paquet ntopng disponible dans les dépôts locaux, installation..."
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ntopng
else
    echo "Ajout du dépôt officiel ntop..."
    UBUNTU_CODENAME=$(lsb_release -cs)
    wget -q https://packages.ntop.org/apt/ntop.key -O - | sudo gpg --dearmor -o /usr/share/keyrings/ntop.gpg --yes
    echo "deb [signed-by=/usr/share/keyrings/ntop.gpg] https://packages.ntop.org/apt/${UBUNTU_CODENAME}/ x64/" | sudo tee /etc/apt/sources.list.d/ntop.list
    echo "deb [signed-by=/usr/share/keyrings/ntop.gpg] https://packages.ntop.org/apt/${UBUNTU_CODENAME}/ all/" | sudo tee -a /etc/apt/sources.list.d/ntop.list
    sudo apt-get update -y
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y ntopng
fi

echo "=========================================================="
echo " [3/4] Configuration de NTOPng (Supervision LAN exclusive)..."
echo "=========================================================="

sudo mkdir -p /etc/ntopng

# Configuration restreinte aux VLANs locaux (ens19.10, ens19.20, ens19.30)
sudo tee /etc/ntopng/ntopng.conf > /dev/null << 'EOF'
-i=ens19.10
-i=ens19.20
-i=ens19.30
-w=3000
-m=192.168.10.0/24,192.168.20.0/24,192.168.30.0/24
-d=/var/lib/ntopng
EOF

# Ajustement de l'unité systemd (Type=simple pour démarrage robuste)
sudo tee /etc/systemd/system/ntopng.service > /dev/null << 'EOF'
[Unit]
Description=ntopng - High-Speed Web-based Traffic Analysis and Flow Collection Tool
After=network.target redis-server.service

[Service]
Type=simple
ExecStart=/usr/sbin/ntopng /etc/ntopng/ntopng.conf
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "=========================================================="
echo " [4/4] Démarrage du service NTOPng..."
echo "=========================================================="

sudo systemctl daemon-reload
sudo systemctl enable ntopng
sudo systemctl restart ntopng

echo ""
echo "Vérification de l'écoute sur le port 3000 :"
sudo ss -tulpn | grep 3000 || echo "NTOPng est en cours d'initialisation..."

echo ""
echo "=========================================================="
echo " NTOPng est déployé avec succès !"
echo " Accès Web : http://10.153.4.174:3000"
echo " Interfaces surveillées : ens19.10, ens19.20, ens19.30 (LAN Only)"
echo "=========================================================="
