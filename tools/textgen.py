"""Generadores de preguntas de texto y de lógica para la app web.

Cada generador recibe (nivel, rng) y devuelve un dict:
  t: tipo · n: nivel (F, M, D, MD) · r: regla (etiqueta estable para repasos)
  q: enunciado · x: visual opcional · o: 5 opciones (la correcta en la posición 0)
  e: explicación (lista de líneas) · k: [índice de la opción trampa, por qué] (opcional)
Todas las respuestas se calculan y se verifican por código (unicidad por fuerza bruta
cuando aplica). Si un intento no cumple, se lanza Fallo y se intenta de nuevo.
"""
import itertools, math, random

class Fallo(Exception):
    pass

ALFA = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"  # 27 letras
NIVELES = ['F', 'M', 'D', 'MD']


def opciones(correcta, candidatos, rng, extra=None, n=4):
    """Devuelve [correcta] + n distractores distintos (como texto)."""
    c = str(correcta)
    vistos, out = {c}, []
    for d in candidatos:
        d = str(d)
        if d not in vistos:
            vistos.add(d); out.append(d)
        if len(out) == n:
            break
    if len(out) < n and extra:
        pool = [str(x) for x in extra if str(x) not in vistos]
        rng.shuffle(pool)
        for d in pool:
            if d not in vistos:
                vistos.add(d); out.append(d)
            if len(out) == n:
                break
    if len(out) < n:
        raise Fallo('faltan distractores')
    return [c] + out


def item(t, n, r, q, o, e, x=None, k=None):
    d = {'t': t, 'n': n, 'r': r, 'q': q, 'o': o, 'e': e if isinstance(e, list) else [e]}
    if x is not None: d['x'] = x
    if k is not None: d['k'] = k
    return d


# ---------------------------------------------------------------- series numéricas
def _arit(v):
    return len(v) >= 3 and len({b - a for a, b in zip(v, v[1:])}) == 1

def _geo(v):
    if any(a == 0 for a in v[:-1]): return False
    rs = {b / a for a, b in zip(v, v[1:])}
    return len(rs) == 1

def _dif2(v):
    d = [b - a for a, b in zip(v, v[1:])]
    return _arit(d)

def _inter(v):
    return len(v) >= 6 and _arit(v[0::2]) and _arit(v[1::2])

def _fibo(v):
    return all(v[i] == v[i - 1] + v[i - 2] for i in range(2, len(v)))

def _alt_dif(v):
    d = [b - a for a, b in zip(v, v[1:])]
    return len(d) >= 4 and all(d[i] == d[i - 2] for i in range(2, len(d)))

def _dif_geo(v):
    d = [b - a for a, b in zip(v, v[1:])]
    return len(d) >= 3 and _geo(d) and d[0] != 0

def _lin_rec(v):
    """a(n+1) = m*a(n) + c con m, c enteros pequeños."""
    for m in range(-3, 4):
        if m in (0,):
            continue
        c = v[1] - m * v[0]
        if all(v[i + 1] == m * v[i] + c for i in range(len(v) - 1)):
            return True
    return False

REGLAS_SIMPLES = [_arit, _geo, _dif2, _inter, _fibo, _alt_dif, _dif_geo, _lin_rec]

def explicable(v):
    return any(f(v) for f in REGLAS_SIMPLES)


def gen_serie_num(nivel, rng):
    L = 6
    if nivel == 'F':
        kind = rng.choice(['arit', 'arit', 'geo'])
    elif nivel == 'M':
        kind = rng.choice(['dif2', 'alt', 'cuadrados', 'lin'])
    elif nivel == 'D':
        kind = rng.choice(['inter', 'fibo', 'difgeo', 'lin2'])
    else:
        kind = rng.choice(['inter_ops', 'dif3', 'prod', 'alt_ops'])
    if kind == 'arit':
        a, d = rng.randint(1, 30), rng.choice([2, 3, 4, 5, 6, 7, 9, 11, -3, -4, -6])
        if d < 0: a += 60
        v = [a + d * i for i in range(L + 1)]
        exp = f"Cada número {'suma' if d > 0 else 'resta'} {abs(d)}."; regla = 'serie:suma constante'
    elif kind == 'geo':
        a, r = rng.randint(1, 5), rng.choice([2, 3])
        v = [a * r ** i for i in range(L + 1)]
        exp = f"Cada número se multiplica por {r}."; regla = 'serie:multiplica constante'
    elif kind == 'dif2':
        a, d, s = rng.randint(1, 20), rng.randint(1, 5), rng.choice([1, 2, 3])
        v = [a]
        for i in range(L):
            v.append(v[-1] + d + s * i)
        exp = f"Las diferencias aumentan de {s} en {s}: +{d}, +{d+s}, +{d+2*s}…"; regla = 'serie:diferencias crecientes'
    elif kind == 'alt':
        a, p, q = rng.randint(5, 30), rng.randint(3, 9), rng.randint(1, 5)
        if p == q: raise Fallo('alt')
        v = [a]
        for i in range(L):
            v.append(v[-1] + (p if i % 2 == 0 else -q))
        exp = f"Se alterna: +{p}, −{q}, +{p}, −{q}…"; regla = 'serie:alterna dos operaciones'
    elif kind == 'cuadrados':
        s, c = rng.randint(1, 4), rng.choice([0, 1, -1, 2])
        v = [(s + i) ** 2 + c for i in range(L + 1)]
        exp = f"Son cuadrados ({s}², {s+1}², {s+2}²…)" + (f" {'+' if c > 0 else '−'} {abs(c)}." if c else ".")
        regla = 'serie:cuadrados'
    elif kind == 'lin':
        a, m, c = rng.randint(1, 6), 2, rng.choice([1, -1, 2, 3])
        v = [a]
        for i in range(L):
            v.append(v[-1] * m + c)
        if max(v) > 999: raise Fallo('grande')
        exp = f"Cada número se multiplica por {m} y {'se le suma' if c > 0 else 'se le resta'} {abs(c)}."
        regla = 'serie:multiplica y suma'
    elif kind == 'inter':
        a, d1, b, d2 = rng.randint(1, 20), rng.choice([2, 3, 4, 5]), rng.randint(20, 60), rng.choice([-2, -3, -5, 4, 6])
        if d1 == d2: raise Fallo('inter')
        s1 = [a + d1 * i for i in range(4)]; s2 = [b + d2 * i for i in range(4)]
        v = [s1[0], s2[0], s1[1], s2[1], s1[2], s2[2], s1[3]]
        exp = f"Son dos series intercaladas: posiciones impares {'+' if d1>0 else '−'}{abs(d1)}, posiciones pares {'+' if d2>0 else '−'}{abs(d2)}."
        regla = 'serie:intercaladas'
    elif kind == 'fibo':
        a, b = rng.randint(1, 6), rng.randint(1, 8)
        v = [a, b]
        while len(v) < L + 1:
            v.append(v[-1] + v[-2])
        exp = "Cada número es la suma de los dos anteriores."; regla = 'serie:suma de los dos anteriores'
    elif kind == 'difgeo':
        a, d0, r = rng.randint(1, 20), rng.choice([1, 2, 3]), 2
        v = [a]
        for i in range(L):
            v.append(v[-1] + d0 * r ** i)
        exp = f"Las diferencias se duplican: +{d0}, +{d0*2}, +{d0*4}…"; regla = 'serie:diferencias que se multiplican'
    elif kind == 'lin2':
        a, m, c = rng.randint(1, 4), 3, rng.choice([-1, 1, -2])
        v = [a]
        for i in range(L - 1):
            v.append(v[-1] * m + c)
        L2 = len(v) - 1
        if max(v) > 2000 or min(v) < 0: raise Fallo('grande')
        exp = f"Cada número se multiplica por {m} y {'se le suma' if c > 0 else 'se le resta'} {abs(c)}."
        regla = 'serie:multiplica y suma'
    elif kind == 'inter_ops':
        a, b = rng.randint(1, 5), rng.randint(30, 60)
        m, d = rng.choice([2, 3]), rng.choice([-3, -4, -5, -7])
        s1 = [a * m ** i for i in range(4)]; s2 = [b + d * i for i in range(4)]
        v = [s1[0], s2[0], s1[1], s2[1], s1[2], s2[2], s1[3]]
        exp = f"Dos series intercaladas: en las posiciones impares se multiplica por {m}; en las pares se resta {abs(d)}."
        regla = 'serie:intercaladas con operaciones distintas'
    elif kind == 'dif3':
        a = rng.randint(1, 10)
        dd = [rng.randint(1, 3)]
        s = rng.randint(1, 2)
        d = [dd[0]]
        for i in range(L - 1):
            d.append(d[-1] + s * (i + 1))
        v = [a]
        for x in d:
            v.append(v[-1] + x)
        exp = "Las diferencias forman su propia serie: " + ", ".join(f"+{x}" for x in d) + f" (esas diferencias crecen {s}, {2*s}, {3*s}…)."
        regla = 'serie:diferencias de diferencias'
    elif kind == 'prod':
        a = rng.randint(1, 3)
        v = [a]
        for i in range(L):
            v.append(v[-1] * (i + 2) if rng.random() < 2 else 0)
        if max(v) > 50000: raise Fallo('grande')
        exp = "Se multiplica por 2, luego por 3, luego por 4… (un número más cada vez)."; regla = 'serie:multiplicador creciente'
    else:  # alt_ops
        a, m, c = rng.randint(2, 6), rng.choice([2, 3]), rng.choice([1, 2, 3, 4])
        v = [a]
        for i in range(L):
            v.append(v[-1] * m if i % 2 == 0 else v[-1] + c)
        if max(v) > 5000: raise Fallo('grande')
        exp = f"Se alterna: ×{m}, +{c}, ×{m}, +{c}…"; regla = 'serie:alterna multiplicar y sumar'
    shown, ans = v[:-1], v[-1]
    last_d = shown[-1] - shown[-2]
    cands = [shown[-1] + last_d, ans + 1, ans - 1, ans + (last_d if last_d else 2), ans - (abs(last_d) or 2),
             ans + 2, ans - 2, ans * 2 if abs(ans) < 500 else ans + 10, shown[-1] + shown[-2]]
    cands = [c for c in cands if c != ans and not explicable(shown + [c])]
    rng.shuffle(cands)
    extra = [ans + k for k in range(-12, 13) if k and not explicable(shown + [ans + k])]
    o = opciones(ans, cands, rng, extra)
    return item('serie_num', nivel, regla, '¿Qué número sigue?', o, [exp],
                x={'seq': [str(s) for s in shown] + ['?']})


