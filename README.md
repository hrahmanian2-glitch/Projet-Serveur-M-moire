
## Projet Serveur Mémoire

### Identité

* Nom : Hadi Rahmanian
* Numéro étudiant : 22206278
* Matière : Système_2 - L2 Université de Nice

---

## Présentation générale

Ce projet consiste à implémenter un serveur mémoire en Python.
Le serveur héberge une mémoire et permet à des clients d'y accéder
pour créer des segments, lire et écrire des données.

Le projet est divisé en 7 étapes progressives :
- Les étapes 1 et 2 mettent en place le backend qui gère la mémoire
- L'étape 3 ajoute la segmentation avec un frontend
- L'étape 4 compose frontend et backend avec des pipes
- L'étape 5 transforme le tout en vrai serveur TCP
- L'étape 6 teste le serveur avec un client Python
- L'étape 7 ajoute un cache local pour améliorer les performances

Les techniques utilisées sont : bytearray, signaux, pipes,
redirections, fork, socket TCP, segmentation, pagination et
mise en cache.

### Étape 1 — Pilotage depuis le terminal

Cette partie a été réalisée sans difficulté majeure. Le programme `server_mem_backend.py` lit les commandes `GET` et `POST` depuis l’entrée standard et les applique sur une zone mémoire représentée par un `bytearray`, initialisé avec des espaces (valeur 32). La taille de cette mémoire est passée en argument au lancement.

J’ai également ajouté des vérifications pour éviter les accès hors limites ainsi que les valeurs invalides (en dehors de 0–255). Lorsque l’entrée standard est fermée, le programme affiche `"bye"` puis se termine proprement.

---

### Étape 2 — Sauvegarde périodique

J’ai ajouté une option `--periodic-log` qui permet d’activer une sauvegarde automatique de la mémoire. Cela repose sur l’utilisation du signal `SIGALRM`, déclenché toutes les secondes.

À chaque déclenchement, le contenu complet de la mémoire est écrit sur la sortie d’erreur. Le signal est réarmé après chaque appel avec `signal.alarm(1)`.

---

### Étape 3 — Mémoire segmentée

Dans cette étape, j’ai introduit un frontend (`server_mem_frontend.py`) chargé de gérer une mémoire segmentée. Les segments sont stockés dans un dictionnaire Python.

Le frontend traduit les adresses virtuelles en adresses physiques avant de les transmettre au backend. Par exemple, une commande comme `GET seg0 3` est transformée en une adresse physique correspondante.

Les opérations `PUT` et `DELETE` permettent d’ajouter ou supprimer des segments. L’allocation utilise une stratégie *first fit*. Les messages de succès ou d’erreur sont envoyés sur `stderr`, tandis que les commandes traduites sont envoyées sur `stdout`.

---

### Étape 4 — Communication frontend/backend

J’ai ensuite regroupé le frontend et le backend dans un même programme (`server_mem.py`) en utilisant `os.fork()`.

Deux processus fils sont créés, et des pipes permettent de faire circuler les données entre eux :

* parent → frontend
* frontend → backend

Le processus parent lit les commandes depuis l’entrée standard et les transmet au frontend.


**
Lors de la démo du 27/04, mon chargé de TP m'a dit que si je
terminais l'étape 4 avant la fin de la séance j'aurais 12/20.
J'ai terminé l'étape 4 et montré mon travail pendant la séance,
mais le chargé de TP n'a pas eu le temps de vérifier et de
mettre à jour ma note.
**
---

### Étape 5 — Serveur TCP

Le programme a été adapté pour fonctionner comme un serveur TCP. Il accepte les connexions entrantes, lit les commandes envoyées par un client, puis les transmet au frontend.

La réponse produite est ensuite renvoyée au client avant de fermer la connexion. Trois pipes sont utilisés pour organiser les échanges entre les différents composants.

Les tests réalisés avec `telnet` montrent que les commandes `PUT`, `GET`, `POST` et `DELETE` fonctionnent correctement.

---

### Étape 6 — Client sans cache

**6.1**
J’ai utilisé la librairie `remotememory`, qui permet de manipuler la mémoire distante via un context manager (`with`). Les méthodes `__enter__` et `__exit__` facilitent l’utilisation, notamment en automatisant l’envoi de `DELETE` à la fin du bloc.

**6.2**
J’ai testé l’exécution de deux clients en parallèle sur des segments différents (500 000 accès chacun). Aucun problème n’a été observé, ce qui est cohérent puisque les segments ne se chevauchent pas.

Un bug lié au mélange des réponses dans les pipes a été corrigé en s’assurant de lire les réponses complètes jusqu’au caractère de fin de ligne.

**6.3**
J’ai ajouté un paramètre `alloc=True` pour contrôler l’allocation automatique. Avec l’option `--no-alloc`, deux clients peuvent accéder au même segment. Dans ce cas, des corruptions apparaissent, ce qui confirme l’absence de synchronisation entre accès concurrents.

---

### Étape 7 — Client avec cache

J’ai implémenté un mécanisme de cache côté client dans `remotememory.py`.

Le serveur a été légèrement modifié pour travailler par pages :

* `PUT` accepte une taille de page
* `GET` lit une page complète
* `POST` écrit une page complète

Le cache est basé sur un dictionnaire avec :

* les données des pages
* un indicateur *dirty*

J’ai utilisé une politique FIFO pour le remplacement. Les pages modifiées sont renvoyées au serveur avant suppression, tandis que les autres sont simplement supprimées localement.

Les performances ont été nettement améliorées :

* sans cache : ~70 secondes
* avec cache : ~7,75 secondes

Le gain est donc d’environ un facteur 9.

---

## Estimation de note

Je pense que le projet est globalement complet et fonctionne comme attendu. Une note autour de 18–19/20 me semble cohérente.





## Mot personnel



Bonjour,

Je suis étudiant iranien. Ce semestre a été particulièrement
difficile pour moi en raison de la situation de guerre en Iran
et des manifestations. J'ai perdu un ami proche durant cette
période, ce qui m'a empêché de me concentrer pleinement sur
mes études et de participer régulièrement aux cours et aux TDs.

Malgré ces circonstances très difficiles, j'ai persévéré et
j'ai réussi à terminer ce projet en entier. Ce projet m'a
permis d'apprendre et de comprendre pleinement les concepts
du cours : pipes, signaux, sockets, segmentation, pagination
et mise en cache. C'est en travaillant sur ce projet que j'ai
vraiment assimilé la matière.

Je suis fier du chemin parcouru malgré les obstacles et je
vous remercie sincèrement pour votre compréhension et votre
bienveillance.

Cordialement,
Hadi Rahmanian