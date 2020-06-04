"""
Bot to implement Game of 99
"""

import discord
import discord.ext
import discord.ext.commands
import random

client = discord.ext.commands.Bot(command_prefix = '99')

with open("ninety_nine.key") as f:
    auth_key = f.read().strip()

class Player:

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

class NinetyNineBot:

    def __init__(self):
        self.deck = list(range(100))
        random.shuffle(self.deck)

        self.players = {}
        self.player_id_list = []

    def add_player(self, id, name):
        """Adds this player to the game."""
        self.players[id] = Player(name)
        self.player_id_list.append(id)

    def draw(self, id):
        """Draws a card, adds it to player id's hand, and returns it."""
        card = self.deck.pop()
        self.players[id].add_card(card)
        return card

    def hand(self, id):
        """Returns hand of player given by id"""
        return self.players[id].cards

    def play(self, id, card):
        """Plays the card from hand of player id."""
        self.players[id].remove_card(card)

    def cards_per_hand(self):
        """Returns a string of the number of cards per hand for each player."""
        s = ""
        for id in self.player_id_list:
            name = self.players[id].name
            cards = len(self.players[id])
            s += "{} has {} cards.\n".format(name, cards)
        return s[:-1]


NNB = NinetyNineBot()


@client.event
async def on_ready():
    """ Displayed in the terminal when the bot is logged in. """
    print("Who wants to play The Game of 99?")

@client.command(aliases=['join'])
async def _99join(ctx):
    """Adds this player to the game."""
    NNB.add_player(ctx.message.author.id, ctx.message.author.name)
    await ctx.send("Welcome to the game, {}".format(ctx.message.author.name))
    print("Added {} to the game.".format(ctx.message.author.name))


@client.command(aliases=['draw'])
async def _99draw(ctx):
    """Run with the 99draw command"""
    card = NNB.draw(ctx.message.author.id)
    hand = NNB.hand(ctx.message.author.id)
    await ctx.message.author.send("You draw the card {}, and your hand is {}.".format(card, hand))
    print(ctx.message.author.name, "drew a card.")

    # Say number of cards in each hand
    message = NNB.cards_per_hand()
    await ctx.send(message)

@client.command(aliases=['play'])
async def _99play(ctx, card):
    """Play the card 'card' from the hand."""
    try:
        card = int(card)
    except Exception:
        await ctx.send("Sorry {}, you did not provide a reasonable card number.".format(ctx.message.author.name))

    if card in NNB.hand(ctx.message.author.id):
        NNB.play(ctx.message.author.id, card)
        hand = NNB.hand(ctx.message.author.id)
        await ctx.send("{} played the card {}.".format(ctx.message.author.name, card))
        await ctx.message.author.send("You played the card {}, and your hand is {}.".format(card, hand))

        print(ctx.message.author.name, "played the card", card)

        # Say number of cards in each hand
        message = NNB.cards_per_hand()
        await ctx.send(message)

    else:
        await ctx.send("Sorry {}, you do not have card {} in your hand.".format(ctx.message.author.name, card))

@_99play.error
async def _99play_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please tell me which card to play, as in `99play 29` to play card 29.")



@client.command(aliases=['hand'])
async def _99hand(ctx):
    """DMs the players hand to them."""
    hand = NNB.hand(ctx.message.author.id)
    await ctx.message.author.send("Your current hand is {}.".format(hand))
    print(ctx.message.author.name, "requested to see their hand.")



if auth_key == '':
    print("Invalid auth key for bot")
else:
    client.run(auth_key)
