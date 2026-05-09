### Naissance du projet

L'idée de concevoir ce projet m'es venu lors de ma dernière année d'école d'ingénieur car je voulais construire quelques chose qui touche à l'IoT et l'edge computing. J'ai beaucoup apprécier ces deux domaines lors d'un cours à l'école et j'ai directement voulu en apprendre d'avantage.
### Pourquoi les prises électriques connectées ?

J'ai choisi les prises électriques connectées car elles combinent plusieurs problématiques intéressantes (consommation énergétique, état de connexion et détection d'anomalies). ==De plus j'ai pour objectif d'ajouter les aspects GreenOps et FinOps au sein de mon projet car ce sont des aspects que j'ai envie d'implémenter car ce sont des enjeux importants au sein de notre société. (phrase à réécrire)==
### Première obstacle - L'idée de l'API 

Au départ je voulais partir sur une API REST entre le publisher et le broker MQTT car l'API devait réglementer la communication entre les deux. Puis l'API devait envoyer les données vers le cloud. L'idée me semblait logique sur le papier mais en commençant à implémenter, j'ai réaliser que le publisher, broker et subscriber me suffisait, le filtrage des données se faisait tard et non avant d'arriver dans le cloud.
### Ressources

Stéphane Robert : https://blog.stephane-robert.info