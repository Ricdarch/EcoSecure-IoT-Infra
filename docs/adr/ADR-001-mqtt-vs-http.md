# ADR-001 — Choix de MQTT plutôt que HTTP

## Contexte
Je devais choisir un protocole de communication entre les devices simulés et le broker.

## Options considérées
- HTTP REST — simple mais trop verbeux pour l'IoT
- WebSocket — bidirectionnel mais complexe à gérer
- MQTT — léger, publish/subscribe, standard IoT

## Décision
MQTT via Mosquitto, puis migration prévue vers AWS IoT Core.

## Raisons
- Protocole standard de l'industrie IoT
- Léger — idéal pour des devices à ressources limitées
- Le modèle pub/sub permet de brancher facilement 
  de nouveaux composants sans modifier les existants

## Conséquences
- Nécessite un broker (Mosquitto conteneurisé)
- TLS à configurer manuellement (erreur rencontrée 
  sur les chemins dans Docker — voir ADR-003)

## Statut
✅ Implémenté