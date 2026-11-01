#!/usr/bin/env python3
"""Generador de examenes de razonamiento logico y abstracto (practica tipo psicotecnico).

Entrada: un plan JSON con preguntas de texto (escritas por quien arma el examen) y
especificaciones de preguntas de figuras (generadas y verificadas aqui).
Salida: examen.pdf (solo preguntas), respuestas.pdf (clave y explicaciones) y clave.json.

Tipos de figuras: matriz, serie, rotacion, superposicion, domino, intrusa, analogia.
Niveles: F (facil), M (media), D (dificil), MD (muy dificil).
Cada pregunta de figuras se verifica: exactamente UNA opcion es compatible con alguna
regla del repertorio del tipo (por filas o columnas en matrices).

Uso: python3 examen.py --plan plan.json --salida carpeta
     python3 examen.py --autotest 300   (prueba de estres)
"""
import argparse
import json
import math
import os
import random
import sys
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

LETRAS = "ABCDE"
FORMAS = ["triángulo", "cuadrado", "pentágono", "círculo", "estrella"]
TAMANOS = ["pequeño", "mediano", "grande"]
COLORES = ["blanco", "gris", "negro"]
COLOR_HEX = ["white", "#808080", "black"]
RADIOS = [0.05, 0.085, 0.12]
NIVEL_N = {"F": 1, "M": 2, "D": 3, "MD": 4}
NOMBRE_NIVEL = {"F": "fácil", "M": "media", "D": "difícil", "MD": "muy difícil"}
NOMBRE_ATTR = {"forma": "forma", "cantidad": "cantidad", "tamano": "tamaño", "color": "color",
               "ang": "giro de la flecha", "pos": "posición del punto", "col": "color de la flecha",
               "arriba": "mitad de arriba", "abajo": "mitad de abajo"}
POSICIONES = {1: [4], 2: [3, 5], 3: [3, 4, 5], 4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8],
              6: [0, 2, 3, 5, 6, 8], 7: [0, 2, 3, 4, 5, 6, 8], 8: [0, 1, 2, 3, 5, 6, 7, 8], 9: list(range(9))}


class Fallo(Exception):
    pass


# ============================================================ utilidades de reglas en secuencias
def es_constante(v):
    return all(x == v[0] for x in v)


def es_aritmetica(v, mod=None):
    if len(v) < 2:
        return True
    d = v[1] - v[0]
    for i in range(1, len(v) - 1):
        e = v[i + 1] - v[i]
        if mod:
            if (e - d) % mod:
                return False
        elif e != d:
            return False
    return True


def es_periodica(v, p):
    return len(v) > p and all(v[i] == v[i - p] for i in range(p, len(v)))


def es_intercalada(v, mod=None):
    return len(v) >= 5 and es_aritmetica(v[0::2], mod) and es_aritmetica(v[1::2], mod)


def secuencia_explicable(v, clase):
    """clase: 'num' (aritmetica sin modulo), 'mod7', 'mod8', 'cat' (categorica)."""
    if es_constante(v) or es_periodica(v, 2) or es_periodica(v, 3):
        return True
    if clase == "num":
        return es_aritmetica(v) or es_intercalada(v)
    if clase == "mod7":
        return es_aritmetica(v, 7) or es_intercalada(v, 7)
    if clase == "mod8":
        return es_aritmetica(v, 8) or es_intercalada(v, 8)
    return False


def elegir_distractores(correcta, alternativas, rng, validar, cobertura=True, n=4):
    """alternativas: {atributo: [valores trampa]}. Combina cambios (estilo I-RAVEN) y
    devuelve n opciones invalidas y distintas, cubriendo cada atributo cambiado."""
    attrs = [a for a in alternativas if alternativas[a]][:4]
    if len(attrs) < 2:
        raise Fallo("sin alternativas")
    for _ in range(80):
        # un solo valor trampa por atributo: las opciones son vertices de un "cubo" de cambios
        # (como I-RAVEN), asi ningun valor domina y no se puede adivinar por mayoria
        alt = {a: rng.choice(alternativas[a]) for a in attrs}
        elegidos, vistos = [], {clave(correcta)}
        combos = []
        for mask in range(1, 2 ** len(attrs)):
            o = dict(correcta)
            cambiados = []
            for i, a in enumerate(attrs):
                if mask >> i & 1:
                    o[a] = alt[a]
                    cambiados.append(a)
            combos.append((o, cambiados))
        rng.shuffle(combos)
        for o, cam in combos:
            k = clave(o)
            if k in vistos or validar(o):
                continue
            vistos.add(k)
            elegidos.append((o, cam))
            if len(elegidos) == n:
                break
        if len(elegidos) < n:
            continue
        if cobertura:
            cubiertos = {a for _, cam in elegidos for a in cam}
            if not set(attrs) <= cubiertos:
                continue
        # Medido con 1.000 preguntas por tipo: elegir la opcion "mas parecida a las demas" o la
        # "menos parecida" acierta ~20% (igual que el azar), asi que no hay atajo sin razonar.
        return elegidos
    raise Fallo("no se pudieron elegir distractores")


def clave(o):
    return tuple(sorted((k, tuple(sorted(v)) if isinstance(v, (set, frozenset)) else v) for k, v in o.items()))


def trampa_de(elegidos):
    for i, (o, cam) in enumerate(elegidos):
        if len(cam) == 1:
            return i, f"tiene todo bien excepto {NOMBRE_ATTR.get(cam[0], cam[0])}"
    return None, None


# ============================================================ MATRIZ 3x3 (forma, cantidad, tamano, color)
MATRIZ_ATTR = {
    "forma": (0, 4, ["constante", "distribucion"]),
    "cantidad": (1, 9, ["constante", "progresion", "aritmetica", "distribucion"]),
    "tamano": (0, 2, ["constante", "progresion", "distribucion"]),
    "color": (0, 2, ["constante", "progresion", "distribucion"]),
}


def _m_const(f):
    return all(r[0] == r[1] == r[2] for r in f)


def _m_prog(f):
    d = f[0][1] - f[0][0]
    return d != 0 and all(r[1] - r[0] == d and r[2] - r[1] == d for r in f)


def _m_arit(f):
    return all(r[2] == r[0] + r[1] for r in f) or all(r[2] == r[0] - r[1] and r[2] > 0 for r in f)


def _m_dist(f):
    s = set(f[0])
    if len(s) != 3 or any(set(r) != s for r in f) or len({tuple(r) for r in f}) != 3:
        return False
    return all({f[r][c] for r in range(3)} == s for c in range(3))


M_VALIDA = {"constante": _m_const, "progresion": _m_prog, "aritmetica": _m_arit, "distribucion": _m_dist}


def matriz_valida(m, op):
    for a, (_, _, reglas) in MATRIZ_ATTR.items():
        g = [[m[r][c][a] if (r, c) != (2, 2) else op[a] for c in range(3)] for r in range(3)]
        cols = [[g[r][c] for r in range(3)] for c in range(3)]
        if not any(M_VALIDA[x](g) or M_VALIDA[x](cols) for x in reglas):
            return False
    return True


