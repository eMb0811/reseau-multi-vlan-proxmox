#!/usr/bin/env bash
# ==============================================================================
# Script : setup_router_nat.sh
# Description : Activation du routage IPv4, configuration NAT et persistance
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " [1/4] Activation de l'IP Forwarding (Routage Linux)..."
echo "=========================================================="

# Activer immédiatement dans le noyau
sudo sysctl -w net.ipv4.ip_forward=1

# Rendre permanent dans /etc/sysctl.conf
if grep -q "^#net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    sudo sed -i 's/^#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
elif ! grep -q "^net.ipv4.ip_forward=1" /etc/sysctl.conf; then
    echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
fi

sudo sysctl -p

echo "=========================================================="
echo " [2/4] Configuration des règles Iptables (NAT & Filtrage)..."
echo "=========================================================="

# Interface WAN (sortie Internet)
WAN_IF="eth0"

# Règle de NAT / Masquerade demandée
sudo iptables -t nat -C POSTROUTING -o "$WAN_IF" -j MASQUERADE 2>/dev/null || \
sudo iptables -t nat -A POSTROUTING -o "$WAN_IF" -j MASQUERADE

# Autoriser le transfert (FORWARD) des VLANs vers Internet
sudo iptables -C FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \
sudo iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Autoriser le trafic sortant de tous les VLANs vers le WAN
sudo iptables -C FORWARD -i vlan10 -o "$WAN_IF" -j ACCEPT 2>/dev/null || \
sudo iptables -A FORWARD -i vlan10 -o "$WAN_IF" -j ACCEPT

sudo iptables -C FORWARD -i vlan20 -o "$WAN_IF" -j ACCEPT 2>/dev/null || \
sudo iptables -A FORWARD -i vlan20 -o "$WAN_IF" -j ACCEPT

sudo iptables -C FORWARD -i vlan30 -o "$WAN_IF" -j ACCEPT 2>/dev/null || \
sudo iptables -A FORWARD -i vlan30 -o "$WAN_IF" -j ACCEPT

echo "=========================================================="
echo " [3/4] Installation et sauvegarde de la persistance Iptables..."
echo "=========================================================="

# Pré-configuration debconf pour éviter les invites interactives bloquantes
echo "iptables-persistent iptables-persistent/autosave_v4 boolean true" | sudo debconf-set-selections
echo "iptables-persistent iptables-persistent/autosave_v6 boolean true" | sudo debconf-set-selections

# Installation silencieuse de iptables-persistent
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent netfilter-persistent

# Sauvegarde des règles IPv4 dans /etc/iptables/rules.v4
sudo netfilter-persistent save

echo "=========================================================="
echo " [4/4] Vérification de la configuration"
echo "=========================================================="
echo "Règles NAT actives :"
sudo iptables -t nat -L POSTROUTING -v -n
echo ""
echo "Statut IP Forwarding :"
cat /proc/sys/net/ipv4/ip_forward
echo ""
echo "=> Routage IPv4 et NAT configurés avec succès et persistants au reboot !"
