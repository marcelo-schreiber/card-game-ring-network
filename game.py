import random

class Deck:
    cardSuits = ['♦', '♠', '♥', '♣']
    cardValues = ['4', '5', '6', '7', 'J', 'Q', 'K', 'A', '2', '3']

    def __init__(self):
        self.cards = [f"{valor}{naipe}" for valor in self.cardValues for naipe in self.cardSuits]
        random.shuffle(self.cards)

    def deal_cards(self, player_count, card_count):
        player_hands = [[] for _ in range(player_count)]
        for _ in range(card_count):
            for j in range(player_count):
                if self.cards:
                    player_hands[j].append(self.cards.pop())

        return player_hands

class Player:
    def __init__(self, name):
        self.name = name
        self.lifeCount = 13
        self.cards = []
        self.prediction = 0
        self.roundsWonCount = 0

    def set_cards(self, cards):
        self.cards = cards

    def set_prediction(self, prediction):
        self.prediction = prediction

    def drop_card(self, card=None, should_pop = False):
        if not card:
            if should_pop:
                return self.cards.pop(0)
            else:
                return self.cards[0]
        
        idx = self.cards.index(card)

        if self.cards:
            if should_pop:
                return self.cards.pop(idx)
            else:
                return self.cards[idx]

        return None

    def updateLifeCount(self):
        self.lifeCount -= abs(self.prediction - self.roundsWonCount)
        self.roundsWonCount = 0
    
    def __repr__(self) -> str:
        return f"Nome: {self.name}, Cartas: {self.cards}, Vidas: {self.lifeCount}, Palpite: {self.prediction}, Jogadas feitas: {self.roundsWonCount}"


class FodinhaGame:
    def __init__(self, players):
        self.players = {player: Player(player) for player in players}
        self.deck = Deck()
        self.currentRound = 1

    def calculate_card_value(self, card):
        card_value = card[:-1]
        cardSuit = card[-1:]
        return Deck.cardValues.index(card_value) * 10 + Deck.cardSuits.index(cardSuit)

    def is_game_over(self):
        return any(jogador.lifeCount <= 0 for jogador in self.players.values()) or self.currentRound == 13

    def get_winner(self):
        return max(self.players.values(), key=lambda x: x.lifeCount)

# msgs types can be:
# 'distribution', 'bet', 'share_bet', 'play_round', 'update_round', 'update_results', 'end', 'change_card_dealer'

