import socket
import random

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
    
    def get_gato(self):
        return self.cards.pop()

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

class Node:
    def __init__(self, address, next_address):
        self.address = address
        self.next_address = next_address

        # socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.address)

def playerDead(Player):
    if Player.lifeCount <= 0:
        return True

def terminouJogo(players):
    if len(players) == 1 or len(players) == 0:
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

def receiveBets(node, players, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, apostas, player_d = msg.split(":")
        if tip == "fala_apostas":
            if not playerDead(player_local):
                lista_apostas = apostas.split(" ")
                for i in range(len(players)):
                    players[i].set_prediction(lista_apostas[i])
                print("As apostas dos jogadores são: ")
                print(apostas)
            node.sock.sendto(msg.encode(), node.next_address)
            break

def sendBetsNonDealer(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, apostas, player_d = msg.split(":")
        if tip == "aposta":
            if not playerDead(player_local):
                bet = input("Digite suas apostas: ")
                bets = apostas + " " + bet
                frame = f"{tip}:{bets}:{player_d}"
                node.sock.sendto(frame.encode(), node.next_address)
            else:
                node.sock.sendto(msg.encode(), node.next_address)
            break

def send_cards(node, cards, player_dest):
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

def sendFimDeJogo(node, player_local, winner_name):
    tipo = "fim_de_jogo"
    player_dest = player_local.name
    imprimeVencedorJogo(player_local, winner_name)
    frame = f"{tipo}:{winner_name}:{player_dest}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, winner_name, player_d = msg.split(":")
        if player_d == player_local.name:
            break

def listen_cards(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, data, player_d = msg.split(":")

        if tip == "cards":
            if not playerDead(player_local):
                if player_d == player_local.name:
                    cards_str = data
                    cards = cards_str.split(" ")
                    player_local.set_cards(cards)
                    node.sock.sendto(msg.encode(), node.next_address)
                else:
                    node.sock.sendto(msg.encode(), node.next_address)
            else:
                node.sock.sendto(msg.encode(), node.next_address)
        elif tip == "confirmation":
            node.sock.sendto(msg.encode(), node.next_address)
            break
        elif tip == "fim_de_jogo":
            winner_name = data
            imprimeVencedorJogo(player_local, winner_name)
            node.sock.sendto(msg.encode(), node.next_address)
            exit(0)

def receiveFimDeJogo(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, winner_name, player_d = msg.split(":")
        if tip == "fim_de_jogo":
            imprimeVencedorJogo(player_local, winner_name)
            node.sock.sendto(msg.encode(), node.next_address)
            break

def throwCardDealer(node, player_local, players, gato):
    tipo = "throw_cards"
    player_dest = player_local.name
    frame = f"{tipo}:{player_dest}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, cards, player_d = msg.split(":")
        if player_d == player_local.name:
            break
    print("Cartas jogadas:")
    print(cards)
    imprimeCartas(player_local)
    card_index = int(input("Digite o indice da carta que voce quer usar: "))
    while card_index > len(player_local.cards):
        print("Indice inválido, por favor digite um número válido")
        card_index = int(input("Digite o indice da carta que voce quer usar: "))
    chosen_card = player_local.cards[card_index-1]
    chosen_card = player_local.drop_card(chosen_card, True)
    cards = cards + " " + chosen_card
    sendRoundResults(node, player_local, cards, players, gato)

def throwCardNonDealer(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        if not playerDead(player_local):
            if player_local.name == players[1].name:
                tip, player_d = msg.split(":")
                if tip == "throw_cards":
                    imprimeCartas(player_local)
                    card_index = int(input("Digite o indice da carta que voce quer usar: "))
                    while(card_index > len(player_local.cards)):
                        print("Indice inválido, por favor digite um número válido")
                        card_index = int(input("Digite o indice da carta que voce quer usar: "))
                    chosen_card = player_local.cards[card_index-1]
                    chosen_card = player_local.drop_card(chosen_card, True)
                    frame = f"{tip}:{chosen_card}:{player_d}"
                    node.sock.sendto(frame.encode(), node.next_address)
                    break
            else:
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
        else:
            node.sock.sendto(msg.encode(), node.next_address)
        break

def calculate_card_value(card, gato):
    card_value = card[:-1]
    cardSuit = card[-1:]
    gato_value = gato[:-1]
    index_gato = Deck.cardValues.index(gato_value)
    if index_gato == 9:
        index_gato = 0
    else:
        index_gato += 1
    gato_value = Deck.cardValues[index_gato]
    if card_value == gato_value:
        return 12 * 10 + Deck.cardSuits.index(cardSuit)
    else:
        return Deck.cardValues.index(card_value) * 10 + Deck.cardSuits.index(cardSuit)

def calculate_round_winner(thrown_cards, gato):
    thrown_cards_list = thrown_cards.split(" ")
    max_card = thrown_cards_list[0]
    max_card_value = calculate_card_value(thrown_cards_list[0], gato)
    for card in thrown_cards_list:
        card_value = calculate_card_value(card, gato)
        if card_value > max_card_value:
            max_card = card
            max_card_value = card_value
    return thrown_cards_list.index(max_card)

def sendRoundResults(node, player_local, thrown_cards, players, gato):
    print("Cartas jogadas na rodada foram:")
    print(thrown_cards)
    winner_card_index = calculate_round_winner(thrown_cards, gato)
    winner = players[winner_card_index]
    winner.roundsWonCount += 1

    print(f"O vencedor da rodada foi: {winner.name}")

    tipo = "round_results"
    frame = f"{tipo}:{winner.name}:{thrown_cards}:{player_local.name}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, winner_name, thrown_cards, player_d = msg.split(":")
        if player_d == player_local.name:
            break

def receiveRoundResults(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, winner_name, thrown_cards, player_d = msg.split(":")
        if tip == "round_results":
            node.sock.sendto(msg.encode(), node.next_address)
            break
    if not playerDead(player_local):
        print("Cartas jogadas na rodada foram:")
        print(thrown_cards)
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

def receiveHandResults(node, players, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, rounds_won, player_d = msg.split(":")
        if tip == "hand_results":
            if not playerDead(player_local):
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

def eliminateDeadPlayers(players):
    players_aux = []
    for player in players:
        if not playerDead(player):
            players_aux.append(player)
    return players_aux

def organizeOrder(players, player_dealer, player_local):
    players = eliminateDeadPlayers(players)
    if not playerDead(player_local):
        print("Jogadores vivos:")
        for player in players:
            print(player.name)
    players_aux = []
    if len(players) == 2 and players[0].name == player_dealer.name:
        players_aux.append(players[1])
        players_aux.append(players[0])
        return players_aux
    if len(players) == 3 and players[0].name == player_dealer.name:
        players_aux.append(players[1])
        players_aux.append(players[2])
        players_aux.append(players[0])
        return players_aux
    if len(players) == 4:
        players_aux.append(players[1])
        players_aux.append(players[2])
        players_aux.append(players[3])
        players_aux.append(players[0])
        return players_aux
    return players

def sendBastao(node, player_local, player_dest):
    tipo = "bastao"
    data = "1"
    frame = f"{tipo}:{data}:{player_dest}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, dat, player_d = msg.split(":")
        if player_d == player_dest:
            break
    player_local.isDealer = False
    print(f"O bastão foi passado para o jogador {player_dest}")

def receiveBastao(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, dat, player_d = msg.split(":")
        if tip == "bastao":
            if not playerDead(player_local):
                if player_d == player_local.name:
                    player_local.isDealer = True
                    print(f"O bastão foi passado para você")
                else:
                    print(f"O bastão foi passado para o jogador {player_d}")
            node.sock.sendto(msg.encode(), node.next_address)
            break
        if tip == "fim_de_jogo":
            winner_name = dat
            imprimeVencedorJogo(player_local, winner_name)
            node.sock.sendto(msg.encode(), node.next_address)
            exit(0)

def imprimeDeadPlayers(players):
    for player in players:
        if playerDead(player):
            print(f"O jogador {player.name} está morto")

def vencedorJogo(players):
    for player in players:
        if player.lifeCount > 0:
            return player.name
    return None

def imprimeVencedorJogo(player_local, winner_name):
    if winner_name == 'N':
        print("O jogo terminou em empate!")
    else:
        if winner_name == player_local.name:
            print("Você venceu o jogo!")
        else:
            print(f"O jogador {winner_name} venceu o jogo!")

def sendGato(node, gato, player_local):
    tipo = "gato"
    print(f"A carta virada é: {gato}")
    frame = f"{tipo}:{gato}:{player_local.name}"
    node.sock.sendto(frame.encode(), node.next_address)

    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, gato, player_d = msg.split(":")
        if player_d == player_local.name:
            break

def receiveGato(node, player_local):
    while True:
        data, addr = node.sock.recvfrom(1024)
        msg = data.decode()
        tip, gato, player_d = msg.split(":")
        if tip == "gato":
            if not playerDead(player_local):
                print(f"A carta virada é: {gato}")
            node.sock.sendto(msg.encode(), node.next_address)
            break

if __name__ == "__main__":
    player_letter = input()
    from_ip = input("")
    port = int(input(""))
    ip = input("")
    next_port = int(input(""))

    if player_letter == 'A':
        print("Voce comeca com o bastao")
    else:
        print("Voce não comeca com o bastao")
    
    if from_ip == "":
        from_ip = socket.gethostbyname(socket.gethostname())
    
    node = Node((from_ip, port), (ip, next_port))
    
    Player_A = Player('A')
    Player_B = Player('B')
    Player_C = Player('C')
    Player_D = Player('D')
    Player_A.set_dealer(True)
    Player_local = criaPlayerLocal(Player_A, Player_B, Player_C, Player_D, player_letter)
    Player_dealer = Player_A

    players = [Player_A, Player_B, Player_C, Player_D]

    cardNum = 4
    cardNumRound = cardNum

    while not terminouJogo(players):
        if Player_local.isDealer:
            deck = Deck()
            hands = deck.deal_cards(len(players), cardNum)
            gato = deck.get_gato()
            enviaTodasAsCartas(hands, node, Player_local, players)
        else:
            listen_cards(node, Player_local)
        if Player_local.isDealer:
            sendGato(node, gato, Player_local)
        else:
            receiveGato(node, Player_local)
        if not playerDead(Player_local):
            imprimeCartas(Player_local)
        if Player_local.isDealer:
            sendBetsDealer(node, Player_local, players)
        else:
            sendBetsNonDealer(node, Player_local)
            receiveBets(node, players, Player_local)
        while cardNumRound != 0:
            if Player_local.isDealer:
                throwCardDealer(node, Player_local, players, gato)
            else:
                throwCardNonDealer(node, Player_local)
                receiveRoundResults(node, Player_local)
            cardNumRound -= 1
        if Player_local.isDealer:
            sendHandResults(node, players, Player_local)
        else:
            receiveHandResults(node, players, Player_local)
        for player in players:
            player.updateLifeCount()
        if not playerDead(Player_local):
            imprimeVida(players)
            imprimeDeadPlayers(players)
        if playerDead(Player_local):
            print("Você está morto, espere o jogo acabar")
        players = organizeOrder(players, Player_dealer, Player_local)
        if terminouJogo(players):
            break
        Player_dealer = players[0]
        if Player_local.isDealer:
            sendBastao(node, Player_local, players[0].name)
        else:
            receiveBastao(node, Player_local)
        if cardNum == 1:
            cardNum = 4
        else:
            cardNum -= 1
        cardNumRound = cardNum
    
    winner = vencedorJogo(players)
    if winner == None:
        winner = 'N'
    if Player_local.isDealer:
        sendFimDeJogo(node, Player_local, winner)
    else:
        receiveFimDeJogo(node, Player_local)