import customtkinter as ctk
from data import filter, list_conv

TYPE_COLORS = {
    "Normal": "#A8A878", "Fire": "#F08030", "Water": "#6890F0", "Grass": "#78C850",
    "Electric": "#F8D030", "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0",
    "Ground": "#E0C068", "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820",
    "Rock": "#B8A038", "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848",
    "Steel": "#B8B8D0", "Fairy": "#EE99AC",
}

PAR_PAGE = 18 #Nombre de pokémons par Page

def badge_type(master, type_):
    """Petit badge arrondi coloré pour un type."""
    return ctk.CTkLabel(master, text=type_, width=70, height=22, corner_radius=11,
                        fg_color=TYPE_COLORS.get(type_, "gray40"), text_color="white",
                        font=("Arial", 11, "bold"))

class HomePage(ctk.CTkFrame):
    """Page principale : affichage de la liste des pokémons et fonction de trie"""
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.filtres = list_conv(app.pokemons) # Liste affichée
        self.page = 0
        
        self.grid_columnconfigure(0, weight=1)   
        self.grid_rowconfigure(1, weight=1)

        self.search_frame = Search_frame(self, on_search=self.appliquer_filtre)
        self.search_frame.grid(row=0,column=0,sticky="ew")
        
        self.contenu_frame = Contenu_frame(self, on_select=self.open_pokemon)
        self.contenu_frame.grid(row=1,column=0,sticky="nsew")

        # Barre de pagination
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=2, column=0, pady=5)
        self.btn_prec = ctk.CTkButton(nav, text="< Précédent", width=110, command=self.precedent)
        self.btn_prec.pack(side="left", padx=10)
        self.label_page = ctk.CTkLabel(nav, text="")
        self.label_page.pack(side="left", padx=10)
        self.btn_suiv = ctk.CTkButton(nav, text="Suivant >", width=110, command=self.suivant)
        self.btn_suiv.pack(side="left", padx=10)

        self.affiche_page()
    
    def affiche_page(self):
        """Affichage des N pokémons de la page"""
        debut = self.page * PAR_PAGE
        if (debut + PAR_PAGE <= len(self.filtres)) :
            self.contenu_frame.afficher(self.filtres[debut:debut + PAR_PAGE])
        else : # Permet d'afficher uniquement le nombre nécessaire de widget sur la dernière page
            self.contenu_frame.afficher(self.filtres[debut:debut + (len(self.filtres)-debut)])

        total = max(1, -(-len(self.filtres) // PAR_PAGE))     # division arrondie au-dessus
        self.label_page.configure(
            text=f"Page {self.page + 1} / {total}  ({len(self.filtres)} Pokémon)")
        #self.btn_prec.configure(state="normal" if self.page > 0 else "disabled")
        #self.btn_suiv.configure(state="normal" if self.page < total - 1 else "disabled")
    
    def appliquer_filtre(self, nom, generation, type, legendaire, groupe):
        """Fonction de trie"""
        resultat = filter(self.app.pokemons, nom, generation, type, legendaire, groupe)
        self.filtres = list_conv(resultat)
        self.page = 0
        self.affiche_page()

    # Navigation entre les pages
    def precedent(self):
        self.page -= 1
        if self.page < 0:
            self.page = max(1, -(-len(self.filtres) // PAR_PAGE)) - 1
        self.affiche_page()

    def suivant(self):
        self.page += 1
        if self.page >=  max(1, -(-len(self.filtres) // PAR_PAGE)):
            self.page = 0
        self.affiche_page()

    def open_pokemon(self,pokemon):
        """Ouverture page avec informations complémentaires sur le pokémon"""
        print(pokemon["name"])


    def on_show(self):
        print("Home")

    
# Pages à définir
class InfoPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.text = ctk.CTkLabel(self, text="Infos", fg_color="#bdffff")
        self.text.pack(fill="x")

    def on_show(self):
            print("Infos")

class PredictionPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.text = ctk.CTkLabel(self, text="Prediction", fg_color="#bdffff")
        self.text.pack(fill="x")

    def on_show(self):
            print("Predictions")

class ScanPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.text = ctk.CTkLabel(self, text="Scan", fg_color="#bdffff")
        self.text.pack(fill="x")

    def on_show(self):
            print("Scan")



# Ensemble des sous-frames

class Search_frame(ctk.CTkFrame):
    """Barre de recherche de la page principale"""
    def __init__(self, master, on_search):
        super().__init__(master, fg_color= ["#DC0A2D", "#bdffff"], corner_radius=0, height=30)
        self.grid_columnconfigure((0,1,2,3,4,5, 6), weight=1)

        self.on_search = on_search

        self.entry = ctk.CTkEntry(self, placeholder_text="Search Pokemon")
        self.entry.grid(row=1, column=0, pady=(0,10), padx=20, sticky="ew", columnspan=2)

        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_pokemon, fg_color=["#DC0A2D","#144870"], hover_color=["#DC0A2D","#44eee6"])
        self.search_button.grid(row=1, column=6, pady=(0,10), sticky = 'ew')

        self.genLab = ctk.CTkLabel(self, text="Génération")
        self.genLab.grid(row=0,column=2,pady=0,padx=10,sticky="sew")
        Generation = ["All","1", "2", "3", "4", "5", "6"]
        self.generation_filter = ctk.CTkOptionMenu(self, values=Generation)
        self.generation_filter.grid(row=1, column=2, pady=(0,10), padx=10,sticky="ew")

        self.typeLab = ctk.CTkLabel(self,text="Types")
        self.typeLab.grid(row=0,column=3,pady=0,padx=10,sticky="sew")
        Type = ["All","Normal", "Fire", "Water", "Grass", "Electric", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
        self.type_filter = ctk.CTkOptionMenu(self, values=Type)
        self.type_filter.grid(row=1, column=3, pady=(0,10), padx=10,sticky="ew")

        self.check_leg = ctk.CTkCheckBox(self, text="Legendary")
        self.check_leg.grid(row=1, column=5, pady=(0,10), padx=10)

        self.grLabel = ctk.CTkLabel(self,text="Groupe")
        self.grLabel.grid(row=0,column=4,pady=0,padx=10,sticky="sew")
        self.grfilter = ctk.CTkOptionMenu(self, values=["All","0","1","2","3"])
        self.grfilter.grid(row=1, column=4, pady=(0,10), padx=10,sticky="ew")


    def search_pokemon(self):
        # Récupération données nécessaire à la recherche
        pokemon_name = self.entry.get().strip()
        generation_filter = self.generation_filter.get()
        type_filter = self.type_filter.get()
        legendary_filter = self.check_leg.get()
        gr_filter = self.grfilter.get()

        self.on_search(pokemon_name, generation_filter, type_filter, legendary_filter, gr_filter)

        # if not pokemon_name:
        #     print("Please enter a Pokemon name.")
        # else:
        #     print(f"Searching for Pokemon: {pokemon_name}")

        # print(f"Generation filter: {generation_filter}")
        # print(f"Type filter: {type_filter}")
        # print(f"Legendary filter: {legendary_filter}")


class Contenu_frame(ctk.CTkScrollableFrame):
    """Cadre qui contient l'ensemble des widgets des pokémons"""
    def __init__(self, master,on_select=None):
        super().__init__(master, corner_radius=0)
        self.on_select = on_select
        self.rows = []
        self.grid_columnconfigure(0, weight=1)

    def afficher(self, pokemons): # Affichage des pokémons nécessaires
        # Crée seulement les barres qui manquent
        while len(self.rows) < len(pokemons):
            row = PokemonRow(self, on_click=self.on_select)
            row.grid(row=len(self.rows), column=0, sticky="ew", padx=10, pady=3)
            self.rows.append(row)

        # Réutilise les barres existantes et met à jour le contenu
        for i, row in enumerate(self.rows):
            if i < len(pokemons):
                row.maj(pokemons[i])
                row.grid()                     # réaffiche si elle était cachée
            else:
                row.grid_remove()              # cache les barres en trop

        self._parent_canvas.yview_moveto(0)    # remonte en haut à chaque nouvelle page


class PokemonRow(ctk.CTkFrame):
    """Barre clickable pour chaque pokémon"""

    COULEUR = "#999697"
    COULEUR_SURVOL = "#3F3F3F"

    def __init__(self, master, on_click=None):
        super().__init__(master, height=30, corner_radius=8, fg_color="#999697")

        self.on_click = on_click

        self.grid_columnconfigure(0,weight=1)

        self.nameLabel = ctk.CTkLabel(self, text="", anchor="w")
        self.nameLabel.grid(row=0,column=0,padx=15, sticky="w")

        types = ctk.CTkFrame(self,fg_color="transparent")
        types.grid(row=0,column=1,padx=10)
        self.badge1 = badge_type(types, "")
        self.badge1.grid(row=0, column=0, padx=2)
        self.badge2 = badge_type(types, "")
        self.badge2.configure(fg_color="transparent")
        self.badge2.grid(row=0, column=1, padx=2)
        

        self.genLabel = ctk.CTkLabel(self,text="", anchor="w")
        self.genLabel.grid(row=0,column=2,padx=15, sticky="w")

        self.grLabel = ctk.CTkLabel(self, text="", anchor="w")
        self.grLabel.grid(row=0,column=3,padx=15, sticky="w")

        self._lier(self)

    def maj(self, pokemon):
        """Change le contenu sans recréer de widget"""
        self.pokemon = pokemon

        if self.nameLabel.cget("text") != pokemon["name"]:
            self.nameLabel.configure(text=pokemon["name"])

        if self.badge1.cget("text") != pokemon["type1"]:
            self.badge1.configure(text=pokemon["type1"], fg_color=TYPE_COLORS.get(pokemon["type1"], "#999697"))
        
        if pokemon["type2"]:
            if self.badge2.cget("text") != pokemon["type2"]:
                self.badge2.configure(text=pokemon["type2"],
                                      fg_color=TYPE_COLORS.get(pokemon["type2"], "#999697"))
        else:
            if self.badge2.cget("text") != "":
                self.badge2.configure(text="", fg_color="transparent") # Rend invisible la badge
        gen = f"Gen {pokemon['generation']}"

        if self.genLabel.cget("text") != gen:
            self.genLabel.configure(text=gen)

        gr = f"Gr {pokemon['cluster']}"
        if self.grLabel.cget("text") != gr:
                    self.grLabel.configure(text=gr)

    def _lier(self,widget):
        # Lier l'ensemble des éléments en une barre clickable
        widget.bind("<Button-1>", self._click)
        widget.bind("<Enter>", lambda e: self.configure(fg_color=self.COULEUR_SURVOL), add="+")
        widget.bind("<Leave>", lambda e: self.configure(fg_color=self.COULEUR), add="+")
        for enfant in widget.winfo_children():
            self._lier(enfant)

    def _click(self,event):
        if self.on_click:
            self.on_click(self.pokemon)

