"""
Blockchain simplificado com prova de trabalho (PoW) - implementação do zero.

Projeto 9 - Criptografia Aplicada
Única dependência criptográfica: hashlib.sha256 da biblioteca padrão.
"""

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class Block:
    """Um bloco da cadeia.

    Campos que entram no hash: index, timestamp, data, previous_hash, nonce
    e difficulty. O campo `hash` guarda o resultado e NÃO entra no cálculo.
    """
    index: int
    timestamp: float
    data: list            # lista de "transações" (dicionários)
    previous_hash: str
    difficulty: int = 0   # número de zeros hexadecimais exigidos
    nonce: int = 0
    hash: str = field(default="")

    def header_bytes(self) -> bytes:
        """Serialização determinística dos campos protegidos pelo hash.

        json.dumps com sort_keys e separadores fixos garante que o mesmo
        conteúdo sempre gere exatamente os mesmos bytes.
        """
        content = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
        }
        return json.dumps(content, sort_keys=True, separators=(",", ":")).encode()

    def compute_hash(self) -> str:
        """SHA-256 sobre os demais campos do bloco (hex, 64 caracteres)."""
        return hashlib.sha256(self.header_bytes()).hexdigest()

    def mine(self) -> int:
        """Prova de trabalho: incrementa o nonce até o hash começar com
        `difficulty` zeros hexadecimais. Retorna o número de tentativas.

        Cada dígito hex tem 16 valores possíveis, então a chance de uma
        tentativa ser válida é 1/16^d e o número esperado de tentativas é 16^d.
        """
        target = "0" * self.difficulty
        self.nonce = 0
        attempts = 0
        while True:
            attempts += 1
            h = self.compute_hash()
            if h.startswith(target):
                self.hash = h
                return attempts
            self.nonce += 1


GENESIS_PREVIOUS_HASH = "0" * 64


class Blockchain:
    """Cadeia de blocos com mineração e validação."""

    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty
        self.chain: list[Block] = []
        self._create_genesis()

    def _create_genesis(self) -> None:
        genesis = Block(
            index=0,
            timestamp=time.time(),
            data=[{"msg": "Bloco genesis"}],
            previous_hash=GENESIS_PREVIOUS_HASH,
            difficulty=self.difficulty,
        )
        genesis.mine()
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: list) -> tuple[Block, int, float]:
        """Cria, minera e anexa um novo bloco.

        Retorna (bloco, tentativas, segundos gastos na mineração).
        """
        block = Block(
            index=self.last_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=self.last_block.hash,   # o encadeamento acontece aqui
            difficulty=self.difficulty,
        )
        t0 = time.perf_counter()
        attempts = block.mine()
        elapsed = time.perf_counter() - t0
        self.chain.append(block)
        return block, attempts, elapsed

    def validate(self) -> tuple[bool, list[str]]:
        """Valida a cadeia completa, do gênesis ao último bloco.

        Para cada bloco i são feitas três verificações:
          1. integridade: o hash armazenado é igual ao hash recalculado?
          2. encadeamento: previous_hash é igual ao hash armazenado do bloco i-1?
          3. prova de trabalho: o hash atende à dificuldade declarada?

        Retorna (válida?, lista de problemas encontrados). A lista indica
        o índice do bloco e qual verificação falhou.
        """
        problems = []
        for i, block in enumerate(self.chain):
            recomputed = block.compute_hash()
            if block.hash != recomputed:
                problems.append(
                    f"Bloco {i}: hash armazenado ({block.hash[:16]}...) difere do "
                    f"recalculado ({recomputed[:16]}...) -> conteúdo do bloco foi alterado"
                )
            if not block.hash.startswith("0" * block.difficulty):
                problems.append(
                    f"Bloco {i}: hash não atende à prova de trabalho "
                    f"({block.difficulty} zeros)"
                )
            expected_prev = GENESIS_PREVIOUS_HASH if i == 0 else self.chain[i - 1].hash
            if block.previous_hash != expected_prev:
                problems.append(
                    f"Bloco {i}: previous_hash não corresponde ao hash do bloco {i - 1} "
                    f"-> elo da cadeia quebrado"
                )
        return (len(problems) == 0, problems)

    def first_invalid_block(self) -> int | None:
        """Índice do primeiro bloco em que a validação falha (ou None)."""
        ok, problems = self.validate()
        if ok:
            return None
        return int(problems[0].split(":")[0].split()[1])

    def print_chain(self) -> None:
        for b in self.chain:
            print(f"  #{b.index}  nonce={b.nonce:<9} prev={b.previous_hash[:12]}...  "
                  f"hash={b.hash[:12]}...  data={json.dumps(b.data, ensure_ascii=False)}")
