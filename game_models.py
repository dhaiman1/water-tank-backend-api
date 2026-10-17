"""Object-oriented models for the Water Tank card game."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from random import shuffle
from typing import Sequence


class Card(ABC):
    """Base class for cards that can be played by a player."""

    @abstractmethod
    def play(self, player: Player, opponent: Player) -> None:
        """Apply this card's effect to the two players."""


@dataclass
class WaterCard(Card):
    """A card that adds water to its player's tank."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("A water card value must be a positive integer.")

    def play(self, player: Player, opponent: Player) -> None:
        player.tank_level += self.value

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class PowerCard(Card):
    """A special-effect card: SOH, DOT, or DMT."""

    type: str

    def __post_init__(self) -> None:
        self.type = self.type.upper()
        if self.type not in {"SOH", "DOT", "DMT"}:
            raise ValueError("A power card type must be SOH, DOT, or DMT.")

    def play(self, player: Player, opponent: Player) -> None:
        if self.type == "SOH":
            transferred_water = opponent.tank_level // 2
            player.tank_level += transferred_water
            opponent.tank_level -= transferred_water
        elif self.type == "DOT":
            opponent.tank_level = 0
        else:  # DMT
            player.tank_level *= 2

    def __str__(self) -> str:
        return self.type


class Deck:
    """Owns the water and power piles, including their draw and recycle rules."""

    def __init__(
        self,
        water_cards: list[WaterCard] | None = None,
        power_cards: list[PowerCard] | None = None,
    ) -> None:
        self.water_cards = self._create_water_pile() if water_cards is None else list(water_cards)
        self.power_cards = self._create_power_pile() if power_cards is None else list(power_cards)

    @staticmethod
    def _create_water_pile() -> list[WaterCard]:
        cards = [WaterCard(1) for _ in range(30)]
        cards.extend(WaterCard(5) for _ in range(15))
        cards.extend(WaterCard(10) for _ in range(8))
        shuffle(cards)
        return cards

    @staticmethod
    def _create_power_pile() -> list[PowerCard]:
        cards = [PowerCard("SOH") for _ in range(10)]
        cards.extend(PowerCard("DOT") for _ in range(2))
        cards.extend(PowerCard("DMT") for _ in range(3))
        shuffle(cards)
        return cards

    def shuffle(self) -> None:
        """Shuffle both current piles in place."""
        shuffle(self.water_cards)
        shuffle(self.power_cards)

    def replenish_empty_piles(self) -> None:
        """Recreate and shuffle either pile that has run out."""
        if not self.water_cards:
            self.water_cards.extend(self._create_water_pile())
        if not self.power_cards:
            self.power_cards.extend(self._create_power_pile())

    def draw_water_card(self) -> WaterCard:
        """Draw the next water card, replenishing its pile first if needed."""
        if not self.water_cards:
            self.water_cards.extend(self._create_water_pile())
        return self.water_cards.pop(0)

    def draw_power_card(self) -> PowerCard:
        """Draw the next power card, replenishing its pile first if needed."""
        if not self.power_cards:
            self.power_cards.extend(self._create_power_pile())
        return self.power_cards.pop(0)

    def draw_card(self, card: Card) -> Card:
        """Draw a replacement card from the pile matching ``card``."""
        if isinstance(card, WaterCard):
            return self.draw_water_card()
        if isinstance(card, PowerCard):
            return self.draw_power_card()
        raise TypeError("A replacement can only be drawn for a WaterCard or PowerCard.")

    def discard_card(self, card: Card) -> None:
        """Place a discarded card at the bottom of its corresponding pile."""
        if isinstance(card, WaterCard):
            self.water_cards.append(card)
        elif isinstance(card, PowerCard):
            self.power_cards.append(card)
        else:
            raise TypeError("Only WaterCard and PowerCard instances belong in the deck.")


class Player:
    """A player with a tank level and a hand of cards."""

    def __init__(
        self,
        name: str,
        tank_level: int = 0,
        hand: Sequence[Card] | None = None,
    ) -> None:
        self.name = name
        self.tank_level = tank_level
        self.hand = list(hand) if hand is not None else []
        self.arrange_hand()

    def use_card(self, card: Card, opponent: Player) -> None:
        """Play and remove a card, then apply this player's tank overflow."""
        if card not in self.hand:
            raise ValueError(f"{card} is not in {self.name}'s hand.")
        card.play(self, opponent)
        self.hand.remove(card)
        self.apply_overflow()

    def discard_card(self, card: Card, deck: Deck) -> None:
        """Remove a card from this hand and return it to its pile."""
        if card not in self.hand:
            raise ValueError(f"{card} is not in {self.name}'s hand.")
        self.hand.remove(card)
        deck.discard_card(card)

    def arrange_hand(self) -> None:
        """Sort water cards numerically, followed by power cards alphabetically."""
        water_cards = sorted(
            (card for card in self.hand if isinstance(card, WaterCard)),
            key=lambda card: card.value,
        )
        power_cards = sorted(
            (card for card in self.hand if isinstance(card, PowerCard)),
            key=lambda card: card.type,
        )
        self.hand[:] = water_cards + power_cards

    def apply_overflow(self) -> int:
        """Reflect a tank level above 80 back down from the 160 mark."""
        if self.tank_level > 80:
            self.tank_level = 160 - self.tank_level
        return self.tank_level


