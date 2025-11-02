# Character class
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Character:
    name: str
    hp: int = 30
    max_hp: int = 30
    attack: int = 7
    defense: int = 4
    level: int = 1
    exp: int = 0
    inventory: Dict[str, int] = field(default_factory=dict)

    # Check if character is alive
    def is_alive(self) -> bool:
        return self.hp > 0
    
    # Calculate damage taken after defense
    def take_damage(self, damage: int) -> int:
        final_damage = max(0, damage - self.defense)
        self.hp = max(0, self.hp - final_damage)
        return final_damage
    
    # Heal the character
    def heal(self, amount: int) -> int:
        heal_amount = min(amount, self.max_hp - self.hp)
        self.hp = min(self.max_hp, self.hp + amount)
        return heal_amount

    # Show inventory
    def show_inventory(self):
        return self.inventory

    # Use an item from inventory
    def use_item(self, item: str) -> bool:
        if self.inventory.get(item, 0) <= 0:
            return f"No {item} left!"
        if item == "Potion":
            self.heal(15)
            self.inventory[item] -= 1
            return f"{self.name} used a Potion and healed 15 HP!"
        return f"{item} cannot be used!"

    # Add item to inventory
    def add_item(self, item: str, quantity: int = 1):
        self.inventory[item] = self.inventory.get(item, 0) + quantity

    # Gain experience and level up if applicable
    def gain_exp(self, amount: int):
        self.exp += amount
        leveled = False
        while self.exp >= self.exp_to_next_level():
            self.exp -= self.exp_to_next_level()
            self.level += 1
            self.max_hp += 5
            self.hp = self.max_hp
            self.attack += 2
            self.defense += 1
            self.hp = self.max_hp
            leveled = True
        return leveled

    # Experience required for next level
    def exp_to_next_level(self) -> int:
        return 20 + (self.level - 1) * 15

    # String representation of the character
    def __str__(self):
        return f"{self.name}: HP {self.hp}/{self.max_hp}, ATK {self.attack}, DEF {self.defense}, EXP {self.exp}, Level {self.level}"