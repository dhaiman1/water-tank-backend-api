# Student Name in Canvas: David Haiman
# Penn ID: 19575853
# Did you do this homework on your own (yes / no): yes
# Resources used outside course materials: stackoverflow.com, w3schools, youtube

# Import statements
from random import shuffle, randint

def get_user_input(question):
    """
    Prompts the user for input and formats the response based on type.

    Prompts until some answer is received. Converts numeric
    strings to integers, capitalizes power card names, and lowercases
    all other strings.
    """
    answer = ""
    while not answer:
        answer = input(question).strip()
        if answer.isnumeric():
            answer = int(answer)
        elif answer.lower() in ("soh", "dot", "dmt"):
            answer = answer.upper()
        else:
            answer = answer.lower()
    return answer


def setup_water_cards():
    """
    Creates a shuffled list of cards 53 water cards represented by ints, 30 (1s), 15(5s), 8(10s)
    takes no arguments
    returns a list of ints representing the water cards
    """
    ones, fives, tens, = [1] * 30, [5] * 15, [10] * 8
    water_cards = ones + fives + tens
    shuffle(water_cards)
    return water_cards

def setup_power_cards():
    """
    Creates a shuffled list of 15 power cards represented by strings (SOH, DOT, DMT)
    takes no args
    returns a list of strings representing the power cards
    """
    soh, dot, dmt = ["SOH"] * 10, ["DOT"] * 2, ["DMT"] * 3
    power_cards = soh + dot + dmt
    shuffle(power_cards)
    return power_cards

def setup_cards():
    """
    Takes no arguments
    returns a two-tuple of lists, one list of ints representing the water cards,
    and another list of strings representing the power cards
    """
    return setup_water_cards(), setup_power_cards()

def get_card_from_pile(pile, index):
    """
    Removes and returns a card from a specific position in a card pile.
    """
    return pile.pop(index)

def arrange_cards(cards_list):
    """
    Takes a cards list as an argument and sorts it in place, numerically then alphanumerically.
    Then updates the original list in place using slice assignment.
    Returns nothing
    """
    water_cards, power_cards = [], []
    for card in cards_list:
        if isinstance(card, int):
            water_cards.append(card)
        else:
            power_cards.append(card)

    water_cards.sort()
    power_cards.sort()
    # Using slice notation alters the list in place without reassigning
    cards_list[:] = water_cards + power_cards

def deal_cards(water_cards_pile, power_cards_pile):
    """
    Takes water cards pile and power cards pile as args (lists)
    returns an arranged two-tuple of lists, each of which containing 2 power cards and 3 water cards
    """
    player_1, player_2 = [], []
    for i in range(3):
        player_1.append(get_card_from_pile(water_cards_pile, 0))
        player_2.append(get_card_from_pile(water_cards_pile, 0))
    for i in range(2):
        player_1.append(get_card_from_pile(power_cards_pile, 0))
        player_2.append(get_card_from_pile(power_cards_pile, 0))

    arrange_cards(player_1)
    arrange_cards(player_2)
    return player_1, player_2


def apply_overflow(tank_level):
    """
    Applies overflow logic if a player's tank level exceeds maximum capacity.
    If tank level > 80, the level overflows and reduces to (160 - tank_level).
    """
    if tank_level > 80:
        tank_level = 160 - tank_level
    return tank_level

