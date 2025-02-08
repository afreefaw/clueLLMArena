import gym
from gym import spaces
import random
import numpy as np

class ClueEnv(gym.Env):
    def __init__(self):
        super(ClueEnv, self).__init__()

        # Game elements
        self.characters = ["Miss Scarlett", "Colonel Mustard", "Mrs. White", "Reverend Green", "Mrs. Peacock", "Professor Plum"]
        self.weapons = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
        self.rooms = [
            "Kitchen", "Ballroom", "Conservatory", "Dining Room", 
            "Billiard Room", "Library", "Lounge", "Hall", "Study"
        ]
        
        self.players = ["Player 1", "Player 2", "Player 3"]
        self.current_player_idx = 0

        # Randomly choose solution
        self.solution = {
            "character": random.choice(self.characters),
            "weapon": random.choice(self.weapons),
            "room": random.choice(self.rooms),
        }

        # Distribute cards to players
        self.player_hands = self._distribute_cards()

        # Action space: Suggestion = (character, weapon, room)
        self.action_space = spaces.MultiDiscrete([len(self.characters), len(self.weapons), len(self.rooms)])

        # Observation space
        self.observation_space = spaces.Dict({
            "current_player": spaces.Discrete(len(self.players)),
            "player_hands": spaces.MultiBinary(len(self.characters) + len(self.weapons) + len(self.rooms)),  
            "last_suggestion": spaces.MultiDiscrete([len(self.characters), len(self.weapons), len(self.rooms)]),
        })

    def _distribute_cards(self):
        """Randomly distribute cards among players."""
        all_cards = self.characters + self.weapons + self.rooms
        random.shuffle(all_cards)
        player_hands = {player: [] for player in self.players}
        while all_cards:
            for player in self.players:
                if all_cards:
                    player_hands[player].append(all_cards.pop())
        return player_hands

    def reset(self, seed=None, options=None):
        """Reset the game state."""
        super().reset(seed=seed)  # Ensures Gym's built-in seeding behavior
        self.current_player_idx = 0
        self.solution = {
            "character": random.choice(self.characters),
            "weapon": random.choice(self.weapons),
            "room": random.choice(self.rooms),
        }
        self.player_hands = self._distribute_cards()
        return self._get_observation(), {}  # Now returning a tuple (obs, info)

    def step(self, action):
        """Apply an action (suggestion or accusation)."""
        character_idx, weapon_idx, room_idx = action
        character = self.characters[character_idx]
        weapon = self.weapons[weapon_idx]
        room = self.rooms[room_idx]

        current_player = self.players[self.current_player_idx]

        # Handle Suggestion
        disproved = self._make_suggestion(character, weapon, room, current_player)
        reward = 0
        terminated = False
        truncated = False

        # Handle Accusation (Random probability to accuse)
        if random.random() < 0.1:
            if self._make_accusation(character, weapon, room):
                reward = 10  # Big reward for correct accusation
                terminated = True
            else:
                reward = -5  # Penalty for incorrect accusation
                self.players.pop(self.current_player_idx)
                if len(self.players) == 1:  # Game over if only one player left
                    terminated = True
                else:
                    self.current_player_idx %= len(self.players)

        # Rotate turn
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        return self._get_observation(), reward, terminated, truncated, {}

    def _make_suggestion(self, character, weapon, room, current_player):
        """Check if any of the suggested elements can be disproven."""
        for player in self.players:
            if player != current_player:
                for card in [character, weapon, room]:
                    if card in self.player_hands[player]:
                        return True  # Suggestion disproved
        return False

    def _make_accusation(self, character, weapon, room):
        """Check if the accusation is correct."""
        return (
            character == self.solution["character"]
            and weapon == self.solution["weapon"]
            and room == self.solution["room"]
        )

    def _get_observation(self):
        """Return an encoded game state as observation."""
        current_player = self.current_player_idx
        last_suggestion = np.zeros(3, dtype=np.int32)  # Placeholder for last suggestion
        player_hand_encoding = np.zeros(len(self.characters) + len(self.weapons) + len(self.rooms), dtype=np.int32)

        for card in self.player_hands[self.players[current_player]]:
            if card in self.characters:
                player_hand_encoding[self.characters.index(card)] = 1
            elif card in self.weapons:
                player_hand_encoding[len(self.characters) + self.weapons.index(card)] = 1
            elif card in self.rooms:
                player_hand_encoding[len(self.characters) + len(self.weapons) + self.rooms.index(card)] = 1

        return {
            "current_player": current_player,
            "player_hands": player_hand_encoding,
            "last_suggestion": last_suggestion
        }

    def render(self, mode="human"):
        """Print game state for debugging."""
        print(f"Current Player: {self.players[self.current_player_idx]}")
        print(f"Solution: {self.solution}")
        print(f"Player Hands: {self.player_hands}")

    def close(self):
        pass


# Register Environment
from gym.envs.registration import register

register(
    id='Clue-v0',
    entry_point='__main__:ClueEnv',
)

# Example Usage
if __name__ == "__main__":
    env = gym.make("Clue-v0")
    obs, _ = env.reset()  # Now correctly unpacking reset()

    done = False
    while not done:
        action = env.action_space.sample()  # Random action (Replace with LLM agent later)
        obs, reward, terminated, truncated, info = env.step(action)  # Unpack new Gym step return
        env.render()
        print(f"Reward: {reward}\n")
        done = terminated or truncated  # Stop loop if game is over

    env.close()
