# Projeto 9 - Blockchain: Estrutura, Prova de Trabalho e Detecção de Adulteração

Criptografia Aplicada - Especialização Lato Sensu

## Requisitos

- Python 3.10 ou superior (usa apenas a biblioteca padrão: `hashlib`, `json`, `time`)
- Opcional: `matplotlib` para gerar o gráfico (`pip install matplotlib`)

## Arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `blockchain.py` | Classes `Block` e `Blockchain`: hash SHA-256, mineração (PoW) e validação da cadeia |
| `experimento_mineracao.py` | Mede o tempo médio de mineração por dificuldade e gera CSV + gráfico |
| `demo_adulteracao.py` | Demonstra cadeia válida vs. adulterada em 4 cenários, indicando o bloco afetado |
| `saida_*.txt`, `resultados_mineracao.csv`, `grafico_mineracao.png` | Saídas obtidas pela equipe |

## Como executar

```bash
# Demonstração de detecção de adulteração (~10 s)
python3 demo_adulteracao.py

# Experimento de tempos de mineração, dificuldades 2 a 5 (~3 min)
python3 experimento_mineracao.py

# Variações
python3 experimento_mineracao.py --dificuldades 3 4 5 --blocos 10
python3 experimento_mineracao.py --dificuldades 6 --blocos 3     # ~2 min por bloco
```

## Uso como biblioteca

```python
from blockchain import Blockchain

bc = Blockchain(difficulty=4)
bc.add_block([{"de": "Alice", "para": "Bob", "valor": 10}])
print(bc.validate())                  # (True, [])

bc.chain[1].data[0]["valor"] = 999    # adulteração
print(bc.validate())                  # (False, ['Bloco 1: hash armazenado ...'])
print(bc.first_invalid_block())       # 1
```
