import customtkinter as ctk
from data import filter, list_conv, STATS
from texte import CLUSTERS
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from prediction import predict_legendary

TYPE_COLORS = {
    "Normal": "#A8A878", "Fire": "#F08030", "Water": "#6890F0", "Grass": "#78C850",
    "Electric": "#F8D030", "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0",
    "Ground": "#E0C068", "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B820",
    "Rock": "#B8A038", "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848",
    "Steel": "#B8B8D0", "Fairy": "#EE99AC",
}

def badge_type(master, type_):
    """Petit badge arrondi coloré pour un type."""
    return ctk.CTkLabel(master, text=type_, width=70, height=22, corner_radius=11,
                        fg_color=TYPE_COLORS.get(type_, "gray40"), text_color="white",
                        font=("Arial", 11, "bold"))


# Pages
PAR_PAGE = 18 #Nombre de pokémons par Page
class HomePage(ctk.CTkFrame):
    """Page principale : affichage de la liste des pokémons et fonction de trie"""
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.filtres = list_conv(app.pokemons) # Liste affichée
        self.page = 0
        self.fenetre = None
        
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

    # Fonctions de traitement
    def appliquer_filtre(self, nom, generation, type, legendaire, groupe):
            """Fonction de trie"""
            resultat = filter(self.app.pokemons, nom, generation, type, legendaire, groupe)
            self.filtres = list_conv(resultat)
            self.page = 0
            self.affiche_page()

    def open_pokemon(self,pokemon):
        """Ouverture de la fiche pokemon à partir du clic de la barre"""
        self.app.ouvrir_fiche(pokemon)

    def on_show(self):
        print("home")


