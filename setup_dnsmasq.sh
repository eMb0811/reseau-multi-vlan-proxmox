#!/usr/bin/env bash
# ==============================================================================
# Script : setup_dnsmasq.sh
# Description : Résolution du conflit systemd-resolved et déploiement dnsmasq
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " [1/3] Résolution du conflit de port 53 (systemd-resolved)..."
echo "=========================================================="

# Sur Ubuntu, systemd-resolved écoute par défaut sur 127.0.0.53:53,
# ce qui empêche dnsmasq de démarrer. On désactive le StubListener :
if [ -f /etc/systemd/resolved.conf ]; then
    sudo sed -i 's/^#DNSStubListener=yes/DNSStubListener=no/' /etc/systemd/resolved.conf
    sudo sed -i 's/^DNSStubListener=yes/DNSStubListener=no/' /etc/systemd/resolved.conf
    if ! grep -q "DNSStubListener=" /etc/systemd/resolved.conf; then
        echo "DNSStubListener=no" | sudo tee -a /etc/systemd/resolved.conf
    fi
    sudo systemctl restart systemd-resolved
fi

echo "=========================================================="
echo " [2/3] Installation de dnsmasq..."
echo "=========================================================="

sudo apt-get update -y
sudo apt-get install -y dnsmasq

# Sauvegarde de la configuration d'origine si présente
if [ -f /etc/dnsmasq.conf ] && [ ! -f /etc/dnsmasq.conf.bak ]; then
    sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.bak
fi

# Copie de notre fichier de configuration
if [ -f ./dnsmasq.conf ]; then
    sudo cp ./dnsmasq.conf /etc/dnsmasq.conf
fi

echo "=========================================================="
echo " [3/3] Validation et démarrage du service dnsmasq..."
echo "=========================================================="

# Tester la syntaxe du fichier de configuration
sudo dnsmasq --test

# Redémarrer et activer dnsmasq
sudo systemctl enable dnsmasq
sudo systemctl restart dnsmasq

# Vérifier le statut
sudo systemctl status dnsmasq --no-pager

echo "=> Serveur DHCP et Cache DNS actif sur VLAN 10, 20 et 30 !"
