"""Preguntas espaciales nuevas, verificadas por código:
  espejo  – imagen en un espejo (reflexión)
  giro2d  – la misma figura girada (no reflejada)
  papel   – papel doblado y perforado: ¿cómo queda al desdoblarlo?
Las figuras viven en una cuadrícula N×N; cada celda pintada es [fila, col, color] (1 = negro, 2 = gris).
Formato de ítem igual al de textgen (o: opciones con la correcta en 0).
"""
import json, os, random, sys

class Fallo(Exception):
    pass

NIVELES = ['F', 'M', 'D', 'MD']

def norm(cells):
    return tuple(sorted(tuple(c) for c in cells))

def refl_v(cells, N):   # espejo a la derecha (eje vertical)
    return norm([(r, N - 1 - c, k) for r, c, k in cells])

def refl_h(cells, N):   # espejo abajo (eje horizontal)
    return norm([(N - 1 - r, c, k) for r, c, k in cells])

def rot90(cells, N):    # giro horario
    return norm([(c, N - 1 - r, k) for r, c, k in cells])

def rots(cells, N):
    out, x = [], norm(cells)
    for _ in range(4):
        out.append(x); x = rot90(x, N)
    return out

def figura(rng, N, n, colores):
    """Figura conexa de n celdas, sin simetrías (quiral y sin ejes)."""
    for _ in range(500):
        start = (rng.randrange(N), rng.randrange(N))
        s = {start}
        while len(s) < n:
            r, c = rng.choice(sorted(s))
            dr, dc = rng.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
            if 0 <= r + dr < N and 0 <= c + dc < N:
                s.add((r + dr, c + dc))
        cells = norm([(r, c, rng.choice(colores)) for r, c in s])
        R = rots(cells, N)
        if len({forma(x) for x in R}) < 4: continue
        FR = {forma(x) for x in R}
        if forma(refl_v(cells, N)) in FR: continue   # ni siquiera la forma puede ser simétrica
        if forma(refl_h(cells, N)) in FR: continue
        return cells
    raise Fallo('figura')

def forma(cells):
    return tuple(sorted((r, c) for r, c, _ in cells))

def formas_rot(cells, N):
    return {forma(x) for x in rots(cells, N)}

def mover_una(cells, N, rng):
    cells = list(cells)
    i = rng.randrange(len(cells))
    r, c, k = cells[i]
    libres = [(a, b) for a in range(N) for b in range(N) if (a, b) not in {(x, y) for x, y, _ in cells}]
    a, b = rng.choice(libres)
    cells[i] = (a, b, k)
    return norm(cells)

def cambiar_color(cells, rng):
    cells = list(cells)
    i = rng.randrange(len(cells))
    r, c, k = cells[i]
    cells[i] = (r, c, 1 if k == 2 else 2)
    return norm(cells)

def item(t, n, r, q, o, e, x=None, k=None):
    d = {'t': t, 'n': n, 'r': r, 'q': q, 'o': o, 'e': e}
    if x is not None: d['x'] = x
    if k is not None: d['k'] = k
    return d

def L(cells):
    return [list(c) for c in cells]

