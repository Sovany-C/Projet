import pandas as pd

COLONNES = {
    "#": "id", "Name": "name", "Type 1": "type1", "Type 2": "type2",
    "HP": "hp", "Attack": "attack", "Defense": "defense",
    "Sp. Atk": "sp_atk", "Sp. Def": "sp_def", "Speed": "speed",
    "Generation": "generation", "Legendary": "legendary",
}

def load_pokemons(path="pokemon.csv"):
    """Chargement du fichier pokemon.csv"""

    df = pd.read_csv(path).rename(columns=COLONNES)
    df.loc[df["id"] == 63, "name"] = "Primeape"       # nom manquant dans le fichier
    df["type2"] = df["type2"].fillna("")
    return df

def filter(df,nom="",generation="All",type="All",legendaire=False): #Valeur par défaut
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
    