class ClusterPage(ctk.CTkFrame):
    """Page d'affichage des données de clustering : graphe et analyse"""
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.derniere_donnee = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.text = ctk.CTkLabel(self, text="Clustering", fg_color="#bdffff")
        self.text.grid(row=0, pady=0, padx=0, sticky="snew", columnspan=2)

        # Graphique
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor="#fefefe83")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.points = None          # coordonnées (pc1, pc2) de tous les Pokémon
        self.records = []           # les dictionnaires correspondants, dans le même ordre
        self.ax = None
        self.info = None            # infobulle
        self.survol = None          # indice du point survolé

        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_move)

        self.zone = self.canvas.get_tk_widget()
        self.zone.grid(row=1, column=0, pady=10,padx=10, sticky="snew")

        # Zone de texte pour l'analyse
        self.droite = ctk.CTkFrame(self, fg_color="transparent")
        self.droite.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=15)

        self.cadre_table = ctk.CTkFrame(self.droite, fg_color="transparent")
        self.cadre_table.pack(anchor="w")

        self.paragraphe = ctk.CTkLabel(self.droite, text=CLUSTERS, wraplength=420,
                                       justify="left", anchor="w", font=("Arial", 13))
        self.paragraphe.pack(fill="x", pady=(20, 0))
        self.droite.bind("<Configure>",
                         lambda e: self.paragraphe.configure(wraplength=max(200, e.width - 10)))

    def on_show(self):
        """Charge le graphe et les données qu'une fois si le jeu de donnée ne change pas"""
        if self.app.pokemons is not self.derniere_donnee:
            self.derniere_donnee = self.app.pokemons
            moyennes_clusters = self.app.pokemons.groupby("cluster")[STATS].mean().round(2)
            self.remplir_tableau(moyennes_clusters)
            self.tracer()

    def remplir_tableau(self, moyennes):
        """Remplisage du tableau selon moyenne des stats par groupe"""
        for w in self.cadre_table.winfo_children():
            w.destroy()

        # En-tête
        ctk.CTkLabel(self.cadre_table, text="Cluster", width=60).grid(row=0,column=0,padx=2,pady=4)
        for j, stat in enumerate(STATS, start=1):
            ctk.CTkLabel(self.cadre_table, text=stat, width=62,).grid(row=0, column=j, padx=2, pady=4)

        # Cellules
        for i, (c, ligne) in enumerate(moyennes.iterrows(), start=1):
            ctk.CTkLabel(self.cadre_table, text=str(c), width=60, corner_radius=6,).grid(row=i, column=0, padx=2, pady=2)
            for j, stat in enumerate(STATS, start=1):
                ctk.CTkLabel(self.cadre_table, text=f"{ligne[stat]:.2f}", width=62).grid(row=i, column=j, padx=2, pady=2)

    # Fonctions du graphe
    def tracer(self):
        """Trace le graphe"""
        df = self.app.pokemons
        variance = df.attrs.get("pca_variance", [0, 0])
    
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        for c in range(4):
            sous = df[df["cluster"]==c]
            ax.scatter(sous["pc1"],sous["pc2"],label=f"Cluster {c}", s=12, alpha=0.8)

        ax.set_xlabel(f"PC1 ({variance[0] * 100:.0f} % de la variance)")
        ax.set_ylabel(f"PC2 ({variance[1] * 100:.0f} % de la variance)")
        ax.legend(facecolor="#fefefe83", labelcolor="black")

        self.ax = ax
        self.points = df[["pc1", "pc2"]].to_numpy()
        self.records = list_conv(df)                 # même ordre que les lignes du DataFrame
        self.survol = None
        self.info = ax.annotate("", xy=(0, 0), xytext=(12, 12), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="white", ec="gray"),
                                visible=False, zorder=10)
        
        self.fig.tight_layout()
        self.canvas.draw_idle()

    def plus_proche(self, event, rayon=10):
        """Indice du point le plus proche du curseur (à moins de `rayon` pixels), sinon None."""
        if self.points is None or event.inaxes is not self.ax:
            return None
        xy = self.ax.transData.transform(self.points)         # données -> pixels écran
        distances = np.hypot(xy[:, 0] - event.x, xy[:, 1] - event.y)
        i = int(distances.argmin())
        return i if distances[i] <= rayon else None

    def on_click(self, event):
        if event.button != 1:                                  # clic gauche uniquement
            return
        i = self.plus_proche(event)
        if i is not None:
            self.app.ouvrir_fiche(self.records[i])

    def on_move(self, event):
        i = self.plus_proche(event)
        if i == self.survol:                                   # rien n'a changé : pas de redessin
            return
        self.survol = i
        zone = self.canvas.get_tk_widget()
        if i is None:
            self.info.set_visible(False)
            zone.configure(cursor="")
        else:
            p = self.records[i]
            self.info.xy = self.points[i]
            self.info.set_text(f"{p['name']}\nGroupe {p['cluster']}")
            self.info.set_visible(True)
            zone.configure(cursor="hand2")                     # curseur main
        self.canvas.draw_idle()


