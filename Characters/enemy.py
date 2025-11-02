# Enemy class
import json, os, random
from dataclasses import dataclass

@dataclass
class Enemy():
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    xp_reward: int

    # Check if enemy is alive
    def is_alive(self) -> bool:
        return self.hp > 0

    # Calculate damage taken after defense
    def take_damage(self, damage: int) -> int:
        final_damage = max(0, damage - self.defense)
        self.hp = max(0, self.hp - final_damage)
        return final_damage

    # String representation of the enemy
    def __str__(self):
        return (f"Enemy: {self.name}\n"
                f"HP: {self.hp}\n"
                f"Attack: {self.attack}\n"
                f"Defense: {self.defense}\n"
                f"XP Reward: {self.xp_reward}")

    # Load enemy data from JSON file
    @staticmethod
    def load_enemies_from_file(enemy_id: str, jsonpath: str = "enemies.json") -> 'Enemy':
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, jsonpath)
        with open(full_path, 'r') as file:
            enemies_data = json.load(file)
        if enemy_id not in enemies_data:
            raise ValueError(f"Enemy '{enemy_id}' not found in {full_path}.")
        return Enemy(enemies_data[enemy_id])

    # Select a random enemy from the JSON file
    @staticmethod
    def random_enemy(jsonpath: str = "enemies.json") -> 'Enemy':
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, jsonpath)
        with open(full_path, 'r') as file:
            enemies_data = json.load(file)
        enemy_id = random.choice(list(enemies_data.keys()))
        return Enemy(
            name=enemies_data[enemy_id]["name"],
            hp=enemies_data[enemy_id]["hp"],
            max_hp=enemies_data[enemy_id]["hp"],
            attack=enemies_data[enemy_id]["attack"],
            defense=enemies_data[enemy_id]["defense"],
            xp_reward=enemies_data[enemy_id]["xp_reward"]
        )