# ------------------------------------------------------------------ espejo
def gen_espejo(nivel, rng):
    N, n, cols = {'F': (4, 4, [1]), 'M': (4, 5, [1, 2]), 'D': (5, 6, [1, 2]), 'MD': (5, 7, [1, 2])}[nivel]
    fig = figura(rng, N, n, cols)
    eje = 'v' if nivel in ('F', 'M') or rng.random() < 0.5 else 'h'
    corr = refl_v(fig, N) if eje == 'v' else refl_h(fig, N)
    otro = refl_h(fig, N) if eje == 'v' else refl_v(fig, N)
    cands = [(otro, 'refleja con el espejo en el otro lado'),
             (rots(fig, N)[2], 'es la figura girada media vuelta, no reflejada'),
             (fig, 'es la figura original sin reflejar'),
             (rots(corr, N)[1], 'es el reflejo pero además girado'),
             (mover_una(corr, N, rng), 'tiene una casilla fuera de lugar')]
    if 2 in cols:
        cands.append((cambiar_color(corr, rng), 'tiene una casilla con el color cambiado'))
    vistos, ds, trampa = {corr}, [], None
    for c, why in cands:
        if c not in vistos:
            vistos.add(c); ds.append((c, why))
        if len(ds) == 4: break
    if len(ds) < 4: raise Fallo('pocas')
    rng.shuffle(ds)
    lugar = 'a la derecha' if eje == 'v' else 'debajo'
    q = f"Si pones un espejo {lugar} de la figura, ¿cómo se ve su reflejo?"
    e = [f"En un espejo {lugar}, cada casilla queda a la misma distancia del espejo pero del otro lado: " +
         ("lo de la izquierda pasa a la derecha y lo de arriba sigue arriba." if eje == 'v' else "lo de arriba pasa abajo y lo de la izquierda sigue a la izquierda."),
         "Revisa casilla por casilla (y su color) antes de marcar."]
    k = next(([i + 1, why] for i, (c, why) in enumerate(ds) if 'girada' in why or 'otro lado' in why), None)
    return item('espejo', nivel, f'espejo:{eje}', q, [L(corr)] + [L(c) for c, _ in ds], e,
                x={'fig': L(fig), 'N': N, 'eje': eje}, k=k)

# ------------------------------------------------------------------ giro de figura (rotación mental)
def gen_giro2d(nivel, rng):
    N, n, cols = {'F': (4, 4, [1]), 'M': (4, 5, [1, 2]), 'D': (5, 6, [1, 2]), 'MD': (5, 7, [1, 2])}[nivel]
    fig = figura(rng, N, n, cols)
    R = rots(fig, N)
    g = rng.choice([1, 2, 3]) if nivel != 'F' else rng.choice([1, 3])
    corr = R[g]
    FR = formas_rot(fig, N)
    mir = refl_v(fig, N)
    MR = rots(mir, N)
    ds = [m for m in MR if forma(m) not in FR]
    rng.shuffle(ds)
    ds = ds[:3]
    for _ in range(20):
        extra = mover_una(corr, N, rng)
        if forma(extra) not in FR and forma(extra) not in {forma(d) for d in ds}: break
    else:
        raise Fallo('extra')
    ds.append(extra)
    if len({forma(x) for x in ds + [corr]}) != 5: raise Fallo('dup')
    rng.shuffle(ds)
    grados = {1: '90° a la derecha', 2: '180°', 3: '90° a la izquierda'}[g]
    q = "¿Cuál opción es la MISMA figura, solo girada (sin darle la vuelta como en un espejo)?"
    e = [f"La correcta es la figura girada {grados}.",
         "Las otras son la figura reflejada (como vista en un espejo) o tienen una casilla distinta.",
         "Truco: fíjate en una esquina o casilla especial y sigue hacia dónde queda al girar."]
    k = next(([i + 1, 'es la figura reflejada en espejo y girada: parece igual, pero está al revés'] for i, d in enumerate(ds) if d in MR), None)
    return item('giro2d', nivel, 'giro:rotar sin reflejar', q, [L(corr)] + [L(d) for d in ds], e,
                x={'fig': L(fig), 'N': N}, k=k)