class MessageHandler:
    def __init__(self, players=["Alice", "Bob", "Charlie"], me="Alice", is_dealer=False):
        self.cardGame = FodinhaGame(players)
        self.me = me
        self.is_dealer = is_dealer

    # one receive and one send message for each msg type
    def receive_distribution(self, data):
        distribution = data['distribution']
        for player in distribution:
            self.cardGame.players[player['player']].set_cards(player['cards'])
        
    def send_distribution(self):
        distribution = Deck().deal_cards(len(self.cardGame.players), 14 - self.cardGame.currentRound)
        for i, jogador in enumerate(self.cardGame.players.values()):
            jogador.set_cards(distribution[i])
        return {
            "type": "distribution",
            "data": {
                "distribution": [{"player": jogador.name, "cards": jogador.cards} for jogador in self.cardGame.players.values()]
            }
        }

    def receive_bet(self, data):
        for player in data['bets']:
            self.cardGame.players[player['player']].set_prediction(player['bet'])
    
    def send_bet(self, data={"bets": []}):
        # append my bet
        return {
            "type": "bet",
            "data": {
                "bets": data['bets'] + [{"player": self.me, "bet": random.randint(0, 14 - self.cardGame.currentRound)}]
            }
        }
    
    def receive_share_bet(self, data):
        for player in data['bets']:
            self.cardGame.players[player['player']].set_prediction(player['bet'])
        
    def send_share_bet(self, data):
        for player in data['bets']:
            player['bet'] = self.cardGame.players[player['player']].prediction

        return {
            "type": "share_bet",
            "data": {
                "bets": data['bets']
            }
        }
    
    def receive_play_round(self, data):
        if len(data['table']) == 0:
            print(f"--- Rodada {self.cardGame.currentRound} ---")
        
        # if is the last player to play, update the number of plays
        if len(data['table']) == len(self.cardGame.players):
            for player in data['table']:
                if player['player'] == self.me:
                    continue

                self.cardGame.players[player['player']].drop_card(player['card'])
        
    def send_play_round(self, data={"table": []}):
        # append my card
        return {
            "type": "play_round",
            "data": {
                "table": data['table'] + [{"player": self.me, "card": self.cardGame.players[self.me].drop_card()}]
            }
        }
    
    def receive_update_round(self, data):
        self.cardGame.players[data['winner']].roundsWonCount += 1

        for player in data['table']:
            if player['card'] in self.cardGame.players[player['player']].cards:
                self.cardGame.players[player['player']].drop_card(player['card'], should_pop=True)

        # print(f"Vencedor: {data[f'winner']}")

    
    def send_update_round(self):
        mesa = []
        for jogador in self.cardGame.players.values():
            carta = jogador.drop_card(should_pop=True)
            mesa.append((jogador, carta))
            
        vencedor = max(mesa, key=lambda x: self.cardGame.calculate_card_value(x[1]))  # Determina a maior carta
        # vencedor[0].roundsWonCount += 1
        
        return {
            "type": "update_round",
            "data": {
                "winner": vencedor[0].name,
                "table": [{"player": jogador.name, "card": carta} for jogador, carta in mesa]
            }
        }

    def receive_update_results(self, data):
        for player in data['results']:
            self.cardGame.players[player['player']].lifeCount = player['lives']
            self.cardGame.players[player['player']].roundsWonCount = 0
        
        self.cardGame.currentRound += 1
        
    def send_update_results(self):
        for jogador in self.cardGame.players.values():
            jogador.updateLifeCount()

        return {
            "type": "update_results",
            "data": {
                "results": [{"player": jogador.name, "lives": jogador.lifeCount} for jogador in self.cardGame.players.values()]
            }
        }

    def receive_end(self, data):
        print(f"Vencedor: {data['winner']}")
    
    def send_end(self):
        return {
            "type": "end",
            "data": {
                "winner": self.cardGame.get_winner().name
            }
        }

    def receive_change_card_dealer(self):
        self.is_dealer = True
        self.baralho = Deck()

    def send_change_card_dealer(self):
        self.is_dealer = False
        self.baralho = Deck()
        return {
            "type": "change_card_dealer"
        }

# Initialize players
players = ["Alice", "Bob", "Charlie"]
alice = MessageHandler(players, "Alice", is_dealer=True)
bob = MessageHandler(players, "Bob")
charlie = MessageHandler(players, "Charlie")


i = 0
while True:
    # # Distribute cards
    distribution = alice.send_distribution()

    bob.receive_distribution(distribution['data'])
    charlie.receive_distribution(distribution['data'])
    alice.receive_distribution(distribution['data'])

    # Bet
    bet = alice.send_bet()
    bob.receive_bet(bet['data'])
    bet = bob.send_bet(bet['data'])
    charlie.receive_bet(bet['data'])
    bet = charlie.send_bet(bet['data'])
    alice.receive_bet(bet['data'])

    # # Share bet
    share_bet = alice.send_share_bet(bet['data'])
    bob.receive_share_bet(share_bet['data'])
    charlie.receive_share_bet(share_bet['data'])
    print('share_bet', share_bet['data'])


    for _ in range(13-i):
        # Play round
        play_round = alice.send_play_round()
        bob.receive_play_round(play_round['data'])
        play_round = bob.send_play_round(play_round['data'])
        charlie.receive_play_round(play_round['data'])
        play_round = charlie.send_play_round(play_round['data'])
        alice.receive_play_round(play_round['data'])

        # # Update round
        update_round = alice.send_update_round()
        bob.receive_update_round(update_round['data'])
        charlie.receive_update_round(update_round['data'])
        alice.receive_update_round(update_round['data'])
        
        print('update_round', update_round['data'])

    # # Update results
    update_results = alice.send_update_results()
    bob.receive_update_results(update_results['data'])
    charlie.receive_update_results(update_results['data'])
    alice.receive_update_results(update_results['data'])
    print('update_results', update_results)

    if alice.cardGame.is_game_over():
        print('winner: ', alice.cardGame.get_winner())
        break


    i += 1
    


print('-=' * 20)
print(alice.cardGame.players)
print('-=' * 20)
print(bob.cardGame.players)
print('-=' * 20)
print(charlie.cardGame.players)
print('-=' * 20)

