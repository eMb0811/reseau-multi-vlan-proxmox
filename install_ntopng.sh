#!/usr/bin/env bash
# ==============================================================================
# Script : install_ntopng.sh
# Description : Installation de Redis, NTOPng, configuration du port 3000
#               et supervision des interfaces (WAN + 3 VLANs)
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " [1/4] Installation des dépendances et de Redis Server..."
echo "=========================================================="

sudo apt-get update -y
sudo apt-get install -y redis-server curl wget gnupg software-properties-common lsb-release

# Démarrer et activer Redis (requis par NTOPng pour stocker l'état et les métriques)
sudo systemctl enable redis-server
sudo systemctl restart redis-server

echo "=========================================================="
echo " [2/4] Configuration du dépôt NTOPng et installation..."
echo "=========================================================="

# Essayer d'installer ntopng directement depuis les dépôts Ubuntu
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
echo " [3/4] Configuration de NTOPng (/etc/ntopng/ntopng.conf)..."
echo "=========================================================="

sudo mkdir -p /etc/ntopng

# Création du fichier de configuration ntopng.conf
sudo tee /etc/ntopng/ntopng.conf > /dev/null << 'EOF'
# Fichier PID
-G=/var/run/ntopng.pid

# Port du serveur HTTP (Interface Web)
-w=3000

# Interfaces à écouter (WAN + les 3 VLANs)
-i=eth0
-i=vlan10
-i=vlan20
-i=vlan30

# Définition des sous-réseaux locaux pour le suivi des flux internes
-m=192.168.10.0/24,192.168.20.0/24,192.168.30.0/24

# Résolution DNS numérique (évite la saturation DNS)
-n=1

# Journalisation
-e=
EOF

echo "=========================================================="
echo " [4/4] Démarrage du service NTOPng..."
echo "=========================================================="

# Recharger les démons et démarrer ntopng
sudo systemctl daemon-reload
sudo systemctl enable ntopng
sudo systemctl restart ntopng

# Vérification du port 3000
echo ""
echo "Vérification de l'écoute sur le port 3000 :"
sudo ss -tulpn | grep 3000 || echo "NTOPng est en cours d'initialisation..."

echo ""
echo "=========================================================="
echo " NTOPng est déployé avec succès !"
echo " Accès Web : http://<IP_DE_VOTRE_VM>:3000"
echo " Identifiants par défaut :"
echo "   - Utilisateur : admin"
echo "   - Mot de passe : admin"
echo " (Le mot de passe vous sera demandé d'être modifié dès la 1ère connexion)"
echo "=========================================================="