# ---------------------------------------------------------------- series de letras
def L_(i):
    return ALFA[i % 27]

def _lseq_explicable(idx):
    d = [(b - a) % 27 for a, b in zip(idx, idx[1:])]
    if len(set(d)) == 1: return True
    if len(d) >= 3 and len({(b - a) % 27 for a, b in zip(d, d[1:])}) == 1: return True
    if len(idx) >= 6:
        d1 = {(b - a) % 27 for a, b in zip(idx[0::2], idx[2::2])}
        d2 = {(b - a) % 27 for a, b in zip(idx[1::2], idx[3::2])}
        if len(d1) == 1 and len(d2) == 1: return True
    if len(d) >= 4 and all(d[i] == d[i - 2] for i in range(2, len(d))): return True
    return False


def gen_serie_letras(nivel, rng):
    if nivel == 'F':
        kind = 'paso'
    elif nivel == 'M':
        kind = rng.choice(['alterna', 'atras', 'creciente'])
    elif nivel == 'D':
        kind = rng.choice(['inter', 'creciente', 'pares'])
    else:
        kind = rng.choice(['inter_dist', 'pares_mix'])
    s = rng.randrange(27)
    if kind == 'paso':
        k = rng.choice([2, 3, 4])
        idx = [s + k * i for i in range(7)]
        exp = f"Se avanza {k} letras cada vez (cuenta la Ñ)."; regla = 'letras:paso constante'
    elif kind == 'atras':
        k = rng.choice([2, 3])
        idx = [s - k * i for i in range(7)]
        exp = f"Se retrocede {k} letras cada vez (cuenta la Ñ)."; regla = 'letras:paso constante'
    elif kind == 'alterna':
        p, q = rng.choice([(1, 2), (2, 1), (1, 3), (3, 1), (2, 3)])
        idx = [s]
        for i in range(6): idx.append(idx[-1] + (p if i % 2 == 0 else q))
        exp = f"Se alterna: avanza {p}, avanza {q}, avanza {p}… (cuenta la Ñ)."; regla = 'letras:pasos alternos'
    elif kind == 'creciente':
        idx = [s]
        for i in range(6): idx.append(idx[-1] + i + 1)
        exp = "Se avanza 1, luego 2, luego 3… letras (cuenta la Ñ)."; regla = 'letras:paso creciente'
    elif kind in ('inter', 'inter_dist'):
        k1 = rng.choice([1, 2, 3]); k2 = -rng.choice([1, 2]) if kind == 'inter_dist' else rng.choice([1, 2, 3])
        if k1 == k2: raise Fallo('inter')
        b = rng.randrange(27)
        a1 = [s + k1 * i for i in range(4)]; a2 = [b + k2 * i for i in range(3)]
        idx = [a1[0], a2[0], a1[1], a2[1], a1[2], a2[2], a1[3]]
        exp = f"Dos series intercaladas: posiciones impares avanzan {k1}; posiciones pares {'avanzan' if k2>0 else 'retroceden'} {abs(k2)}."
        regla = 'letras:intercaladas'
    else:
        # pares de letras: AB, DE, GH, ?
        k = rng.choice([3, 4]) if kind == 'pares' else rng.choice([3, 5])
        gap = 1 if kind == 'pares' else rng.choice([2])
        prs = [(s + k * i, s + k * i + gap) for i in range(5)]
        shown = [L_(a) + L_(b) for a, b in prs[:4]]
        ans = L_(prs[4][0]) + L_(prs[4][1])
        cands = [L_(prs[4][0] + 1) + L_(prs[4][1] + 1), L_(prs[4][0] - 1) + L_(prs[4][1] - 1),
                 L_(prs[4][0]) + L_(prs[4][1] + 1), L_(prs[4][1]) + L_(prs[4][0]),
                 L_(prs[4][0] + 1) + L_(prs[4][1]), L_(prs[4][0] - 2) + L_(prs[4][1] - 2)]
        o = opciones(ans, cands, rng)
        exp = f"Cada par empieza {k} letras después del anterior y sus dos letras están separadas por {gap} (cuenta la Ñ)."
        return item('serie_letras', nivel, 'letras:pares', '¿Qué par de letras sigue?', o, [exp],
                    x={'seq': shown + ['?']})
    shown_i, ans_i = idx[:-1], idx[-1]
    ans = L_(ans_i)
    cands = [L_(ans_i + d) for d in (1, -1, 2, -2, 3)]
    # la trampa clásica: olvidar la Ñ
    sin_n = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cands = [c for c in cands if not _lseq_explicable(shown_i + [ALFA.index(c)])]
    rng.shuffle(cands)
    o = opciones(ans, cands, rng, [L_(ans_i + d) for d in range(-6, 7) if d and not _lseq_explicable(shown_i + [ans_i + d])])
    return item('serie_letras', nivel, regla, '¿Qué letra sigue?', o,
                [exp, 'Tip: escribe el alfabeto numerado con la Ñ (A1 … N14, Ñ15, O16 … Z27).'],
                x={'seq': [L_(i) for i in shown_i] + ['?']})


