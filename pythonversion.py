import random

class Wheel:
    def __init__(self):
        self.current_number = None
        self.remaining_numbers = set(range(1, 13))
        self.history = []

    def spin(self):
        self.current_number = random.choice(list(self.remaining_numbers))
        self.remaining_numbers.remove(self.current_number)
        self.append(self.current_number)

    def payout(self):
        return self.current_number * 10

    def is_valid_guess(self, guess):
        return guess in ['H', 'L', 'B', 'F']

class Game:
    def __init__(self, num_players):
        self.wheel = Wheel()
        self.players = []
        for i in range(num_players):
            player_name = input(f"Enter name for player {i+1}: ")
            self.players.append(Player(player_name, self.wheel))
        num_bots = 8 - num_players
        for i in range(num_bots):
            bot_name = f"Bot {i+1}"
            cautious_coeff = random.uniform(0.5, 1.0)
            aggressive_coeff = random.uniform(0.5, 1.0)
            risky_coeff = random.uniform(0.5, 1.0)
            contrarian_coeff = random.uniform(0.5, 1.0)
            self.players.append(Bot(bot_name, cautious_coeff, aggressive_coeff, risky_coeff, contrarian_coeff, self.wheel))

    def play(self):
        round_num = 1
        while True:
            print(f"\n--- ROUND {round_num} ---\n")
            self.wheel = Wheel()
            for player in self.players:
                player.score = 0
                player.free_spin = True
                player.guess = None
                player.banked = False
            while self.wheel.remaining_numbers:
                print(f"\n--- SPIN {13 - len(self.wheel.remaining_numbers)} ---\n")
                for player in self.players:
                    if player.banked:
                        continue
                    if isinstance(player, Bot):
                        choice = player.make_choice()
                        if choice == "higher":
                            player.guess_higher()
                        elif choice == "lower":
                            player.guess_lower()
                        elif choice == "bank":
                            player.bank()
                        continue
                    player.make_guess()
                    while not self.wheel.is_valid_guess(player.guess):
                        print("Invalid guess.")
                        player.make_guess()
                    if player.guess == "F":
                        player.use_free_spin()
                        continue
                    if player.guess == "B":
                        player.bank()
                        continue
                    self.wheel.spin()
                    if (player.guess == "H" and self.wheel.current_number > 6) or \
                            (player.guess == "L" and self.wheel.current_number < 7):
                        print(f"{player.name} guessed correctly and wins {self.wheel.current_number} points!")
                        player.score += self.wheel.current_number
                        self.wheel.spin()
                    else:
                        print(f"{player.name} guessed incorrectly.")
            round_num += 1
            print("\n--- ROUND OVER ---\n")
            for player in self.players:
                print(f"{player.name}: {player.score} points")
                if player.score >= 100:
                    print(f"{player.name} wins with {player.score} points!")
                    return

class Player:
    def __init__(self, name, wheel):
        self.name = name
        self.score = 0
        self.free_spin = True
        self.guess = None
        self.wheel = wheel
        self.banked = False
    def make_guess(self, wheel):
        if self.banked == False:
            return None
        if self.free_spin:
            self.guess = input("Enter 'H' for higher, 'L' for lower, or 'B' to bank: ")
            self.free_spin = False
        else:
            self.guess = input("Enter 'H' for higher, 'L' for lower, or 'B' to bank, or 'F' to use your free spin: ")

        while self.guess not in ['H', 'L', 'B', 'F']:
            self.guess = input("Invalid input. Enter 'H' for higher, 'L' for lower, or 'B' to bank, or 'F' to use your free spin: ")

    def use_free_spin(self):
        self.free_spin = False

    def bank(self):
        self.score += self.wheel.current_number
        self.banked = True
        self.wheel.spin()

    def guess_higher(self):
        self.guess = 'H'

    def guess_lower(self):
        self.guess = 'L'

class Bot(Player):
    def __init__(self, name, cautious_coeff, aggressive_coeff, risky_coeff, contrarian_coeff, wheel):
        super().__init__(name, wheel)
        self.cautious_coeff = cautious_coeff
        self.aggressive_coeff = aggressive_coeff
        self.risky_coeff = risky_coeff
        self.contrarian_coeff = contrarian_coeff
    def make_choice(self, wheel):
        """
        Makes a choice based on the bot's coefficients and the current state of the wheel
        """
        if self.banked == False:
            return None
        current_number = wheel.current_number
        remaining_numbers = wheel.remaining_numbers
        choice = None
        max_expected_value = 0
        
        # calculate the expected value for each possible choice
        for option in ["higher", "lower", "bank"]:
            expected_value = 0
            if option == "higher":
                for num in remaining_numbers:
                    if num > current_number:
                        expected_value += (num - current_number) * self.aggressive_coeff
                    elif num < current_number:
                        expected_value += (current_number - num) * self.risky_coeff
                    else:
                        expected_value += 7 * self.risky_coeff # if the number is the same, pick higher for higher expected value
            elif option == "lower":
                for num in remaining_numbers:
                    if num < current_number:
                        expected_value += (current_number - num) * self.aggressive_coeff
                    elif num > current_number:
                        expected_value += (num - current_number) * self.risky_coeff
                    else:
                        expected_value += 7 * self.risky_coeff # if the number is the same, pick lower for higher expected value
            elif option == "bank":
                self.banked = True
                expected_value = wheel.payout()
            
            # adjust expected value based on the bot's coefficients
            if option == "higher":
                expected_value *= self.aggressive_coeff
            elif option == "lower":
                expected_value *= self.cautious_coeff
            elif option == "bank":
                expected_value *= self.contrarian_coeff
            
            # update the best choice so far
            if expected_value > max_expected_value:
                max_expected_value = expected_value
                choice = option
        
        return choice
