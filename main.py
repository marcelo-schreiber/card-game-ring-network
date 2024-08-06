import socket
import random
from time import sleep

class Deck:
    cardSuits = ['♦', '♠', '♥', '♣']
    cardValues = ['4', '5', '6', '7', 'J', 'Q', 'K', 'A', '2', '3']

    def __init__(self):
        self.cards = [f"{valor}{naipe}" for valor in self.cardValues for naipe in self.cardSuits]
        #duplica o baralho
        self.cards += [f"{valor}{naipe}" for valor in self.cardValues for naipe in self.cardSuits]
        random.shuffle(self.cards)

    def deal_cards(self, player_count, card_count):
        player_hands = [[] for _ in range(player_count)]
        for _ in range(card_count):
            for j in range(len(players)):
                if self.cards:
                    player_hands[j].append(self.cards.pop())

        return player_hands

class Player:
    def __init__(self, name):
        self.name = name
        self.lifeCount = 12
        self.cards = []
        self.prediction = 0
        self.roundsWonCount = 0
        self.isDealer = False

    def set_cards(self, cards):
        self.cards = cards

    def set_prediction(self, prediction):
        self.prediction = int(prediction)

    def set_dealer(self, isDealer):
        self.isDealer = isDealer

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
        return f"Nome: {self.name}, Cartas: {self.cards}, lifeCount: {self.lifeCount}, Palpite: {self.prediction}, Jogadas feitas: {self.roundsWonCount}"

class Node:
    def __init__(self, address, next_address, has_token=False):
        self.address = address
        self.next_address = next_address
        self.has_token = has_token

        # socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)

    def send_data(self, message, player_dest):
        if not self.has_token and not frame:
            return            
        port_to_send_to = self.next_address[1]
        port_from = self.address[1]
        frame = f"{port_from}:{port_to_send_to}:{message}:{player_dest}"

        self.sock.sendto(frame.encode(), self.next_address)

    def send_token(self):
        self.has_token = False
        self.sock.sendto("TOKEN".encode(), self.next_address)


def player_dead(Player):
    if Player.lifeCount == 0:
        return True

def terminouJogo(players):
    if player_dead(players[0]) and player_dead(players[1]) and player_dead(players[2]) and player_dead(players[3]):
        print("Ninguem venceu")
        return True
    if player_dead(players[0]) and player_dead(players[1]) and player_dead(players[2]):
        print("Player D venceu")
        return True
    if player_dead(players[0]) and player_dead(players[1]) and player_dead(players[3]):
        print("Player C venceu")
        return True
    if player_dead(players[0]) and player_dead(players[2]) and player_dead(players[3]):
        print("Player B venceu")
        return True
    if player_dead(players[1]) and player_dead(players[2]) and player_dead(players[3]):
        print("Player A venceu")
        return True

def criaPlayerLocal(Player_A, Player_B, Player_C, Player_D, player_letter):
    if player_letter == 'A':
        Player_local = Player_A
    elif player_letter == 'B':
        Player_local = Player_B
    elif player_letter == 'C':
        Player_local = Player_C
    else:
        Player_local = Player_D
    return Player_local

def send_token(node):
    node.has_token = False
    node.sock.sendto("TOKEN".encode(), node.next_address)

def send_confirmation(node, player_dest):
    tipo = "confirmation"
    confirmation = "1"
    frame = f"{tipo}:{confirmation}:{player_dest}"
    node.sock.sendto(frame.encode(), node.next_address)
    
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, confirm, player_d = msg.split(":")
        if player_dest == player_d:
            break

def sendBetsDealer(node, player_local, players):
    tipo = "aposta"
    apostas = input("Digite suas apostas: ")
    
    player_dest = player_local.name
    frame = f"{tipo}:{apostas}:{player_dest}"
    node.sock.sendto(frame.encode(), node.next_address)
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, apostas, player_d = msg.split(":")
        if tip == "aposta":
            if player_d == player_local.name:
                break
    apostas_list = apostas.split(" ")
    for i in range(len(players)):
        players[i].set_prediction(apostas_list[i])

    tellBets(node, apostas, player_local, players)

def tellBets(node, apostas, player_local, players):
    print("As apostas dos jogadores são: ")
    print(apostas)
    lista_apostas = apostas.split(" ")
    for i in range(len(lista_apostas)):
        players[i].set_prediction(lista_apostas[i])
    tipo = "fala_apostas"
    player_dist = player_local.name
    frame = f"{tipo}:{apostas}:{player_dist}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, bets, player_d = msg.split(":")
        if player_d == player_local.name:
            break