class PredictionPage(ctk.CTkFrame):
    STATS = [("HP", "hp"), ("Attack", "attack"), ("Defense", "defense"),
                 ("Sp. Atk", "sp_atk"), ("Sp. Def", "sp_def"), ("Speed", "speed")]
    
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure(2,weight=1)

        self.text = ctk.CTkLabel(self, text="Prediction", fg_color="#bdffff")
        self.text.grid(row=0, pady=0, padx=0, sticky="snew", columnspan=2)

        self.erreur = ctk.CTkLabel(self, text="", text_color="#E74C3C", border_color="black", border_width=2)
        self.erreur.grid(row=1, padx = 10, pady=10, sticky="ew", columnspan=2) 

        self.zone = ctk.CTkFrame(self,fg_color="gray", border_color="black", border_width=2)
        self.zone.grid(row=2, column=0, padx=40,pady=40)

        self.stat_ent = {}
        for j, (stat,cle) in enumerate(self.STATS):
            ctk.CTkLabel(self.zone, text=str(stat), width=110, corner_radius=6,font=("Arial", 14, "bold"), anchor="w").grid(row=j, column=0, padx=10, pady=10)
            entry = ctk.CTkEntry(self.zone,  width=240, height=30, placeholder_text="Taper un nombre")
            entry.grid(row=j, column=1, padx=10, pady=10)
            self.stat_ent[cle] = entry

        self.pred_button = ctk.CTkButton(self.zone, text="Prediction", command=self.predict, fg_color=["#DC0A2D","#144870"], hover_color=["#DC0A2D","#44eee6"])
        self.pred_button.grid(row=7, column=0, pady=(0,10), padx=10, sticky = 'ew', columnspan=2)
        self.resultat = ctk.CTkLabel(self.zone, text="")
        self.resultat.grid(row=8, column=0, columnspan=2, pady=10)

        
    def stat_read(self):
        valeurs = {}
        for (stat,cle) in self.STATS:
            texte = self.stat_ent[cle].get().strip()

            if texte == "":
                valeurs[cle] = 1
                continue

            # Verification pour accepter uniquement des entiers
            if not (texte.isascii() and texte.isdigit()):
                self.erreur.configure(text=f"{stat} : entre un nombre entier")
                self.stat_ent[cle].focus()
                return None

            valeur = int(texte)
            if not 1 <= valeur <= 255:                                  # plage des stats de base
                self.erreur.configure(text=f"{stat} : valeur entre 1 et 255")
                self.stat_ent[cle].focus()
                return None
            valeurs[cle] = valeur

        self.erreur.configure(text="")                                  # tout est bon : efface le message
        return valeurs

    def predict(self):
        stats = self.stat_read()
        if stats is None:                  # saisie invalide : on s'arrête, le message est affiché
            return
        print(stats)
        resultat = predict_legendary(stats)
        print(resultat)
        self.vider_champs()

        if resultat == 1:
            self.resultat.configure(text="Ce Pokémon est légendaire !", text_color="#83f158")
        else:
            self.resultat.configure(text="Ce Pokémon n'est pas légendaire.", text_color="#E74C3C")

    def vider_champs(self):
        for entree in self.stat_ent.values():
            entree.delete(0, "end")    # efface tout le texte du champ
        self.erreur.configure(text="")
        self.focus()                   # retire le curseur des champs (voir plus bas)

        

    def on_show(self):
            print("Predictions")




# Pages à définir

class ScanPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.text = ctk.CTkLabel(self, text="Scan", fg_color="#bdffff")
        self.text.pack(fill="x")

    def on_show(self):
            print("Scan")


# Fenêtre supplémentaire
class PokemonWindow(ctk.CTkToplevel):
    """Fiche Pokemon dans une fenêtre secondaire"""

    STATS = [("HP", "hp"), ("Attack", "attack"), ("Defense", "defense"),
             ("Sp. Atk", "sp_atk"), ("Sp. Def", "sp_def"), ("Speed", "speed")]

    def __init__(self, master):
        super().__init__(master)
        self.title("Fiche Pokémon")
        self.geometry("420x480")
        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self.destroy())       # Échap ferme la fenêtre

        self.titre = ctk.CTkLabel(self, text="", font=("Arial", 26, "bold"))
        self.titre.pack(pady=(25, 5))

        self.zone_types = ctk.CTkFrame(self, fg_color="transparent")
        self.zone_types.pack()

        self.details = ctk.CTkLabel(self, text="")
        self.details.pack(pady=(10, 15))

        # Une ligne par stat : stat, barre, valeur (créées une seule fois)
        self.barres = {}
        cadre = ctk.CTkFrame(self, fg_color="transparent")
        cadre.pack(padx=30)
        for i, (label, cle) in enumerate(self.STATS):
            ctk.CTkLabel(cadre, text=label, width=70, anchor="w").grid(row=i, column=0, pady=5)
            barre = ctk.CTkProgressBar(cadre, width=220, height=12)
            barre.grid(row=i, column=1, padx=10)
            valeur = ctk.CTkLabel(cadre, text="", width=35)
            valeur.grid(row=i, column=2)
            self.barres[cle] = (barre, valeur)

        self.total = ctk.CTkLabel(self, text="", font=("Arial", 14, "bold"))
        self.total.pack(pady=(20, 0))

    def afficher(self, p):
        """Remplit la fenêtre avec les données du Pokémon"""

        self.titre.configure(text=p["name"])

        for w in self.zone_types.winfo_children():
            w.destroy()
        for t in (p["type1"], p["type2"]):
            if t:
                badge_type(self.zone_types, t).pack(side="left", padx=3)

        infos = f"Génération {p['generation']}"
        if p["legendary"]:
            infos += "  •  Légendaire"
        if "cluster" in p:  # présent seulement après le clustering
            infos += f"  •  Groupe {p['cluster']}"
        self.details.configure(text=infos)

        for cle, (barre, valeur) in self.barres.items():
            barre.configure(progress_color="#83f158")
            barre.set(0)
            self.animer(barre, min(p[cle] / 255, 1))    # 255 = valeur maximale d'une stat
            valeur.configure(text=str(p[cle]))

        self.total.configure(text=f"Total : {sum(p[cle] for _, cle in self.STATS)}")

        self.premier_plan()

    def premier_plan(self):
        """Passe la fiche devant les autres fenêtres une seule fois, puis la laisse se comporter normalement."""
        self.deiconify() # la réaffiche si elle était réduite
        self.lift()
        self.attributes("-topmost", True)   # force le premier plan...
        self.after(300, lambda: self.attributes("-topmost", False))   # ...puis le retire
        self.after(350, self.focus_force)   # donne le focus clavier (Échap fonctionne)

    def animer(self, barre, cible, etape=0, etapes=15):
        """Animation de la barre de stat"""
        barre.set(cible * (etape + 1) / etapes)
        if etape + 1 < etapes:
            self.after(15, lambda: self.animer(barre, cible, etape + 1, etapes))