# ------------------------------------------------------------------ papel doblado y perforado
def gen_papel(nivel, rng):
    if nivel == 'F':
        N = rng.choice([4, 6]); fs = [rng.choice(['v', 'h'])]; nh = 1
    elif nivel == 'M':
        N = rng.choice([4, 6]); fs = [rng.choice(['v', 'h'])]; nh = 2
    elif nivel == 'D':
        N = 4; fs = rng.sample(['v', 'h'], 2); nh = 1
    else:
        N = 4; fs = rng.sample(['v', 'h'], 2); nh = 2
    # sentido del doblez: '+' = se dobla la primera mitad (izquierda/arriba) sobre la segunda; '-' = al revés
    folds = [f + rng.choice('+-') for f in fs]
    rows = list(range(N)); cols = list(range(N))
    steps = [{'r0': 0, 'c0': 0, 'h': N, 'w': N, 'fold': folds[0], 'holes': []}]
    for i, f in enumerate(folds):
        if f[0] == 'v': cols = cols[len(cols) // 2:] if f[1] == '+' else cols[:len(cols) // 2]
        else: rows = rows[len(rows) // 2:] if f[1] == '+' else rows[:len(rows) // 2]
        steps.append({'r0': rows[0], 'c0': cols[0], 'h': len(rows), 'w': len(cols), 'fold': folds[i + 1] if i + 1 < len(folds) else None, 'holes': []})
    holes = rng.sample([(r, c) for r in rows for c in cols], nh)
    steps[-1]['holes'] = [list(h) for h in holes]
    def desdoblar(hs, fs):
        out = set(hs)
        for f in reversed(fs):
            nuevo = set(out)
            for r, c in out:
                nuevo.add((r, N - 1 - c) if f[0] == 'v' else (N - 1 - r, c))
            out = nuevo
        return out
    corr = desdoblar(holes, folds)
    cands = [(set(holes), 'solo muestra las perforaciones sin desdoblar'),
             (desdoblar(holes, folds[:-1]) if len(folds) > 1 else desdoblar(holes, ['h' if folds[0][0] == 'v' else 'v']),
              'desdobla solo una vez' if len(folds) > 1 else 'refleja hacia el lado equivocado'),
             (desdoblar(holes, ['h' if f[0] == 'v' else 'v' for f in folds]), 'refleja con los ejes cambiados'),
             (corr - {sorted(corr)[0]}, 'le falta una perforación'),
             (corr | {rng.choice([(r, c) for r in range(N) for c in range(N) if (r, c) not in corr])}, 'tiene una perforación de más'),
             (desdoblar([(r, (c + 1) % N if c + 1 < N else c - 1) for r, c in holes], folds), 'las perforaciones están corridas una casilla')]
    vistos, ds = {frozenset(corr)}, []
    for c, why in cands:
        fc = frozenset(c)
        if fc and fc not in vistos:
            vistos.add(fc); ds.append((c, why))
        if len(ds) == 4: break
    if len(ds) < 4: raise Fallo('pocas')
    rng.shuffle(ds)
    toL = lambda s: [[r, c, 1] for r, c in sorted(s)]
    nf = len(folds)
    q = f"Se dobla una hoja cuadrada {('una vez' if nf == 1 else 'dos veces')} como muestran los pasos y se perfora donde están los círculos. ¿Cómo queda al desdoblarla?"
    e = [f"Al desdoblar, cada perforación se refleja sobre la línea del doblez{'; con dos dobleces, se refleja dos veces (4 agujeros por cada perforación)' if nf == 2 else ''}.",
         f"Resultado: {len(corr)} perforaciones."]
    k = next(([i + 1, why] for i, (c, why) in enumerate(ds) if 'una vez' in why or 'equivocado' in why), None)
    return item('papel', nivel, f"papel:{nf} {'doblez' if nf == 1 else 'dobleces'}", q, [toL(corr)] + [toL(c) for c, _ in ds], e,
                x={'steps': steps, 'N': N}, k=k)

GENERADORES = {'espejo': gen_espejo, 'giro2d': gen_giro2d, 'papel': gen_papel}

if __name__ == '__main__':
    POR = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'bank')
    rng = random.Random(20261102)
    for t, g in GENERADORES.items():
        items, vistos = [], set()
        for n in NIVELES:
            k = tries = 0
            while k < POR and tries < POR * 50:
                tries += 1
                try: it = g(n, rng)
                except Fallo: continue
                key = json.dumps([it['x'], it['o'][0]])
                if key in vistos: continue
                assert len({json.dumps(o) for o in it['o']}) == 5
                vistos.add(key); it['i'] = f"{t[:4]}{n}{k}"; items.append(it); k += 1
        json.dump(items, open(os.path.join(OUT, f'{t}.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
        print(t, len(items))
