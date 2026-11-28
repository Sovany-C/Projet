import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from data import load_pokemons, STATS

data = load_pokemons()

X_leg=data[STATS]
Y_leg=data["legendary"].astype(int)

#Normaliser les données

scaler=StandardScaler()
scaler.fit(X_leg)
X_leg_scaled=scaler.transform(X_leg)

#Création + entrainement du modèle KNN

model_scaled_3=KNeighborsClassifier(n_neighbors=3)
model_scaled_3.fit(X_leg_scaled,Y_leg)

# Prédire le caractère légendaire d'un Pokémon à partir des statistiques données par l'utilisateur
# Créer une fonction qui reçoit les stats du Poké
def predict_legendary(stats):
    pokemon=pd.DataFrame([stats], columns=STATS)
    # Normaliser les données du Pokémon
    pokemon_scaled=scaler.transform(pokemon)
    return model_scaled_3.predict(pokemon_scaled)[0]
    # pour extraire la première valeur du tableau de sortie, on met [0] à la fin de la ligne, puisque la fonction renvoie un tableau avec une seule valeur.


# TEST Poké legendaire

# print(predict_legendary({
#     "hp": 106,
#     "attack": 110,
#     "defense": 90,
#     "sp_atk": 154,
#     "sp_def": 90,
#     "speed": 130
# }))

# # TEST Poké non legendaire

# # TEST
# print(predict_legendary({
#     "hp": 35,
#     "attack": 55,
#     "defense": 40,
#     "sp_atk": 50,
#     "sp_def": 50,
#     "speed": 90
# }))