# Ensemble des sous-frames

class Search_frame(ctk.CTkFrame):
    """Barre de recherche de la page principale"""
    def __init__(self, master, on_search):
        super().__init__(master, fg_color= ["#DC0A2D", "#bdffff"], corner_radius=0, height=30)
        self.grid_columnconfigure((0,1,2,3,4,5, 6), weight=1)

        self.on_search = on_search

        i = 3
        self.entry = ctk.CTkEntry(self, placeholder_text="Search Pokemon")
        self.entry.grid(row=1, column=0, pady=(0,10), padx=20, sticky="ew", columnspan=i)

        self.search_button = ctk.CTkButton(self, text="Search", command=self.search_pokemon, fg_color=["#DC0A2D","#144870"], hover_color=["#DC0A2D","#44eee6"])
        self.search_button.grid(row=1, column=i+4, pady=(0,10), padx=10, sticky = 'ew')

        # Filtres
        self.genLab = ctk.CTkLabel(self, text="Génération")
        self.genLab.grid(row=0,column=i,pady=0,padx=10,sticky="sew")
        Generation = ["All","1", "2", "3", "4", "5", "6"]
        self.generation_filter = ctk.CTkOptionMenu(self, values=Generation)
        self.generation_filter.grid(row=1, column=i, pady=(0,10), padx=10,sticky="ew")

        self.typeLab = ctk.CTkLabel(self,text="Types")
        self.typeLab.grid(row=0,column=i+1,pady=0,padx=10,sticky="sew")
        Type = ["All","Normal", "Fire", "Water", "Grass", "Electric", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
        self.type_filter = ctk.CTkOptionMenu(self, values=Type)
        self.type_filter.grid(row=1, column=i+1, pady=(0,10), padx=10,sticky="ew")

        self.check_leg = ctk.CTkCheckBox(self, text="Legendary")
        self.check_leg.grid(row=1, column=i+3, pady=(0,10), padx=10)

        self.grLabel = ctk.CTkLabel(self,text="Groupe")
        self.grLabel.grid(row=0,column=i+2,pady=0,padx=10,sticky="sew")
        self.grfilter = ctk.CTkOptionMenu(self, values=["All","0","1","2","3"])
        self.grfilter.grid(row=1, column=i+2, pady=(0,10), padx=10,sticky="ew")


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




