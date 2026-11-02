"""Genera el banco de preguntas de texto/lógica para la app web (docs/bank/<tipo>.json)."""
import json, os, random, sys, time
import textgen as T

POR_NIVEL = int(sys.argv[1]) if len(sys.argv) > 1 else 120
OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'bank')
LIMITE_S = 120  # segundos máximos por tipo y nivel

def main():
    rng = random.Random(20261102)
    for tipo, gen in T.GENERADORES.items():
        items, vistos = [], set()
        for nivel in T.NIVELES:
            k, t0 = 0, time.time()
            while k < POR_NIVEL and time.time() - t0 < LIMITE_S:
                try:
                    it = gen(nivel, rng)
                except T.Fallo:
                    continue
                key = it['q'] + json.dumps(it.get('x'), ensure_ascii=False)
                if key in vistos: continue
                assert len(it['o']) == 5 and len(set(it['o'])) == 5, (tipo, it)
                vistos.add(key)
                it['i'] = f"{tipo[:4]}{nivel}{k}"
                items.append(it); k += 1
            print(tipo, nivel, k, flush=True)
        with open(os.path.join(OUT, f'{tipo}.json'), 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, separators=(',', ':'))
    av = T.banco_analogias(rng)
    for k, it in enumerate(av): it['i'] = f"verb{k}"
    with open(os.path.join(OUT, 'analogia_verbal.json'), 'w', encoding='utf-8') as f:
        json.dump(av, f, ensure_ascii=False, separators=(',', ':'))
    print('analogia_verbal', len(av))

if __name__ == '__main__':
    main()
