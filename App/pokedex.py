import customtkinter as ctk
from pages import HomePage,InfoPage,PredictionPage,ScanPage
from data import load_pokemons

ctk.set_appearance_mode("dark")  # "light", "dark" or "system"
ctk.set_default_color_theme("App/pokedex_theme.json")  # "blue", "dark-blue", "green" or "gold"

# Bloc principale - lancement application
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("POKEDEX")

        # Chargement des données dans app
        self.pokemons = load_pokemons("pokemon.csv")

        self.main_view = MainView(self, app=self)
        self.main_view.pack(fill="both", expand = True)

        

class MainView(ctk.CTkFrame):
    """Barre de navigation entre différentes pages avec une seule visible à la fois"""

    def __init__(self, master, app, fg_color="transparent"):
        super().__init__(master)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.menubar = ctk.CTkFrame(self, corner_radius=0,fg_color="#DC0A2D")
        self.menubar.grid(row=0, column=0, sticky="ew")


        # Liste des pages
        self.pages = {
            "home" : HomePage(self, app),
            "infos" : InfoPage(self,app),
            "prediction" : PredictionPage(self,app),
            "scan" : ScanPage(self,app)
        }

        for page in self.pages.values():
            page.grid(row=1, column=0,sticky="nsew")
            page.grid_remove()

        # Boutons de navigations
        self.nav_buttons = {}
        for column, (name,text) in enumerate([("home", "Home"), ("infos", "Infos"), ("prediction","Prediction"), ("scan","Scan")]):
            button = ctk.CTkButton(self.menubar, text=text, width=100, height=30, corner_radius=0, command=lambda o=name: self.show_page(o))
            button.grid(row=0, column=column)
            self.nav_buttons[name] = button

        self.current = None
        self.show_page("home")
        
    def show_page(self, name):
        # Affichage page selectionnée
        if name == self.current:
            return
        if self.current is not None:
            self.pages[self.current].grid_remove()

        self.current = name
        self.pages[name].grid()
        self.pages[name].on_show()
     


app = App()
app.mainloop()
