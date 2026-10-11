"""
Demonstração de detecção de adulteração.

Uso:
    python3 demo_adulteracao.py

Cenários:
  1. Cadeia íntegra -> validação OK.
  2. Atacante altera os dados do bloco 2 sem recalcular nada
     -> detectado no bloco 2 (hash não confere).
  3. Atacante altera o bloco 2 e recalcula só o hash dele (sem PoW)
     -> detectado no bloco 2 (PoW inválida) e no bloco 3 (elo quebrado).
  4. Atacante altera o bloco 2 e REMINERA o bloco 2 e todos os seguintes
     -> cadeia passa na validação local; só o consenso (comparar com a
        cadeia dos outros nós / custo da PoW) protege. Mostra o custo.
"""

import copy
import time

from blockchain import Blockchain

DIFICULDADE = 4
SEP = "=" * 78


def build_chain() -> Blockchain:
    bc = Blockchain(difficulty=DIFICULDADE)
    txs = [
        [{"de": "Alice", "para": "Bob", "valor": 50}],
        [{"de": "Bob", "para": "Carol", "valor": 20}],
        [{"de": "Carol", "para": "Dave", "valor": 5}],
        [{"de": "Dave", "para": "Alice", "valor": 2}],
    ]
    for t in txs:
        bc.add_block(t)
    return bc


def report(bc: Blockchain, title: str) -> None:
    print(f"\n{SEP}\n{title}\n{SEP}")
    bc.print_chain()
    ok, problems = bc.validate()
    if ok:
        print("\n  RESULTADO: cadeia VÁLIDA")
    else:
        print(f"\n  RESULTADO: cadeia INVÁLIDA - adulteração detectada no bloco "
              f"{bc.first_invalid_block()}")
        for p in problems:
            print(f"    - {p}")


def main():
    print(f"Construindo cadeia com dificuldade {DIFICULDADE} (gênesis + 4 blocos)...")
    original = build_chain()

    # Cenário 1
    report(original, "CENÁRIO 1: cadeia original")

    # Cenário 2: altera dados sem recalcular hash
    c2 = copy.deepcopy(original)
    c2.chain[2].data[0]["valor"] = 2000   # Bob -> Carol: 20 vira 2000
    report(c2, "CENÁRIO 2: valor do bloco 2 alterado de 20 para 2000 (sem recalcular hashes)")

    # Cenário 3: altera e recalcula o hash do bloco adulterado (sem minerar)
    c3 = copy.deepcopy(original)
    c3.chain[2].data[0]["valor"] = 2000
    c3.chain[2].hash = c3.chain[2].compute_hash()
    report(c3, "CENÁRIO 3: bloco 2 alterado e seu hash recalculado (sem prova de trabalho)")

    # Cenário 4: altera e reminera bloco 2 em diante
    c4 = copy.deepcopy(original)
    c4.chain[2].data[0]["valor"] = 2000
    t0 = time.perf_counter()
    total_attempts = 0
    for i in range(2, len(c4.chain)):
        c4.chain[i].previous_hash = c4.chain[i - 1].hash
        total_attempts += c4.chain[i].mine()
    elapsed = time.perf_counter() - t0
    report(c4, "CENÁRIO 4: bloco 2 alterado e blocos 2..4 reminerados pelo atacante")
    print(f"\n  Custo do ataque: {total_attempts:,} hashes em {elapsed:.2f} s "
          f"para reescrever {len(c4.chain) - 2} blocos.")
    print(f"  Hash do último bloco original : {original.last_block.hash}")
    print(f"  Hash do último bloco adulterado: {c4.last_block.hash}")
    print("  -> Os hashes finais diferem: quem guarda o hash 'oficial' do topo da cadeia")
    print("     (ou compara com os outros nós) ainda detecta a fraude. Em uma rede real,")
    print("     o atacante teria de superar o poder de mineração de toda a rede honesta.")


if __name__ == "__main__":
    main()