def use_card(player_tank, card_to_use, player_cards, opponent_tank):
    """
    Takes 4 arguments, player tank, opponent tank, card to be used, and player's cards.
    Modifies player and opponent tank levels based on card type,
    removes the played card from player's cards in place, and
    applies tank overflow logic to the player's tank.
    Returns a tuple containing the player tank and opponent tank
    """
    # check what kind of card is being used
    # if card_to_use is an int, we know its a water card, update player tank tank
    # else it's a power card, check what the power card is and alter appropriate tanks as per rules
    if isinstance(card_to_use, int):
        player_tank += card_to_use
    else:
        if card_to_use == "SOH":
            player_tank += (opponent_tank // 2)
            opponent_tank -= (opponent_tank // 2)
        elif card_to_use == "DOT":
            opponent_tank = 0
        else:               # card_to_use == "DMT" (double my tank)
            player_tank *= 2
    # remove the used card from the player's current cards
    player_cards.remove(card_to_use)

    return apply_overflow(player_tank), opponent_tank

def utility(player_tank, card_to_use, opponent_tank):
    """
    Takes a player's tank, card to be used, and opponent's tank
    and returns the difference between the player and opponent tank before and after the use of the card,
    does not actually use a card, no tank is updated and no card is discarded
    Same logic as use_card except it returns only an int
    """
    before_difference = player_tank - opponent_tank
    if isinstance(card_to_use, int):
        player_tank += card_to_use
    else:
        if card_to_use == "SOH":
            player_tank += (opponent_tank // 2)
            opponent_tank -= (opponent_tank // 2)
        elif card_to_use == "DOT":
            opponent_tank = 0
        else:               # card_to_use == "DMT" (double my tank)
            player_tank *= 2

    delta = ((apply_overflow(player_tank) - opponent_tank) - before_difference)

    return delta

def discard_card(card_to_discard, player_cards, water_cards_pile, power_cards_pile):
    """
    Takes card_to_discard as first argument and removes card from player_cards(second argument)
    and adds it to the back of the proper pile (either water cards pile or power cards pile
    returns None
    """
    if isinstance(card_to_discard, int):
        water_cards_pile.append(card_to_discard)
    else:
        power_cards_pile.append(card_to_discard)

    player_cards.remove(card_to_discard)

def filled_tank(tank):
    """
    Checks if a tank level meets winning level.
    Returns boolean value
    """
    return 75 <= tank <= 80

def check_pile(pile, pile_type):
    """
    Takes a cards pile as an argument and checks to see if it is empty
    If pile list is empty, modify list inplace with a setup ot a new shuffled pile
    by calling setup_cards(). Does not return anything.
    """
    # Uses list index to modify list in place
    if len(pile) == 0:
        if pile_type == "water":
            pile[:] = setup_water_cards()
        else:
            pile[:] = setup_power_cards()


def human_play(human_tank, human_cards, water_cards_pile, power_cards_pile, opponent_tank):
    """
    Executes turn logic for human player.
    Prints current status, prompts user for action (use/discard) and card choice,
    performs chosen action, draws replacement card from pile, and sorts hand.
    Returns a two-tuple of player tank and opponent tank
    """
    print(f"""=== Player's turn ===
Your water level is at: {human_tank}
The Computer's water level is at: {opponent_tank}
Your cards are {human_cards}""")
    player_tank, computer_tank = human_tank, opponent_tank

    # Validate input for both choose_move and pick_card
    choose_move, pick_card = '', ''
    while choose_move not in ('u', 'd'):
        choose_move = get_user_input("Do you want to use or discard a card? (u/d) ")
        if choose_move not in ('u', 'd'):
            print("Please enter either \'u\' or \'d\'")

    while pick_card not in human_cards:
        pick_card = get_user_input("Which card do you want to use or discard? ")
        if pick_card not in human_cards:
            print("Please select a card currently in your hand.")
    # Use or discard appropriate card
    if choose_move == 'u':
        player_tank, computer_tank = use_card(human_tank, pick_card, human_cards, opponent_tank)
    else:
        discard_card(pick_card, human_cards, water_cards_pile, power_cards_pile)

    # Draw card from appropriate pile
    if isinstance(pick_card, int):
        human_cards.append(get_card_from_pile(water_cards_pile, 0))
    else:
        human_cards.append(get_card_from_pile(power_cards_pile, 0))
    # Arrange cards after use/discard and redraw
    arrange_cards(human_cards)

    print(f"Your water level is now at: {player_tank}\n"
          f"Computer's water level is now at:  {opponent_tank}\n"
          f"Your cards are now:  {human_cards}")
    print()
    return player_tank, computer_tank

def computer_play(computer_tank, computer_cards, water_cards_pile, power_cards_pile, opponent_tank):
    """
    Executes turn logic for computer player.
    Evaluates hand to prioritize direct winning moves first, if there is no winning card it prioritizes by max utility,
    updates game state, draws replacement card, and arranges hand.
    Returns computer_tank and player_tank as a tuple
    """
    print(f"=== Computer Player's turn ===\n"
          f"Computer's water level is at:  {computer_tank}\n"
          f"Your water level is at:  {opponent_tank}")
    # Check if any of the cards in hand will directly result in a win
    card_use = None
    for card in computer_cards:
        if isinstance(card, int):
            possible_tank = apply_overflow(computer_tank + card)
            if filled_tank(possible_tank):
                card_use = card
                break           # Break as we already have a card that wins.
        else:
            if card == "DMT" and filled_tank(apply_overflow(computer_tank * 2)):
                card_use = card
            elif card == "SOH" and filled_tank(apply_overflow(computer_tank + (opponent_tank // 2))):
                card_use = card

    # Secondarily checks if we don't have a winning card, uses the max utility to choose card to use
    if card_use is None:
        max_util = 0
        for card in computer_cards:
            util = utility(computer_tank, card, opponent_tank)
            if util > max_util:
                max_util = util
                card_use = card

    computer_tank, opponent_tank = use_card(computer_tank, card_use, computer_cards, opponent_tank)
    print(f"Computer is playing card: {card_use}\n"
          f"Computer's water level is now at: {computer_tank}\n"
          f"Your water level is now at: {opponent_tank}")
    print()
    # Draw card from appropriate pile
    if isinstance(card_use, int):
        computer_cards.append(get_card_from_pile(water_cards_pile, 0))
    else:
        computer_cards.append(get_card_from_pile(power_cards_pile, 0))
    # Arrange cards after use/discard and redraw
    arrange_cards(computer_cards)

    return computer_tank, opponent_tank


def main():
    # Print game instructions
    print("""Welcome to the WATER TANK game and play against the computer!
Fill your tank by using or discarding a card for each turn.
The first player to fill their tank wins the game.
Good luck!""")
    print()
    # Setup player and computer water tanks
    player_tank = 0
    computer_tank = 0

    # Determine which player will have the first turn
    turn = ''
    if randint(0, 1) == 0:
        turn = "player"
        print("The Human player has been selected to go first")
    else:
        turn = "computer"
        print("The Computer opponent has been selected to go first")
    print()
    # Setup cards, water pile and power pile will be lists
    water_pile, power_pile = setup_cards()

    # Deal cards to players (each player gets 3 water and 2 power cards), each players cards will be represented by a list
    player_cards, computer_cards = deal_cards(water_pile, power_pile)

    # Run game
    game_not_over = True
    while game_not_over:
        if turn == "player":
            player_tank, computer_tank = human_play(player_tank, player_cards, water_pile, power_pile, computer_tank)
            if filled_tank(player_tank):
                game_not_over = False
                print("Human Player wins!")
                break
            turn = "computer"
        else:
            computer_tank, player_tank = computer_play(computer_tank, computer_cards, water_pile, power_pile, player_tank)
            if filled_tank(computer_tank):
                game_not_over = False
                print("Computer Player wins!")
                break
            turn = "player"

        # Check if water/power piles are empty, if so refill them
        check_pile(water_pile, "water")
        check_pile(power_pile, "power")




if __name__ == "__main__":
    main()