class GameSession:
    """Tracks players, whose turn it is, and whether either player has won."""

    MIN_WINNING_LEVEL = 75
    MAX_WINNING_LEVEL = 80

    def __init__(
        self,
        players: Sequence[Player],
        deck: Deck | None = None,
        starting_player: Player | None = None,
    ) -> None:
        if len(players) != 2:
            raise ValueError("A game session requires exactly two players.")
        self.players = list(players)
        self.deck = deck if deck is not None else Deck()
        if starting_player is not None and starting_player not in self.players:
            raise ValueError("The starting player must belong to this game session.")
        self.current_player_index = (
            self.players.index(starting_player) if starting_player is not None else 0
        )

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    @property
    def opponent(self) -> Player:
        return self.players[1 - self.current_player_index]

    @property
    def winner(self) -> Player | None:
        """Return a player with a winning tank level, if one exists."""
        return next((player for player in self.players if self.has_won(player)), None)

    @classmethod
    def has_won(cls, player: Player) -> bool:
        return cls.MIN_WINNING_LEVEL <= player.tank_level <= cls.MAX_WINNING_LEVEL

    @property
    def is_over(self) -> bool:
        return self.winner is not None

    def advance_turn(self) -> Player:
        """Move play to the other player and return that player."""
        self.current_player_index = 1 - self.current_player_index
        return self.current_player

    def computer_turn(self) -> Card:
        """Play the current player's best card, draw its replacement, and advance.

        Winning cards are preferred. Otherwise, the chosen card maximizes the
        change in the current player's tank advantage over the opponent.
        """
        if self.is_over:
            raise RuntimeError("The game is already over.")

        player = self.current_player
        opponent = self.opponent
        if not player.hand:
            raise ValueError(f"{player.name} has no cards to play.")

        def resulting_levels(card: Card) -> tuple[int, int]:
            player_level = player.tank_level
            opponent_level = opponent.tank_level
            if isinstance(card, WaterCard):
                player_level += card.value
            elif isinstance(card, PowerCard):
                if card.type == "SOH":
                    transferred_water = opponent_level // 2
                    player_level += transferred_water
                    opponent_level -= transferred_water
                elif card.type == "DOT":
                    opponent_level = 0
                else:  # DMT
                    player_level *= 2
            else:
                raise TypeError("A player's hand can only contain WaterCard or PowerCard instances.")
            if player_level > 80:
                player_level = 160 - player_level
            return player_level, opponent_level

        chosen_card = next(
            (
                card
                for card in player.hand
                if self.MIN_WINNING_LEVEL
                <= resulting_levels(card)[0]
                <= self.MAX_WINNING_LEVEL
            ),
            None,
        )

        if chosen_card is None:
            previous_advantage = player.tank_level - opponent.tank_level

            def utility_delta(card: Card) -> int:
                player_level, opponent_level = resulting_levels(card)
                return player_level - opponent_level - previous_advantage

            chosen_card = max(player.hand, key=utility_delta)

        player.use_card(chosen_card, opponent)
        player.hand.append(self.deck.draw_card(chosen_card))
        player.arrange_hand()

        if not self.is_over:
            self.advance_turn()
        return chosen_card