# parimpar/par_impar.py

from random import randint

class ParImpar:
    def __init__(self, nome, n):
        self.nome = nome
        self.n = n

    def gerar(self):
        return randint(0, 999)  # Gera um número aleatório de 0 a 999

    def vencedor(self):
        computador = self.gerar()
        total = computador + self.n
        if total % 2 == 0:
            return f"{self.nome} venceu! O total foi par."
        else:
            return f"O computador venceu! O total foi ímpar."

    def exibir_resultado(self):
        if self.n % 2 == 0:
            print("O número que você digitou é par.")
        else:
            print("O número que você digitou é ímpar.")
