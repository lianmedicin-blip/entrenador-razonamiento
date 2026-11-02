"""Exporta un banco de preguntas de figuras (verificadas por examen.py) a JSON compacto para la app web."""
import json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import examen as E

POR_NIVEL = int(sys.argv[1]) if len(sys.argv) > 1 else 150
OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'bank')

def celda(tipo, c):
    if c is None: return None
    if tipo == 'rotacion': return [c['ang'], c['pos'], c['col']]
    if tipo == 'domino': return [c['arriba'], c['abajo']]
    if tipo == 'superposicion': return sorted(c['puntos'])
    return [c['forma'], c['cantidad'], c['tamano'], c['color']]

def stem(tipo, q):
    s = q['stem']
    if tipo == 'matriz':
        m = s['matriz']; return [[celda(tipo, m[r][k]) if (r, k) != (2, 2) else None for k in range(3)] for r in range(3)]
    if tipo == 'superposicion': return {'g': [[celda(tipo, c) for c in row] for row in s['dots']], 'n': s['n']}
    if tipo == 'serie': return [celda(tipo, c) for c in s['serie']]
    if tipo == 'rotacion': return [celda(tipo, c) for c in s['rot']]
    if tipo == 'domino': return [celda(tipo, c) for c in s['dom']]
    if tipo == 'analogia': return [celda(tipo, c) for c in s['abc']]
    return None

def main():
    rng = random.Random(20261102)
    for tipo, gen in E.GENERADORES.items():
        items, vistos = [], set()
        for nivel in ['F', 'M', 'D', 'MD']:
            k, intentos = 0, 0
            while k < POR_NIVEL and intentos < POR_NIVEL * 6:
                intentos += 1
                try: q = gen(nivel, rng)
                except E.Fallo: continue
                st = stem(tipo, q); op = [celda(tipo, o) for o in q['opciones']]
                key = json.dumps([st, op])
                if key in vistos: continue
                # verificación de unicidad
                if q['valida'] is not None:
                    ok = [i for i, o in enumerate(q['opciones']) if q['valida'](o)]
                    assert ok == [0], (tipo, nivel, ok)
                vistos.add(key)
                fallos = q.get('fallos') or [None] + [q['regla']] * 4
                if tipo == 'intrusa':
                    q['explicacion'] = [x.replace('La figura correcta', 'La figura que no pertenece') for x in q['explicacion']]
                it = {'i': f"{tipo[:3]}{nivel}{k}", 't': tipo, 'n': nivel, 'r': q['regla'], 's': st, 'o': op,
                      'f': fallos, 'e': q['explicacion']}
                if q.get('trampa'): it['k'] = list(q['trampa'])
                items.append(it); k += 1
        with open(os.path.join(OUT, f'{tipo}.json'), 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, separators=(',', ':'))
        print(tipo, len(items), os.path.getsize(os.path.join(OUT, f'{tipo}.json')) // 1024, 'KB')

if __name__ == '__main__':
    main()
