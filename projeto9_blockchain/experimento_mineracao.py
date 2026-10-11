"""
Experimento: tempo médio de mineração por nível de dificuldade.

Uso:
    python3 experimento_mineracao.py                 # dificuldades 2,3,4,5 (padrão)
    python3 experimento_mineracao.py --dificuldades 3 4 5 6 --blocos 5

Para cada dificuldade minera N blocos (cada um com dados diferentes) e mede
tempo e número de tentativas. Salva resultados_mineracao.csv e, se o
matplotlib estiver instalado, grafico_mineracao.png.
"""

import argparse
import csv
import platform
import statistics

from blockchain import Blockchain

# Quantidade padrão de blocos por dificuldade (mais blocos nas fáceis,
# onde cada mineração é rápida e a variância relativa é maior).
DEFAULT_BLOCKS = {2: 50, 3: 50, 4: 30, 5: 15, 6: 5}


def run(difficulties, blocks_override=None):
    results = []
    for d in difficulties:
        n = blocks_override or DEFAULT_BLOCKS.get(d, 5)
        bc = Blockchain(difficulty=d)
        times, attempts = [], []
        for i in range(n):
            _, att, t = bc.add_block([{"de": "Alice", "para": "Bob", "valor": i + 1}])
            times.append(t)
            attempts.append(att)
        ok, _ = bc.validate()
        hashrate = sum(attempts) / sum(times)
        row = {
            "dificuldade": d,
            "blocos": n,
            "tempo_medio_s": statistics.mean(times),
            "desvio_padrao_s": statistics.stdev(times) if n > 1 else 0.0,
            "tempo_min_s": min(times),
            "tempo_max_s": max(times),
            "tentativas_medias": statistics.mean(attempts),
            "tentativas_esperadas": 16 ** d,
            "hashes_por_s": hashrate,
            "cadeia_valida": ok,
        }
        results.append(row)
        print(f"d={d}: {n} blocos | tempo médio {row['tempo_medio_s']:.4f} s "
              f"(dp {row['desvio_padrao_s']:.4f}) | tentativas médias "
              f"{row['tentativas_medias']:.0f} (esperado {16**d}) | "
              f"{hashrate:,.0f} H/s | cadeia válida: {ok}")
    return results


def save_csv(results, path="resultados_mineracao.csv"):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)
    print(f"\nResultados salvos em {path}")


def plot(results, path="grafico_mineracao.png"):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado: gráfico não gerado")
        return
    ds = [r["dificuldade"] for r in results]
    ts = [r["tempo_medio_s"] for r in results]
    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    ax.plot(ds, ts, marker="o", color="#1f6feb", linewidth=2)
    ax.set_yscale("log")
    ax.set_xticks(ds)
    ax.set_xlabel("Dificuldade (zeros hexadecimais à esquerda)")
    ax.set_ylabel("Tempo médio de mineração (s, escala log)")
    ax.set_title("Cada zero a mais multiplica o tempo por ~16")
    ax.grid(axis="y", which="major", alpha=0.3)
    for d, t in zip(ds, ts):
        ax.text(d, t * 1.6, f"{t:.4f} s" if t < 1 else f"{t:.2f} s", ha="center", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    print(f"Gráfico salvo em {path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dificuldades", type=int, nargs="+", default=[2, 3, 4, 5])
    p.add_argument("--blocos", type=int, default=None, help="blocos por dificuldade (sobrescreve o padrão)")
    args = p.parse_args()
    print(f"Python {platform.python_version()} | {platform.processor() or platform.machine()}\n")
    res = run(args.dificuldades, args.blocos)
    save_csv(res)
    plot(res)