def _m_filas(a, regla, rng, nivel):
    lo, hi, _ = MATRIZ_ATTR[a]
    if regla == "constante":
        vals = rng.sample(range(lo, hi + 1), 3)
        return [[v] * 3 for v in vals], {}
    if regla == "progresion":
        pasos = [1, -1] + ([2, -2] if a == "cantidad" and nivel in ("D", "MD") else [])
        d = rng.choice(pasos)
        filas = []
        for _ in range(3):
            s = rng.choice([s for s in range(lo, hi + 1) if lo <= s + 2 * d <= hi])
            filas.append([s, s + d, s + 2 * d])
        return filas, {"paso": d}
    if regla == "aritmetica":
        op = rng.choice(["suma", "resta"])
        filas = []
        for _ in range(3):
            if op == "suma":
                x = rng.randint(1, 5)
                y = rng.randint(1, 9 - x)
                filas.append([x, y, x + y])
            else:
                x = rng.randint(3, 9)
                y = rng.randint(1, x - 1)
                filas.append([x, y, x - y])
        return filas, {"operacion": op}
    vals = rng.sample(range(lo, hi + 1), 3)
    sh = rng.choice([1, 2])
    return [[vals[(c + sh * r) % 3] for c in range(3)] for r in range(3)], {"valores": vals}


def _nombre_valor(a, v):
    return {"forma": FORMAS, "tamano": TAMANOS, "color": COLORES}[a][v] if a in ("forma", "tamano", "color") else str(v)


def _m_desc(a, regla, ex):
    n = NOMBRE_ATTR[a].capitalize()
    if regla == "progresion":
        d = ex["paso"]
        return f"{n}: {'aumenta' if d > 0 else 'disminuye'} {abs(d)} en cada paso de la fila."
    if regla == "aritmetica":
        return f"{n}: tercera casilla = primera {'+' if ex['operacion'] == 'suma' else '−'} segunda."
    if regla == "distribucion":
        return f"{n}: cada fila y columna tiene una vez cada valor ({', '.join(_nombre_valor(a, v) for v in ex['valores'])})."
    return f"{n}: igual dentro de cada fila."


def gen_matriz(nivel, rng, forzar=None):
    n_var = NIVEL_N[nivel]
    for _ in range(400):
        attrs = list(MATRIZ_ATTR)
        forz = dict(forzar or {})
        variables = list(forz)
        resto = [a for a in attrs if a not in variables]
        rng.shuffle(resto)
        variables += resto[:max(0, n_var - len(variables))]
        reglas = {}
        for a in attrs:
            if a in forz:
                reglas[a] = forz[a]
            elif a in variables:
                ops = [r for r in MATRIZ_ATTR[a][2] if r != "constante"]
                if nivel in ("F", "M"):
                    ops = [r for r in ops if r != "aritmetica"]
                reglas[a] = rng.choice(ops)
            else:
                reglas[a] = "constante"
        if nivel == "MD" and not any(reglas[a] in ("aritmetica", "distribucion") for a in attrs):
            continue
        filas, ex = {}, {}
        for a in attrs:
            filas[a], ex[a] = _m_filas(a, reglas[a], rng, nivel)
        m = [[{a: filas[a][r][c] for a in attrs} for c in range(3)] for r in range(3)]
        correcta = dict(m[2][2])
        if not matriz_valida(m, correcta):
            continue
        var = [a for a in attrs if reglas[a] != "constante"]
        cons = [a for a in attrs if reglas[a] == "constante"]
        cambiar = var[:4] if nivel in ("D", "MD") else (var + cons)[:3]
        alts = {}
        for a in cambiar:
            lo, hi, _ = MATRIZ_ATTR[a]
            if a == "cantidad":
                f3 = [m[2][0][a], m[2][1][a]]
                cand = [correcta[a] + 1, correcta[a] - 1, f3[0], f3[1], f3[0] + f3[1], abs(f3[0] - f3[1])]
            else:
                cand = list(range(lo, hi + 1)) + [m[2][0][a], m[2][1][a]]
            cand = sorted({c for c in cand if lo <= c <= hi and c != correcta[a]})
            alts[a] = [rng.choice(cand)] if cand else []
        try:
            eleg = elegir_distractores(correcta, alts, rng, lambda o: matriz_valida(m, o))
        except Fallo:
            continue
        ti, tp = trampa_de(eleg)
        return {
            "tipo": "matriz", "nivel": nivel, "stem": {"matriz": m},
            "opciones": [correcta] + [o for o, _ in eleg], "correcta": 0,
            "fallos": [None] + ["; ".join(f"{a}:{reglas[a]}" for a in cam) for _, cam in eleg],
            "trampa": None if ti is None else (ti + 1, tp),
            "regla": "; ".join(f"{a}:{reglas[a]}" for a in var) or "constantes",
            "explicacion": [_m_desc(a, reglas[a], ex[a]) for a in var] or ["Todo igual dentro de cada fila."],
            "valida": lambda o, m=m: matriz_valida(m, o),
        }
    raise Fallo("matriz")


# ============================================================ SERIE de figuras en linea (5 + ?)
SERIE_CLASE = {"forma": "cat", "cantidad": "num", "tamano": "cat", "color": "cat"}


def gen_serie(nivel, rng, forzar=None):
    n_var = NIVEL_N[nivel]
    for _ in range(400):
        attrs = ["forma", "cantidad", "tamano", "color"]
        rng.shuffle(attrs)
        variables = attrs[:n_var]
        seq, desc, regla = {}, [], []
        for a in ["forma", "cantidad", "tamano", "color"]:
            if a not in variables:
                v = rng.randint(1, 5) if a == "cantidad" else rng.randint(0, {"forma": 4, "tamano": 2, "color": 2}[a])
                seq[a] = [v] * 6
                continue
            if a == "cantidad":
                tipo = rng.choice(["arit", "arit", "inter"] if nivel in ("D", "MD") else ["arit"])
                if tipo == "arit":
                    d = rng.choice([1, -1])
                    s = rng.randint(1, 4) if d > 0 else rng.randint(6, 9)
                    seq[a] = [s + d * i for i in range(6)]
                    desc.append(f"Cantidad: {'aumenta' if d > 0 else 'disminuye'} 1 en cada paso.")
                    regla.append("cantidad:progresion")
                else:
                    d1, d2 = rng.choice([(1, -1), (-1, 1), (2, -1), (1, 0)])
                    s1 = rng.randint(1, 9 - 2 * max(d1, 0))
                    s1 = max(s1, 1 - 2 * min(d1, 0))
                    s2 = rng.randint(max(1, 1 - 2 * min(d2, 0)), min(9, 9 - 2 * max(d2, 0)))
                    pares = [s1 + d1 * i for i in range(3)]
                    impares = [s2 + d2 * i for i in range(3)]
                    if not all(1 <= x <= 9 for x in pares + impares):
                        continue
                    seq[a] = [pares[0], impares[0], pares[1], impares[1], pares[2], impares[2]]
                    desc.append("Cantidad: dos series intercaladas (posiciones 1-3-5 y 2-4-6), cada una con su propio paso.")
                    regla.append("cantidad:intercalada")
            else:
                maxv = {"forma": 4, "tamano": 2, "color": 2}[a]
                p = rng.choice([2, 3] if nivel in ("M", "D", "MD") else [2])
                ciclo = rng.sample(range(maxv + 1), p)
                seq[a] = [ciclo[i % p] for i in range(6)]
                desc.append(f"{NOMBRE_ATTR[a].capitalize()}: se repite un ciclo de {p} ({', '.join(_nombre_valor(a, v) for v in ciclo)}).")
                regla.append(f"{a}:ciclo{p}")
        celdas = [{a: seq[a][i] for a in seq} for i in range(6)]
        correcta = celdas[5]

        def valida(o, celdas=celdas):
            return all(secuencia_explicable([c[a] for c in celdas[:5]] + [o[a]], SERIE_CLASE[a]) for a in o)

        if not valida(correcta):
            continue
        alts = {}
        for a in variables + [x for x in ["forma", "cantidad", "tamano", "color"] if x not in variables]:
            if len(alts) >= 3:
                break
            if a == "cantidad":
                cand = [correcta[a] + 1, correcta[a] - 1, celdas[4][a], celdas[3][a]]
                cand = [c for c in cand if 1 <= c <= 9 and c != correcta[a]]
            else:
                maxv = {"forma": 4, "tamano": 2, "color": 2}[a]
                cand = [celdas[4][a], celdas[3][a]] + list(range(maxv + 1))
                cand = [c for c in cand if c != correcta[a]]
            if cand:
                alts[a] = [rng.choice(cand)]
        try:
            eleg = elegir_distractores(correcta, alts, rng, valida)
        except Fallo:
            continue
        ti, tp = trampa_de(eleg)
        return {
            "tipo": "serie", "nivel": nivel, "stem": {"serie": celdas[:5]},
            "opciones": [correcta] + [o for o, _ in eleg], "correcta": 0,
            "fallos": [None] + ["; ".join(next((r for r in regla if r.startswith(a + ":")), "serie:" + a) for a in cam)
                                for _, cam in eleg],
            "trampa": None if ti is None else (ti + 1, tp),
            "regla": "; ".join(regla) or "constante", "explicacion": desc or ["Todo constante."], "valida": valida,
        }
    raise Fallo("serie")


