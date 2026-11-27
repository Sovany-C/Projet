import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import time

STATS = ["hp", "attack", "defense", "sp_atk", "sp_def", "speed"]
COLONNES = {
    "#": "id", "Name": "name", "Type 1": "type1", "Type 2": "type2",
    "HP": "hp", "Attack": "attack", "Defense": "defense",
    "Sp. Atk": "sp_atk", "Sp. Def": "sp_def", "Speed": "speed",
    "Generation": "generation", "Legendary": "legendary",
    "Cluster" : "cluster"
}

def load_pokemons(path="pokemon.csv"):
    """Chargement du fichier pokemon.csv"""

    df = pd.read_csv(path).rename(columns=COLONNES)
    df.loc[df["id"] == 63, "name"] = "Primeape"       # nom manquant dans le fichier
    df["type2"] = df["type2"].fillna("")
    return df

def filter(df,nom="",generation="All",type="All",legendaire=False,gr="All"): #Valeur par défaut
    """Filtrage selon paramètres en entrée"""

    masque = pd.Series(True, index=df.index) # applique une valeur True à tout les éléments (pokémons)
    
    if nom : #si paramètre non nul
        # modifie valeur de l'élément si le nom ne correspond pas à la chaine de caractère taper
        masque &= df["name"].str.contains(nom, case=False, regex=False)
    if generation != "All":
        masque &= df["generation"] == int(generation)
    if type!= "All":
        masque &= (df["type1"] == type) | (df["type2"] == type)
    if legendaire:
        masque &= df["legendary"]
    if gr != "All":
        masque &= df["cluster"] == int(gr)
    return df[masque]

def list_conv(df):
    """Convertit le dataFrame en dictionnaire = format attendu par l'interface"""
    return df.to_dict("records")


# Test
if __name__ == "__main__":
    tous = load_pokemons("pokemon.csv")
    print(len(tous),"Pokémon chargés")
    feu = list_conv(filter(tous, type="Fire"))
    print([p["name"] for p in feu[:5]])

    
# Groupe Clustering

def cluster(df):
    # Normalisation
    scaler = StandardScaler()

    # Clustering
    # t0 = time.perf_counter()
    kmeans = KMeans(n_clusters=4, random_state=42)
    X = scaler.fit_transform(df[STATS])
    kmeans.fit(X)
    labels = kmeans.predict(X)
    # t_kmeans = time.perf_counter() - t0

    # print(t_kmeans)

    # Projection sur PCA
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X)

    dt_cluster = df.copy()
    dt_cluster["cluster"] = labels
    dt_cluster["pc1"] = coords[:,0]
    dt_cluster["pc2"] = coords[:,1]

    # Infos pour le graphique et l'interprétation, rangées dans .attrs
    dt_cluster.attrs["pca_variance"] = pca.explained_variance_ratio_.tolist()
    dt_cluster.attrs["pca_poids"] = {
        stat: (float(p1), float(p2))
        for stat, p1, p2 in zip(STATS, pca.components_[0], pca.components_[1])
    }
    return dt_cluster


