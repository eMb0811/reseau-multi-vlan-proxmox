#!/usr/bin/env bash
# ==============================================================================
# Script : setup_router_nat.sh
# Description : Activation du routage IPv4, filtrage d'état, filtrage MAC,
#               NAT Masquerade et persistance (iptables-persistent)
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

# Interface WAN (sortie réseau campus / Internet)
WAN_IF="ens18"

# 1. Règle de NAT / Masquerade
sudo iptables -t nat -C POSTROUTING -o "$WAN_IF" -j MASQUERADE 2>/dev/null || \
sudo iptables -t nat -A POSTROUTING -o "$WAN_IF" -j MASQUERADE

# 2. Sécurité : Filtrage par adresse MAC (Exemple de blocage spécifique)
# Note : Toujours utiliser le format avec deux-points (ex: ac:ed:5c:11:9a:a4)
# sudo iptables -I FORWARD 1 -m mac --mac-source ac:ed:5c:11:9a:a4 -o "$WAN_IF" -j REJECT --reject-with icmp-port-unreachable

# 3. Autoriser les paquets de retour (Stateful Firewall)
sudo iptables -C FORWARD -i "$WAN_IF" -o ens19.+ -m conntrack --ctstate RELATED,ESTABLISHED 2>/dev/null || \
sudo iptables -A FORWARD -i "$WAN_IF" -o ens19.+ -m conntrack --ctstate RELATED,ESTABLISHED

# 4. Autoriser le trafic sortant des VLANs (ens19.10, ens19.20, ens19.30) vers ens18
sudo iptables -C FORWARD -i ens19.+ -o "$WAN_IF" -j ACCEPT 2>/dev/null || \
sudo iptables -A FORWARD -i ens19.+ -o "$WAN_IF" -j ACCEPT

echo "=========================================================="
echo " [3/4] Sauvegarde de la persistance Iptables..."
echo "=========================================================="

# Sauvegarde des règles IPv4 dans /etc/iptables/rules.v4
sudo netfilter-persistent save

echo "=========================================================="
echo " [4/4] Vérification de la configuration"
echo "=========================================================="
echo "Règles de filtrage FORWARD actives :"
sudo iptables -L FORWARD -v -n
echo ""
echo "Règles NAT actives :"
sudo iptables -t nat -L POSTROUTING -v -n
echo ""
echo "Statut IP Forwarding :"
cat /proc/sys/net/ipv4/ip_forward
echo ""
echo "=> Routage IPv4, filtrage et NAT configurés avec succès !"
