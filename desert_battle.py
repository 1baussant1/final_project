import random
import tkinter as tk

class Character:
    def __init__(self, name, health, attack):
        self.name = name
        self.health = health
        self.attack = attack
    
    def is_alive(self):
        return self.health > 0
    
    def take_damage(self, damage):
        self.health -= damage
    
    def attack_enemy(self, enemy):
        damage = random.randint(1, self.attack)
        enemy.take_damage(damage)
        return damage

class Player(Character):
    def __init__(self, name, canvas, img, status_label):
        super().__init__(name, 10, 5)  # Commencer avec 10 points de vie
        self.position = (100, 100)
        self.canvas = canvas
        self.image = canvas.create_image(self.position[0], self.position[1], image=img)
        self.enemies_defeated = 0  # Compteur d'ennemis tués
        self.status_label = status_label  # Label pour afficher les infos du joueur
    
    def move(self, direction):
        x, y = self.position
        if direction == "north":
            self.position = (x, y - 20)
        elif direction == "south":
            self.position = (x, y + 20)
        elif direction == "east":
            self.position = (x + 20, y)
        elif direction == "west":
            self.position = (x - 20, y)
        self.canvas.coords(self.image, self.position[0], self.position[1])

    def heal(self, amount):
        """Augmenter les points de vie du joueur et mettre à jour l'affichage"""
        self.health += amount
        if self.health > 10:  # Limiter les points de vie à 10
            self.health = 10
        # Mettre à jour le label avec les nouveaux points de vie du joueur
        self.status_label.config(text=f"Vie du joueur: {self.health} / 10")


class Enemy(Character):
    def __init__(self, name, position, canvas):
        # Points de vie entre 3 et 15
        health = random.randint(3, 15)
        super().__init__(name, health, 3)  # Points de vie aléatoires et attaque fixe
        self.position = position
        self.canvas = canvas
        # Créer un cercle représentant l'ennemi (ID retourné par canvas.create_oval)
        self.image = canvas.create_oval(self.position[0] - 10, self.position[1] - 10, 
                                        self.position[0] + 10, self.position[1] + 10, 
                                        fill="red", tags=name)  # Représentation simple d'un ennemi

# Fonction pour générer des ennemis de manière aléatoire sur le canevas
def generate_enemies(num_enemies, canvas):
    enemies = []
    for i in range(num_enemies):
        x = random.randint(20, 580)  # Position x aléatoire
        y = random.randint(20, 380)  # Position y aléatoire
        enemy = Enemy(f"Ennemi_{i}", (x, y), canvas)
        enemies.append(enemy)
    return enemies

# Fonction de bataille avec l'interface graphique
def battle(player, enemy, status_label, attack_button, flee_button):
    status_label.config(text=f"Un {enemy.name} apparaît ! Vie de l'ennemi: {enemy.health}")
    
    def attack_action():
        damage = player.attack_enemy(enemy)
        status_label.config(text=f"Vous infligez {damage} dégâts au {enemy.name}. Vie de l'ennemi: {enemy.health}")
        if enemy.is_alive():
            damage = enemy.attack_enemy(player)
            status_label.config(text=f"Le {enemy.name} vous inflige {damage} dégâts. Vie du joueur: {player.health}")
        else:
            status_label.config(text=f"Vous avez vaincu le {enemy.name} !")
            player.enemies_defeated += 1
            # Si l'ennemi a 5 PV ou plus, régénérer des points de vie pour le joueur
            if enemy.health >= 5:
                heal_amount = random.randint(1, 5)  # Gagner entre 1 et 5 points de vie
                player.heal(heal_amount)
                status_label.config(text=f"Vous avez récupéré {heal_amount} points de vie grâce à votre victoire.")
            # Supprimer l'ennemi du canevas (ici on utilise son ID)
            player.canvas.delete(enemy.image)
            attack_button.config(state=tk.DISABLED)  # Désactiver les boutons après la victoire
            flee_button.config(state=tk.DISABLED)
            # Générer un nouvel ennemi pour relancer un combat
            if player.enemies_defeated < 5:  # Vérifier que le joueur n'a pas encore vaincu 5 ennemis
                new_enemy = generate_enemies(1, player.canvas)[0]
                battle(player, new_enemy, status_label, attack_button, flee_button)
    
    def flee_action():
        status_label.config(text="Vous prenez la fuite !")
        attack_button.config(state=tk.DISABLED)  # Désactiver les boutons si fuite
        flee_button.config(state=tk.DISABLED)
    
    # Activer ou désactiver les boutons de combat en fonction du statut
    attack_button.config(state=tk.NORMAL)
    flee_button.config(state=tk.NORMAL)

    # Afficher l'option de combat
    attack_button.config(command=attack_action)
    flee_button.config(command=flee_action)

# Interface graphique
def start_game():
    root = tk.Tk()
    root.title("RPG Désert")
    
    canvas = tk.Canvas(root, width=600, height=400)
    canvas.pack()
    
    desert_img = tk.PhotoImage(file="C:/Users/bland/Documents/Cours/master/projet_final/desert.png")
    canvas.create_image(0, 0, anchor=tk.NW, image=desert_img)
    
    player_img = tk.PhotoImage(file="C:/Users/bland/Documents/Cours/master/projet_final/sandman-creatures.png")
    
    # Ajouter un label pour afficher les informations sur le joueur
    status_label = tk.Label(root, text="Vie du joueur: 10 / 10")
    status_label.pack()
    
    player = Player("Aventurier du désert", canvas, player_img, status_label)
    
    # Créer au moins 5 ennemis
    enemies = generate_enemies(5, canvas)
    
    # Fonction de sélection d'un ennemi à attaquer
    def select_enemy(event, player, enemies, status_label, attack_button, flee_button):
        # Vérifier si l'ennemi a été cliqué
        for enemy in enemies:
            if canvas.bbox(enemy.image) and canvas.bbox(enemy.image)[0] <= event.x <= canvas.bbox(enemy.image)[2] and canvas.bbox(enemy.image)[1] <= event.y <= canvas.bbox(enemy.image)[3]:
                battle(player, enemy, status_label, attack_button, flee_button)
                break
    
    # Ajouter un événement de clic sur le canevas pour sélectionner l'ennemi
    canvas.bind("<Button-1>", lambda event: select_enemy(event, player, enemies, status_label, attack_button, flee_button))
    
    # Créer les boutons d'attaque et de fuite
    attack_button = tk.Button(root, text="Attaquer")
    flee_button = tk.Button(root, text="Fuir")
    
    attack_button.pack()
    flee_button.pack()
    
    # Créer des boutons pour déplacer le joueur
    def move_up():
        player.move("north")
    def move_down():
        player.move("south")
    def move_left():
        player.move("west")
    def move_right():
        player.move("east")
    
    move_up_button = tk.Button(root, text="↑", command=move_up)
    move_down_button = tk.Button(root, text="↓", command=move_down)
    move_left_button = tk.Button(root, text="←", command=move_left)
    move_right_button = tk.Button(root, text="→", command=move_right)
    
    # Afficher les boutons de mouvement
    move_up_button.pack()
    move_down_button.pack()
    move_left_button.pack()
    move_right_button.pack()

    root.mainloop()

start_game()
