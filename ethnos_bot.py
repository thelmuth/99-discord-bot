"""
Bot to implement Ethnos

Usage:
python3 ethnos_bot.py

OR to unpickle a saved game:
python3 ethnos_bot.py backup_ethnos_bot_DATETIME.dat

To do:
- !untable command
"""

import discord
import discord.ext
import discord.ext.commands
import random, dill, time, sys

client = discord.ext.commands.Bot(command_prefix = '!')

with open("ethnos.key", "r") as f:
    auth_key = f.read().strip()

TRIBES = ["Centaur",
          "Dwarf",
          # "Elf",
          "Giant",
          # "Halfling",
          # "Merfolk",
          # "Minotaur",
          # "Orc",
          "Skeleton",
          "Troll",
          # "Wingfolk",
          "Wizard"
          ]

# random.shuffle(TRIBES)
# print(TRIBES[:6])
# 1 / 0

COLORS = ["Red", "Green", "Blue", "Gray", "Purple", "Orange"]

class Player:
    """Stores player data"""

    def __init__(self, name):
        self.name = name
        self.cards = []

    def __len__(self):
        return len(self.cards)

    def add_card(self, card):
        self.cards.append(card)
        self.cards.sort()

    def remove_card(self, card):
        self.cards.remove(card)

    def empty_hand(self):
        self.cards = []

class EthnosBot:
    """Implements control of Ethnos."""

    def __init__(self):
        self.deck = []
        for tribe in TRIBES:
            for color in COLORS:
                card = f"{color} {tribe}"
                if tribe == "Halfling":
                    self.deck.extend([card] * 4)
                else:
                    self.deck.extend([card] * 2)

        random.shuffle(self.deck)

        self.started = False
        self.dragons = 0
        self.just_drew_dragon

        self.players = {}
        self.player_id_list = []
        self.available_cards = []

    @classmethod
    def load_ethnos_bot(cls, filename):
        with open(filename, "rb") as f:
            bot = dill.load(f)
            return bot

    def pickle_ethnos_bot(self):
        filename = f"backup_ethnos_bot_{time.strftime('%Y-%m-%d_%H-%M-%S')}.dat"
        with open(filename, "wb") as f:
            dill.dump(self, f)

    def add_player(self, user):
        """Adds this player to the game, if not already there."""
        id = user.id
        if id in self.player_id_list or self.started:
            return

        name = user.name
        self.players[id] = Player(name)
        self.player_id_list.append(id)

        # Each player draws a single card at the start
        return self.draw(id)

    def start(self):
        """Starts the game of Ethnos"""
        if self.started:
            return

        self.started = True

        # Deal out available cards
        players = len(self.player_id_list)
        for _ in range(players * 2):
            self.available_cards.append(self.deck.pop())
        self.available_cards.sort()

        # Add dragon cards
        half = len(self.deck) // 2
        first_half = self.deck[:half]
        second_half = self.deck[half:]

        second_half.extend(["Dragon"] * 3)
        random.shuffle(second_half)
        self.deck = second_half + first_half

    def available(self, card):
        """Checks if card is available, ignoring caps."""
        c = card.title()
        return c in self.available_cards

    def draw(self, id):
        """Draws a card, adds it to player id's hand, and returns it."""
        card = None

        while len(self.deck) > 0:
            card = self.deck.pop()
            if card == "Dragon":
                self.dragons += 1
                self.just_drew_dragon = True
            else:
                break

        self.players[id].add_card(card)
        return card

    def pickup(self, id, card):
        """Has player pick up card, adds it to player id's hand."""
        c = card.title()
        self.players[id].add_card(c)
        self.available_cards.remove(c)

    def add_card(self, id, card):
        """Has player add card to hand (out of thin air)."""
        c = card.title()
        self.players[id].add_card(c)

    def hand(self, id):
        """Returns hand of player given by id"""
        return self.players[id].cards

    def empty_hand(self, id):
        """Empties the player's hand."""
        self.players[id].empty_hand()

    def play(self, id, card):
        """Plays the card from hand of player id."""
        self.players[id].remove_card(card)

    def table_card(self, card):
        """Adds card to available cards."""
        self.available_cards.append(card)
        self.available_cards.sort()

    def untable_card(self, card):
        """Removes card from available cards."""
        c = card.title()
        self.available_cards.remove(c)

    def drew_a_dragon(self):
        """Returns True if a Dragon was drawn. Resets self.just_drew_dragon to False"""
        result = self.just_drew_dragon
        self.just_drew_dragon = False
        return result

    def cards_per_hand(self):
        """Returns a string of the number of cards per hand for each player."""
        s = ""
        for id in self.player_id_list:
            name = self.players[id].name
            cards = len(self.players[id])
            s += "{} has {} cards.\n".format(name, cards)
        return s[:-1]

    def next_player(self, id):
        """Finds the next player after name for player turn order. Return's that
        player's id"""
        index = self.player_id_list.index(id)
        next_index = (index + 1) % len(self.player_id_list)
        return self.player_id_list[next_index]