def receiveBets(node, players):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, apostas, player_d = msg.split(":")
        if tip == "fala_apostas":
            lista_apostas = apostas.split(" ")
            for i in range(len(players)):
                players[i].set_prediction(lista_apostas[i])
            print("As apostas dos jogadores são: ")
            print(apostas)
            node.sock.sendto(msg.encode(), node.next_address)
            break


def sendBetsNonDealer(node):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, apostas, player_d = msg.split(":")
        if tip == "aposta":
            bet = input("Digite suas apostas: ")
            bets = apostas + " " + bet
            frame = f"{tip}:{bets}:{player_d}"
            node.sock.sendto(frame.encode(), node.next_address)
            break

def send_cards(node, cards, player_dest):
    if not node.has_token:
            return
    
    tipo = "cards"
    cards_str = " ".join(cards)
    frame = f"{tipo}:{cards_str}:{player_dest}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, cards, player_d = msg.split(":")
        if player_dest == player_d:
            break

def enviaTodasAsCartas(hands, node, player_local, players):
    for i in range(len(players)):
        if players[i].name == player_local.name:
            player_local.set_cards(hands[i])
            continue
        else:
            send_cards(node, hands[i], players[i].name)
    send_confirmation(node, player_local.name)

def listen_cards_or_dealer_change(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        if msg == "TOKEN":
            node.has_token = True
            player_local.set_dealer(True)
            break

        tip, cards_str, player_d = msg.split(":")
            

        if tip == "cards":
            if player_d == player_local.name:
                cards = cards_str.split(" ")
                player_local.set_cards(cards)
                node.sock.sendto(msg.encode(), node.next_address)
            else:
                node.sock.sendto(msg.encode(), node.next_address)
        elif tip == "confirmation":
            node.sock.sendto(msg.encode(), node.next_address)
            break

def throwCardDealer(node, player_local, players):
    tipo = "throw_cards"
    imprimeCartas(player_local)
    card_index = int(input("Digite o indice da carta que voce quer usar: "))
    while card_index > len(player_local.cards):
        print("Indice inválido, por favor digite um número válido")
        card_index = int(input("Digite o indice da carta que voce quer usar: "))
    chosen_card = player_local.cards[card_index-1]
    chosen_card = player_local.drop_card(chosen_card, True)
    player_dest = player_local.name
    frame = f"{tipo}:{chosen_card}:{player_dest}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, cards, player_d = msg.split(":")
        if player_d == player_local.name:
            break
    print("Cartas jogadas: ")
    print(cards)
    sendRoundResults(node, player_local, cards, players)

def throwCardNonDealer(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, cards, player_d = msg.split(":")
        if tip == "throw_cards":
            print("Cartas jogadas: ")
            print(cards)
            imprimeCartas(player_local)
            card_index = int(input("Digite o indice da carta que voce quer usar: "))
            while(card_index > len(player_local.cards)):
                print("Indice inválido, por favor digite um número válido")
                card_index = int(input("Digite o indice da carta que voce quer usar: "))
            chosen_card = player_local.cards[card_index-1]
            chosen_card = player_local.drop_card(chosen_card, True)
            new_cards = cards + " " + chosen_card
            frame = f"{tip}:{new_cards}:{player_d}"
            node.sock.sendto(frame.encode(), node.next_address)
            break


def calculate_card_value(card):
    card_value = card[:-1]
    cardSuit = card[-1:]
    return Deck.cardValues.index(card_value) * 10 + Deck.cardSuits.index(cardSuit)

def calculate_round_winner(thrown_cards):
    thrown_cards = thrown_cards.split(" ")
    max_card = thrown_cards[0]
    max_card_value = calculate_card_value(thrown_cards[0])
    for card in thrown_cards:
        card_value = calculate_card_value(card)
        if card_value > max_card_value:
            max_card = card
            max_card_value = card_value
    return thrown_cards.index(max_card)

def sendRoundResults(node, player_local, thrown_cards, players):
    winner_card_index = calculate_round_winner(thrown_cards)
    winner = players[winner_card_index]
    winner.roundsWonCount += 1

    print(f"O vencedor da rodada foi: {winner.name}")

    tipo = "round_results"
    frame = f"{tipo}:{winner.name}:{player_local.name}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, winner, player_d = msg.split(":")
        if player_d == player_local.name:
            break

def receiveRoundResults(node, players):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, winner_name, player_d = msg.split(":")
        if tip == "round_results":
            node.sock.sendto(msg.encode(), node.next_address)
            break
    print(f"O vencedor da rodada foi: {winner_name}")

def sendHandResults(node, players, player_local):
    tipo = "hand_results"
    rounds_won = " ".join([f"{player.roundsWonCount}" for player in players])
    imprimeRoundsVencidas(players)
    frame = f"{tipo}:{rounds_won}:{player_local.name}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, players, player_d = msg.split(":")
        if player_d == player_local.name:
            break

def imprimeRoundsVencidas(players):
    for player in players:
        print(f"O jogador {player.name} venceu {player.roundsWonCount} rodadas")

def receiveHandResults(node, players):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, rounds_won, player_d = msg.split(":")
        if tip == "hand_results":
            rounds_won_list = rounds_won.split(" ")
            for i in range(len(players)):
                players[i].roundsWonCount = int(rounds_won_list[i])
            imprimeRoundsVencidas(players)
            node.sock.sendto(msg.encode(), node.next_address)
            break

def imprimeCartas(player):
    print(f"Suas cartas são: {player.cards}")

def imprimeVida(players):
    for player in players:
        print(f"O jogador {player.name} tem {player.lifeCount} vidas")

if __name__ == "__main__":
    player_letter = input()
    from_ip = input("")
    port = int(input(""))
    ip = input("")
    next_port = int(input(""))

    if player_letter == 'A':
        has_token = True
        print("You are the dealer")
    else:
        has_token = False
        print("You are not the dealer")
    
    if from_ip == "":
        from_ip = socket.gethostbyname(socket.gethostname())
    
    node = Node((from_ip, port), (ip, next_port), has_token)
    
    Player_A = Player('A')
    Player_B = Player('B')
    Player_C = Player('C')
    Player_D = Player('D')
    Player_A.set_dealer(True)
    Player_local = criaPlayerLocal(Player_A, Player_B, Player_C, Player_D, player_letter)

    players = [Player_A, Player_B, Player_C, Player_D]

    cardNum = 2

    while not terminouJogo(players):
        if Player_local.isDealer:
            deck = Deck()
            hands = deck.deal_cards(len(players), cardNum)
            enviaTodasAsCartas(hands, node, Player_local, players)
        else:
            listen_cards_or_dealer_change(node, Player_local)
            if Player_local.isDealer: # se o dealer mudou
                continue # volta pro começo do loop

        imprimeCartas(Player_local)

        if Player_local.isDealer:
            sendBetsDealer(node, Player_local, players)
        else:
            sendBetsNonDealer(node)
            receiveBets(node, players)

        while len(Player_local.cards) != 0:
            if Player_local.isDealer:
                throwCardDealer(node, Player_local, players)
            else:
                throwCardNonDealer(node, Player_local)
                receiveRoundResults(node, players)

        if Player_local.isDealer:
            sendHandResults(node, players, Player_local)
        else:
            receiveHandResults(node, players)

        for player in players:
            player.updateLifeCount()

        imprimeVida(players)

        if Player_local.isDealer:
            sleep(0.1) # espera para que o proximo jogador esteja pronto
            send_token(node)      
            Player_local.set_dealer(False)  
        
        # set the dealer for all instances
        if cardNum == 1:
            cardNum = 4
        else:
            cardNum -= 1




    #loop da mão, acaba quando as cartas acabarem   

    #começa a rodada
    
    #dealer envia mensagem para que os jogadores adicionem suas cartas

    #o primeiro a adicionar carta é o jogador a direita do dealer

    #quando a mensagem chegar no dealer, ele computa os resultados da rodada e envia uma mensagem para a rede

    #resultados da rodada: quem fez a rodada

    #cada máquina recebe a mensagem, atualiza as váriaveis de controle,
    #imprime os resultados na tela e envia para a próxima máquina

    #se tem cartas, continua o loop da mão
    #se não tem cartas, acaba o loop da mão

    #atualiza as váriaveis de controle(lifeCount)
    #envia mensagem para a rede contendo as lifeCount de cada jogador

    #se num_cartas == 1, passa a ser 13
    #se não for, reduz em uma carta

    #se a máquina da direita do dealer estiver viva, ela se torna o novo dealer
    #se não, a máquina da direita dela se torna o novo dealer, e assim por diante