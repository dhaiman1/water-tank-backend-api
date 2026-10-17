"""FastAPI endpoints for starting and playing Water Tank games."""

from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from game_models import Deck, GameSession, Player, PowerCard, WaterCard

app = FastAPI(title="Water Tank Game API")
games: dict[str, GameSession] = {}


class MoveRequest(BaseModel):
    action: str = Field(description="Either 'use' or 'discard'.")
    card: int | str = Field(description="A water card value or power card type.")


def _board_state(session_id: str, session: GameSession) -> dict:
    return {
        "session_id": session_id,
        "players": [
            {
                "name": player.name,
                "tank_level": player.tank_level,
                "hand": (
                    None
                    if player is session.players[1]
                    else [
                        {"type": "water", "value": card.value}
                        if isinstance(card, WaterCard)
                        else {"type": "power", "value": card.type}
                        for card in player.hand
                    ]
                ),
                "hand_size": len(player.hand),
            }
            for player in session.players
        ],
        "current_player": session.current_player.name,
        "winner": session.winner.name if session.winner else None,
        "game_over": session.is_over,
    }


def _find_card(player: Player, requested_card: int | str):
    if isinstance(requested_card, bool):
        raise HTTPException(status_code=400, detail="The selected card is invalid.")

    if isinstance(requested_card, int):
        target_value = requested_card
        matches = [
            card
            for card in player.hand
            if isinstance(card, WaterCard) and card.value == target_value
        ]
    else:
        normalized = requested_card.strip().upper()
        if normalized.isdecimal():
            target_value = int(normalized)
            matches = [
                card
                for card in player.hand
                if isinstance(card, WaterCard) and card.value == target_value
            ]
        else:
            matches = [
                card
                for card in player.hand
                if isinstance(card, PowerCard) and card.type == normalized
            ]

    if not matches:
        raise HTTPException(status_code=400, detail="That card is not in your hand.")
    return matches[0]


@app.post("/api/game/new")
def new_game() -> dict:
    """Create a session with a five-card hand for each player."""
    deck = Deck()
    human = Player("Human")
    computer = Player("Computer")

    for _ in range(3):
        human.hand.append(deck.draw_water_card())
        computer.hand.append(deck.draw_water_card())
    for _ in range(2):
        human.hand.append(deck.draw_power_card())
        computer.hand.append(deck.draw_power_card())
    human.arrange_hand()
    computer.arrange_hand()

    session = GameSession([human, computer], deck, starting_player=human)
    session_id = str(uuid4())
    games[session_id] = session
    return _board_state(session_id, session)


@app.get("/api/game/{session_id}")
def get_game(session_id: str) -> dict:
    """Return the current board state for a session."""
    session = games.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found.")
    return _board_state(session_id, session)


@app.post("/api/game/{session_id}/move")
def make_move(session_id: str, move: MoveRequest) -> dict:
    """Execute the human move and, if needed, the computer's response."""
    session = games.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game session not found.")
    if session.is_over:
        raise HTTPException(status_code=409, detail="This game is already over.")
    if session.current_player.name != "Human":
        raise HTTPException(status_code=409, detail="It is not the human player's turn.")

    action = move.action.strip().lower()
    if action not in {"use", "discard"}:
        raise HTTPException(status_code=400, detail="Action must be 'use' or 'discard'.")

    human = session.current_player
    computer = session.opponent
    card = _find_card(human, move.card)

    if action == "use":
        human.use_card(card, computer)
    else:
        human.discard_card(card, session.deck)

    human.hand.append(session.deck.draw_card(card))
    human.arrange_hand()

    if not session.is_over:
        session.advance_turn()
        session.computer_turn()

    return _board_state(session_id, session)