#########################################################
### Setting up EB and on_ready
#########################################################

if len(sys.argv) == 1:
    EB = EthnosBot()
elif len(sys.argv) == 2:
    EB = EthnosBot.load_ethnos_bot(sys.argv[1])
else:
    raise Exception("Incorrect command line arguments.")

@client.event
async def on_ready():
    """ Displayed in the terminal when the bot is logged in. """
    channel = client.get_channel(720073170500976801)
    # await channel.send("Who wants to play Ethnos?")
    print("Who wants to play Ethnos?")

    commands = """Here are the commands you will need:
- `!join` - joins game before it starts
- `!draw` - draw a random card from the deck
- `!pickup color tribe` - pickup card from available cards with given color and tribe
- `!band` - form a band from the cards in your hand.
- `!hand` - DMs you your current hand.
- `!available` - Tells what cards are available on the table.

The following commands will be helpful in uncommon situations, and should be used only if the above commands don't do what you need:
- `!add color tribe` - Adds card with given card and tribe to your hand out of thin air.
- `!discard color tribe` - Discards card with given card and tribe from your hand. _Does not_ put it in available cards
- `!table color tribe` - Puts card with given card and tribe on the table out of thin air.
- `!untable color tribe` - Removes card with given card and tribe from the table to nowhere.
"""
    await channel.send(commands)

#########################################################
### Helper functions that aren't commands
#########################################################

async def next_player_message(ctx):
    """Used to tell who is the next player. Argument is context from which next
    player can be determined."""
    user = client.get_user(EB.next_player(ctx.message.author.id))
    message = "It is now {}'s turn.".format(user.mention)
    await ctx.send(message)

async def available_cards_message(ctx):
    """Tells what the available cards are."""
    await ctx.send("Available cards: " + str(EB.available_cards))

async def cards_per_hand(ctx):
    """Used to tell number of cards in each hand."""
    message = EB.cards_per_hand()
    await ctx.send(message)

async def dragons(ctx):
    """Checks number of Dragons drawn"""
    if EB.drew_a_dragon():
        await ctx.send("**A Dragon card was drawn!!**")
        await ctx.send(":dragon:")

    message = f"There are now {len(EB.deck)} cards in the deck.\n{EB.dragons} Dragon cards have been drawn."

    if EB.dragons == 3:
        message = "==========================\n3 Dragon cards have been drawn! This Age is over!\n=========================="
    await ctx.send(message)
    return EB.dragons

#########################################################
### Commands
#########################################################

@client.command()
async def join(ctx):
    """Adds this player to the game."""
    card = EB.add_player(ctx.message.author)
    if card == None:
        return
    hand = EB.hand(ctx.message.author.id)

    await ctx.send("Welcome to the game, {}".format(ctx.message.author.name))
    await ctx.message.author.send("You draw the card {}, and your hand is {}.".format(card, hand))

    print("Added {} to the game.".format(ctx.message.author.name))

@client.command()
async def start(ctx):
    """Starts the game."""
    EB.start()
    await ctx.send("Starting game of Ethnos!")
    await available_cards_message(ctx)

@client.command()
async def draw(ctx):
    """Have player draw a random card"""
    if not EB.started:
        await ctx.send("You cannot draw a card until the game has been started.")
        return

    card = EB.draw(ctx.message.author.id)
    hand = EB.hand(ctx.message.author.id)
    await ctx.message.author.send("You draw the card {}, and your hand is {}.".format(card, hand))
    print(ctx.message.author.name, "drew a card.")

    # Check dragons
    await dragons(ctx)

    if EB.dragons < 3:
        # Say number of cards in each hand
        await cards_per_hand(ctx)

        # Available cards
        await available_cards_message(ctx)

        # Say next player's turn
        await next_player_message(ctx)

@client.command()
async def pickup(ctx, color, tribe):
    """Have player pickup a card from the table."""
    if not EB.started:
        await ctx.send("You cannot pickup a card until the game has been started.")
        return

    card = f"{color} {tribe}"
    if EB.available(card):
        EB.pickup(ctx.message.author.id, card)
        hand = EB.hand(ctx.message.author.id)
        await ctx.message.author.send("You pickup the card {}, and your hand is {}.".format(card, hand))
        await ctx.send(f"{ctx.message.author.name} picked up the card {card}.")
        print(ctx.message.author.name, "picked up the card", card)

        # Say number of cards in each hand
        await cards_per_hand(ctx)

        # Available cards
        await available_cards_message(ctx)

        # Say next player's turn
        await next_player_message(ctx)
    else:
        await ctx.send(f"Sorry, '{color} {tribe}' is not an available card.")

@pickup.error
async def pickup_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please tell me which card to pickup, as in `!pickup Red Dwarf` to pickup the card 'Red Dwarf'.")


