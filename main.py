import os, sys, random
import time

sys.path.append("Characters")

from Characters.character import Character
from Characters.enemy import Enemy

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.box import HEAVY
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.align import Align

from pynput import keyboard

console = Console()

# Menu class
class Menu:
    def __init__(self, options: dict, console: Console):
        self.options = options
        self.selected_index = 0
        self.console = console

    # Display the menu
    def display(self):
        lines = []
        for k, option in enumerate(self.options):
            if k == self.selected_index:
                lines.append(f"> [bold yellow]{option}[/bold yellow] <")
            else:
                lines.append(f"  {option}")
        self.console.print(Panel("\n".join(lines), title="Menu", border_style="blue", box=HEAVY, width=64), justify="center")

    # Handle menu navigation
    def on_press(self, key):
        if key == keyboard.Key.up:
            if self.selected_index > 0:
                self.selected_index -= 1
            self.console.clear()
            self.display()
        elif key == keyboard.Key.down:
            if self.selected_index < len(self.options) - 1:
                self.selected_index += 1
            self.console.clear()
            self.display()
        elif key == keyboard.Key.enter:
            return False
        else:
            self.console.clear()
            self.display()

    # Choose an option
    def choose(self):
        self.display()
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

        # Clear any remaining key presses
        clear_input_buffer()

        return list(self.options.values())[self.selected_index]

# Battle class
class Battle(Menu):
    def __init__(self, player: Character, enemy: Enemy, console: Console):
        self.player = player
        self.enemy = enemy
        self.console = console
        self.options = {"Attack": "attack", "Use Item": "use item", "Run": "run"}
        self.selected_index = 0
        self.battle_log = []
        self.choice_made = False
        self.excute_inventory = Inventory(player, console)

    # Create a character sheet
    def make_sheet(self, player: Character):
        sheet = Text()
        sheet.append(Text(f"{player.name}\n", style="bold"))
        sheet.append(Text("  HP:                 " + str(player.hp) + '/' + str(player.max_hp)))
        sheet.append(Text("\nATK:                " + str(player.attack)))
        sheet.append(Text("\nDEF:                " + str(player.defense)))
        return sheet

    # Add message to battle log
    def add_log(self, message: str):
        self.battle_log.append(message)

    # Clear input buffer
    def clear_input_buffer(self):
        clear_input_buffer()

    # Create battle display
    def make_battle_display(self):
        # Battle title panel
        title = Panel(
            Text("Battle", justify="center", style="bold white"),
            box=HEAVY,
            border_style="grey37",
            width=64,
            height=3
        )

        # Player and enemy panels
        player_panel = Panel(
            self.make_sheet(self.player),
            title=self.player.name,
            box=HEAVY,
            width=31
        )
        enemy_panel = Panel(
            self.make_sheet(self.enemy),
            title=self.enemy.name,
            box=HEAVY,
            width=31
        )

        # Character stats table
        chars = Table.grid(expand=False, padding=2)
        chars.add_column(justify="center")
        chars.add_column(justify="center")
        chars.add_row(player_panel, enemy_panel)

        # Battle log panel
        battle_log_panel = Panel(
            "\n".join(self.battle_log[-6:]) if self.battle_log else "Battle Started!",
            title="Battle Log",
            box=HEAVY,
            height=10,
            width=64
        )

        # Action menu panel
        menu_lines = []
        for k, option in enumerate(self.options):
            if k == self.selected_index:
                menu_lines.append(f"> [bold yellow]{option}[/bold yellow] <")
            else:
                menu_lines.append(f"  {option}")
        menu_panel = Panel(
            Align.center("\n".join(menu_lines)),
            title="Menu",
            border_style="grey37",
            box=HEAVY,
            width=36
        )

        # All together centered
        content = Group(
            title,
            chars,
            battle_log_panel,
            Align.center(menu_panel)
        )

        return Align.center(content)

    # Handle menu navigation
    def on_press(self, key):
        if key == keyboard.Key.up:
            if self.selected_index > 0:
                self.selected_index -= 1
        elif key == keyboard.Key.down:
            if self.selected_index < len(self.options) - 1:
                self.selected_index += 1
        elif key == keyboard.Key.enter:
            self.choice = list(self.options.values())[self.selected_index]
            self.choice_made = True
            return False
        
    # Get player choice
    def get_player_choice(self, live: Live):
        self.action_choice = None
        self.choice_made = False

        self.clear_input_buffer()

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        while not self.choice_made:
            live.update(self.make_battle_display())
            time.sleep(0.05)

        if self.listener:
            self.listener.stop()
            self.listener.join()

        self.clear_input_buffer()

        return list(self.options.values())[self.selected_index]

    # Battle loop
    def battle_loop(self):
        # Live display for battle updates
        live = Live(self.make_battle_display(), console=self.console, refresh_per_second=20)
        live.start()

        try:
            while self.player.is_alive() and self.enemy.is_alive():
                choice = self.get_player_choice(live)
                self.add_log(f"[bold green]Player's Turn:[/bold green]")

                # Player's turn
                if choice == 'attack':
                    damage = self.enemy.take_damage(self.player.attack)
                    self.add_log(f"[green]You dealt {damage} damage to {self.enemy.name}![/green]")
                    live.update(self.make_battle_display())
                    time.sleep(0.1)
                elif choice == 'use item':
                    self.add_log(f"[bold magenta]Using Item[/bold magenta]")
                    live.stop()
                    self.excute_inventory.use_from_inventory()
                    live.start()
                    time.sleep(0.1)
                elif choice == 'run':
                    if random.randint(0, 10) > 5:
                        self.add_log(f"[yellow]You successfully ran away![/yellow]")
                        live.update(self.make_battle_display())
                        pause()
                        return True
                    else:
                        self.add_log(f"[bold red]Failed to run away![/bold red]")
                        live.update(self.make_battle_display())
                        time.sleep(0.1)

                # Check if enemy is defeated
                if not self.enemy.is_alive():
                    self.add_log(f"[green]You defeated the {self.enemy.name}! Gained {self.enemy.xp_reward} XP.[/green]")
                    leveled = self.player.gain_exp(self.enemy.xp_reward)

                    # Check for level up
                    if leveled:
                        self.add_log(f"[bold]Level UP! {self.player.level - 1} -> level {self.player.level}[/bold]")
                    live.update(self.make_battle_display())
                    time.sleep(0.1)
                    break

                # Enemy's turn
                self.add_log(f"[bold red]Enemy's Turn:[/bold red]")
                enemy_damage = self.player.take_damage(self.enemy.attack)
                self.add_log(f"[red]{self.enemy.name} dealt {enemy_damage} damage to you![/red]")
                live.update(self.make_battle_display())
                time.sleep(0.1)

                # Check if player is defeated
                if not self.player.is_alive():
                    self.add_log(f"[red]You have been defeated...[/red]")
                    live.update(self.make_battle_display())
                    time.sleep(0.1)
                    break
        finally:
            live.stop()
            if self.listener:
                self.listener.stop()
            self.clear_input_buffer()

        pause()
        # Return whether the player is still alive
        return self.player.is_alive()

