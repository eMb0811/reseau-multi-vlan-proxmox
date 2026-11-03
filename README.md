# 🌐 Architecture Réseau Multi-VLAN & Routeur Linux Dédié (TP4)

[![Status](https://img.shields.io/badge/Status-100%25%20Validé-success?style=for-the-badge&logo=checkmarx)](rapport_tp_admin_reseau.pdf)
[![Platform](https://img.shields.io/badge/Hyperviseur-Proxmox%20VE%208.x-E57000?style=for-the-badge&logo=proxmox)](https://www.proxmox.com)
[![OS](https://img.shields.io/badge/Routeur-Ubuntu%2022.04%20LTS-E95420?style=for-the-badge&logo=ubuntu)](https://ubuntu.com)
[![Hardware](https://img.shields.io/badge/Switch-Cisco%20Catalyst%202950G-1BA0D7?style=for-the-badge&logo=cisco)](https://www.cisco.com)
[![Monitoring](https://img.shields.io/badge/Supervision-NTOPng%20LAN%20Only-blue?style=for-the-badge)](http://10.153.4.174:3000)

> **Projet complet d'administration système & réseau :** Déploiement d'un routeur virtuel d'entreprise (*Router-on-a-Stick*), segmentation 802.1Q sur commutateur physique Cisco, services ISC-DHCP / DNS récursif BIND9, filtrage par état & adresses MAC, translation d'adresses NAT Masquerade et métrologie de flux réseau en temps réel avec NTOPng (restreint au LAN).

---

## 📑 Rapport Technique d'Exploitation (PDF)

Le rapport complet de 19 pages détaillant l'ensemble des étapes, justifications théoriques, tests physiques et fichiers de configuration commentés ligne par ligne est disponible directement :
* 📄 **[Consulter / Télécharger le Rapport PDF (rapport_tp_admin_reseau.pdf)](rapport_tp_admin_reseau.pdf)**
* 🌐 **[Version HTML Paged Media (rapport_tp_admin_reseau.html)](rapport_tp_admin_reseau.html)**

---

## 🏗️ Topologie & Architecture Réseau

```text
+------------------------------------------------------------------------------------------------------+
|                                     RÉSEAU UNIVERSITAIRE / CAMPUS                                     |
|                                    10.153.4.0/24  (Passerelle: 10.153.4.254)                          |
+---------------------------------------------------+--------------------------------------------------+
                                                    | (Uplink WAN physique enp4s0f0)
                                                    v
+------------------------------------------------------------------------------------------------------+
| HYPERVISEUR PROXMOX VE (10.153.4.186)                                                                |
|                                                                                                      |
|   +-----------------------+     +-----------------------+     +----------------------------------+   |
|   | Bridge WAN : vmbr0    |     | Bridge GROUPE 1: vmbr1|     | Bridge NOTRE GROUPE : vmbr2      |   |
|   | (Liaison WAN campus)  |     | (Autre Groupe - VM311)|     | (Esclave physique : enp3s0f1)    |   |
|   +-----------+-----------+     +-----------------------+     +-----------------+----------------+   |
|               |                                                                 |                    |
|               +-------------------------------+                                 | (Trunk 802.1Q)     |
|                                               |                                 |                    |
|       +---------------------------------------v---------------------------------v----------------+   |
|       | VM 312 : "routeur-groupe" (Ubuntu Server 22.04 LTS)                                      |   |
|       |                                                                                          |   |
|       | - WAN ens18 : 10.153.4.174/24 (Passerelle amont: 10.153.4.254)                          |   |
|       | - LAN ens19 (Trunk 802.1Q vers vmbr2) :                                                  |   |
|       |      * ens19.10 : 192.168.10.254/24 (Passerelle Étudiants)                               |   |
|       |      * ens19.20 : 192.168.20.254/24 (Passerelle Personnel)                               |   |
|       |      * ens19.30 : 192.168.30.254/24 (Passerelle Visiteurs)                               |   |
|       | - Services : Routage Kernel, NAT Masquerade, DHCP ISC, Cache BIND9, NTOPng (LAN Only)    |   |
|       +------------------------------------------------------------------------------------------+   |
+----------------------------------------------------------------------------------|-------------------+
                                                                                   | Câble Ethernet
                                                                                   v
+------------------------------------------------------------------------------------------------------+
| COMMUTATEUR PHYSIQUE CISCO CATALYST 2950G (Console Série COM7)                                       |
|                                                                                                      |
|   Port Fa0/1 : TRUNK 802.1Q (Allowed VLANs: 10, 20, 30)                                              |
|                                                                                                      |
|   [ Ports Fa0/2 - 16 ]            [ Ports Fa0/17 - 32 ]                 [ Ports Fa0/33 - 48 ]        |
|   Mode Accès : VLAN 10            Mode Accès : VLAN 20                  Mode Accès : VLAN 30         |
|   « Étudiants »                   « Personnel »                         « Visiteurs »                |
|   Spanning-Tree Portfast          Spanning-Tree Portfast                Spanning-Tree Portfast       |
+-----------+-----------------------------------+----------------------------------+-------------------+
            | (ex: Port Fa0/2)                  |                                  |
            v                                   v                                  v
    +---------------+                   +---------------+                  +---------------+
    |   PC Client   |                   |   PC Client   |                  |   PC Client   |
    | 192.168.10.101|                   | 192.168.20.X  |                  | 192.168.30.X  |
    +---------------+                   +---------------+                  +---------------+
```

---

## 📊 Matrice d'Adressage IP & Segmentation

| Segment Réseau | VLAN ID | Sous-Réseau | Passerelle VM 312 | Plage DHCP | Suffixe DNS | Ports Commutateur Cisco |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **WAN Campus** | - | `10.153.4.0/24` | `10.153.4.174` (Fixe) | Statique | `172.16.2.11` / `1.1.1.1` | Uplink `enp4s0f0` |
| **Étudiants** | **10** | `192.168.10.0/24` | `192.168.10.254` | `.100` à `.200` | `etudiants.local` | `FastEthernet 0/2 - 16` |
| **Personnel** | **20** | `192.168.20.0/24` | `192.168.20.254` | `.100` à `.200` | `personnel.local` | `FastEthernet 0/17 - 32` |
| **Visiteurs** | **30** | `192.168.30.0/24` | `192.168.30.254` | `.100` à `.200` | `visiteurs.local` | `FastEthernet 0/33 - 48` |

---

## 📁 Structure du Répertoire & Fichiers de Configuration

```text
├── rapport_tp_admin_reseau.pdf      # Rapport complet d'exploitation (19 pages)
├── rapport_tp_admin_reseau.html     # Source HTML haute fidélité du rapport
├── generate_pdf_report.py           # Script Python de compilation PDF vectoriel
├── cisco_switch_config.ios          # Script IOS Cisco complet commenté
├── 60-routeur-tp.yaml               # Configuration Netplan en production sur la VM 312
├── 01-netplan-static.yaml           # Variante Netplan statique
├── 01-netplan-dhcp.yaml             # Variante Netplan en DHCP
├── dhcpd.conf                       # Configuration ISC-DHCP Server (3 pools VLANs)
├── named.conf.options               # Configuration DNS récursif BIND9
├── rules.v4                         # Règles de filtrage Iptables & NAT Masquerade
├── ntopng.conf                      # Configuration NTOPng (Supervision LAN exclusive)
├── setup_router_nat.sh              # Script d'automatisation routage Kernel & NAT iptables
├── setup_dnsmasq.sh                 # Script d'automatisation alternatif Dnsmasq
├── dnsmasq.conf                     # Configuration alternative Dnsmasq
├── install_ntopng.sh                # Script de déploiement NTOPng & Redis
├── GUIDE_DEPLOIEMENT.md             # Synthèse textuelle d'exploitation
├── ntopng_dashboard.png             # Capture du tableau de bord NTOPng (Port 3000)
└── README.md                        # Documentation d'accueil GitHub
```

---

## 🛡️ Filtrage de Sécurité & Commandes Administrateur

### 1. Blocage d'une adresse MAC vers Internet
Pour empêcher une station de travail spécifique d'accéder au WAN / Internet tout en conservant son accès au réseau local :

```bash
# Blocage immédiat avec notification ICMP (REJECT)
# ATTENTION : Les adresses MAC sous Linux s'écrivent avec des deux-points (:)
sudo iptables -I FORWARD 1 -m mac --mac-source ac:ed:5c:11:9a:a4 -o ens18 -j REJECT

# Variante silencieuse (DROP)
sudo iptables -I FORWARD 1 -m mac --mac-source ac:ed:5c:11:9a:a4 -o ens18 -j DROP

# Sauvegarde permanente au redémarrage
sudo netfilter-persistent save
```

### 2. Supervision NTOPng restreinte au LAN
Pour concentrer l'analyse uniquement sur les flux des utilisateurs internes et éliminer le bruit du réseau universitaire :
* **Interfaces capturées :** `ens19.10`, `ens19.20`, `ens19.30` (exclusion de `ens18`).
* **Sous-réseaux locaux :** `192.168.10.0/24, 192.168.20.0/24, 192.168.30.0/24`.
* **Accès web :** `http://10.153.4.174:3000`.

---

## 🛠️ Points Techniques Remarquables

1. **Isolation Multi-Tenant :** Affectation de l'autre groupe (VM 311) sur `vmbr1` / `enp3s0f0`, et étanchéité de notre **VM 312** (`routeur-groupe`, WAN `10.153.4.174` sur `vmbr2` / `enp3s0f1`).
2. **Cisco Spanning-Tree Portfast :** Activation de `spanning-tree portfast` sur tous les ports d'accès pour contourner le délai de 30 secondes d'apprentissage STP 802.1D et garantir la négociation immédiate des baux DHCP.
3. **Détection Physique sur Proxmox :** Identification de la porteuse active (`carrier = 1`) sur l'interface serveur `enp3s0f1` et liaison à chaud sur `vmbr2` en mode `bridge-vlan-aware yes`.
4. **NAT Masquerade & Stateful Filtering :** Translation dynamique SNAT par `iptables` sur `ens18` et filtrage de retour sécurisé par suivi d'état `RELATED,ESTABLISHED`.
5. **Résolution DNS & Sonde NTOPng :** Cache BIND9 avec récursion amont (`172.16.2.11`, `1.1.1.1`, `8.8.8.8`) et sonde NTOPng active sur le port HTTP 3000 (`admin` / `passer2026`).

---

## 🧪 Preuves de Validation en Conditions Réelles

* **Bail DHCP PC Client (Port Fa0/2 - VLAN 10) :** `192.168.10.101/24`, Passerelle `192.168.10.254`, Suffixe `etudiants.local`.
* **Ping Passerelle du Routeur :** 0% de perte, latence `< 1 ms`.
* **Sortie Internet Réelle :** `curl -I --interface 192.168.10.101 https://www.google.com` &rarr; `HTTP/1.1 200 OK`.
* **Tableau de Bord NTOPng :** Capture des flux en temps réel sur les interfaces locales (`ens19.10`, `ens19.20`, `ens19.30`).

---

## 👤 Auteur & Contexte Académique
* **Auteur :** Mouhamet Barry ([@eMb0811](https://github.com/eMb0811))
* **Session :** Travaux Pratiques d'Administration Système & Réseau — Novembre 2026
