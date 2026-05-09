# ADR-002 — Suppression de l'API entre le publisher et le broker

## Contexte
Dans la conception initiale, j'envisageais une API REST entre le mock publisher et le broker MQTT pour contrôler la communication entre les deux.

## Idée initiale
Publisher → API REST → Broker MQTT

## Pourquoi j'ai abandonné cette idée
En analysant le rôle de chaque composant, j'ai réalisé que MQTT est lui-même un protocole de communication ajouter une API entre les deux revenait à dupliquer cette responsabilité inutilement.

L'API aurait introduit :
- Une latence supplémentaire
- Un point de défaillance de plus
- Une complexité sans valeur ajoutée

## Décision finale
Publisher → MQTT direct → Broker

## Ce que ça m'a appris
Un bon système distribué minimise les intermédiaires inutiles. Chaque composant doit avoir une responsabilité claire et unique (principe de responsabilité unique).

## Statut
✅ Décision validée et implémentée