""" Mini-project #6 - Blackjack

Rohan Lewis

October 2017 """

import random
import simplegui

# Card info.
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")    

# Global variables.
in_play = False
outcome = ""
DealerScore = 100
PlayerScore = 100
Pot = 0

# Define globals for cards.
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}

# Define card class.
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print "Invalid card: ", suit, rank

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def draw(self, canvas, pos):
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank), 
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        canvas.draw_image(card_images, card_loc, CARD_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], CARD_SIZE)
        
# Define hand class.
class Hand:
    def __init__(self):
        self.hand = []

    def __str__(self):
        return str(self.hand)

    def add_card(self, card):
        self.hand.append(card)

    def get_value(self):
        value = 0
        HasAce = False
        for card in self.hand :
            if card.rank == 'A' :
                HasAce = True
            value += VALUES[card.rank]
        #Aces are counted as 1 by default.  If the hand has an ace and the value of the ace as 11 does
        #not bust the hand, then let the ace be 11.
        if (HasAce == True) and (value + 10 <= 21) :
            value += 10
        return value    
        
    def draw(self, canvas, pos):
        h = 0
        v = 0
        for card in self.hand :
            if in_play == True and h==0 and pos[1] == 114:
                #Hole card is hidden until Player stands.
                canvas.draw_image(card_back, (CARD_CENTER[0] + CARD_SIZE[0], CARD_CENTER[1]), CARD_SIZE, [264 + CARD_CENTER[0], 114 + CARD_CENTER[1]], CARD_SIZE)
            else :
                card.draw(canvas, [pos[0]+h, pos[1]+v])
            if pos[1] == 114 :
                h -= 13
                v -= 11
            else :
                h += 13
                v += 11
        
#Define deck class.
class Deck:
    def __init__(self):
        self.deck = []
        for suit in SUITS :
            for rank in RANKS:
                self.deck.append(Card(suit,rank))               
                       
    def shuffle(self):
        random.shuffle(self.deck)
        print self.deck
        
    def deal_card(self):
        return self.deck.pop(-1)
    
    def __str__(self):
        return str(self.deck)

#Event handlers for buttons.
def deal():
    global in_play, outcome, NewDeck, DealerHand, PlayerHand, DealerScore, PlayerScore, Pot
    
    # If player hits Deal in middle of game, Dealer wins.
    if in_play == True :
        in_play = False
        outcome = "Player quit!  Dealer wins with " + str(DealerHand.get_value()) + "!  Deal Again?"
        DealerScore += Pot
        Pot = 0
        
    else:
        NewDeck = Deck()
        NewDeck.shuffle()
        PlayerHand = Hand()
        DealerHand = Hand()
        outcome = "Hit or Stand?"
        in_play = True
        #Dealer and Player ante up $10, both are dealt two cards.  Constant sum of $200 in game.
        DealerScore -= 10
        PlayerScore -= 10
        Pot = 20
        PlayerHand.add_card(NewDeck.deal_card())
        DealerHand.add_card(NewDeck.deal_card())
        PlayerHand.add_card(NewDeck.deal_card())
        DealerHand.add_card(NewDeck.deal_card())

def hit():
    global in_play, outcome, DealerScore, Pot
    if in_play == True :
        #Player is allowed to hit as long as score is less than 21.  Once over 21, game is over.
        #If player reaches 21, Player automatically stands.
        if PlayerHand.get_value() < 21 :
            PlayerHand.add_card(NewDeck.deal_card())
            if PlayerHand.get_value() > 21 :
                in_play = False
                outcome = "Player bust!  Dealer wins with " + str(DealerHand.get_value()) + "!  Deal Again?"
                DealerScore += Pot
                Pot = 0
            elif PlayerHand.get_value() == 21 :
                stand()
      
def stand():
    global in_play, outcome, DealerScore, PlayerScore, Pot
    if in_play == True :
        in_play = False
        #Repeatedly hit Dealer until Dealer has at least 17.
        while DealerHand.get_value() < 17 :
            DealerHand.add_card(NewDeck.deal_card())
        if DealerHand.get_value() > 21 :
            outcome = "Dealer bust!  Player wins with " + str(PlayerHand.get_value()) + "!  Deal Again?"
            PlayerScore += Pot
            Pot = 0
        #If Dealer does not bust, compare hands.  Dealer wins ties.
        elif PlayerHand.get_value() > DealerHand.get_value() :
            outcome = "Player wins, " + str(PlayerHand.get_value()) + " to " + str(DealerHand.get_value()) + "!  Deal Again?"
            PlayerScore += Pot
            Pot = 0
        else :
            outcome = "Dealer wins, " + str(DealerHand.get_value()) + " to " + str(PlayerHand.get_value()) + "!  Deal Again?"
            DealerScore += Pot
            Pot = 0
                
# Draw handler.
def draw(canvas):
    canvas.draw_text(outcome, (15, 50), 30, 'Black')
    DealerHand.draw(canvas, [264,114])
    canvas.draw_text("Dealer: $" + str(DealerScore), (410, 140), 30, 'Black')
    canvas.draw_text("Blackjack", (150, 290), 80, 'Black')
    canvas.draw_text("$10 Ante! Unlimited Bankroll!", (125, 325), 30, 'Red')
    canvas.draw_text("Pot: $" + str(Pot), (250, 360), 30, 'Black')    
    PlayerHand.draw(canvas, [264,390])
    canvas.draw_text("Player: $" + str(PlayerScore), (410, 480), 30, 'Black')    

# Initialize frame.
frame = simplegui.create_frame("Blackjack", 600, 600)
frame.set_canvas_background("Green")

# Create buttons and canvas callback.
frame.add_button("Deal", deal, 200)
frame.add_button("Hit",  hit, 200)
frame.add_button("Stand", stand, 200)
frame.set_draw_handler(draw)

# Play!
deal()
frame.start()