# ============================================================ ROTACION (flecha que gira + punto que se mueve)
def gen_rotacion(nivel, rng, forzar=None):
    for _ in range(300):
        cfg = {"F": ([2, -2], [0], None), "M": ([1, -1], [1, -1], None),
               "D": ([3, -3], [2, -2], 2), "MD": ([3, -3], [3, -3], 3)}[nivel]
        da, dp, pcol = rng.choice(cfg[0]), rng.choice(cfg[1]), cfg[2]
        a0, p0 = rng.randrange(8), rng.randrange(8)
        ciclo = rng.sample([0, 1, 2], pcol) if pcol else [rng.choice([0, 2])]
        celdas = [{"ang": (a0 + da * i) % 8, "pos": (p0 + dp * i) % 8, "col": ciclo[i % len(ciclo)]} for i in range(6)]
        correcta = celdas[5]
        clases = {"ang": "mod8", "pos": "mod8", "col": "cat"}

        def valida(o, celdas=celdas):
            return all(secuencia_explicable([c[a] for c in celdas[:5]] + [o[a]], clases[a]) for a in o)

        if not valida(correcta):
            continue
        alts = {"ang": [(correcta["ang"] + x) % 8 for x in (1, -1, 4)] + [(-correcta["ang"]) % 8, celdas[4]["ang"]],
                "pos": [(correcta["pos"] + x) % 8 for x in (1, -1)] + [celdas[4]["pos"], (p0 - dp * 5) % 8]}
        alts["col"] = [c for c in (0, 1, 2) if c != correcta["col"]]
        alts = {k: sorted(x for x in set(v) if x != correcta[k]) for k, v in alts.items()}
        try:
            eleg = elegir_distractores(correcta, alts, rng, valida)
        except Fallo:
            continue
        ti, tp = trampa_de(eleg)
        sent = lambda d: "a la derecha (horario)" if d > 0 else "a la izquierda (antihorario)"
        desc = [f"Flecha: gira {abs(da) * 45}° {sent(da)} en cada paso."]
        if dp:
            desc.append(f"Punto: avanza {abs(dp)} casilla(s) por el borde {sent(dp)} en cada paso.")
        else:
            desc.append("Punto: no se mueve.")
        if pcol:
            desc.append(f"Color de la flecha: ciclo de {pcol} ({', '.join(COLORES[c] for c in ciclo)}).")
        return {
            "tipo": "rotacion", "nivel": nivel, "stem": {"rot": celdas[:5]},
            "opciones": [correcta] + [o for o, _ in eleg], "correcta": 0,
            "fallos": [None] + ["; ".join("rotacion:" + {"ang": "giro", "pos": "punto", "col": "color"}[a] for a in cam)
                                for _, cam in eleg],
            "trampa": None if ti is None else (ti + 1, tp),
            "regla": f"giro {da * 45}°; punto {dp:+d}" + (f"; color ciclo{pcol}" if pcol else ""),
            "explicacion": desc, "valida": valida,
        }
    raise Fallo("rotacion")


# ============================================================ SUPERPOSICION (union, interseccion, diferencia, resta)
OPS = {
    "union": (lambda a, b: a | b, "se juntan todos los puntos de las dos primeras casillas (unión)"),
    "interseccion": (lambda a, b: a & b, "solo quedan los puntos que se repiten en las dos primeras (intersección)"),
    "xor": (lambda a, b: a ^ b, "quedan los puntos que NO se repiten; los repetidos desaparecen"),
    "resta": (lambda a, b: a - b, "a la primera se le quitan los puntos de la segunda (resta)"),
}


