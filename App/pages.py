import customtkinter as ctk
from data import filter, list_conv

TYPE_COLORS = {
    "Normal": "#A8A878", "Fire": "#F08030", "Water": "#6890F0", "Grass": "#78C850",
    "Electric": "#F8D030", "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0",
    "Ground": "#E0C068", "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820",
    "Rock": "#B8A038", "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848",
    "Steel": "#B8B8D0", "Fairy": "#EE99AC",
}

PAR_PAGE = 18


def badge_type(master, type_):
    """Petit badge arrondi coloré pour un type."""
    return ctk.CTkLabel(master, text=type_, width=70, height=22, corner_radius=11,
                        fg_color=TYPE_COLORS.get(type_, "gray40"), text_color="white",
                        font=("Arial", 11, "bold"))

class HomePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.filtres = list_conv(app.pokemons)    # liste actuellement affichée
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
        debut = self.page * PAR_PAGE
        if (debut + PAR_PAGE <= len(self.filtres)) : # Fonctionne pas car je détruit pas les éléments en plus de la grille
            self.contenu_frame.afficher(self.filtres[debut:debut + PAR_PAGE])
        else :
            self.contenu_frame.afficher(self.filtres[debut:debut + (len(self.filtres)-debut)])

        total = max(1, -(-len(self.filtres) // PAR_PAGE))     # division arrondie au-dessus
        self.label_page.configure(
            text=f"Page {self.page + 1} / {total}  ({len(self.filtres)} Pokémon)")
        #self.btn_prec.configure(state="normal" if self.page > 0 else "disabled")
        #self.btn_suiv.configure(state="normal" if self.page < total - 1 else "disabled")
    
    def appliquer_filtre(self, nom, generation, type, legendaire):
        resultat = filter(self.app.pokemons, nom, generation, type, legendaire)
        self.filtres = list_conv(resultat)
        self.page = 0
        self.affiche_page()


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
        print(pokemon["name"])


    def on_show(self):
        print("Home")

    

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
    def __init__(self, master, on_search):
        super().__init__(master, fg_color= ["#DC0A2D", "#bdffff"], corner_radius=0, height=30)
        self.grid_columnconfigure((0,1,2,3,4,5), weight=1)

        self.on_search = on_search

        self.entry = ctk.CTkEntry(self, placeholder_text="Search Pokemon")
        self.entry.grid(row=0, column=0, pady=20, padx=20, sticky="ew", columnspan=2)

        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_pokemon, fg_color=["#DC0A2D","#144870"], hover_color=["#DC0A2D","#44eee6"])
        self.search_button.grid(row=0, column=5, pady=10, sticky = 'ew')

        Generation = ["All","1", "2", "3", "4", "5", "6"]
        self.generation_filter = ctk.CTkOptionMenu(self, values=Generation)
        self.generation_filter.grid(row=0, column=2, pady=10, padx=10,sticky="ew")

        Type = ["All","Normal", "Fire", "Water", "Grass", "Electric", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
        self.type_filter = ctk.CTkOptionMenu(self, values=Type)
        self.type_filter.grid(row=0, column=3, pady=10, padx=10,sticky="ew")

        self.check_leg = ctk.CTkCheckBox(self, text="Legendary")
        self.check_leg.grid(row=0, column=4, pady=10, padx=10)

    def search_pokemon(self):
        pokemon_name = self.entry.get().strip()
        generation_filter = self.generation_filter.get()
        type_filter = self.type_filter.get()
        legendary_filter = self.check_leg.get()

        self.on_search(pokemon_name, generation_filter, type_filter, legendary_filter)

        if not pokemon_name:
            print("Please enter a Pokemon name.")
        else:
            print(f"Searching for Pokemon: {pokemon_name}")

        print(f"Generation filter: {generation_filter}")
        print(f"Type filter: {type_filter}")
        print(f"Legendary filter: {legendary_filter}")


class Contenu_frame(ctk.CTkScrollableFrame):
    def __init__(self, master,on_select=None):
        super().__init__(master, corner_radius=0)
        self.on_select = on_select
        self.grid_columnconfigure(0, weight=1)

    def afficher(self,pokemons):
        for widget in self.winfo_children():
            widget.destroy()
        for i, p in enumerate(pokemons):
            PokemonRow(self, p, on_click=self.on_select).grid(row=i, column=0, sticky="ew", padx=10, pady=3)


class PokemonRow(ctk.CTkFrame):
    """Barre clickable pour chaque pokémon"""

    COULEUR = "#999697"
    COULEUR_SURVOL = "#3F3F3F"

    def __init__(self, master, pokemon, on_click=None):
        super().__init__(master, height=30, corner_radius=8, fg_color="#999697")

        self.on_click = on_click
        self.pokemon = pokemon

        self.grid_columnconfigure(0,weight=1)

        nameLabel = ctk.CTkLabel(self, text=f"# {pokemon["id"]} {pokemon["name"]}", anchor="w")
        nameLabel.grid(row=0,column=0,padx=15, sticky="w")

        types = ctk.CTkFrame(self,fg_color="transparent")
        types.grid(row=0,column=1,padx=10)
        for t in (pokemon["type1"], pokemon["type2"]):
            if t:
                badge_type(types,t).pack(side="left",padx=2)

        generationLabel = ctk.CTkLabel(self,text=f"Gen {pokemon["generation"]}", anchor="w")
        generationLabel.grid(row=0,column=2,padx=15, sticky="w")

        self._lier(self)

    def _lier(self,widget):
        widget.bind("<Button-1>", self._click)
        widget.bind("<Enter>", lambda e: self.configure(fg_color=self.COULEUR_SURVOL), add="+")
        widget.bind("<Leave>", lambda e: self.configure(fg_color=self.COULEUR), add="+")
        for enfant in widget.winfo_children():
            self._lier(enfant)

    def _click(self,event):
        if self.on_click:
            self.on_click(self.pokemon)

