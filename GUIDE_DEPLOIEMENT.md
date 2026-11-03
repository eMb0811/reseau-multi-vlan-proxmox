# Rapport Final de Déploiement : VM Dédiée Groupe (VM 312) & Switch Cisco

Toutes les opérations de séparation des environnements et de déploiement de votre VM groupe ont été achevées avec succès.

---

## 1. Séparation des Deux Groupes sur Proxmox (`10.153.4.186`)

| Machine | Propriétaire | Statut | Rôle & Adresses IP |
| :--- | :--- | :--- | :--- |
| **VM 311 (`routeur-tp`)** | **Autre Groupe** | ✅ **Restaurée** | Remise dans son état initial via son snapshot `Final`. IP WAN : `10.153.4.173`. |
| **VM 312 (`routeur-groupe`)** | **VOTRE GROUPE** | ✅ **Déployée & Active** | Votre VM dédiée. IP WAN : **`10.153.4.174`**. Trunk sur `vmbr2` vers votre switch physique. |

---

## 2. État Complet de Votre VM Dédiée (VM 312 - `routeur-groupe`)

* **Interface WAN (`ens18` sur `vmbr0`) :**
  * **Adresse IP statique :** `10.153.4.174/24`
  * **Passerelle université :** `10.153.4.254`
  * **Serveurs DNS :** `172.16.2.11` et `1.1.1.1`
* **Interface LAN Trunk (`ens19` sur `vmbr2`) :**
  * **VLAN 10 (Étudiants) :** sous-interface `ens19.10` en `192.168.10.254/24`
  * **VLAN 20 (Personnel) :** sous-interface `ens19.20` en `192.168.20.254/24`
  * **VLAN 30 (Visiteurs) :** sous-interface `ens19.30` en `192.168.30.254/24`
* **Routage & NAT Masquerade :**
  * `net.ipv4.ip_forward = 1` actif et persistant dans `/etc/sysctl.d/99-ipforward.conf`.
  * `iptables -t nat -A POSTROUTING -o ens18 -j MASQUERADE` sauvegardé dans `/etc/iptables/rules.v4`.
* **Services DHCP & Cache DNS :**
  * `isc-dhcp-server` actif sur les sous-interfaces VLAN, distribuant les baux `.100` à `.200`.
  * `bind9` (DNS cache) actif sur les passerelles `.254`.
* **Sonde de Monitoring NTOPng :**
  * Service actif sur le port HTTP `3000`.
  * Supervisant les flux de `ens18` (WAN) et des 3 VLANs internes.
  * **URL d'accès :** 👉 **`http://10.153.4.174:3000`** *(identifiants : `admin` / `admin`)*.

---

## 3. Configuration Active du Switch Physique Cisco (Catalyst 2950G)

Configuré directement via votre port console série (COM7) et sauvegardé en NVRAM :

* **Port `FastEthernet0/1` :** Mode **Trunk 802.1Q** vers Proxmox `vmbr2` (VLANs autorisés : 10, 20, 30).
* **Ports `FastEthernet0/2` à `16` :** Mode **Accès VLAN 10 (Étudiants)** avec `portfast`.
* **Ports `FastEthernet0/17` à `32` :** Mode **Accès VLAN 20 (Personnel)** avec `portfast`.
* **Ports `FastEthernet0/33` à `48` :** Mode **Accès VLAN 30 (Visiteurs)** avec `portfast`.