def gen_superposicion(nivel, rng, forzar=None):
    n = 4 if nivel == "MD" else 3
    op = {"F": "union", "M": rng.choice(["interseccion", "xor"]), "D": rng.choice(["xor", "resta"]),
          "MD": rng.choice(["xor", "resta"])}[nivel]
    total = n * n
    for _ in range(500):
        filas = []
        for _r in range(3):
            a = frozenset(rng.sample(range(total), rng.randint(3, total // 2 + 1)))
            b = frozenset(rng.sample(range(total), rng.randint(3, total // 2 + 1)))
            c = frozenset(OPS[op][0](a, b))
            filas.append([a, b, c])
        if not filas[2][2] or any(not f[2] for f in filas):
            continue
        # unicidad de la operacion por filas (filas 1 y 2) y sin operacion por columnas que lleve a otra respuesta
        ops_filas = [k for k, (f, _) in OPS.items() if all(f(filas[r][0], filas[r][1]) == filas[r][2] for r in range(2))]
        if ops_filas != [op]:
            continue
        col_ok = True
        for k, (f, _) in OPS.items():
            if all(f(filas[0][c], filas[1][c]) == filas[2][c] for c in range(2)):
                if f(filas[0][2], filas[1][2]) != filas[2][2]:
                    col_ok = False
        if not col_ok:
            continue
        correcta = filas[2][2]

        def valida(o, filas=filas):
            s = o["puntos"]
            for k, (f, _) in OPS.items():
                if all(f(filas[r][0], filas[r][1]) == filas[r][2] for r in range(2)) and f(filas[2][0], filas[2][1]) == s:
                    return True
                if all(f(filas[0][c], filas[1][c]) == filas[2][c] for c in range(2)) and f(filas[0][2], filas[1][2]) == s:
                    return True
            return False

        # distractores: resultados de OTRAS operaciones y variantes de un punto de esos resultados
        # (no solo de la correcta), para que la respuesta no sea la opcion "mas central"
        pool = {}
        otros = []
        for k, (f, _) in OPS.items():
            r = frozenset(f(filas[2][0], filas[2][1]))
            if r and r != correcta and not valida({"puntos": r}):
                pool.setdefault(r, f"aplicar «{k}» en vez de la regla correcta")
                otros.append(r)
        for base in otros + [correcta]:
            for x in rng.sample(range(total), min(total, 6)):
                r = frozenset(base ^ {x})
                if r and r != correcta and not valida({"puntos": r}):
                    pool.setdefault(r, "le sobra o le falta un punto" if base == correcta else "otra regla y un punto distinto")
        if len(pool) < 4 or not otros:
            continue
        elegido = None
        for _t in range(60):
            cand = rng.sample(list(pool), 4)
            if not any(c in otros for c in cand):
                continue
            todas = [correcta] + cand
            dist = [sum(len(x ^ y) for y in todas) for x in todas]
            centro = [i for i, d in enumerate(dist) if d == min(dist)]
            lejos = [i for i, d in enumerate(dist) if d == max(dist)]
            if (centro == [0] or lejos == [0]) and rng.random() > 0.7:
                continue
            elegido = cand
            break
        if elegido is None:
            continue
        eleg = [({"puntos": c}, pool[c]) for c in elegido]
        trampa = next(((i + 1, m) for i, (_, m) in enumerate(eleg) if m.startswith("aplicar")), None)
        stem = [[{"puntos": filas[r][c]} if (r, c) != (2, 2) else None for c in range(3)] for r in range(3)]
        return {
            "tipo": "superposicion", "nivel": nivel, "stem": {"dots": stem, "n": n},
            "opciones": [{"puntos": correcta}] + [o for o, _ in eleg], "correcta": 0, "trampa": trampa,
            "fallos": [None] + [f"superposicion:{op}"] * 4,
            "regla": f"superposicion:{op}", "explicacion": [f"En cada fila, la tercera casilla: {OPS[op][1]}."],
            "valida": valida, "n": n,
        }
    raise Fallo("superposicion")


# ============================================================ DOMINO (serie de fichas, mitades 0-6, ciclo 6 -> 0)
def gen_domino(nivel, rng, forzar=None):
    for _ in range(400):
        def serie_mitad(modo):
            if modo == "const":
                v = rng.randrange(7)
                return [v] * 6, "se queda igual"
            if modo == "inter":
                s1, s2 = rng.randrange(7), rng.randrange(7)
                d1, d2 = rng.choice([1, 2, -1]), rng.choice([1, -1, 2, 3])
                if d1 == d2:
                    return None, None
                pares = [(s1 + d1 * i) % 7 for i in range(3)]
                imp = [(s2 + d2 * i) % 7 for i in range(3)]
                return [pares[0], imp[0], pares[1], imp[1], pares[2], imp[2]], \
                    f"dos series intercaladas (pasos {d1:+d} y {d2:+d})"
            d = modo
            s = rng.randrange(7)
            return [(s + d * i) % 7 for i in range(6)], f"{'suma' if d > 0 else 'resta'} {abs(d)} en cada ficha"

        modos = {"F": (1, "const"), "M": (rng.choice([1, 2, -1]), rng.choice([1, -1, 2])),
                 "D": (rng.choice([2, 3, -2]), "inter"), "MD": ("inter", rng.choice([3, -3, 2]))}[nivel]
        arr, darr = serie_mitad(modos[0])
        aba, daba = serie_mitad(modos[1])
        if arr is None or aba is None or arr == aba:
            continue
        if nivel == "M" and modos[0] == modos[1]:
            continue
        celdas = [{"arriba": arr[i], "abajo": aba[i]} for i in range(6)]
        correcta = celdas[5]

        def valida(o, celdas=celdas):
            return all(secuencia_explicable([c[a] for c in celdas[:5]] + [o[a]], "mod7") for a in o)

        if not valida(correcta):
            continue
        alts = {a: list({(correcta[a] + 1) % 7, (correcta[a] - 1) % 7, celdas[4][a]} - {correcta[a]})
                for a in ("arriba", "abajo")}
        try:
            eleg = elegir_distractores(correcta, alts, rng, valida, n=3)
        except Fallo:
            continue
        invertida = {"arriba": correcta["abajo"], "abajo": correcta["arriba"]}
        opciones = [correcta] + [o for o, _ in eleg]
        trampa = None
        if invertida != correcta and not valida(invertida) and clave(invertida) not in {clave(o) for o in opciones}:
            opciones.append(invertida)
            trampa = (len(opciones) - 1, "es la ficha correcta pero al revés (arriba y abajo cambiados)")
        else:
            extra = {"arriba": rng.randrange(7), "abajo": rng.randrange(7)}
            tries = 0
            while (valida(extra) or clave(extra) in {clave(o) for o in opciones}) and tries < 50:
                extra = {"arriba": rng.randrange(7), "abajo": rng.randrange(7)}
                tries += 1
            if tries >= 50:
                continue
            opciones.append(extra)
        if trampa is None:
            ti, tp = trampa_de(eleg)
            trampa = None if ti is None else (ti + 1, tp)
        return {
            "tipo": "domino", "nivel": nivel, "stem": {"dom": celdas[:5]},
            "opciones": opciones, "correcta": 0, "trampa": trampa,
            "fallos": [None] + ["; ".join("domino:" + a for a in cam) for _, cam in eleg] +
                      (["domino:orden de las mitades"] if len(opciones) > len(eleg) + 1 and trampa and "revés" in trampa[1]
                       else ["domino:serie"]) * (len(opciones) - len(eleg) - 1),
            "regla": f"domino arriba:{modos[0]} abajo:{modos[1]}",
            "explicacion": [f"Mitad de arriba: {darr}.", f"Mitad de abajo: {daba}.",
                            "Recuerda: en el dominó después del 6 viene el 0 (blanco)."],
            "valida": valida,
        }
    raise Fallo("domino")


# ============================================================ INTRUSA (cual no pertenece)
def gen_intrusa(nivel, rng, forzar=None):
    """5 figuras; 4 comparten un rasgo y 1 no. Ningun otro rasgo destaca a una figura:
    cada rasgo distinto del objetivo se reparte 5 iguales, 3+2, o todos distintos."""
    rasgo = {"F": "color", "M": rng.choice(["forma", "tamano"]), "D": "paridad", "MD": "paridad"}[nivel]
    maximos = {"forma": 4, "tamano": 2, "color": 2}

    def reparto(valores_posibles, permitir_distintos):
        modos = ["3+2", "5"] + (["todos"] if permitir_distintos else [])
        modo = rng.choice(modos)
        if modo == "5":
            return [rng.choice(valores_posibles)] * 5
        if modo == "todos":
            return rng.sample(valores_posibles, 5)
        x, y = rng.sample(valores_posibles, 2)
        v = [x, x, x, y, y]
        rng.shuffle(v)
        return v

    for _ in range(500):
        intr = rng.randrange(5)
        items = [dict() for _ in range(5)]
        for a in ("forma", "tamano", "color"):
            if a == rasgo:
                v = rng.randint(0, maximos[a])
                otro = rng.choice([x for x in range(maximos[a] + 1) if x != v])
                vals = [v if i != intr else otro for i in range(5)]
            else:
                vals = reparto(list(range(maximos[a] + 1)), a == "forma")
            for i in range(5):
                items[i][a] = vals[i]
        if rasgo == "paridad":
            par = rng.choice([0, 1])
            impares = [3, 5, 7, 9]
            grupo = rng.sample([2, 4, 6, 8] if par == 0 else impares, 4)
            fuera = rng.choice(impares if par == 0 else [2, 4, 6, 8])
            it = iter(grupo)
            cant = [next(it) if i != intr else fuera for i in range(5)]
        else:
            cant = reparto(list(range(1, 9)), True)
        for i in range(5):
            items[i]["cantidad"] = cant[i]
        rasgos = {"forma": [x["forma"] for x in items], "color": [x["color"] for x in items],
                  "tamano": [x["tamano"] for x in items], "cantidad": cant, "paridad": [c % 2 for c in cant]}
        extra = {"primo": [c in (2, 3, 5, 7) for c in cant], "multiplo3": [c % 3 == 0 for c in cant],
                 "cuadrado": [c in (1, 4, 9) for c in cant], "mayor5": [c > 5 for c in cant]}
        ok = len({clave(x) for x in items}) == 5
        for nombre, vals in rasgos.items():
            sing = [i for i, x in enumerate(vals) if vals.count(x) == 1]
            if nombre == rasgo:
                ok = ok and sing == [intr]
            else:
                ok = ok and len(sing) in (0, 5)
        for vals in extra.values():
            sing = [i for i, x in enumerate(vals) if vals.count(x) == 1]
            if sing and sing != [intr]:
                ok = False
        if nivel in ("D", "MD") and len(set(cant)) < 4:
            ok = False
        if nivel == "MD" and len(set(rasgos["forma"])) < 2:
            ok = False
        if not ok:
            continue
        orden = [intr] + [i for i in range(5) if i != intr]
        texto = {"color": "es la única de otro color", "forma": "es la única con otra forma",
                 "tamano": "es la única de otro tamaño",
                 "paridad": "es la única con cantidad " + ("impar" if cant[intr] % 2 else "par") +
                            " de figuras; las demás tienen cantidad " + ("par" if cant[intr] % 2 else "impar")}[rasgo]
        return {
            "tipo": "intrusa", "nivel": nivel, "stem": {}, "opciones": [items[i] for i in orden], "correcta": 0,
            "fallos": [None] + [f"intrusa:{rasgo}"] * 4,
            "trampa": None, "regla": f"intrusa:{rasgo}", "explicacion": [f"La figura correcta {texto}."],
            "valida": None, "rasgos_ok": True,
        }
    raise Fallo("intrusa")


# ============================================================ ANALOGIA (A es a B como C es a ?)
def gen_analogia(nivel, rng, forzar=None):
    k = {"F": 1, "M": 2, "D": 3, "MD": 3}[nivel]
    for _ in range(500):
        A = {"forma": rng.randrange(5), "cantidad": rng.randint(1, 5), "tamano": rng.randrange(3), "color": rng.randrange(3)}
        cambian = rng.sample(["forma", "tamano", "color", "cantidad"], k)
        B = dict(A)
        for a in cambian:
            maxv = {"forma": 4, "tamano": 2, "color": 2, "cantidad": 6}[a]
            lo = 1 if a == "cantidad" else 0
            B[a] = rng.choice([x for x in range(lo, maxv + 1) if x != A[a]])
        fijos = [a for a in A if a not in cambian]
        if not fijos:
            continue
        C = dict(A)
        n_dif = 2 if nivel == "MD" and len(fijos) >= 2 else 1
        for a in rng.sample(fijos, min(n_dif, len(fijos))):
            maxv = {"forma": 4, "tamano": 2, "color": 2, "cantidad": 6}[a]
            lo = 1 if a == "cantidad" else 0
            C[a] = rng.choice([x for x in range(lo, maxv + 1) if x != A[a]])
        resp = dict(C)
        for a in cambian:
            resp[a] = B[a]

        def valida(o, A=A, B=B, C=C):
            for a in o:
                if A[a] == B[a]:
                    if o[a] != C[a]:
                        return False
                else:
                    ok = {B[a]}
                    if a == "cantidad":
                        ok.add(C[a] + B[a] - A[a])
                    if o[a] not in ok:
                        return False
            return True

        if not valida(resp):
            continue
        # trampas: olvidar un cambio (valor de C) o cambiar lo que no debía (valor de A/B u otro)
        alts = {}
        for a in cambian:
            alts[a] = [C[a]]
        for a in fijos:
            maxv = {"forma": 4, "tamano": 2, "color": 2, "cantidad": 6}[a]
            lo = 1 if a == "cantidad" else 0
            alts[a] = [B[a]] if B[a] != C[a] else [x for x in range(lo, maxv + 1) if x != C[a]]
        orden_attrs = cambian + [a for a in fijos if B[a] != C[a]] + [a for a in fijos if B[a] == C[a]]
        alts = {a: alts[a] for a in orden_attrs[:3]}
        try:
            eleg = elegir_distractores(resp, alts, rng, valida)
        except Fallo:
            continue
        eleg = [(o, ("copiar B tal cual" if clave(o) == clave(B) else
                     "olvidar el cambio de " + ", ".join(NOMBRE_ATTR[a] for a in cam if a in cambian)
                     if all(a in cambian for a in cam) else
                     "cambiar " + ", ".join(NOMBRE_ATTR[a] for a in cam if a not in cambian) + ", que no debía cambiar"))
                for o, cam in eleg]
        trampa = next(((i + 1, m) for i, (_, m) in enumerate(eleg) if m == "copiar B tal cual" or m.startswith("olvidar")), None)
        desc = [f"De A a B cambia: {', '.join(NOMBRE_ATTR[a] for a in cambian)}. Aplica solo esos cambios a C; lo demás de C se mantiene."]
        return {
            "tipo": "analogia", "nivel": nivel, "stem": {"abc": [A, B, C]},
            "opciones": [resp] + [o for o, _ in eleg], "correcta": 0, "trampa": trampa,
            "fallos": [None] + ["analogia: " + m for _, m in eleg],
            "regla": "analogia:" + "+".join(sorted(cambian)), "explicacion": desc, "valida": valida,
        }
    raise Fallo("analogia")


GENERADORES = {"matriz": gen_matriz, "serie": gen_serie, "rotacion": gen_rotacion,
               "superposicion": gen_superposicion, "domino": gen_domino, "intrusa": gen_intrusa,
               "analogia": gen_analogia}


# ============================================================ dibujo
def poligono(n, cx, cy, r, rot=90):
    return [(cx + r * math.cos(math.radians(rot + 360 * k / n)), cy + r * math.sin(math.radians(rot + 360 * k / n)))
            for k in range(n)]


def estrella(cx, cy, r):
    return [(cx + (r if k % 2 == 0 else r * 0.45) * math.cos(math.radians(90 + 36 * k)),
             cy + (r if k % 2 == 0 else r * 0.45) * math.sin(math.radians(90 + 36 * k))) for k in range(10)]


def figura(ax, forma, cx, cy, r, color):
    kw = dict(facecolor=COLOR_HEX[color], edgecolor="black", linewidth=1.3)
    if forma == 3:
        ax.add_patch(Circle((cx, cy), r, **kw))
    elif forma == 0:
        R = 1.2 * r
        ax.add_patch(Polygon(poligono(3, cx, cy - R / 4, R), **kw))
    elif forma == 1:
        ax.add_patch(Polygon(poligono(4, cx, cy, 0.9 * r * math.sqrt(2), rot=45), **kw))
    elif forma == 2:
        ax.add_patch(Polygon(poligono(5, cx, cy - 0.05 * r, 1.08 * r), **kw))
    else:
        ax.add_patch(Polygon(estrella(cx, cy - 0.05 * r, 1.1 * r), **kw))


def marco(ax, x0, y0, w, h):
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False, edgecolor="#333333", linewidth=1.1))


def interrogacion(ax, x0, y0, w, h):
    ax.text(x0 + w / 2, y0 + h / 2, "?", ha="center", va="center", fontsize=28, fontweight="bold")


def celda_fig(ax, x0, y0, L, c):
    for p in POSICIONES[c["cantidad"]]:
        f, k = divmod(p, 3)
        figura(ax, c["forma"], x0 + L * (0.2 + 0.3 * k), y0 + L * (0.8 - 0.3 * f), L * RADIOS[c["tamano"]], c["color"])


BORDE = [(0.14, 0.86), (0.5, 0.86), (0.86, 0.86), (0.86, 0.5), (0.86, 0.14), (0.5, 0.14), (0.14, 0.14), (0.14, 0.5)]


def celda_rot(ax, x0, y0, L, c):
    ang = math.radians(90 - 45 * c["ang"])  # 0 = arriba, sentido horario
    pts = [(-0.2, -0.035), (0.08, -0.035), (0.08, -0.085), (0.2, 0), (0.08, 0.085), (0.08, 0.035), (-0.2, 0.035)]
    rot = [(x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)) for x, y in pts]
    ax.add_patch(Polygon([(x0 + L * (0.5 + x), y0 + L * (0.5 + y)) for x, y in rot],
                         facecolor=COLOR_HEX[c["col"]], edgecolor="black", linewidth=1.3))
    bx, by = BORDE[c["pos"]]
    ax.add_patch(Circle((x0 + L * bx, y0 + L * by), L * 0.055, facecolor="black", edgecolor="black"))


def celda_dots(ax, x0, y0, L, c, n):
    paso = 1.0 / (n + 1)
    for i in range(n * n):
        f, k = divmod(i, n)
        cx, cy = x0 + L * paso * (k + 1), y0 + L * (1 - paso * (f + 1))
        if i in c["puntos"]:
            ax.add_patch(Circle((cx, cy), L * (0.085 if n == 3 else 0.065), facecolor="black"))
        else:
            ax.add_patch(Circle((cx, cy), L * 0.018, facecolor="#bbbbbb", edgecolor="none"))


PIPS = {0: [], 1: [(0.5, 0.5)], 2: [(0.25, 0.75), (0.75, 0.25)], 3: [(0.25, 0.75), (0.5, 0.5), (0.75, 0.25)],
        4: [(0.25, 0.75), (0.75, 0.75), (0.25, 0.25), (0.75, 0.25)],
        5: [(0.25, 0.75), (0.75, 0.75), (0.5, 0.5), (0.25, 0.25), (0.75, 0.25)],
        6: [(0.25, 0.78), (0.75, 0.78), (0.25, 0.5), (0.75, 0.5), (0.25, 0.22), (0.75, 0.22)]}


def ficha(ax, x0, y0, w, c):
    h = 2 * w
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor="white", edgecolor="black", linewidth=1.4))
    ax.plot([x0 + 0.1 * w, x0 + 0.9 * w], [y0 + w, y0 + w], color="black", linewidth=1.2)
    for mitad, base in (("arriba", y0 + w), ("abajo", y0)):
        for px, py in PIPS[c[mitad]]:
            ax.add_patch(Circle((x0 + px * w, base + py * w), w * 0.08, facecolor="black"))


def dibujar_celda(ax, tipo, x0, y0, L, c, n=3):
    if tipo == "domino":
        if c is None:
            ax.add_patch(Rectangle((x0, y0), L, 2 * L, fill=False, edgecolor="#333333", linewidth=1.1, linestyle="--"))
            interrogacion(ax, x0, y0, L, 2 * L)
        else:
            ficha(ax, x0, y0, L, c)
        return
    marco(ax, x0, y0, L, L)
    if c is None:
        interrogacion(ax, x0, y0, L, L)
    elif tipo == "rotacion":
        celda_rot(ax, x0, y0, L, c)
    elif tipo == "superposicion":
        celda_dots(ax, x0, y0, L, c, n)
    else:
        celda_fig(ax, x0, y0, L, c)


W, H = 8.27, 11.69


def nueva_pagina():
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    return fig, ax


INSTR = {
    "matriz": "¿Qué opción completa la matriz? Revisa cada atributo por filas y por columnas.",
    "serie": "¿Qué figura sigue en la serie?",
    "rotacion": "¿Qué figura sigue? Fíjate en el giro de la flecha, el punto del borde y el color.",
    "superposicion": "¿Qué opción completa la matriz? Compara las dos primeras casillas de cada fila con la tercera.",
    "domino": "¿Qué ficha sigue en la serie? (después del 6 viene el 0)",
    "intrusa": "¿Cuál figura NO pertenece al grupo?",
    "analogia": "A es a B como C es a ... ¿cuál?",
}


def pagina_figura(pdf, numero, q):
    fig, ax = nueva_pagina()
    ax.text(0.6, 11.0, f"Pregunta {numero}", fontsize=20, fontweight="bold")
    ax.text(0.6, 10.6, INSTR[q["tipo"]], fontsize=10.5, color="#333333")
    ax.text(0.6, 10.3, "Revisa cada rasgo: forma, color, tamaño, cantidad (par o impar)." if q["tipo"] == "intrusa"
            else "Construye tu respuesta ANTES de mirar las opciones.", fontsize=9, color="#777777")
    t, s = q["tipo"], q["stem"]
    if t == "intrusa":
        L, sep = 1.3, 0.2
        x = (W - (5 * L + 4 * sep)) / 2
        for i, o in enumerate(q["opciones"]):
            dibujar_celda(ax, "intrusa", x + i * (L + sep), 6.5, L, o)
            ax.text(x + i * (L + sep) + L / 2, 6.1, LETRAS[i], ha="center", fontsize=16, fontweight="bold")
        pdf.savefig(fig)
        plt.close(fig)
        return
    if t in ("matriz", "superposicion"):
        L = 1.45
        x0 = (W - 3 * L) / 2
        y_top = 9.9
        grid = s.get("matriz") or s.get("dots")
        for r in range(3):
            for c in range(3):
                cel = None if (r, c) == (2, 2) else grid[r][c]
                dibujar_celda(ax, t, x0 + c * L, y_top - (r + 1) * L, L, cel, q.get("n", 3))
        y_op = 3.0
    elif t in ("serie", "rotacion"):
        L = 1.15
        x0 = (W - 6 * L - 5 * 0.08) / 2
        for i, c in enumerate(s.get("serie") or s.get("rot")):
            dibujar_celda(ax, t, x0 + i * (L + 0.08), 7.6, L, c)
        dibujar_celda(ax, t, x0 + 5 * (L + 0.08), 7.6, L, None)
        y_op = 4.2
    elif t == "domino":
        L = 0.75
        x0 = (W - 6 * L - 5 * 0.35) / 2
        for i, c in enumerate(s["dom"]):
            dibujar_celda(ax, t, x0 + i * (L + 0.35), 6.9, L, c)
        dibujar_celda(ax, t, x0 + 5 * (L + 0.35), 6.9, L, None)
        y_op = 2.6
    elif t == "analogia":
        L = 1.35
        A, B, C = s["abc"]
        xs = [0.55, 2.35, 4.65, 6.45]
        for xx, c in zip(xs, [A, B, C, None]):
            dibujar_celda(ax, t, xx, 7.4, L, c)
        ax.text(2.125, 8.07, ":", fontsize=26, ha="center", va="center", fontweight="bold")
        ax.text(4.175, 8.07, "::", fontsize=26, ha="center", va="center", fontweight="bold")
        ax.text(6.225, 8.07, ":", fontsize=26, ha="center", va="center", fontweight="bold")
        for xx, lab in zip(xs, "ABC?"):
            ax.text(xx + L / 2, 7.1, lab if lab != "?" else "", ha="center", fontsize=12, color="#555555")
        y_op = 4.0
    # opciones: MISMA escala que el enunciado
    sep = 0.12 if t != "domino" else 0.45
    x_o = (W - (5 * L + 4 * sep)) / 2
    ax.text(0.6, y_op + (2 * L if t == "domino" else L) + 0.35, "Opciones:", fontsize=11, color="#333333")
    for i, o in enumerate(q["opciones"]):
        x = x_o + i * (L + sep)
        dibujar_celda(ax, t, x, y_op, L, o, q.get("n", 3))
        ax.text(x + L / 2, y_op - 0.4, LETRAS[i], ha="center", fontsize=16, fontweight="bold")
    pdf.savefig(fig)
    plt.close(fig)


def bloque_texto(ax, x, y, texto, ancho, size, **kw):
    lineas = []
    for parrafo in str(texto).split("\n"):
        lineas += textwrap.wrap(parrafo, ancho) or [""]
    for ln in lineas:
        ax.text(x, y, ln, fontsize=size, va="top", **kw)
        y -= size / 72 * 1.45
    return y


def pagina_texto(pdf, numero, q):
    fig, ax = nueva_pagina()
    ax.text(0.6, 11.0, f"Pregunta {numero}", fontsize=20, fontweight="bold")
    y = bloque_texto(ax, 0.6, 10.4, q["enunciado"], 62, 14)
    y -= 0.35
    for i, op in enumerate(q["opciones"]):
        y = bloque_texto(ax, 0.8, y, f"{LETRAS[i]})  {op}", 58, 14) - 0.18
    pdf.savefig(fig)
    plt.close(fig)


def paginas_lista(pdf, titulo, lineas, size=11):
    fig, ax = nueva_pagina()
    ax.text(0.6, 11.0, titulo, fontsize=18, fontweight="bold")
    y = 10.4
    for ln in lineas:
        if y < 0.9:
            pdf.savefig(fig)
            plt.close(fig)
            fig, ax = nueva_pagina()
            y = 11.0
        y = bloque_texto(ax, 0.6, y, ln, 88, size) - 0.08
    pdf.savefig(fig)
    plt.close(fig)


# ============================================================ armado del examen
def letras_balanceadas(n, rng):
    base = list(LETRAS) * (n // 5 + 1)
    base = base[:n]
    rng.shuffle(base)
    return base


def construir(plan, salida):
    rng = random.Random(int(plan["semilla"]))
    prefijo = str(plan.get("prefijo", ""))
    textos, figuras = [], []
    for it in plan["items"]:
        if it.get("t") == "texto":
            d = [str(x) for x in it["distractores"]]
            if len(d) != 4 or len(set(d + [str(it["correcta"])])) != 5:
                raise SystemExit(f"Pregunta de texto con opciones repetidas o sin 4 distractores: {it.get('enunciado', '')[:60]}")
            textos.append(it)
        else:
            figuras.append(it)
    # orden: intercalar figuras entre las de texto de forma pareja
    orden = []
    if plan.get("orden", "intercalar") == "intercalar" and textos and figuras:
        i = j = 0
        while i < len(textos) or j < len(figuras):
            if j >= len(figuras) or (i < len(textos) and (i + 1) / len(textos) <= (j + 1) / len(figuras)):
                orden.append(textos[i])
                i += 1
            else:
                orden.append(figuras[j])
                j += 1
    else:
        orden = list(plan["items"])
    letras = letras_balanceadas(len(orden), rng)
    clave_out, resp_lineas, preguntas = [], [], []
    for numero, (it, letra) in enumerate(zip(orden, letras), 1):
        objetivo = LETRAS.index(letra)
        if it.get("t") == "texto":
            ops = [str(x) for x in it["distractores"]]
            rng.shuffle(ops)
            ops.insert(objetivo, str(it["correcta"]))
            q = {"t": "texto", "enunciado": it["enunciado"], "opciones": ops}
            pid = f"T{prefijo}-{numero:02d}"
            tipo, regla, nivel = it.get("tipo", "texto"), it.get("regla", ""), it.get("nivel", "")
            expl = [it.get("explicacion", "")]
            trampa = it.get("trampa", "")
            fallo_letra = {}
        else:
            forz = None
            if it.get("forzar"):
                forz = {}
                for p in str(it["forzar"]).replace(";", "+").replace(",", "+").split("+"):
                    p = p.strip()
                    if not p:
                        continue
                    if ":" not in p:
                        raise SystemExit(f"forzar mal escrito: {p} (usa atributo:regla)")
                    a_, r_ = [x.strip() for x in p.split(":", 1)]
                    if a_ not in MATRIZ_ATTR or r_ not in MATRIZ_ATTR[a_][2]:
                        raise SystemExit(f"forzar no valido: {p}. Validos: " +
                                         "; ".join(f"{k}: {', '.join(v[2])}" for k, v in MATRIZ_ATTR.items()))
                    forz[a_] = r_
                if it.get("tipo", "matriz") != "matriz":
                    forz = None
            tipo = it.get("tipo", "matriz")
            nivel = it.get("nivel", "M")
            g = GENERADORES[tipo](nivel, rng, forz)
            ops = g["opciones"]
            correcta = ops[g["correcta"]]
            resto = [(k, o) for k, o in enumerate(ops) if k != g["correcta"]]
            rng.shuffle(resto)
            nuevo = [o for _, o in resto]
            nuevo.insert(objetivo, correcta)
            mapa = {}
            pos_resto = [p for p in range(5) if p != objetivo]
            for p, (k, _) in zip(pos_resto, resto):
                mapa[k] = p
            g["opciones"] = nuevo
            fallos = g.get("fallos") or [None] + [g["regla"]] * 4
            fallo_letra = {LETRAS[mapa[k]]: (fallos[k] or g["regla"]) for k, _ in resto}
            q = dict(g)
            q["t"] = "figura"
            pid = f"F{prefijo}-{numero:02d}"
            regla = g["regla"]
            expl = g["explicacion"]
            trampa = ""
            if g["trampa"]:
                trampa = f"La trampa más tentadora era la {LETRAS[mapa[g['trampa'][0]]]}: {g['trampa'][1]}."
            # verificacion final de unicidad
            if g["valida"] is not None:
                validas = [k for k, o in enumerate(nuevo) if g["valida"](o)]
                if validas != [objetivo]:
                    raise SystemExit(f"Fallo de unicidad en {pid}: {validas}")
        preguntas.append((numero, q))
        clave_out.append({"numero": numero, "id": pid, "tipo": tipo, "regla": regla, "nivel": nivel,
                          "correcta": LETRAS[objetivo], "repaso_de": it.get("repaso_de", ""),
                          "fallo_por_letra": fallo_letra})
        linea = f"{numero}. {LETRAS[objetivo]}  ({tipo}) " + " ".join(e for e in expl if e)
        if trampa:
            linea += " " + trampa
        resp_lineas.append(linea)
    os.makedirs(salida, exist_ok=True)
    n = len(preguntas)
    minutos = round(2.4 * n)
    with PdfPages(os.path.join(salida, "examen.pdf")) as pdf:
        portada = [f"{n} preguntas · tiempo sugerido: {minutos} minutos (~2,4 min por pregunta).",
                   "1. Cronómetro en marcha, papel y lápiz. Sin ayuda.",
                   "2. Construye tu respuesta ANTES de mirar las opciones.",
                   "3. Si una pregunta te traba más de 3 minutos, márcala, sáltala y vuelve al final.",
                   "4. Anota tus letras en orden en la última página.",
                   "5. NO abras respuestas.pdf hasta terminar."]
        if n >= 30:
            portada.append("Control de ritmo: " + ", ".join(
                f"pregunta {k} al minuto {round(2.4 * k)}" for k in (10, 25, 40) if k <= n) + ".")
        paginas_lista(pdf, plan.get("titulo", "Práctica"), portada, 13)
        for numero, q in preguntas:
            if q["t"] == "texto":
                pagina_texto(pdf, numero, q)
            else:
                pagina_figura(pdf, numero, q)
        hoja = [" ".join(f"{k}:___" for k in range(i, min(i + 5, n + 1))) for i in range(1, n + 1, 5)]
        paginas_lista(pdf, "Hoja de respuestas", hoja + ["", "Luego escribe tus letras seguidas en la pestaña 'Respuestas' de tu hoja (ej. ABDC?E-…).",
                                                         "? = dudé o la pregunta está mal hecha · - = en blanco",
                                                         "En 'Comentario': en 1 línea, qué regla no viste en tu peor error."], 13)
    with PdfPages(os.path.join(salida, "respuestas.pdf")) as pdf:
        extra = [plan["extra_respuestas"]] if plan.get("extra_respuestas") else []
        paginas_lista(pdf, "Respuestas (ábrelo solo al terminar)",
                      ["Letras seguidas: " + "".join(c["correcta"] for c in clave_out), ""] + resp_lineas + [""] + extra, 11)
    with open(os.path.join(salida, "clave.json"), "w", encoding="utf-8") as f:
        json.dump(clave_out, f, ensure_ascii=False, indent=1)
    return clave_out


# ============================================================ autotest
def autotest(n):
    rng = random.Random(7)
    fallos = 0
    sesgo = {}
    sup = {}
    for tipo, gen in GENERADORES.items():
        aciertos_mayoria = 0
        total = 0
        for nivel in NIVEL_N:
            for _ in range(n):
                g = gen(nivel, rng)
                ops = g["opciones"]
                if len({clave(o) for o in ops}) != 5:
                    fallos += 1
                    print("opciones repetidas", tipo, nivel)
                if g["valida"] is not None:
                    validas = [k for k, o in enumerate(ops) if g["valida"](o)]
                    if validas != [g["correcta"]]:
                        fallos += 1
                        print("unicidad", tipo, nivel, validas)
                if tipo == "superposicion":
                    todas = [o["puntos"] for o in ops]
                    dist = [sum(len(x ^ y) for y in todas) for x in todas]
                    for nombre, objetivo in (("centro", min(dist)), ("lejos", max(dist))):
                        cand = [k for k, d in enumerate(dist) if d == objetivo]
                        sup[nombre] = sup.get(nombre, 0) + ((1 / len(cand)) if g["correcta"] in cand else 0)
                    sup["n"] = sup.get("n", 0) + 1
                if tipo == "intrusa":
                    feats = {"forma": [o["forma"] for o in ops], "color": [o["color"] for o in ops],
                             "tamano": [o["tamano"] for o in ops], "cantidad": [o["cantidad"] for o in ops],
                             "paridad": [o["cantidad"] % 2 for o in ops]}
                    if g["nivel"] in ("D", "MD"):
                        for f in (lambda c: c in (2, 3, 5, 7), lambda c: c % 3 == 0, lambda c: c in (1, 4, 9), lambda c: c > 5):
                            v = [f(o["cantidad"]) for o in ops]
                            sg = [i for i, x in enumerate(v) if v.count(x) == 1]
                            if sg and sg != [g["correcta"]]:
                                fallos += 1
                                print("intrusa: rasgo numerico ambiguo", [o["cantidad"] for o in ops])
                    unicos = {i for v in feats.values() for i, x in enumerate(v) if v.count(x) == 1
                              and sum(1 for y in v if v.count(y) == 1) < 5}
                    if unicos != {g["correcta"]}:
                        fallos += 1
                        print("intrusa ambigua", nivel, unicos)
                # heuristica de mayoria (adivinar sin razonar)
                if tipo not in ("intrusa", "superposicion"):
                    score = []
                    for o in ops:
                        s = sum(sum(1 for p in ops if p[a] == o[a]) for a in o)
                        score.append(s)
                    mejor = [k for k, s in enumerate(score) if s == max(score)]
                    aciertos_mayoria += (1 / len(mejor)) if g["correcta"] in mejor else 0
                    total += 1
        if total:
            sesgo[tipo] = round(100 * aciertos_mayoria / total, 1)
    print("FALLOS:", fallos)
    print("Acierto adivinando por mayoría (azar = 20%):", sesgo)
    if sup.get("n"):
        print("Superposición, acierto eligiendo la más central / la más lejana (azar = 20%):",
              round(100 * sup["centro"] / sup["n"], 1), "/", round(100 * sup["lejos"] / sup["n"], 1))
    return fallos


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan")
    ap.add_argument("--salida", default="salida")
    ap.add_argument("--autotest", type=int, default=0)
    a = ap.parse_args()
    if a.autotest:
        sys.exit(1 if autotest(a.autotest) else 0)
    with open(a.plan, encoding="utf-8") as f:
        p = json.load(f)
    out = construir(p, a.salida)
    print(json.dumps(out, ensure_ascii=False))