# Inventory class
class Inventory(Menu):
    def __init__(self, player: Character, console: Console):
        self.player = player
        self.console = console
        self.options = player.show_inventory()
        self.options["Cancel"] = "cancel"
        self.action_choice = None
        self.choice_made = False
        self.selected_index = 0
        self.use_log = []

    # Clear input buffer
    def clear_input_buffer(self):
        clear_input_buffer()

    # Add message to use log
    def add_log(self, message: str):
        self.use_log.append(message)

    # Handle menu navigation
    def on_press(self, key):
        if key == keyboard.Key.up:
            if self.selected_index > 0:
                self.selected_index -= 1
        elif key == keyboard.Key.down:
            if self.selected_index < len(self.options) - 1:
                self.selected_index += 1
        elif key == keyboard.Key.enter:
            self.choice = list(self.options.values())[self.selected_index]
            self.choice_made = True
            return False

    # Get player choice
    def get_player_choice(self, live: Live):
        self.action_choice = None
        self.choice_made = False

        self.clear_input_buffer()

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        # Wait for choice
        while not self.choice_made:
            live.update(self.inventory_display())
            time.sleep(0.05)

        if self.listener:
            self.listener.stop()
            self.listener.join()

        self.clear_input_buffer()

        return list(self.options.keys())[self.selected_index]

    # Inventory display
    def inventory_display(self):
        title = Panel(
            Text("Inventory", justify="center", style="bold white"),
            box=HEAVY,
            border_style="magenta",
            width=64,
            height=3
        )

        t = Table(box=HEAVY, border_style="magenta")
        t.add_column("#", justify="right", width=3, style="dim")
        t.add_column("Item", justify="center", style="bold")
        t.add_column("Quantity", justify="center")

        items = [(k, v) for k, v in self.player.inventory.items()]
        if not items:
            t.add_row("-", "Your inventory is empty.", "-")
        else:
            for i, (item, qty) in enumerate(items[:-1], 1):
                t.add_row(str(i), item, str(qty))

        # Use log panel
        use_log_panel = Panel(
            "\n".join(self.use_log[-6:]) if self.use_log else "Select an item to use.",
            title="Use Log",
            box=HEAVY,
            height=10,
            width=64
        )

        # Action menu panel
        menu_lines = []
        for k, option in enumerate(self.options):
            if k == self.selected_index:
                menu_lines.append(f"> [bold yellow]{option}[/bold yellow] <")
            else:
                menu_lines.append(f"  {option}")
        menu_panel = Panel(
            Align.center("\n".join(menu_lines)),
            title="Use Item",
            border_style="magenta",
            box=HEAVY,
            width=36
        )

        content = Group(
            title,
            Align.center(t),
            use_log_panel,
            Align.center(menu_panel)
        )

        return Align.center(content)

    # Use item from inventory
    def use_from_inventory(self):
        live = Live(self.inventory_display(), console=self.console, refresh_per_second=20)
        live.start()

        try:
            while True:
                choice = self.get_player_choice(live)

                if choice == "Cancel":
                    break

                # Use the selected item
                item_name = choice
                self.add_log(f"[magenta]Using item {item_name}...[/magenta]")
                live.update(self.inventory_display())
                msg = self.player.use_item(item_name)
                self.add_log(f"[green]{msg}[/green]")
                live.update(self.inventory_display())
        finally:
            live.stop()
            if self.listener:
                self.listener.stop()
            self.clear_input_buffer()

