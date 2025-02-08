import random

# Define game elements
characters = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
weapons = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
rooms = [
    "Kitchen",
    "Ballroom",
    "Conservatory",
    "Dining Room",
    "Billiard Room",
    "Library",
    "Lounge",
    "Hall",
    "Study"
]

# Select a random solution
solution = {
    "character": random.choice(characters),
    "weapon": random.choice(weapons),
    "room": random.choice(rooms)
}

# Distribute cards to players

def distribute_cards(players):
    all_cards = characters + weapons + rooms
    random.shuffle(all_cards)
    player_hands = {player: [] for player in players}
    while all_cards:
        for player in players:
            if all_cards:
                player_hands[player].append(all_cards.pop())
    return player_hands


def make_suggestion(character, weapon, room, player_hands, current_player, players):
    """Check if any of the suggested elements can be disproven."""
    for player in players:
        if player != current_player:
            for card in [character, weapon, room]:
                if card in player_hands[player]:
                    return f"{player} disproves the suggestion with {card}!"
    return "No one can disprove."


def make_accusation(character, weapon, room):
    """Check if the accusation matches the solution."""
    if (
        character == solution["character"] and
        weapon == solution["weapon"] and
        room == solution["room"]
    ):
        return "Correct! You win!"
    else:
        return "Incorrect! You are out."


def play_game():
    players = ["Player 1", "Player 2", "Player 3"]
    player_hands = distribute_cards(players)
    print("Players' hands:")
    for player, cards in player_hands.items():
        print(f"{player}: {cards}")

    while True:
        current_player = players[0]
        print(f"\n{current_player}'s turn:")
        character = random.choice(characters)
        weapon = random.choice(weapons)
        room = random.choice(rooms)
        print(f"Suggesting: {character} in the {room} with the {weapon}")
        response = make_suggestion(character, weapon, room, player_hands, current_player, players)
        print(response)
        # Simulate a random accusation
        if random.random() < 0.1:
            print(f"{current_player} makes an accusation!")
            result = make_accusation(character, weapon, room)
            print(result)
            if "win" in result:
                break
        players.append(players.pop(0))  # Rotate turns

if __name__ == "__main__":
    play_game()
