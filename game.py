import random

class Baralho:
    naipes = ['♦', '♠', '♥', '♣']
    valores = ['4', '5', '6', '7', 'J', 'Q', 'K', 'A', '2', '3']

    def __init__(self):
        self.cartas = [f"{valor}{naipe}" for valor in self.valores for naipe in self.naipes]
        random.shuffle(self.cartas)

    def distribuir_cartas(self, num_jogadores, num_cartas):
        distribuicao = [[] for _ in range(num_jogadores)]
        for _ in range(num_cartas):
            for j in range(num_jogadores):
                if self.cartas:
                    distribuicao[j].append(self.cartas.pop())

        return distribuicao

class Jogador:
    def __init__(self, nome):
        self.nome = nome
        self.vidas = 13 # FODASE (= 6 letras)
        self.cartas = []
        self.palpite = 0
        self.jogadas_feitas = 0

    def receber_cartas(self, cartas):
        self.cartas = cartas

    def fazer_palpite(self, palpite):
        self.palpite = palpite

    def jogar_carta(self):
        if self.cartas:
            return self.cartas.pop(0)
        return None

    def atualizar_vidas(self):
        self.vidas -= abs(self.palpite - self.jogadas_feitas)
        self.jogadas_feitas = 0

    def __repr__(self):
        return f"{self.nome}: Vidas={self.vidas}, Cartas={len(self.cartas)}, Palpite={self.palpite}, Jogadas={self.jogadas_feitas}"

class Fodinha:
    def __init__(self, jogadores):
        self.jogadores = {jogador: Jogador(jogador) for jogador in jogadores}
        self.baralho = Baralho()
        self.rodada = 1

    def jogar_rodada(self):
        num_cartas = 14 - self.rodada
        distribuicao = self.baralho.distribuir_cartas(len(self.jogadores), num_cartas)

        for i, jogador in enumerate(self.jogadores.values()):
            jogador.receber_cartas(distribuicao[i])
            jogador.fazer_palpite(random.randint(0, num_cartas))  # Palpite aleatório para simulação

        print(f"--- Rodada {self.rodada} ---")
        for jogador in self.jogadores.values():
            print(jogador)

        for _ in range(num_cartas):
            mesa = []
            for jogador in self.jogadores.values():
                carta = jogador.jogar_carta()
                mesa.append((jogador, carta))
            
            if mesa:
                vencedor = max(mesa, key=lambda x: self.valor_carta(x[1]))  # Determina a maior carta
                vencedor[0].jogadas_feitas += 1
                print(f"Jogada: {[(j.nome, c) for j, c in mesa]} -> Vencedor: {vencedor[0].nome}")

        for jogador in self.jogadores.values():
            jogador.atualizar_vidas() 

        self.rodada += 1
        self.baralho = Baralho() # Embaralha o baralho para a próxima rodada

    def valor_carta(self, carta):
        valor = carta[:-1]
        naipe = carta[-1:]
        return Baralho.valores.index(valor) * 10 + Baralho.naipes.index(naipe)

    def jogo_terminado(self):
        return any(jogador.vidas <= 0 for jogador in self.jogadores.values())

    def vencedor(self):
        return max(self.jogadores.values(), key=lambda x: x.vidas)

# Simulação de um jogo
jogo = Fodinha(["Alice", "Bob", "Charlie"])

while not jogo.jogo_terminado() and jogo.rodada <= 13:
    jogo.jogar_rodada()

print("\n--- Fim do Jogo ---")
print(f"Vencedor: {jogo.vencedor().nome}")

# msgs types can be:
# 'distribution', 'bet', 'share_bet', 'play_round', 'update_round', 'update_results', 'end', 'change_card_dealer'

# JSON MESSAGES EXAMPLE
# {
#     "type": "distribution",
#     "data": {
#         "distribution": [
#             {"player": "Alice", "cards": ["4♦", "5♦", "6♦"]},
#             {"player": "Bob", "cards": ["7♦", "8♦", "9♦"]},
#             {"player": "Charlie", "cards": ["10♦", "J♦", "Q♦"]}
#         ]
#     }
# }

# {
#     "type": "bet",
#     "data": {
#         "bets": [
#             {"player": "Alice", "bet": 2},
#             {"player": "Bob", "bet": 1},
#             {"player": "Charlie", "bet": 3},
#         ]
#     }
# }

# {
#     "type": "share_bet",
#     "data": {
#         "bets": [
#             {"player": "Alice", "bet": 2},
#             {"player": "Bob", "bet": 1},
#             {"player": "Charlie", "bet": 3}
#         ]
#     }

# {
#     "type": "play_round",
#     "data": {
#         "table": [
#             {"player": "Alice", "card": "4♦"},
#             {"player": "Bob", "card": "5♦"},
#             {"player": "Charlie", "card": "6♦"}
#     }
# }

# {
#     "type": "update_round",
#     "data": {
#         "winner": "Alice",
#     }

# {
#     "type": "update_results",
#     "data": {
#         "results": [
#             {"player": "Alice", "lives": 5},
#             {"player": "Bob", "lives": 6},
#             {"player": "Charlie", "lives": 7}
#         ]
#     }

# {
#     "type": "end",
#     "data": {
#         "winner": "Charlie"
#     }

# {
#     "type": "change_card_dealer",
# }


# class MessageHandler(Fodinha):
#     def __init__(self, jogadores = ["Alice", "Bob", "Charlie"]):
#         super().__init__(jogadores)

#     # one receive and one send message for each msg type
#     def receive_distribution(self, data):
#         distribution = data['distribution']
#         for player in distribution:
#             self.jogadores[player['player']].receber_cartas(player['cards'])
        
#     def send_distribution(self):
#         distribution = Baralho().distribuir_cartas(len(self.jogadores), 14 - self.rodada)
#         for i, jogador in enumerate(self.jogadores.values()):
#             jogador.receber_cartas(distribution[i])
#         return {
#             "type": "distribution",
#             "data": {
#                 "distribution": [{"player": jogador.nome, "cards": jogador.cartas} for jogador in self.jogadores.values()]
#             }
#         }