# === Utility Helpers === #
# Pause function
def pause(msg: str = "Press Enter to continue..."):
    console.input(msg)

# Clear input buffer
def clear_input_buffer():
    time.sleep(0.1)
    if sys.platform == "win32":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
# ======================= #

# === UI Utilities === #
# Header panel
def header(title: str) -> Panel:
    return Panel(
        Text(title, justify="center", style="bold white"),
        border_style="cyan",
        box=HEAVY
    )

# Status panel
def render_status(player: Character) -> Panel:
    t = Table.grid(expand=True)
    t.add_column(justify="left")
    t.add_column(justify="right")
    t.add_row(f"[bold]Name: [/bold][bold yellow]{player.name}[/bold yellow]", f"[bold]Level: {player.level}[/bold]")
    t.add_row(f"[bold]HP: [/bold]{player.hp}/{player.max_hp}")
    t.add_row(f"[bold]Attack: [/bold]{player.attack}")
    t.add_row(f"[bold]Defense: [/bold]{player.defense}")
    t.add_row(f"[bold]EXP: [/bold]{player.exp}/{player.exp_to_next_level()}")
    return Panel(t, title="Status", border_style="green", box=HEAVY)

# Rest in town to restore full HP
def rest_in_town(player: Character):
    if hasattr(player, 'heal'):
        gained_hp = player.heal(player.max_hp)
        console.print(Panel(f"[green]{player.name} rested and restored {gained_hp} HP![/green]", border_style="green", box=HEAVY), justify="center")
    else:
        console.print("[red]This character cannot rest.[/red]")
    pause()

# ====================== #

# === Game Functions === #
# Show status screen
def show_status_screen(player: Character):
    console.clear()
    console.print(header("Character Status"))
    console.print(render_status(player))
    pause()
# ====================== #


# Main game loop
def main():
    console.clear()
    console.print(header("Welcome to the RPG Game!"), justify="center")
    name = Prompt.ask("Enter your character's name", default="Hero")
    player = Character(name=name, inventory={"Potion": 2})

    while True:
        console.clear()
        menu = Menu(
            options={"Explore": "1", "Rest in Town": "2", "Show Inventory": "3", "Show Status": "4", "Quit Game": "Q"},
            console=console
        )
        choice = menu.choose()

        if choice == '1':
            fight = Battle(player, Enemy.random_enemy(), console)
            if not fight.battle_loop():
                console.clear()
                console.print("[bold red]Game Over! You have been defeated.[/bold red]", justify="center")
                pause()
                break

        elif choice == '2':
            console.clear()
            console.print(header("Rest in Town"))
            rest_in_town(player)

        elif choice == '3':
            console.clear()
            execute_inventory = Inventory(player, console)
            execute_inventory.use_from_inventory()

        elif choice == '4':
            console.clear()
            show_status_screen(player)

        elif choice.upper() == 'Q':
            console.print("[bold yellow]Thank you for playing! Goodbye![/bold yellow]")
            break

    console.clear()
    console.print(header("Game Over"), justify="center")
    console.print("[bold red]You have exited the game.[/bold red]", justify="center")


if __name__ == "__main__":
    main()