@client.command()
async def band(ctx):
    """Play the card 'card' from the hand."""
    if not EB.started:
        await ctx.send("You cannot form a band until the game has been started.")
        return

    # Most of the band forming will have to happen manually.
    hand = EB.hand(ctx.message.author.id)

    await ctx.send("{} is forming a band with the following cards:\n{}".format(ctx.message.author.name, hand))
    await ctx.send(f"{ctx.message.author.name} should announce which cards are in the band, including the leader.\nThen, make remaining cards available with the `!table Color Tribe` command.")

    print(f"{ctx.message.author.name} is forming a band.")


    # Remove all cards from hand and tell them about it
    EB.empty_hand(ctx.message.author.id)

    hand = EB.hand(ctx.message.author.id)
    await ctx.message.author.send("You just made a band, and your hand is {}.".format(card, hand))

    # Say number of cards in each hand
    await cards_per_hand(ctx)

    # Available cards
    await available_cards_message(ctx)

    # Say next player's turn
    await next_player_message(ctx)


@client.command()
async def hand(ctx):
    """DMs the players hand to them."""
    hand = EB.hand(ctx.message.author.id)
    await ctx.message.author.send("Your current hand is {}.".format(hand))
    print(ctx.message.author.name, "requested to see their hand.")

@client.command()
async def available(ctx):
    """Tells what cards are available."""
    await available_cards_message(ctx)
    print(ctx.message.author.name, "requested to see the available cards.")


@client.command()
async def add(ctx, color, tribe):
    """Adds card to player's hand.
    This should only be used for fixing erroneous situations."""
    c = color.title()
    t = tribe.title()
    card = f"{c} {t}"
    print(f"{ctx.message.author.name} is adding the card {card}.")

    if c not in COLORS or t not in TRIBES:
        await ctx.send(f"Sorry, {card} is not a legal card name; check spelling.")
    else:
        EB.add_card(ctx.message.author.id, card)
        await ctx.send(f"{ctx.message.author.name} added card {card} to their hand.")
        hand = EB.hand(ctx.message.author.id)
        await ctx.message.author.send("You add the card {}, and your hand is {}.".format(card, hand))

@add.error
async def add_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please tell me which card to add to your hand, as in `!add Red Dwarf` to add the card 'Red Dwarf' to your hand.")

@client.command()
async def discard(ctx, color, tribe):
    """Discards card from player's hand.
    This should only be used for fixing erroneous situations."""
    c = color.title()
    t = tribe.title()
    card = f"{c} {t}"
    print(f"{ctx.message.author.name} is discarding the card {card}.")

    if c not in COLORS or t not in TRIBES:
        await ctx.send(f"Sorry, {card} is not a legal card name; check spelling.")
    elif card not in EB.hand(ctx.message.author.id):
        await ctx.send(f"Sorry, {card} is not in your hand.")
    else:
        EB.play(ctx.message.author.id, card)
        await ctx.send(f"{ctx.message.author.name} discarded card {card} from their hand.")
        hand = EB.hand(ctx.message.author.id)
        await ctx.message.author.send("You discard the card {}, and your hand is {}.".format(card, hand))

@discard.error
async def discard_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please tell me which card to discard from your hand, as in `!discard Red Dwarf` to discard the card 'Red Dwarf' from your hand.")

@client.command()
async def table(ctx, color, tribe):
    """Puts card on Table out of thin air.
    This should only be used for fixing erroneous situations."""
    c = color.title()
    t = tribe.title()
    card = f"{c} {t}"
    print(f"{ctx.message.author.name} is tabling the card {card}.")

    if c not in COLORS or t not in TRIBES:
        await ctx.send(f"Sorry, {card} is not a legal card name; check spelling.")
    else:
        EB.table_card(card)
        await available_cards_message(ctx)

@table.error
async def table_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please tell me which card to put on the table, as in `!table Red Dwarf` to put the card 'Red Dwarf' on the table.")

@client.command()
async def untable(ctx, color, tribe):
    """Removes card from Table to thin air.
    This should only be used for fixing erroneous situations."""
    c = color.title()
    t = tribe.title()
    card = f"{c} {t}"
    print(f"{ctx.message.author.name} is untabling the card {card}.")

    if c not in COLORS or t not in TRIBES:
        await ctx.send(f"Sorry, {card} is not a legal card name; check spelling.")
    elif not EB.available(card):
        await ctx.send(f"Sorry, {card} is not on the table.")
    else:
        EB.untable_card(card)
        await available_cards_message(ctx)

@untable.error
async def untable_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please tell me which card to remove from the table, as in `!untable Red Dwarf` to remove the card 'Red Dwarf' from the table.")


@client.command(aliases=["pickle"])
async def pickle_cards(ctx):
    """Pickles gamestate for loading later."""
    EB.pickle_ethnos_bot()
    await ctx.send("Gamestate has been pickled.")
    print("Gamestate has been pickled.")



if auth_key == '':
    print("Invalid auth key for bot")
else:
    client.run(auth_key)