# ---------------------------------------------------------------- números dentro de figuras
FIG_REGLAS = {
    'suma': (lambda a, b: a + b, 'la tercera es la suma de las dos primeras'),
    'resta': (lambda a, b: a - b, 'la tercera es la primera menos la segunda'),
    'producto': (lambda a, b: a * b, 'la tercera es el producto de las dos primeras'),
    'doble_suma': (lambda a, b: 2 * (a + b), 'la tercera es el doble de la suma'),
    'prod_menos': (lambda a, b: a * b - a, 'la tercera es primera × segunda − primera'),
    'cuad_menos': (lambda a, b: a * a - b, 'la tercera es la primera al cuadrado menos la segunda'),
    'suma_cuad': (lambda a, b: a * a + b * b, 'la tercera es la suma de los cuadrados'),
    'prod_mas': (lambda a, b: a * b + b, 'la tercera es primera × segunda + segunda'),
    'div': (lambda a, b: a // b if b and a % b == 0 else None, 'la tercera es la primera dividida entre la segunda'),
    'promedio': (lambda a, b: (a + b) // 2 if (a + b) % 2 == 0 else None, 'la tercera es el promedio de las dos primeras'),
}
FIG_NIVEL = {'F': ['suma', 'resta'], 'M': ['producto', 'doble_suma', 'div'], 'D': ['prod_menos', 'cuad_menos', 'prod_mas'],
             'MD': ['suma_cuad', 'cuad_menos', 'prod_menos']}


def _filas_cumplen(filas, f):
    return all(f(a, b) == c for a, b, c in filas)


def gen_numeros_figura(nivel, rng):
    nombre = rng.choice(FIG_NIVEL[nivel])
    f, desc = FIG_REGLAS[nombre]
    filas = []
    for _ in range(3):
        for _t in range(50):
            a, b = rng.randint(2, 9), rng.randint(1, 9)
            c = f(a, b)
            if c is not None and 0 < c < 200 and (a, b) not in [(x, y) for x, y, _ in filas]:
                filas.append((a, b, c)); break
        else:
            raise Fallo('filas')
    # la regla debe ser la única de la lista que explica las 2 filas completas
    otras = [n for n, (g, _) in FIG_REGLAS.items() if n != nombre and _filas_cumplen(filas[:2], g)]
    if otras:
        raise Fallo('ambigua')
    ans = filas[2][2]
    a, b = filas[2][0], filas[2][1]
    cands = []
    for n, (g, _) in FIG_REGLAS.items():
        v = g(a, b)
        if v is not None and v != ans and v > 0:
            cands.append(v)
    cands += [ans + 1, ans - 1, ans + a, ans - b, ans + 2]
    cands = [c for c in cands if c > 0 and c != ans]
    # ningún distractor puede ser explicado por otra regla que cumpla las filas 1 y 2
    rng.shuffle(cands)
    o = opciones(ans, cands, rng, [ans + k for k in range(-10, 11) if k and ans + k > 0])
    forma = rng.choice(['grid', 'tri'])
    if forma == 'grid':
        x = {'grid': [[str(v) for v in r] for r in filas[:2]] + [[str(a), str(b), '?']]}
        q = '¿Qué número reemplaza el signo de interrogación?'
        exp = [f"En cada fila, {desc}.", f"Fila 3: {a} y {b} → {ans}."]
    else:
        x = {'tri': [[str(v) for v in r] for r in filas[:2]] + [[str(a), str(b), '?']]}
        q = 'En cada triángulo, el número del centro sale de los dos números de abajo con la misma regla. ¿Qué número va en el centro del último?'
        desc2 = desc.replace('la tercera', 'el centro').replace('las dos primeras', 'los dos de abajo').replace('la primera', 'el de la izquierda').replace('la segunda', 'el de la derecha')
        exp = [f"En cada triángulo, {desc2}.", f"Último: {a} (izquierda) y {b} (derecha) → {ans}."]
    return item('numeros_figura', nivel, f'numeros:{nombre}', q, o, exp, x=x)


# ---------------------------------------------------------------- ecuaciones con símbolos
SIMB = ['▲', '●', '■', '★', '◆']

def gen_simbolos(nivel, rng):
    s = rng.sample(SIMB, 3)
    if nivel == 'F':
        x = rng.randint(2, 12); k = rng.choice([2, 3])
        y = rng.randint(1, 15)
        lines = [f"{' + '.join([s[0]] * k)} = {k * x}"]
        ans = x + y
        q = f"¿Cuánto vale {s[0]} + {y}?"
        exp = [f"{s[0]} = {k*x} ÷ {k} = {x}.", f"{x} + {y} = {ans}."]
        cands = [k * x + y, x, x * y if x * y != ans else ans + 3, ans + 1, ans - 1, k * x]
        regla = 'simbolos:una incógnita'
    elif nivel == 'M':
        a, b = rng.randint(2, 12), rng.randint(1, 11)
        if a == b: raise Fallo('igual')
        lines = [f"{s[0]} + {s[1]} = {a + b}", f"{s[0]} − {s[1]} = {a - b}"]
        ans = a * b
        q = f"¿Cuánto vale {s[0]} × {s[1]}?"
        exp = [f"Sumando las dos igualdades: 2·{s[0]} = {2*a} → {s[0]} = {a}.", f"Entonces {s[1]} = {b}.", f"{a} × {b} = {ans}."]
        cands = [a + b, (a + b) * (a - b) if a > b else ans + 4, a * a, b * b, ans + a, ans - b, ans + 1]
        regla = 'simbolos:dos incógnitas'
    elif nivel == 'D':
        a = rng.randint(2, 12)
        lines = [f"{s[0]} + {s[0]} = {s[1]}", f"{s[1]} + {s[0]} = {s[2]}", f"{s[2]} − {s[1]} = {a}"]
        b, c = 2 * a, 3 * a
        ans = a + b + c
        q = f"¿Cuánto vale {s[0]} + {s[1]} + {s[2]}?"
        exp = [f"{s[2]} − {s[1]} = {s[0]}, así que {s[0]} = {a}.", f"{s[1]} = 2·{a} = {b}; {s[2]} = {b} + {a} = {c}.", f"Total: {a} + {b} + {c} = {ans}."]
        cands = [3 * a, 4 * a, 5 * a, 7 * a, ans + 1, ans - a, ans + 2]
        regla = 'simbolos:cadena'
    else:  # balanzas / equivalencias
        p, q1 = rng.randint(2, 4), rng.randint(2, 5)
        r, t = rng.randint(2, 4), rng.randint(2, 6)
        # p·A = q1·B ; r·B = t·C ; ¿cuántas C equivalen a k·A?
        # A = q1/p B ; B = t/r C ; A = q1*t/(p*r) C
        num, den = q1 * t, p * r
        k = den // math.gcd(num, den) * rng.choice([1, 2])
        if (k * num) % den: raise Fallo('frac')
        ans = k * num // den
        if ans > 40 or ans < 2: raise Fallo('rango')
        lines = [f"{p} {s[0]} pesan lo mismo que {q1} {s[1]}", f"{r} {s[1]} pesan lo mismo que {t} {s[2]}"]
        q = f"¿Cuántos {s[2]} pesan lo mismo que {k} {s[0]}?"
        exp = [f"1 {s[0]} = {q1}/{p} de {s[1]}, y 1 {s[1]} = {t}/{r} de {s[2]}.",
               f"{k} {s[0]} = {k}·{q1}/{p} {s[1]} = {k*q1}/{p} · {t}/{r} {s[2]} = {ans} {s[2]}."]
        cands = [k * q1 * t, k * t, round(k * p * r / max(1, q1 * t)) or ans + 3, ans + 1, ans - 1, ans * 2, k + t]
        regla = 'simbolos:balanzas'
    cands = [c for c in cands if c != ans and c >= 0]
    rng.shuffle(cands)
    o = opciones(ans, cands, rng, [ans + k for k in range(-8, 9) if k and ans + k >= 0])
    return item('simbolos', nivel, regla, q, o, exp, x={'lines': lines})


# ---------------------------------------------------------------- operadores definidos
OPS_DEF = [
    ('2a − b', lambda a, b: 2 * a - b),
    ('a + 2b', lambda a, b: a + 2 * b),
    ('a × b − a', lambda a, b: a * b - a),
    ('a² − b', lambda a, b: a * a - b),
    ('(a + b) × 2', lambda a, b: (a + b) * 2),
    ('a × b + 1', lambda a, b: a * b + 1),
    ('3a − 2b', lambda a, b: 3 * a - 2 * b),
]

def gen_operador(nivel, rng):
    (dtxt, f), = rng.sample(OPS_DEF, 1)
    sym = rng.choice(['#', '◇', '⊕', '@'])
    defn = f"a {sym} b = {dtxt}"
    if nivel == 'F':
        a, b = rng.randint(1, 9), rng.randint(1, 9)
        ans = f(a, b); q = f"¿Cuánto es {a} {sym} {b}?"
        exp = [f"Se reemplaza a = {a} y b = {b} en {dtxt}: el resultado es {ans}."]
        cands = [f(b, a), a + b, a * b, ans + 1, ans - 1, ans + 2]
        regla = 'operador:aplicar'
    elif nivel == 'M':
        a, b, c = rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 6)
        inner = f(a, b); ans = f(inner, c)
        q = f"¿Cuánto es ({a} {sym} {b}) {sym} {c}?"
        exp = [f"Primero el paréntesis: {a} {sym} {b} = {inner}.", f"Luego {inner} {sym} {c} = {ans}."]
        cands = [f(a, f(b, c)), inner, f(c, inner), ans + 1, ans - 1, inner + c]
        regla = 'operador:anidado'
    elif nivel == 'D':
        (d2, g), = rng.sample([o for o in OPS_DEF if o[0] != dtxt], 1)
        sym2 = '★' if sym != '★' else '☆'
        defn = defn + f"   ·   a {sym2} b = {d2}"
        a, b, c = rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 6)
        inner = g(a, b); ans = f(inner, c)
        q = f"¿Cuánto es ({a} {sym2} {b}) {sym} {c}?"
        exp = [f"{a} {sym2} {b} = {inner} (usando {d2}).", f"{inner} {sym} {c} = {ans} (usando {dtxt})."]
        cands = [g(f(a, b), c), f(a, b), g(inner, c), ans + 1, ans - 1, f(f(a, b), c)]
        regla = 'operador:dos operadores'
    else:
        b, xv = rng.randint(1, 7), rng.randint(1, 9)
        ans = xv; res = f(xv, b)
        # unicidad de x en 0..30
        sols = [x for x in range(0, 31) if f(x, b) == res]
        if sols != [xv]: raise Fallo('no única')
        q = f"Si x {sym} {b} = {res}, ¿cuánto vale x?"
        exp = [f"Se prueba en {dtxt} con b = {b}: solo x = {xv} da {res}."]
        cands = [res - b, res + b, xv + 1, xv - 1, b, res // 2]
        regla = 'operador:despejar'
    cands = [c for c in cands if c != ans]
    rng.shuffle(cands)
    o = opciones(ans, cands, rng, [ans + k for k in range(-9, 10) if k])
    return item('operador', nivel, regla, q, o, exp, x={'lines': [defn]})


# ---------------------------------------------------------------- algoritmos (pseudocódigo)
def gen_algoritmo(nivel, rng):
    if nivel == 'F':
        x0 = rng.randint(1, 9); ops = []
        x = x0; code = [f"x ← {x0}"]
        for _ in range(3):
            op = rng.choice(['+', '×', '−'])
            k = rng.randint(2, 5)
            if op == '+': x += k
            elif op == '×': x *= k
            else: x -= k
            code.append(f"x ← x {op} {k}")
        code.append("mostrar x")
        ans = x; cands = [x + 1, x - 1, x0, x * 2, x + 2]
        regla = 'algoritmo:secuencia'
        exp = ["Se ejecuta cada línea en orden, de arriba hacia abajo, actualizando x."]
    elif nivel == 'M':
        x0, n, k = rng.randint(1, 5), rng.randint(3, 5), rng.choice([2, 3])
        c = rng.choice([0, 1, -1])
        x = x0
        for _ in range(n): x = x * k + c
        if x > 3000: raise Fallo('grande')
        upd = f"x ← x × {k}" + (f" + {c}" if c > 0 else (f" − {abs(c)}" if c < 0 else ""))
        code = [f"x ← {x0}", f"repetir {n} veces:", f"    {upd}", "mostrar x"]
        y = x0
        for _ in range(n - 1): y = y * k + c
        z = x0
        for _ in range(n + 1): z = z * k + c
        ans = x; cands = [y, z if z < 20000 else x + 7, x + 1, x - 1, x0 * k * n]
        regla = 'algoritmo:repetir'
        exp = [f"El cuerpo del ciclo se ejecuta exactamente {n} veces.", f"Valores: {x0} → " + ' → '.join(str(v) for v in _trace(x0, n, k, c)) + "."]
    elif nivel == 'D':
        x0, lim, k = rng.randint(1, 4), rng.choice([50, 100, 60, 80]), rng.choice([2, 3])
        x, cnt = x0, 0
        while x < lim:
            x = x * k + 1; cnt += 1
        code = [f"x ← {x0}", "c ← 0", f"mientras x < {lim}:", f"    x ← x × {k} + 1", "    c ← c + 1", "mostrar c"]
        ans = cnt; cands = [cnt + 1, cnt - 1, x, cnt + 2, lim // k]
        regla = 'algoritmo:mientras'
        exp = [f"x toma los valores {x0} → " + ' → '.join(str(v) for v in _trace(x0, cnt, k, 1)) + f"; el ciclo para cuando x ya no es menor que {lim}.",
               f"El ciclo se ejecutó {cnt} veces, así que c = {cnt}."]
    else:
        a0, b0, n = rng.randint(1, 5), rng.randint(1, 5), rng.randint(3, 5)
        a, b = a0, b0
        for i in range(n):
            if a % 2 == 0:
                a, b = b, a + b
            else:
                a, b = a + 1, b * 2 if b < 50 else b
        if b > 5000: raise Fallo('grande')
        code = [f"a ← {a0}", f"b ← {b0}", f"repetir {n} veces:", "    si a es par:", "        (a, b) ← (b, a + b)",
                "    si no:", "        a ← a + 1", "        b ← b × 2", "mostrar a + b"]
        # el 'b < 50' no aparece en el código: verificamos que no se activó
        a2, b2 = a0, b0
        for i in range(n):
            if a2 % 2 == 0: a2, b2 = b2, a2 + b2
            else: a2, b2 = a2 + 1, b2 * 2
        if (a2, b2) != (a, b): raise Fallo('rama')
        ans = a + b; cands = [a, b, ans + 1, ans - 1, a * b if a * b != ans else ans + 3, ans + 2]
        regla = 'algoritmo:condicional en ciclo'
        exp = ["En cada vuelta se mira si a es par: si sí, (a, b) pasan a (b, a+b) al mismo tiempo; si no, a suma 1 y b se duplica.",
               f"Al final a = {a} y b = {b}, así que a + b = {ans}."]
    cands = [c for c in cands if c != ans]
    rng.shuffle(cands)
    o = opciones(ans, cands, rng, [ans + k for k in range(-9, 10) if k])
    return item('algoritmo', nivel, regla, '¿Qué muestra este procedimiento al final?', o, exp, x={'code': code})


def _trace(x0, n, k, c):
    out, x = [], x0
    for _ in range(n):
        x = x * k + c; out.append(x)
    return out


# ---------------------------------------------------------------- codificación
PALABRAS = ['CASA', 'PERRO', 'GATO', 'MESA', 'LIBRO', 'PLATO', 'NUBE', 'RIO', 'SOL', 'LUNA', 'PIEDRA', 'CAMINO',
            'FUEGO', 'TIERRA', 'VIENTO', 'MARCO', 'RELOJ', 'BARCO', 'TREN', 'FLOR', 'ARBOL', 'PUERTA', 'CIELO', 'LAPIZ']

def shift(w, k):
    return ''.join(L_(ALFA.index(ch) + k) for ch in w)

def gen_codificacion(nivel, rng):
    w1, w2 = rng.sample(PALABRAS, 2)
    if nivel == 'F':
        k = rng.choice([1, 2, -1])
        f = lambda w: shift(w, k)
        exp = [f"Cada letra se {'adelanta' if k>0 else 'atrasa'} {abs(k)} posición(es) en el alfabeto (con Ñ)."]
        regla = 'codigo:desplazamiento'
    elif nivel == 'M':
        f = lambda w: w[::-1]
        if rng.random() < 0.5:
            k = rng.choice([1, -1])
            f = lambda w, k=k: shift(w[::-1], k)
            exp = [f"La palabra se escribe al revés y cada letra se {'adelanta' if k>0 else 'atrasa'} 1 (con Ñ)."]
        else:
            exp = ["La palabra se escribe al revés."]
        regla = 'codigo:inversion'
    elif nivel == 'D':
        k1, k2 = rng.choice([(1, -1), (2, 1), (1, 2)])
        f = lambda w: ''.join(L_(ALFA.index(ch) + (k1 if i % 2 == 0 else k2)) for i, ch in enumerate(w))
        exp = [f"Las letras en posición impar se mueven {k1:+d} y las de posición par {k2:+d} (con Ñ)."]
        regla = 'codigo:alterno'
    else:
        # número: suma de posiciones
        f = lambda w: str(sum(ALFA.index(ch) + 1 for ch in w))
        exp = ["Cada palabra se codifica con la suma de las posiciones de sus letras (A=1 … Ñ=15 … Z=27)."]
        regla = 'codigo:suma de posiciones'
    c1, ans = f(w1), f(w2)
    if nivel == 'MD':
        a = int(ans)
        cands = [a + 1, a - 1, sum(ALFA.index(ch) for ch in w2), sum("ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(ch) + 1 for ch in w2),
                 a + len(w2), a - 2]
    else:
        cands = [shift(w2, 1), shift(w2, -1), w2[::-1], shift(w2[::-1], 1), shift(w2, 2),
                 ''.join("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[("ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(ch) + 1) % 26] for ch in w2)]
    cands = [c for c in cands if str(c) != ans]
    rng.shuffle(cands)
    o = opciones(ans, cands, rng)
    q = f"Si {w1} se escribe {c1}, ¿cómo se escribe {w2}?"
    return item('codificacion', nivel, regla, q, o, exp)


# ---------------------------------------------------------------- razonamiento numérico
NOMBRES = ['Ana', 'Beto', 'Carla', 'Diego', 'Elena', 'Fabián', 'Gina', 'Hugo', 'Isa', 'Juan', 'Laura', 'Mario', 'Nora', 'Óscar', 'Paula', 'Raúl', 'Sara', 'Tomás']

def money(v):
    return '$' + f"{v:,}".replace(',', '.')


def gen_numerico(nivel, rng):
    if nivel == 'F':
        kind = rng.choice(['tres', 'porc'])
    elif nivel == 'M':
        kind = rng.choice(['tres_inv', 'porc2', 'edades'])
    elif nivel == 'D':
        kind = rng.choice(['trabajo', 'edades2', 'porc_desc'])
    else:
        kind = rng.choice(['mezcla', 'trabajo', 'reparto'])
    if kind == 'tres':
        a, p = rng.randint(2, 6), rng.randint(2, 9) * 500
        b = rng.choice([x for x in range(3, 12) if x != a])
        if (p * b) % a: raise Fallo('frac')
        ans = p * b // a
        q = f"Si {a} cuadernos cuestan {money(p)}, ¿cuánto cuestan {b} cuadernos?"
        exp = [f"Un cuaderno cuesta {p}/{a}; {b} cuadernos cuestan {p}·{b}/{a} = {ans}."]
        cands = [p * a // b if (p * a) % b == 0 else ans + 500, p + (b - a) * 100, ans + p // a, ans - p // a, p * b]
        fmt = lambda v: f"{money(v)}"
        regla = 'numerico:regla de tres'
    elif kind == 'porc':
        base, pc = rng.choice([200, 300, 400, 500, 800, 1200, 1500]), rng.choice([10, 15, 20, 25, 30, 40])
        ans = base * pc // 100
        q = f"¿Cuánto es el {pc}% de {base}?"
        exp = [f"{pc}% de {base} = {base} × {pc} / 100 = {ans}."]
        cands = [base * pc // 10, ans + base // 10, ans - base // 20, base - ans, pc * 10]
        fmt = str; regla = 'numerico:porcentaje'
    elif kind == 'tres_inv':
        w, d = rng.randint(2, 6), rng.randint(4, 12)
        op_w = [x for x in range(2, 13) if x != w and (w * d) % x == 0]
        if not op_w: raise Fallo('frac')
        w2 = rng.choice(op_w)
        ans = w * d // w2
        q = f"{w} personas pintan una casa en {d} días. Trabajando al mismo ritmo, ¿cuántos días tardan {w2} personas?"
        exp = ["Más personas → menos días (proporción inversa).", f"{w} × {d} = {w*d} días-persona; {w*d} / {w2} = {ans} días."]
        cands = [d * w2 // w if (d * w2) % w == 0 else ans + 2, ans + 1, ans - 1, d, d + (w - w2)]
        fmt = lambda v: f"{v} días"; regla = 'numerico:proporción inversa'
    elif kind == 'porc2':
        p0, a, b = rng.choice([1000, 2000, 5000, 10000]), rng.choice([10, 20, 50]), rng.choice([10, 20, 50])
        v = p0 * (100 + a) // 100 * (100 - b) // 100
        ans = v
        q = f"Un producto cuesta {money(p0)}. Sube {a}% y luego baja {b}%. ¿Cuánto cuesta al final?"
        exp = [f"Sube {a}%: {p0} × {(100+a)/100:g} = {p0*(100+a)//100}.", f"Baja {b}%: {p0*(100+a)//100} × {(100-b)/100:g} = {ans}."]
        cands = [p0 * (100 + a - b) // 100, p0, p0 * (100 - b) // 100, p0 * (100 + a) // 100, ans + p0 // 10]
        fmt = lambda v: f"{money(v)}".replace(',', '.'); regla = 'numerico:porcentaje sobre porcentaje'
    elif kind == 'edades':
        hijo, k, t = rng.randint(4, 12), rng.choice([3, 4]), rng.randint(2, 8)
        padre = hijo * k
        ans = padre + t
        n1 = rng.choice(NOMBRES)
        q = f"La mamá de {n1} tiene {k} veces la edad de {n1}. {n1} tiene {hijo} años. ¿Cuántos años tendrá la mamá dentro de {t} años?"
        exp = [f"Mamá hoy: {k} × {hijo} = {padre}.", f"Dentro de {t} años: {padre} + {t} = {ans}."]
        cands = [k * (hijo + t), padre, ans + t, hijo + t, ans - 1]
        fmt = lambda v: f"{v} años"; regla = 'numerico:edades'
    elif kind == 'edades2':
        a, d = rng.randint(5, 15), rng.randint(20, 30)
        # dentro de x años, el padre tendrá el doble: a+d+x = 2(a+x) -> x = d - a
        x = d - a
        if x <= 0: raise Fallo('edad')
        ans = x
        q = f"Un padre tiene {a+d} años y su hija {a}. ¿Dentro de cuántos años el padre tendrá el doble de la edad de su hija?"
        exp = [f"{a+d} + x = 2·({a} + x) → x = {a+d} − 2·{a} = {x}."]
        cands = [d, x + 1, x - 1, (a + d) // 2 - a, a]
        fmt = lambda v: f"{v} años"; regla = 'numerico:edades'
    elif kind == 'porc_desc':
        final, pc = rng.choice([800, 1200, 1600, 2400, 3200, 4000]), rng.choice([20, 25, 50])
        orig = final * 100 // (100 - pc)
        if final * 100 % (100 - pc): raise Fallo('frac')
        ans = orig
        q = f"Después de un descuento del {pc}%, una camisa cuesta {money(final)}. ¿Cuánto costaba antes?"
        exp = [f"Pagar ${final} es pagar el {100-pc}% del precio.", f"Precio original = {final} / {(100-pc)/100:g} = {orig}."]
        cands = [final * (100 + pc) // 100, final + pc * 10, final * 2, ans + 200, ans - 100]
        fmt = lambda v: f"{money(v)}".replace(',', '.'); regla = 'numerico:porcentaje inverso'
    elif kind == 'trabajo':
        a, b = rng.choice([(2, 3), (3, 6), (4, 12), (6, 12), (3, 6), (5, 20), (6, 3), (10, 15), (12, 4)])
        t = a * b / (a + b)
        if t != int(t): raise Fallo('frac')
        ans = int(t)
        q = f"Una llave llena un tanque en {a} horas y otra en {b} horas. Si se abren las dos a la vez, ¿en cuántas horas se llena?"
        exp = [f"En 1 hora llenan 1/{a} + 1/{b} = {a+b}/{a*b} del tanque.", f"Tiempo = {a*b}/{a+b} = {ans} horas."]
        cands = [(a + b) // 2, a + b, abs(a - b), ans + 1, min(a, b)]
        fmt = lambda v: f"{v} horas"; regla = 'numerico:trabajo conjunto'
    elif kind == 'mezcla':
        n, avg, k, avg2 = rng.randint(4, 8), rng.randint(6, 9), 1, None
        total = n * avg
        nuevo = rng.randint(1, 10)
        if (total + nuevo) % (n + 1): raise Fallo('frac')
        ans = (total + nuevo) // (n + 1)
        q = f"El promedio de {n} notas es {avg}. Si se agrega una nota de {nuevo}, ¿cuál es el nuevo promedio?"
        exp = [f"Suma de las {n} notas: {n} × {avg} = {total}.", f"Nueva suma: {total + nuevo}; nuevo promedio = {total+nuevo}/{n+1} = {ans}."]
        cands = [(avg + nuevo) // 2 if (avg + nuevo) % 2 == 0 else ans + 1, avg, ans + 1, ans - 1, (total + nuevo) // n]
        fmt = str; regla = 'numerico:promedios'
    else:  # reparto proporcional
        p1, p2 = rng.randint(1, 5), rng.randint(1, 5)
        if p1 == p2: raise Fallo('igual')
        unidad = rng.choice([1000, 2000, 5000])
        total = (p1 + p2) * unidad
        ans = p1 * unidad
        n1, n2 = rng.sample(NOMBRES, 2)
        q = f"{n1} y {n2} se reparten {money(total)} en proporción {p1}:{p2}. ¿Cuánto recibe {n1}?"
        exp = [f"Hay {p1}+{p2} = {p1+p2} partes; cada parte vale {total}/{p1+p2} = {unidad}.", f"{n1} recibe {p1} × {unidad} = {ans}."]
        cands = [p2 * unidad, total // 2, total // p1 if total % p1 == 0 else ans + 1000, ans + unidad, total - ans + unidad]
        fmt = lambda v: f"{money(v)}".replace(',', '.'); regla = 'numerico:reparto proporcional'
    cands = [c for c in cands if c != ans and c > 0]
    rng.shuffle(cands)
    o = opciones(fmt(ans), [fmt(c) for c in cands], rng, [fmt(ans + k * max(1, ans // 20)) for k in range(-6, 7) if k and ans + k * max(1, ans // 20) > 0])
    return item('numerico', nivel, regla, q, o, exp)


# ---------------------------------------------------------------- silogismos
TERMINOS = [('músicos', 'músico'), ('lectores', 'lector'), ('ciclistas', 'ciclista'), ('pintores', 'pintor'),
            ('viajeros', 'viajero'), ('cocineros', 'cocinero'), ('deportistas', 'deportista'), ('profesores', 'profesor'),
            ('ingenieros', 'ingeniero'), ('estudiantes', 'estudiante'), ('atletas', 'atleta'), ('escritores', 'escritor'),
            ('fotógrafos', 'fotógrafo'), ('jugadores', 'jugador'), ('nadadores', 'nadador'), ('bailarines', 'bailarín')]

def _regiones(n):
    return [r for r in range(1, 2 ** n)]  # cada región = conjunto de términos (bitmask) al que pertenece

def _modelos(n):
    regs = _regiones(n)
    for mask in range(1, 2 ** len(regs)):
        ne = [regs[i] for i in range(len(regs)) if mask >> i & 1]
        # cada término no vacío
        if all(any(r >> t & 1 for r in ne) for t in range(n)):
            yield ne

def _eval(st, ne):
    f, x, y = st
    if f == 'A': return not any((r >> x & 1) and not (r >> y & 1) for r in ne)
    if f == 'E': return not any((r >> x & 1) and (r >> y & 1) for r in ne)
    if f == 'I': return any((r >> x & 1) and (r >> y & 1) for r in ne)
    return any((r >> x & 1) and not (r >> y & 1) for r in ne)

def _texto(st, T):
    f, x, y = st
    if f == 'A': return f"Todos los {T[x][0]} son {T[y][0]}."
    if f == 'E': return f"Ningún {T[x][1]} es {T[y][1]}."
    if f == 'I': return f"Algunos {T[x][0]} son {T[y][0]}."
    return f"Algunos {T[x][0]} no son {T[y][0]}."

NINGUNA = 'Ninguna de estas conclusiones se deduce con certeza.'

def gen_silogismo(nivel, rng):
    nterm = 4 if nivel == 'MD' else 3
    T = rng.sample(TERMINOS, nterm)
    # índices: 0 = S, último = P, intermedios = medios
    if nivel == 'F':
        prem = [('A', 0, 1), ('A', 1, 2)]
        rng.shuffle(prem)
    elif nivel == 'MD':
        forms = ['A', 'A', 'E', 'I']
        prem = [(rng.choice(forms), 0, 1), (rng.choice(['A', 'A', 'E']), 1, 2), (rng.choice(['A', 'E', 'I']), 2, 3)]
        prem = [(f, y, x) if rng.random() < 0.3 and f in 'EI' else (f, x, y) for f, x, y in prem]
        rng.shuffle(prem)
    else:
        prem = [(rng.choice('AEIO'), *rng.sample([0, 1], 2)), (rng.choice('AEIO'), *rng.sample([1, 2], 2))]
        if nivel == 'M':
            prem[0] = ('A', *prem[0][1:])
            rng.shuffle(prem)
    P = nterm - 1
    cands = [(f, a, b) for f in 'AEIO' for a, b in [(0, P), (P, 0)]]
    mods = [ne for ne in _modelos(nterm) if all(_eval(p, ne) for p in prem)]
    if not mods: raise Fallo('inconsistente')
    validas = [c for c in cands if all(_eval(c, ne) for ne in mods)]
    invalidas = [c for c in cands if c not in validas]
    if nivel in ('F', 'M') and not validas: raise Fallo('sin conclusión')
    if validas:
        # preferir la conclusión más fuerte (A/E) como correcta
        validas.sort(key=lambda c: 'AEIO'.index(c[0]))
        corr = _texto(validas[0], T)
        rng.shuffle(invalidas)
        ds = [_texto(c, T) for c in invalidas[:3]] + [NINGUNA]
        exp = [f"De las premisas se deduce: {corr}", "Las otras no se cumplen en todos los casos posibles (dibuja los conjuntos para comprobarlo)."]
        k = None
    else:
        corr = NINGUNA
        rng.shuffle(invalidas)
        ds = [_texto(c, T) for c in invalidas[:4]]
        exp = ["Ninguna conclusión sobre los dos grupos extremos es segura: hay formas de dibujar los conjuntos que cumplen las premisas y contradicen cada opción."]
        k = None
    if len(ds) < 4: raise Fallo('pocas')
    o = [corr] + ds
    if len(set(o)) != 5: raise Fallo('dup')
    q = "Premisas:\n" + "\n".join(_texto(p, T) for p in prem) + "\n¿Qué conclusión se deduce con certeza? (Supón que cada grupo tiene al menos un miembro.)"
    return item('silogismo', nivel, f"silogismo:{''.join(p[0] for p in prem)}", q, o, exp, x={'lines': [_texto(p, T) for p in prem]})


# ---------------------------------------------------------------- condicionales
def gen_condicional(nivel, rng):
    A, B, C = rng.sample(NOMBRES, 3)
    V = [A, B, C]
    # reglas como funciones sobre asignación (a, b, c)
    if nivel == 'F':
        kind = rng.choice(['MP', 'MT'])
        reglas = [(lambda s: (not s[0]) or s[1], f"Si {A} va a la fiesta, entonces {B} va.")]
        hecho = (0, True) if kind == 'MP' else (1, False)
        rid = 'condicional:' + ('afirmar el antecedente' if kind == 'MP' else 'negar el consecuente')
    elif nivel == 'M':
        kind = rng.choice(['AC', 'DA', 'MT'])
        reglas = [(lambda s: (not s[0]) or s[1], f"Si {A} va a la fiesta, entonces {B} va.")]
        hecho = {'AC': (1, True), 'DA': (0, False), 'MT': (1, False)}[kind]
        rid = {'AC': 'condicional:falacia afirmar consecuente', 'DA': 'condicional:falacia negar antecedente', 'MT': 'condicional:negar el consecuente'}[kind]
    elif nivel == 'D':
        reglas = [(lambda s: (not s[0]) or s[1], f"Si {A} va, entonces {B} va."),
                  (lambda s: (not s[1]) or s[2], f"Si {B} va, entonces {C} va.")]
        hecho = rng.choice([(2, False), (0, True), (2, True)])
        rid = 'condicional:cadena'
    else:
        kind = rng.choice(['solo_si', 'a_menos'])
        if kind == 'solo_si':
            reglas = [(lambda s: (not s[0]) or s[1], f"{A} va a la fiesta solo si {B} va."),
                      (lambda s: (not s[1]) or not s[2], f"Si {B} va, {C} no va.")]
            hecho = rng.choice([(2, True), (0, True)])
            rid = 'condicional:solo si'
        else:
            reglas = [(lambda s: s[0] or s[1], f"{A} va a la fiesta, a menos que {B} vaya."),
                      (lambda s: (not s[2]) or not s[1], f"Si {C} va, {B} no va.")]
            hecho = rng.choice([(2, True), (0, False)])
            rid = 'condicional:a menos que'
    mods = [s for s in itertools.product([False, True], repeat=3)
            if all(f(s) for f, _ in reglas) and s[hecho[0]] == hecho[1]]
    if not mods: raise Fallo('inconsistente')
    est = {}
    for i in range(3):
        vals = {s[i] for s in mods}
        est[i] = None if len(vals) == 2 else vals.pop()
    def frase(i, v):
        return f"{V[i]} va." if v else f"{V[i]} no va."
    correctas, incorrectas = [], []
    for i in range(3):
        if i == hecho[0]: continue
        for v in (True, False):
            (correctas if est[i] == v else incorrectas).append(frase(i, v))
        (correctas if est[i] is None else incorrectas).append(f"No se puede saber si {V[i]} va.")
    # elegir una correcta sobre la variable más relevante (la que no es el hecho)
    rng.shuffle(correctas)
    if not correctas: raise Fallo('sin correcta')
    corr = correctas[0]
    # evitar dos opciones correctas: solo incorrectas como distractores
    rng.shuffle(incorrectas)
    ds = incorrectas[:4]
    if len(ds) < 4: raise Fallo('pocas')
    hecho_txt = frase(hecho[0], hecho[1])
    q = "\n".join(t for _, t in reglas) + f"\nSe sabe que: {hecho_txt}\n¿Qué se puede concluir con certeza?"
    exp = [f"Correcta: {corr}"]
    if 'falacia' in rid:
        exp.append("Ojo: de «si P entonces Q» y «Q» (o «no P») no se puede concluir nada sobre la otra parte: es una falacia.")
    elif 'solo si' in rid:
        exp.append("«P solo si Q» significa «si P, entonces Q».")
    elif 'a menos' in rid:
        exp.append("«P, a menos que Q» significa «si no Q, entonces P».")
    else:
        exp.append("«Si P entonces Q» con «no Q» permite concluir «no P» (contrapositiva).")
    return item('condicional', nivel, rid, q, [corr] + ds, exp, x={'lines': [t for _, t in reglas] + [f"Se sabe que: {hecho_txt}"]})


# ---------------------------------------------------------------- ordenamiento
def gen_ordenamiento(nivel, rng):
    n = {'F': 4, 'M': 5, 'D': 5, 'MD': 6}[nivel]
    names = rng.sample(NOMBRES, n)
    orden = names[:]  # orden[0] = el más alto
    rng.shuffle(orden)
    pos = {p: i for i, p in enumerate(orden)}
    pool = []
    for a, b in itertools.permutations(names, 2):
        if pos[a] < pos[b]:
            pool.append((f"{a} mide más que {b}.", lambda P, a=a, b=b: P[a] < P[b]))
            pool.append((f"{b} mide menos que {a}.", lambda P, a=a, b=b: P[a] < P[b]))
    if nivel in ('D', 'MD'):
        for a, b in itertools.combinations(names, 2):
            d = abs(pos[a] - pos[b])
            if d == 2:
                pool.append((f"Entre {a} y {b} hay exactamente una persona.", lambda P, a=a, b=b: abs(P[a] - P[b]) == 2))
            if d == 1:
                pool.append((f"{a} y {b} quedan uno al lado del otro en la fila por estatura.", lambda P, a=a, b=b: abs(P[a] - P[b]) == 1))
        pool.append((f"{orden[-1]} es la persona más baja.", lambda P, x=orden[-1]: P[x] == n - 1))
        for p in names:
            if pos[p] not in (0, n - 1):
                pool.append((f"{p} no es la persona más alta ni la más baja.", lambda P, p=p: P[p] not in (0, n - 1)))
    rng.shuffle(pool)
    perms = [dict(zip(pp, range(n))) for pp in itertools.permutations(names)]
    clues = []
    def cand(cl):
        return [P for P in perms if all(f(P) for _, f in cl)]
    for c in pool:
        if len(cand(clues)) == 1: break
        clues.append(c)
    if len(cand(clues)) != 1: raise Fallo('no única')
    for c in clues[:]:  # quitar pistas sobrantes
        rest = [x for x in clues if x is not c]
        if len(cand(rest)) == 1: clues = rest
    if len(clues) > {'F': 4, 'M': 5, 'D': 6, 'MD': 7}[nivel]: raise Fallo('muchas')
    k = rng.randrange(n)
    etiqueta = ['la persona más alta', 'la segunda persona más alta', 'la tercera persona más alta', 'la cuarta persona más alta', 'la quinta persona más alta', 'la sexta persona más alta']
    pregunta = 'la persona más baja' if k == n - 1 else etiqueta[k]
    ans = orden[k]
    ds = [p for p in names if p != ans]
    rng.shuffle(ds)
    ds = ds[:4]
    if len(ds) < 4: ds.append('No se puede saber')
    q = "\n".join(t for t, _ in clues) + f"\n¿Quién es {pregunta}?"
    exp = ["Orden de más alto a más bajo: " + " > ".join(orden) + ".", "Tip: dibuja una fila y ve ubicando a cada persona pista por pista."]
    return item('ordenamiento', nivel, 'logica:ordenamiento', q, [ans] + ds, exp, x={'lines': [t for t, _ in clues]})


# ---------------------------------------------------------------- verdades y mentiras
def gen_verdad_mentira(nivel, rng):
    n = 4 if nivel == 'MD' else 3
    names = rng.sample(NOMBRES, n)
    def stmts(i):
        out = []
        for j in range(n):
            if j == i: continue
            out.append((f"{names[j]} miente.", lambda s, j=j: not s[j]))
            out.append((f"{names[j]} dice la verdad.", lambda s, j=j: s[j]))
        for j, k in itertools.combinations([x for x in range(n) if x != i], 2):
            out.append((f"{names[j]} y {names[k]} son del mismo tipo (los dos dicen la verdad o los dos mienten).", lambda s, j=j, k=k: s[j] == s[k]))
            if nivel != 'F':
                out.append((f"Al menos uno de {names[j]} y {names[k]} miente.", lambda s, j=j, k=k: not (s[j] and s[k])))
        if nivel in ('D', 'MD'):
            for c in range(0, n + 1):
                pal = {0: 'Ninguno', 1: 'Exactamente uno', 2: 'Exactamente dos', 3: 'Exactamente tres', 4: 'Los cuatro'}[c]
                out.append((f"{pal} de nosotros {'dice' if c == 1 else 'decimos'} la verdad." if c not in (0,) else "Ninguno de nosotros dice la verdad.", lambda s, c=c: sum(s) == c))
        return out
    for _ in range(200):
        dichos = [rng.choice(stmts(i)) for i in range(n)]
        sols = [s for s in itertools.product([False, True], repeat=n)
                if all(dichos[i][1](s) == s[i] for i in range(n))]
        if len(sols) == 1:
            break
    else:
        raise Fallo('no única')
    sol = sols[0]
    def desc(s):
        vs = [names[i] for i in range(n) if s[i]]
        if not vs: return 'Ninguno dice la verdad'
        if len(vs) == n: return 'Todos dicen la verdad'
        if len(vs) == 1: return f'Solo {vs[0]} dice la verdad'
        return ' y '.join([', '.join(vs[:-1]), vs[-1]]) + ' dicen la verdad'
    ans = desc(sol)
    others = [desc(s) for s in itertools.product([False, True], repeat=n) if s != sol]
    rng.shuffle(others)
    q = "Cada persona siempre dice la verdad o siempre miente.\n" + "\n".join(f"{names[i]}: «{dichos[i][0]}»" for i in range(n)) + "\n¿Quién o quiénes dicen la verdad?"
    exp = [f"Solución: {ans}.", "Método: prueba cada combinación (por ejemplo, supón que el primero dice la verdad) y busca contradicciones."]
    return item('verdad_mentira', nivel, 'logica:verdades y mentiras', q, [ans] + others[:4], exp,
                x={'lines': [f"{names[i]}: «{dichos[i][0]}»" for i in range(n)]})


# ---------------------------------------------------------------- tablas lógicas
ATRIBUTOS = {
    'color': ['rojo', 'azul', 'verde', 'amarillo'],
    'mascota': ['perro', 'gato', 'pez', 'loro'],
    'deporte': ['fútbol', 'tenis', 'natación', 'ciclismo'],
}
FEM = {'rojo': 'roja', 'amarillo': 'amarilla'}
ATXT = {'color': ('la casa', 'de color {v}', 'vive en la casa {v}'), 'mascota': ('la mascota', '{v}', 'tiene un {v}'),
        'deporte': ('el deporte', '{v}', 'practica {v}')}

def gen_tabla_logica(nivel, rng):
    n, attrs = {'F': (3, ['mascota']), 'M': (3, ['color', 'mascota']), 'D': (4, ['color', 'mascota']), 'MD': (4, ['color', 'mascota'])}[nivel]
    names = rng.sample(NOMBRES, n)
    vals = {a: rng.sample(ATRIBUTOS[a], n) for a in attrs}
    sol = {a: dict(zip(names, rng.sample(vals[a], n))) for a in attrs}
    def fv(a, v): return FEM.get(v, v) if a == 'color' else v
    def has(a, p, v): return f"{p} {ATXT[a][2].format(v=fv(a, v))}."
    def hasnot(a, p, v): return f"{p} no {ATXT[a][2].format(v=fv(a, v))}."
    pool = []
    for a in attrs:
        for p in names:
            for v in vals[a]:
                if sol[a][p] == v:
                    pool.append((has(a, p, v), lambda S, a=a, p=p, v=v: S[a][p] == v, 1))
                else:
                    pool.append((hasnot(a, p, v), lambda S, a=a, p=p, v=v: S[a][p] != v, 3))
    for a, b in itertools.permutations(attrs, 2):
        for p in names:
            va, vb = sol[a][p], sol[b][p]
            pool.append((f"Quien {ATXT[a][2].format(v=fv(a, va))} {ATXT[b][2].format(v=fv(b, vb))}.",
                         lambda S, a=a, b=b, va=va, vb=vb: any(S[a][q] == va and S[b][q] == vb for q in names), 2))
            for vb2 in vals[b]:
                if vb2 != vb:
                    pool.append((f"Quien {ATXT[a][2].format(v=fv(a, va))} no {ATXT[b][2].format(v=fv(b, vb2))}.",
                                 lambda S, a=a, b=b, va=va, vb2=vb2: not any(S[a][q] == va and S[b][q] == vb2 for q in names), 3))
    # preferir pistas indirectas: ordenar por peso aleatorio favoreciendo negativas/cruzadas
    rng.shuffle(pool)
    pool.sort(key=lambda c: -c[2] * rng.random())
    sols = []
    for combo in itertools.product(*[list(itertools.permutations(vals[a])) for a in attrs]):
        sols.append({a: dict(zip(names, combo[i])) for i, a in enumerate(attrs)})
    def cand(cl): return [S for S in sols if all(f(S) for _, f, _ in cl)]
    clues = []
    for c in pool:
        if len(cand(clues)) == 1: break
        clues.append(c)
    if len(cand(clues)) != 1: raise Fallo('no única')
    for c in clues[:]:
        rest = [x for x in clues if x is not c]
        if len(cand(rest)) == 1: clues = rest
    if len(clues) > {'F': 3, 'M': 6, 'D': 10, 'MD': 8}[nivel]: raise Fallo('muchas')
    rng.shuffle(clues)
    a = rng.choice(attrs); p = rng.choice(names)
    corr = has(a, p, sol[a][p])
    falsas = [has(a2, p2, v) for a2 in attrs for p2 in names for v in vals[a2] if sol[a2][p2] != v]
    rng.shuffle(falsas)
    q = f"{', '.join(names[:-1])} y {names[-1]} " + " y ".join(
        {'color': 'viven cada uno en una casa de distinto color', 'mascota': 'tienen cada uno una mascota distinta',
         'deporte': 'practican cada uno un deporte distinto'}[x] for x in attrs) + ".\n" + "\n".join(t for t, _, _ in clues) + "\n¿Cuál de estas afirmaciones es cierta?"
    exp = ["Solución: " + "; ".join(f"{pp}: " + ", ".join(sol[x][pp] for x in attrs) for pp in names) + ".",
           "Método: haz una tabla (personas × opciones), marca ✗ con cada pista negativa y completa por descarte."]
    return item('tabla_logica', nivel, 'logica:tabla', q, [corr] + falsas[:4], exp, x={'lines': [t for t, _, _ in clues]})


# ---------------------------------------------------------------- analogías verbales (banco escrito a mano)
# (A, B, C, correcta, [4 distractores], relación, nivel)
ANALOGIAS = [
    ('Pez', 'nadar', 'pájaro', 'volar', ['nido', 'pluma', 'árbol', 'cantar'], 'cómo se mueve', 'F'),
    ('Médico', 'hospital', 'profesor', 'colegio', ['libro', 'alumno', 'clase', 'tiza'], 'lugar de trabajo', 'F'),
    ('Tijera', 'cortar', 'lápiz', 'escribir', ['papel', 'punta', 'borrar', 'madera'], 'función', 'F'),
    ('Frío', 'calor', 'oscuro', 'claro', ['noche', 'negro', 'sombra', 'luz'], 'opuesto', 'F'),
    ('Dedo', 'mano', 'hoja', 'árbol', ['verde', 'rama', 'raíz', 'otoño'], 'parte-todo', 'F'),
    ('Perro', 'ladrar', 'gato', 'maullar', ['ronronear', 'cazar', 'dormir', 'saltar'], 'sonido', 'F'),
    ('Libro', 'leer', 'canción', 'escuchar', ['música', 'radio', 'letra', 'disco'], 'acción típica de quien la recibe', 'F'),
    ('Semilla', 'planta', 'huevo', 'pollo', ['gallina', 'nido', 'cáscara', 'yema'], 'origen-resultado', 'F'),
    ('Pintor', 'pincel', 'carpintero', 'martillo', ['madera', 'mesa', 'taller', 'clavo'], 'herramienta', 'F'),
    ('Ojo', 'ver', 'oído', 'oír', ['oreja', 'sonido', 'hablar', 'música'], 'función', 'F'),
    ('Rápido', 'lento', 'alto', 'bajo', ['grande', 'largo', 'altura', 'pequeño'], 'opuesto', 'F'),
    ('Abeja', 'colmena', 'hormiga', 'hormiguero', ['insecto', 'reina', 'tierra', 'trabajo'], 'vivienda', 'F'),
    ('Lluvia', 'paraguas', 'sol', 'gafas', ['calor', 'verano', 'playa', 'luz'], 'protección', 'M'),
    ('Pie', 'zapato', 'mano', 'guante', ['dedo', 'anillo', 'brazo', 'uña'], 'lo que lo cubre', 'M'),
    ('Capitán', 'barco', 'piloto', 'avión', ['aeropuerto', 'vuelo', 'pasajero', 'cielo'], 'quien lo dirige', 'M'),
    ('Kilómetro', 'distancia', 'kilogramo', 'masa', ['gramo', 'balanza', 'volumen', 'peso neto'], 'unidad-magnitud', 'M'),
    ('Sed', 'agua', 'hambre', 'comida', ['estómago', 'plato', 'cocina', 'dieta'], 'necesidad-satisfacción', 'M'),
    ('Escritor', 'novela', 'compositor', 'sinfonía', ['piano', 'orquesta', 'nota', 'músico'], 'autor-obra', 'M'),
    ('Termómetro', 'temperatura', 'reloj', 'tiempo', ['hora', 'alarma', 'aguja', 'pulsera'], 'instrumento-medida', 'M'),
    ('Cachorro', 'perro', 'potro', 'caballo', ['yegua', 'establo', 'crin', 'jinete'], 'cría-adulto', 'M'),
    ('Mar', 'gota', 'desierto', 'grano', ['sol', 'calor', 'duna', 'oasis'], 'todo-unidad mínima', 'M'),
    ('Hielo', 'sólido', 'vapor', 'gaseoso', ['agua', 'líquido', 'nube', 'frío'], 'estado de la materia', 'D'),
    ('Ciego', 'ver', 'mudo', 'hablar', ['oír', 'gritar', 'silencio', 'boca'], 'incapacidad', 'M'),
    ('Arquitecto', 'plano', 'músico', 'partitura', ['canción', 'concierto', 'guitarra', 'nota'], 'documento de trabajo', 'D'),
    ('Sequía', 'lluvia', 'ignorancia', 'conocimiento', ['escuela', 'error', 'duda', 'libro'], 'carencia de', 'D'),
    ('Vela', 'cera', 'mesa', 'madera', ['silla', 'mueble', 'carpintero', 'patas'], 'material', 'D'),
    ('Bosque', 'árbol', 'biblioteca', 'libro', ['estante', 'lector', 'silencio', 'página'], 'conjunto-elemento', 'D'),
    ('Infancia', 'vejez', 'amanecer', 'anochecer', ['mediodía', 'día', 'sol', 'mañana'], 'inicio-final', 'D'),
    ('Herida', 'cicatriz', 'incendio', 'ceniza', ['fuego', 'humo', 'bombero', 'calor'], 'consecuencia que queda', 'D'),
    ('Timón', 'barco', 'volante', 'carro', ['rueda', 'motor', 'conductor', 'carretera'], 'mecanismo de dirección', 'D'),
    ('Novela', 'capítulo', 'edificio', 'piso', ['ladrillo', 'ascensor', 'ciudad', 'arquitecto'], 'todo-parte en serie', 'D'),
    ('Prólogo', 'epílogo', 'prefijo', 'sufijo', ['palabra', 'raíz', 'letra', 'acento'], 'antes-después', 'MD'),
    ('Miope', 'gafas', 'cojo', 'muleta', ['pierna', 'caminar', 'silla', 'médico'], 'ayuda para una limitación', 'MD'),
    ('Erosión', 'roca', 'óxido', 'hierro', ['agua', 'tiempo', 'metal', 'rojo'], 'proceso que desgasta', 'MD'),
    ('Cosecha', 'siembra', 'respuesta', 'pregunta', ['examen', 'duda', 'diálogo', 'solución'], 'efecto-causa', 'MD'),
    ('Pródigo', 'tacaño', 'valiente', 'cobarde', ['héroe', 'miedo', 'fuerte', 'audaz'], 'antónimos', 'MD'),
    ('Mapa', 'territorio', 'partitura', 'música', ['nota', 'pentagrama', 'músico', 'piano'], 'representación-lo representado', 'MD'),
    ('Juez', 'sentencia', 'médico', 'diagnóstico', ['hospital', 'paciente', 'estetoscopio', 'bata'], 'decisión profesional', 'MD'),
    ('Vacuna', 'enfermedad', 'antivirus', 'virus informático', ['computador', 'programa', 'internet', 'contraseña'], 'prevención', 'MD'),
    ('Germinar', 'semilla', 'eclosionar', 'huevo', ['pollito', 'nido', 'cáscara', 'gallina'], 'proceso de nacer', 'MD'),
]

def banco_analogias(rng):
    out = []
    for i, (a, b, c, d, ds, rel, lvl) in enumerate(ANALOGIAS):
        q = f"{a} es a {b.lower()} como {c.lower()} es a…"
        out.append(item('analogia_verbal', lvl, f'verbal:{rel}', q, [d] + ds,
                        [f"Relación: {rel}. {a} → {b}; {c} → {d}."]))
    return out


# ---------------------------------------------------------------- cubos (desarrollos plegables)
def _fold(cells):
    """Pliega un desarrollo (lista de (fila, col)). Devuelve {celda: normal} o None si no es un cubo."""
    cells = set(cells)
    start = min(cells)
    st = {start: ((0, 0, -1), (1, 0, 0), (0, 1, 0))}  # normal, derecha, arriba
    neg = lambda v: tuple(-x for x in v)
    cola = [start]
    while cola:
        c = cola.pop()
        n, r, u = st[c]
        for (dr, dc), (n2, r2, u2) in [((0, 1), (r, neg(n), u)), ((0, -1), (neg(r), n, u)),
                                       ((-1, 0), (u, r, neg(n))), ((1, 0), (neg(u), r, n))]:
            nb = (c[0] + dr, c[1] + dc)
            if nb in cells and nb not in st:
                st[nb] = (n2, r2, u2); cola.append(nb)
    if len(st) != 6 or len({v[0] for v in st.values()}) != 6:
        return None
    return {c: v[0] for c, v in st.items()}

def _desarrollos():
    res, vistos = [], set()
    from itertools import combinations
    grid = [(r, c) for r in range(4) for c in range(5)]
    for comb in combinations(grid, 6):
        s = set(comb)
        # conexo
        stack, seen = [comb[0]], {comb[0]}
        while stack:
            x = stack.pop()
            for d in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                y = (x[0] + d[0], x[1] + d[1])
                if y in s and y not in seen: seen.add(y); stack.append(y)
        if len(seen) != 6: continue
        mr, mc = min(r for r, _ in s), min(c for _, c in s)
        norm = tuple(sorted((r - mr, c - mc) for r, c in s))
        if norm in vistos: continue
        vistos.add(norm)
        f = _fold(norm)
        if f: res.append((norm, f))
    return res

_NETS = None
SIMBOLOS_CUBO = ['★', '●', '▲', '■', '◆', '♥', '✚', '☾']

def gen_cubo(nivel, rng):
    global _NETS
    if _NETS is None: _NETS = _desarrollos()
    # desarrollos en cruz/“T” = más fáciles; los de escalera = más difíciles
    def ancho(net): return max(c for _, c in net[0]) + 1, max(r for r, _ in net[0]) + 1
    faciles = [n for n in _NETS if 4 in ancho(n) and sum(1 for r, c in n[0] if r == 1) == 4]
    net, fold = rng.choice(faciles if nivel == 'F' else _NETS)
    cells = list(net)
    sims = rng.sample(SIMBOLOS_CUBO, 6)
    lab = dict(zip(cells, sims))
    by_normal = {fold[c]: lab[c] for c in cells}
    opp = {lab[c]: by_normal[tuple(-x for x in fold[c])] for c in cells}
    R, C = max(r for r, _ in cells) + 1, max(c for _, c in cells) + 1
    grid = [[lab.get((r, c), '') for c in range(C)] for r in range(R)]
    if nivel in ('F', 'M'):
        s = rng.choice(sims)
        ans = opp[s]
        ds = [x for x in sims if x not in (s, ans)]
        rng.shuffle(ds)
        q = f"Al armar el cubo, ¿qué cara queda opuesta a {s}?"
        exp = [f"Al plegar, {s} y {ans} quedan en caras paralelas.", "Tip: dos caras separadas por una sola cara en línea recta siempre quedan opuestas."]
        return item('cubo', nivel, 'espacial:caras opuestas', q, [ans] + ds[:4], exp, x={'net': grid})
    if nivel == 'D':
        pares_op = sorted({tuple(sorted((a, b))) for a, b in opp.items()})
        corr = rng.choice(pares_op)
        vecinos = [tuple(sorted((a, b))) for a, b in itertools.combinations(sims, 2) if opp[a] != b]
        rng.shuffle(vecinos)
        fmt = lambda p: f"{p[0]} y {p[1]}"
        q = "Al armar el cubo, ¿qué par de caras NUNCA se puede ver al mismo tiempo?"
        exp = [f"{corr[0]} y {corr[1]} quedan opuestas, así que nunca se ven a la vez.", "Las demás parejas son caras vecinas."]
        return item('cubo', nivel, 'espacial:caras opuestas', q, [fmt(corr)] + [fmt(p) for p in vecinos[:4]], exp, x={'net': grid})
    # MD: esquinas (tres caras que se tocan)
    trios_ok = [t for t in itertools.combinations(sims, 3) if all(opp[a] != b for a, b in itertools.combinations(t, 2))]
    trios_no = [t for t in itertools.combinations(sims, 3) if not all(opp[a] != b for a, b in itertools.combinations(t, 2))]
    corr = rng.choice(trios_ok)
    rng.shuffle(trios_no)
    fmt = lambda t: ', '.join(t)
    q = "Al armar el cubo, ¿cuál de estos tríos de caras puede verse a la vez en una esquina?"
    exp = [f"{fmt(corr)} son tres caras vecinas entre sí.", "Cada una de las otras opciones incluye dos caras opuestas, que nunca se tocan."]
    return item('cubo', nivel, 'espacial:esquinas', q, [fmt(corr)] + [fmt(t) for t in trios_no[:4]], exp, x={'net': grid})


GENERADORES = {
    'serie_num': gen_serie_num, 'serie_letras': gen_serie_letras, 'numeros_figura': gen_numeros_figura,
    'simbolos': gen_simbolos, 'operador': gen_operador, 'algoritmo': gen_algoritmo, 'codificacion': gen_codificacion,
    'numerico': gen_numerico, 'silogismo': gen_silogismo, 'condicional': gen_condicional, 'ordenamiento': gen_ordenamiento,
    'verdad_mentira': gen_verdad_mentira, 'tabla_logica': gen_tabla_logica, 'cubo': gen_cubo,
}
