/* Entrenador de razonamiento lógico y abstracto
   Práctica adaptativa: niveles por tipo, repaso espaciado de errores (+1, +3, +7 días),
   simulacros cronometrados y explicación de cada error. Todo se guarda en este dispositivo. */
'use strict';

// ------------------------------------------------------------------ catálogo
const NIV = ['F', 'M', 'D', 'MD'];
const NIV_TXT = ['Nivel 1', 'Nivel 2', 'Nivel 3', 'Nivel 4'];
const LETRAS = 'ABCDE';
const TIPOS = {
  matriz:        { n: 'Matrices de figuras', g: 'fig', w: 3,   yt: 'psicotécnicos matrices de figuras cómo resolver' },
  serie:         { n: 'Series de figuras', g: 'fig', w: 2,     yt: 'psicotécnicos series de figuras explicación' },
  rotacion:      { n: 'Giros y posiciones', g: 'fig', w: 1.5,  yt: 'psicotécnicos figuras que giran explicación' },
  superposicion: { n: 'Superposición de figuras', g: 'fig', w: 1, yt: 'psicotécnicos superposición de figuras' },
  domino:        { n: 'Dominós', g: 'fig', w: 0.8,             yt: 'psicotécnicos fichas de dominó explicación' },
  intrusa:       { n: 'Figura que no pertenece', g: 'fig', w: 1.2, yt: 'psicotécnicos figura diferente explicación' },
  analogia:      { n: 'Analogías de figuras', g: 'fig', w: 1.2, yt: 'psicotécnicos analogías de figuras' },
  cubo:          { n: 'Cubos y desarrollos', g: 'fig', w: 1.5,  yt: 'psicotécnicos desarrollo del cubo caras opuestas' },
  espejo:        { n: 'Espejos (reflejos)', g: 'fig', w: 1.5,   yt: 'psicotécnicos imagen en el espejo figuras' },
  giro2d:        { n: 'Girar figuras', g: 'fig', w: 1.5,        yt: 'psicotécnicos rotación de figuras mental' },
  papel:         { n: 'Papel doblado', g: 'fig', w: 1.2,        yt: 'psicotécnicos papel doblado perforado' },
  serie_num:     { n: 'Series de números', g: 'txt', w: 3,     yt: 'psicotécnicos series numéricas trucos' },
  serie_letras:  { n: 'Series de letras', g: 'txt', w: 2,      yt: 'psicotécnicos series de letras abecedario' },
  numeros_figura:{ n: 'Números en figuras', g: 'txt', w: 2.5,  yt: 'psicotécnicos números en figuras explicación' },
  simbolos:      { n: 'Ecuaciones con símbolos', g: 'txt', w: 2.5, yt: 'acertijos ecuaciones con símbolos razonamiento' },
  operador:      { n: 'Operadores inventados', g: 'txt', w: 1.5, yt: 'operadores matemáticos razonamiento matemático ejercicios' },
  algoritmo:     { n: 'Seguir un procedimiento', g: 'txt', w: 2, yt: 'pensamiento computacional pseudocódigo ejercicios seguir algoritmo' },
  silogismo:     { n: 'Silogismos', g: 'txt', w: 2,            yt: 'silogismos diagramas de Venn psicotécnicos' },
  condicional:   { n: 'Condicionales', g: 'txt', w: 2,         yt: 'lógica condicionales contrapositiva falacias ejercicios' },
  ordenamiento:  { n: 'Ordenamiento', g: 'txt', w: 2,          yt: 'razonamiento lógico ordenamiento lineal ejercicios' },
  verdad_mentira:{ n: 'Verdades y mentiras', g: 'txt', w: 1.5, yt: 'acertijos verdades y mentiras lógica' },
  tabla_logica:  { n: 'Tablas lógicas', g: 'txt', w: 1.5,      yt: 'acertijos de lógica tabla de doble entrada' },
  codificacion:  { n: 'Codificación', g: 'txt', w: 1.2,        yt: 'psicotécnicos codificación de palabras' },
  numerico:      { n: 'Problemas numéricos', g: 'txt', w: 1.2, yt: 'razonamiento numérico regla de tres porcentajes' },
  analogia_verbal:{ n: 'Analogías verbales', g: 'txt', w: 0.6, yt: 'analogías verbales psicotécnicos' },
};
const PREG_FIG = {
  matriz: '¿Qué opción completa la matriz?',
  serie: '¿Qué figura sigue en la serie?',
  rotacion: '¿Qué figura sigue? Fíjate en el giro de la flecha, el punto del borde y el color.',
  superposicion: '¿Qué opción completa la matriz? Compara las dos primeras casillas de cada fila con la tercera.',
  domino: '¿Qué ficha sigue? (Después del 6 viene el 0.)',
  intrusa: '¿Cuál figura NO pertenece al grupo?',
  analogia: 'A es a B como C es a… ¿cuál?',
};
const METODO = {
  matriz: ['Toma un solo atributo: forma, cantidad, tamaño o color.', 'Míralo fila por fila: ¿es igual (constante), sube o baja lo mismo (progresión), aparece cada valor una vez (distribución) o la 3.ª es suma/resta de las dos primeras?', 'Confírmalo por columnas.', 'Repite con los demás atributos.', 'Describe tu respuesta («4 círculos grandes negros») ANTES de mirar las opciones.'],
  serie: ['Revisa cada atributo por separado: forma, cantidad, tamaño, color.', 'Busca un ciclo (se repite cada 2 o 3) o un cambio constante (+1, −1).', 'Si la cantidad no avanza parejo, prueba con dos series intercaladas (posiciones 1-3-5 y 2-4-6).', 'Construye la figura siguiente y luego búscala.'],
  rotacion: ['Sigue cada elemento por separado: la flecha, el punto y el color.', 'Flecha: ¿cuántos grados gira por paso (45°, 90°, 135°) y hacia qué lado?', 'Punto: ¿cuántas casillas avanza por el borde y en qué sentido?', 'Color: ¿se repite un ciclo?', 'Aplica los tres cambios al último paso.'],
  superposicion: ['Compara la 1.ª y 2.ª casilla de cada fila con la 3.ª.', 'Unión: se juntan todos los puntos. Intersección: solo los repetidos.', 'Los no repetidos: los repetidos desaparecen. Resta: a la 1.ª se le quitan los de la 2.ª.', 'Comprueba la regla en las dos primeras filas y aplícala a la tercera.'],
  domino: ['Mira la mitad de arriba sola y luego la de abajo sola.', 'Cuenta en ciclo 0-1-2-3-4-5-6-0 (después del 6 viene el 0).', 'Busca pasos constantes o dos series intercaladas.', 'Cuidado con la ficha correcta pero al revés.'],
  intrusa: ['Revisa un rasgo a la vez: color, forma, tamaño y cantidad (par o impar).', 'Busca el rasgo que comparten cuatro figuras y una no.', 'Si la cantidad es la clave, mira si es par o impar.'],
  analogia: ['Mira qué cambia de A a B (forma, color, tamaño, cantidad).', 'Aplica EXACTAMENTE esos cambios a C.', 'Lo que no cambió de A a B se queda igual en C.'],
  espejo: ['Fíjate dónde está el espejo (a la derecha o abajo).', 'Con el espejo a la derecha, lo de la izquierda pasa a la derecha; arriba y abajo no cambian.', 'Con el espejo abajo, lo de arriba pasa abajo; izquierda y derecha no cambian.', 'Comprueba casilla por casilla, también el color.'],
  giro2d: ['Elige una casilla especial (una esquina, una de color) y sigue a dónde va al girar.', 'Girar NO es reflejar: si la figura quedó «al revés» como en un espejo, es una trampa.', 'Prueba girar 90°, 180° y 270° en tu mente o con el dedo sobre la pantalla.'],
  papel: ['Sigue los dobleces en orden y fíjate qué mitad queda encima.', 'Al desdoblar, cada perforación aparece también reflejada al otro lado del doblez.', 'Con dos dobleces se refleja dos veces: cada perforación se convierte en cuatro.', 'Cuenta: el total de agujeros debe ser perforaciones × 2 por cada doblez.'],
  cubo: ['Dos caras separadas por una sola cara en línea recta quedan opuestas.', 'Las caras opuestas nunca se ven al mismo tiempo ni se tocan.', 'En una esquina se ven tres caras vecinas: ninguna puede ser opuesta a otra.', 'Si dudas, imagina que doblas el papel cara por cara desde la del centro.'],
  serie_num: ['Calcula las diferencias entre números seguidos.', 'Si las diferencias no son iguales, calcula las diferencias de las diferencias.', 'Prueba multiplicar o dividir (×2, ×3).', 'Prueba dos series intercaladas (posiciones impares y pares).', 'Prueba sumar los dos anteriores o alternar dos operaciones.'],
  serie_letras: ['Lee si el enunciado dice CON Ñ (27 letras) o SIN Ñ (26). En el examen real, revisa las instrucciones.', 'Escribe el alfabeto numerado: con Ñ es A1 … N14, Ñ15, O16 … Z27; sin Ñ es A1 … N14, O15 … Z26.', 'Convierte las letras en números y trabaja como en una serie numérica.', 'Después de la Z vuelve la A.'],
  numeros_figura: ['Prueba la regla en la primera fila (o figura): suma, resta, producto, doble, cuadrado…', 'Comprueba que funcione igual en la segunda.', 'Aplícala a la última.'],
  simbolos: ['Empieza por la igualdad que tenga un solo símbolo desconocido.', 'Reemplaza ese valor en las demás.', 'En balanzas, pasa todo a la misma unidad paso a paso.'],
  operador: ['Copia la definición y reemplaza a y b por los números, en ese orden.', 'Resuelve primero lo que está entre paréntesis.', 'Si te piden x, prueba valores pequeños hasta que dé.'],
  algoritmo: ['Haz una tabla con una columna por variable.', 'Ejecuta línea por línea y actualiza la tabla en cada paso.', 'En «repetir n veces», cuenta las vueltas con palitos.', 'En «mientras», revisa la condición ANTES de cada vuelta.'],
  silogismo: ['Dibuja un círculo por grupo (diagrama de Venn).', '«Todos los A son B»: A dentro de B. «Ningún A es B»: separados.', '«Algunos A son B»: se cruzan.', 'Una conclusión es válida solo si se cumple en TODOS los dibujos posibles.'],
  condicional: ['«Si P, entonces Q»: si pasa P, pasa Q.', 'Si NO pasa Q, entonces NO pasó P (contrapositiva).', 'Si pasa Q o si no pasa P, no se puede saber nada de la otra parte (falacias).', '«P solo si Q» = «si P, entonces Q». «P, a menos que Q» = «si no Q, entonces P».'],
  ordenamiento: ['Dibuja una fila y pon a cada persona según las pistas.', 'Empieza por las pistas más seguras (la más baja, quién está al lado de quién).', 'Revisa al final que se cumplan TODAS las pistas.'],
  verdad_mentira: ['Supón que la primera persona dice la verdad y saca consecuencias.', 'Si llegas a una contradicción, entonces miente.', 'Comprueba que la solución final cumpla lo que dijo cada persona.'],
  tabla_logica: ['Haz una tabla: personas en filas, opciones en columnas.', 'Marca ✗ con cada pista negativa y ✓ con las positivas.', 'Si una fila o columna tiene una sola casilla libre, esa es la respuesta.', 'Las pistas «quien tiene X…» unen dos tablas.'],
  codificacion: ['Compara la palabra con su código letra por letra.', 'Mira cuántas posiciones se movió cada letra (con la Ñ).', 'Revisa si se invirtió el orden o si las posiciones pares e impares cambian distinto.'],
  numerico: ['Regla de tres: si una cantidad sube, ¿la otra sube (directa) o baja (inversa)?', 'Porcentajes seguidos se aplican uno tras otro, no se suman.', 'Trabajo conjunto: suma lo que hace cada uno en 1 hora.'],
  analogia_verbal: ['Di la relación entre las dos primeras palabras en una frase («el pez nada»).', 'Aplica la misma frase a la tercera palabra.', 'Si dos opciones encajan, busca la relación más precisa.'],
};
const ANCLA_URL = 'https://redopositor.com/test-psicotecnico-gratis-pdf/';

// ------------------------------------------------------------------ estado
const KEY = 'avz_state_v1', KEY_CUR = 'avz_cur_v1';
function hoy(d = new Date()) {
  const z = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return z.toISOString().slice(0, 10);
}
function addDays(iso, n) { const d = new Date(iso + 'T12:00:00'); d.setDate(d.getDate() + n); return hoy(d); }
function diffDays(a, b) { return Math.round((new Date(b + 'T12:00:00') - new Date(a + 'T12:00:00')) / 864e5); }
function nuevoEstado() {
  return { v: 1, start: hoy(), exam: '2026-11-27', daily: 25, lvl: {}, hist: {}, seen: {}, rev: [], sessions: [], anchors: [], theme: 'auto' };
}
let S = (() => { try { return JSON.parse(localStorage.getItem(KEY)) || nuevoEstado(); } catch (e) { return nuevoEstado(); } })();
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }
let CUR = (() => { try { return JSON.parse(localStorage.getItem(KEY_CUR)); } catch (e) { return null; } })();
function saveCur() { try { CUR ? localStorage.setItem(KEY_CUR, JSON.stringify(CUR)) : localStorage.removeItem(KEY_CUR); } catch (e) {} }
function applyTheme() { if (S.theme === 'auto') document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', S.theme); }
applyTheme();

function lvlOf(t) { return S.lvl[t] || 0; }
function histOf(t) { return S.hist[t] || (S.hist[t] = { n: 0, c: 0, all: [], tot: 0, ok: 0 }); }
function accOf(t) { const h = S.hist[t]; if (!h || !h.all.length) return null; return h.all.reduce((a, b) => a + b, 0) / h.all.length; }

// ------------------------------------------------------------------ bancos
const BANK = {};
async function loadBank(t) {
  if (BANK[t]) return BANK[t];
  const r = await fetch(`bank/${t}.json`);
  BANK[t] = await r.json();
  return BANK[t];
}
function rnd(n) { return Math.floor(Math.random() * n); }
function shuffle(a) { for (let i = a.length - 1; i > 0; i--) { const j = rnd(i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function matchRegla(r, want) {
  if (!want) return true;
  if (r === want) return true;
  return want.split(/;\s*/).some(p => p && r.includes(p.trim()));
}
function pick(t, nivel, regla, usados) {
  const b = BANK[t];
  const niv = NIV[nivel];
  const tries = [
    x => x.n === niv && !S.seen[x.i] && !usados.has(x.i) && matchRegla(x.r, regla),
    x => x.n === niv && !usados.has(x.i) && matchRegla(x.r, regla),
    x => !usados.has(x.i) && matchRegla(x.r, regla),
    x => x.n === niv && !S.seen[x.i] && !usados.has(x.i),
    x => x.n === niv && !usados.has(x.i),
    x => !usados.has(x.i),
  ];
  for (const f of tries) { const c = b.filter(f); if (c.length) return c[rnd(c.length)]; }
  return b[rnd(b.length)];
}
function weightedPick(weights) {
  const tot = Object.values(weights).reduce((a, b) => a + b, 0);
  let x = Math.random() * tot;
  for (const [k, w] of Object.entries(weights)) { x -= w; if (x <= 0) return k; }
  return Object.keys(weights)[0];
}

// ------------------------------------------------------------------ armar sesiones
async function buildSession(mode, opts = {}) {
  const today = hoy();
  let plan = []; // {t, nivel, regla, revId}
  if (mode === 'tipo') {
    for (let k = 0; k < 10; k++) plan.push({ t: opts.tipo, nivel: lvlOf(opts.tipo) });
  } else if (mode === 'repaso') {
    const due = S.rev.filter(r => !r.done && r.due <= today).sort((a, b) => a.due.localeCompare(b.due)).slice(0, 20);
    plan = due.map(r => ({ t: r.t, nivel: lvlOf(r.t), regla: r.r, revId: r.id }));
  } else {
    const N = mode === 'simulacro' ? (opts.corto ? 25 : 50) : S.daily;
    if (mode === 'practica') {
      const due = S.rev.filter(r => !r.done && r.due <= today).sort((a, b) => a.due.localeCompare(b.due));
      const seenKey = new Set();
      for (const r of due) {
        if (plan.length >= Math.floor(N * 0.3)) break;
        const k = r.t + '|' + r.r; if (seenKey.has(k)) continue; seenKey.add(k);
        plan.push({ t: r.t, nivel: lvlOf(r.t), regla: r.r, revId: r.id });
      }
    }
    const count = {};
    plan.forEach(p => count[p.t] = (count[p.t] || 0) + 1);
    const maxPer = Math.ceil(N / 7);
    const nFig = mode === 'simulacro' ? Math.round(N * 0.4) : null;
    let figs = plan.filter(p => TIPOS[p.t].g === 'fig').length;
    while (plan.length < N) {
      const w = {};
      for (const [t, info] of Object.entries(TIPOS)) {
        if ((count[t] || 0) >= maxPer) continue;
        if (nFig !== null) {
          if (info.g === 'fig' && figs >= nFig) continue;
          if (info.g === 'txt' && plan.length - figs >= N - nFig) continue;
        }
        const acc = accOf(t);
        const weak = acc === null ? 1 : 1.6 - acc; // más peso a lo débil
        w[t] = info.w * weak;
      }
      if (!Object.keys(w).length) break;
      const t = weightedPick(w);
      count[t] = (count[t] || 0) + 1;
      if (TIPOS[t].g === 'fig') figs++;
      const nivel = mode === 'simulacro' ? Math.min(3, lvlOf(t) + 1) : lvlOf(t);
      plan.push({ t, nivel });
    }
  }
  if (!plan.length) return null;
  await Promise.all([...new Set(plan.map(p => p.t))].map(loadBank));
  const usados = new Set();
  let items = plan.map(p => {
    const it = pick(p.t, p.nivel, p.regla, usados);
    usados.add(it.i);
    return { t: p.t, it, order: shuffle([0, 1, 2, 3, 4]), ans: null, revId: p.revId || null };
  });
  items = interleave(items);
  return {
    id: Date.now(), mode, items, i: 0, t0: Date.now(), elapsed: 0,
    limit: mode === 'simulacro' ? (opts.corto ? 60 : 120) * 60 : null, tipo: opts.tipo || null,
  };
}
function interleave(items) {
  shuffle(items);
  for (let k = 1; k < items.length; k++) {
    if (items[k].t === items[k - 1].t) {
      const j = items.findIndex((x, idx) => idx > k && x.t !== items[k - 1].t);
      if (j > 0) [items[k], items[j]] = [items[j], items[k]];
    }
  }
  return items;
}

// ------------------------------------------------------------------ SVG de figuras
const COLOR = ['#ffffff', '#808080', '#111111'];
const RAD = [5, 8.5, 12];
const POS = { 1: [4], 2: [3, 5], 3: [3, 4, 5], 4: [0, 2, 6, 8], 5: [0, 2, 4, 6, 8], 6: [0, 2, 3, 5, 6, 8], 7: [0, 2, 3, 4, 5, 6, 8], 8: [0, 1, 2, 3, 5, 6, 7, 8], 9: [0, 1, 2, 3, 4, 5, 6, 7, 8] };
const P = (pts) => pts.map(p => p[0].toFixed(2) + ',' + p[1].toFixed(2)).join(' ');
function poly(n, cx, cy, r, rot = 90) { const o = []; for (let k = 0; k < n; k++) { const a = (rot + 360 * k / n) * Math.PI / 180; o.push([cx + r * Math.cos(a), cy - r * Math.sin(a)]); } return o; }
function star(cx, cy, r) { const o = []; for (let k = 0; k < 10; k++) { const rr = k % 2 ? r * 0.45 : r; const a = (90 + 36 * k) * Math.PI / 180; o.push([cx + rr * Math.cos(a), cy - rr * Math.sin(a)]); } return o; }
function shape(forma, cx, cy, r, color) {
  const st = `fill="${COLOR[color]}" stroke="#111" stroke-width="1.3" stroke-linejoin="round"`;
  if (forma === 3) return `<circle cx="${cx}" cy="${cy}" r="${r}" ${st}/>`;
  if (forma === 0) { const F = 1.2 * r; return `<polygon points="${P(poly(3, cx, cy + F / 4, F))}" ${st}/>`; }
  if (forma === 1) { const h = 0.9 * r; return `<rect x="${cx - h}" y="${cy - h}" width="${2 * h}" height="${2 * h}" ${st}/>`; }
  if (forma === 2) return `<polygon points="${P(poly(5, cx, cy + 0.05 * r, 1.08 * r))}" ${st}/>`;
  return `<polygon points="${P(star(cx, cy + 0.05 * r, 1.1 * r))}" ${st}/>`;
}
function frame(x, y, w = 100, h = 100, dashed = false) {
  return `<rect x="${x + 0.7}" y="${y + 0.7}" width="${w - 1.4}" height="${h - 1.4}" rx="4" fill="#fff" stroke="#3a3a44" stroke-width="1.4"${dashed ? ' stroke-dasharray="5 4"' : ''}/>`;
}
function qmark(x, y, w = 100, h = 100) { return `<text x="${x + w / 2}" y="${y + h / 2 + 11}" text-anchor="middle" font-size="32" font-weight="800" fill="#4338ca" font-family="Plus Jakarta Sans, sans-serif">?</text>`; }
function cellFig(c, x, y) {
  let s = '';
  for (const p of POS[c[1]]) { const r = Math.floor(p / 3), k = p % 3; s += shape(c[0], x + 100 * (0.2 + 0.3 * k), y + 100 * (0.2 + 0.3 * r), RAD[c[2]], c[3]); }
  return s;
}
const BORDE = [[.14, .86], [.5, .86], [.86, .86], [.86, .5], [.86, .14], [.5, .14], [.14, .14], [.14, .5]];
function cellRot(c, x, y) {
  const A = (90 - 45 * c[0]) * Math.PI / 180;
  const B = [[-.2, -.035], [.08, -.035], [.08, -.085], [.2, 0], [.08, .085], [.08, .035], [-.2, .035]];
  const pts = B.map(([u, v]) => [u * Math.cos(A) - v * Math.sin(A), u * Math.sin(A) + v * Math.cos(A)]).map(([u, v]) => [x + 50 + 100 * u, y + 50 - 100 * v]);
  const [bx, by] = BORDE[c[1]];
  return `<polygon points="${P(pts)}" fill="${COLOR[c[2]]}" stroke="#111" stroke-width="1.3" stroke-linejoin="round"/><circle cx="${x + 100 * bx}" cy="${y + 100 * (1 - by)}" r="5.5" fill="#111"/>`;
}
function cellDots(c, x, y, n) {
  const A = 1 / (n + 1); let s = '';
  for (let k = 0; k < n * n; k++) {
    const E = Math.floor(k / n), F = k % n, cx = x + 100 * A * (F + 1), cy = y + 100 * A * (E + 1);
    s += c.includes(k) ? `<circle cx="${cx}" cy="${cy}" r="${n === 3 ? 8.5 : 6.5}" fill="#111"/>` : `<circle cx="${cx}" cy="${cy}" r="1.8" fill="#bbb"/>`;
  }
  return s;
}
const PIPS = { 0: [], 1: [[.5, .5]], 2: [[.25, .75], [.75, .25]], 3: [[.25, .75], [.5, .5], [.75, .25]], 4: [[.25, .75], [.75, .75], [.25, .25], [.75, .25]], 5: [[.25, .75], [.75, .75], [.5, .5], [.25, .25], [.75, .25]], 6: [[.25, .78], [.75, .78], [.25, .5], [.75, .5], [.25, .22], [.75, .22]] };
function tile(c, x, y, w = 50) {
  if (!c) return `<rect x="${x + .7}" y="${y + .7}" width="${w - 1.4}" height="${2 * w - 1.4}" rx="6" fill="#fff" stroke="#3a3a44" stroke-width="1.4" stroke-dasharray="5 4"/>` + qmark(x, y, w, 2 * w);
  let s = `<rect x="${x + .7}" y="${y + .7}" width="${w - 1.4}" height="${2 * w - 1.4}" rx="6" fill="#fff" stroke="#111" stroke-width="1.5"/><line x1="${x + .12 * w}" x2="${x + .88 * w}" y1="${y + w}" y2="${y + w}" stroke="#111" stroke-width="1.3"/>`;
  [[c[0], 0], [c[1], w]].forEach(([v, off]) => PIPS[v].forEach(([u, q]) => { s += `<circle cx="${x + u * w}" cy="${y + off + (1 - q) * w}" r="${w * .085}" fill="#111"/>`; }));
  return s;
}
function cell(t, c, x, y, n) {
  if (t === 'rotacion') return frame(x, y) + cellRot(c, x, y);
  if (t === 'superposicion') return frame(x, y) + cellDots(c, x, y, n || 3);
  return frame(x, y) + cellFig(c, x, y);
}
function svg(w, h, body, label = '') { return `<svg viewBox="0 0 ${w} ${h}" width="${w}" role="img" aria-label="${label}" xmlns="http://www.w3.org/2000/svg">${body}</svg>`; }

function stemFig(t, it) {
  const s = it.s;
  if (t === 'espejo') {
    const x = it.x, v = x.eje === 'v';
    const mirror = v ? `<rect x="104" y="0" width="7" height="100" rx="2" fill="#9fc6e6"/><text x="128" y="54" font-size="12" font-weight="700" fill="#5a8fb8">espejo</text>`
      : `<rect x="0" y="104" width="100" height="7" rx="2" fill="#9fc6e6"/><text x="50" y="128" text-anchor="middle" font-size="12" font-weight="700" fill="#5a8fb8">espejo</text>`;
    return svg(v ? 170 : 100, v ? 100 : 134, gridSvg(x.fig, x.N) + mirror, 'figura y espejo');
  }
  if (t === 'giro2d') return svg(100, 100, gridSvg(it.x.fig, it.x.N), 'figura');
  if (t === 'papel') return papelSvg(it.x.steps, it.x.N);
  if (t === 'matriz' || t === 'superposicion') {
    const g = t === 'matriz' ? s : s.g, n = t === 'superposicion' ? s.n : 3;
    let b = '';
    for (let r = 0; r < 3; r++) for (let k = 0; k < 3; k++) {
      const c = g[r][k], x = k * 104, y = r * 104;
      b += c ? cell(t, c, x, y, n) : frame(x, y, 100, 100, true) + qmark(x, y);
    }
    return svg(308, 308, b, 'matriz');
  }
  if (t === 'serie' || t === 'rotacion') {
    // 3 + 3 en dos filas para que se vea grande en el celular
    let b = ''; const xy = k => [(k % 3) * 108, Math.floor(k / 3) * 120];
    s.forEach((c, k) => { const [x, y] = xy(k); b += cell(t, c, x, y) + `<text x="${x + 50}" y="${y + 116}" text-anchor="middle" font-size="11" font-weight="700" fill="#999">${k + 1}</text>`; });
    const [x5, y5] = xy(5); b += frame(x5, y5, 100, 100, true) + qmark(x5, y5);
    return svg(316, 238, b, "serie");
  }
  if (t === 'domino') {
    let b = ''; s.forEach((c, k) => { b += tile(c, k * 66, 0); }); b += tile(null, 5 * 66, 0);
    return svg(6 * 66 - 16, 100, b, 'dominós');
  }
  if (t === 'analogia') {
    const xs = [0, 140, 300, 440]; let b = '';
    [s[0], s[1], s[2], null].forEach((c, k) => { b += c ? cell(t, c, xs[k], 0) : frame(xs[k], 0, 100, 100, true) + qmark(xs[k], 0); });
    b += `<text x="120" y="60" text-anchor="middle" font-size="30" font-weight="800" fill="#666">:</text><text x="270" y="60" text-anchor="middle" font-size="30" font-weight="800" fill="#666">::</text><text x="420" y="60" text-anchor="middle" font-size="30" font-weight="800" fill="#666">:</text>`;
    ['A', 'B', 'C'].forEach((L, k) => { b += `<text x="${xs[k] + 50}" y="122" text-anchor="middle" font-size="14" font-weight="700" fill="#888">${L}</text>`; });
    return svg(540, 128, b, 'analogía');
  }
  return '';
}
function gridSvg(cells, N, holes = false, extra = '') {
  const L = 100 / N; let b = frame(0, 0);
  for (let k = 1; k < N; k++) b += `<line x1="${k * L}" x2="${k * L}" y1="3" y2="97" stroke="#e3e3e3" stroke-width="1"/><line y1="${k * L}" y2="${k * L}" x1="3" x2="97" stroke="#e3e3e3" stroke-width="1"/>`;
  cells.forEach(([r, c, k]) => {
    b += holes ? `<circle cx="${c * L + L / 2}" cy="${r * L + L / 2}" r="${L * 0.28}" fill="#111"/>`
      : `<rect x="${c * L + 2}" y="${r * L + 2}" width="${L - 4}" height="${L - 4}" rx="2" fill="${k === 2 ? '#8a8a8a' : '#111'}"/>`;
  });
  return b + extra;
}
function papelSvg(st, N) {
  const L = 100 / N, W = 112; let b = '';
  st.forEach((p, i) => {
    const x0 = i * W;
    b += `<rect x="${x0 + 1}" y="1" width="98" height="98" fill="none" stroke="#bbb" stroke-dasharray="3 3"/>`;
    b += `<rect x="${x0 + p.c0 * L + 1}" y="${p.r0 * L + 1}" width="${p.w * L - 2}" height="${p.h * L - 2}" fill="#fff" stroke="#111" stroke-width="1.6"/>`;
    for (let k = 1; k < p.w; k++) b += `<line x1="${x0 + (p.c0 + k) * L}" x2="${x0 + (p.c0 + k) * L}" y1="${p.r0 * L + 2}" y2="${(p.r0 + p.h) * L - 2}" stroke="#e6e6e6"/>`;
    for (let k = 1; k < p.h; k++) b += `<line y1="${(p.r0 + k) * L}" y2="${(p.r0 + k) * L}" x1="${x0 + p.c0 * L + 2}" x2="${x0 + (p.c0 + p.w) * L - 2}" stroke="#e6e6e6"/>`;
    const dir = p.fold ? (p.fold[1] === '-' ? -1 : 1) : 1;
    p.holes.forEach(([r, c]) => { b += `<circle cx="${x0 + c * L + L / 2}" cy="${r * L + L / 2}" r="${L * 0.28}" fill="#111"/>`; });
    if (p.fold && p.fold[0] === 'v') {
      const fx = x0 + (p.c0 + p.w / 2) * L, my = (p.r0 + p.h / 2) * L, a = dir * p.w * L / 4;
      b += `<line x1="${fx}" x2="${fx}" y1="${p.r0 * L + 2}" y2="${(p.r0 + p.h) * L - 2}" stroke="#4338ca" stroke-width="2" stroke-dasharray="5 4"/>`;
      b += `<path d="M${fx - a} ${my} Q ${fx} ${my - 18} ${fx + a} ${my}" fill="none" stroke="#4338ca" stroke-width="2.4"/><path d="M${fx + a - 7 * dir} ${my - 6} L${fx + a} ${my} L${fx + a - 8 * dir} ${my + 3}" fill="none" stroke="#4338ca" stroke-width="2.4"/>`;
    } else if (p.fold && p.fold[0] === 'h') {
      const fy = (p.r0 + p.h / 2) * L, mx = x0 + (p.c0 + p.w / 2) * L, a = dir * p.h * L / 4;
      b += `<line y1="${fy}" y2="${fy}" x1="${x0 + p.c0 * L + 2}" x2="${x0 + (p.c0 + p.w) * L - 2}" stroke="#4338ca" stroke-width="2" stroke-dasharray="5 4"/>`;
      b += `<path d="M${mx} ${fy - a} Q ${mx + 18} ${fy} ${mx} ${fy + a}" fill="none" stroke="#4338ca" stroke-width="2.4"/><path d="M${mx - 6} ${fy + a - 7 * dir} L${mx} ${fy + a} L${mx + 3} ${fy + a - 8 * dir}" fill="none" stroke="#4338ca" stroke-width="2.4"/>`;
    }
    b += `<text x="${x0 + 50}" y="116" text-anchor="middle" font-size="11" font-weight="700" fill="#999">${i < st.length - 1 ? 'Paso ' + (i + 1) : 'Perforado'}</text>`;
  });
  return svg(st.length * W - 12, 120, b, 'papel doblado');
}
function optFig(t, c, n) {
  if (t === 'espejo' || t === 'giro2d') return svg(100, 100, gridSvg(c, n));
  if (t === 'papel') return svg(100, 100, gridSvg(c, n, true));
  if (t === 'domino') return svg(50, 100, tile(c, 0, 0));
  return svg(100, 100, cell(t, c, 0, 0, n));
}
function esc(s) { return String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch])); }
function triSvg(rows) {
  let b = '';
  rows.forEach((r, k) => {
    const x = k * 120;
    b += `<polygon points="${x + 55},6 ${x + 6},96 ${x + 104},96" fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/>`;
    b += `<text x="${x + 22}" y="118" text-anchor="middle" font-size="17" font-weight="700" fill="#111">${esc(r[0])}</text>`;
    b += `<text x="${x + 88}" y="118" text-anchor="middle" font-size="17" font-weight="700" fill="#111">${esc(r[1])}</text>`;
    b += `<text x="${x + 55}" y="74" text-anchor="middle" font-size="19" font-weight="800" fill="${r[2] === '?' ? '#4338ca' : '#111'}">${esc(r[2])}</text>`;
  });
  return svg(352, 126, b, 'triángulos');
}
function netSvg(grid) {
  const R = grid.length, C = grid[0].length, L = 52; let b = '';
  grid.forEach((row, r) => row.forEach((v, c) => {
    if (!v) return;
    b += `<rect x="${c * L + 1}" y="${r * L + 1}" width="${L}" height="${L}" fill="#fff" stroke="#111" stroke-width="1.6"/>`;
    b += `<text x="${c * L + 1 + L / 2}" y="${r * L + 1 + L / 2 + 10}" text-anchor="middle" font-size="28" fill="#111">${esc(v)}</text>`;
  }));
  return svg(C * L + 2, R * L + 2, b, 'desarrollo de un cubo');
}

// ------------------------------------------------------------------ render helpers
const $app = document.getElementById('app');
const $modal = document.getElementById('modal');
const ICON = {
  play: '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13a1 1 0 0 0 1.5.86l10.5-6.5a1 1 0 0 0 0-1.72L9.5 4.64A1 1 0 0 0 8 5.5z"/></svg>',
  redo: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>',
  clock: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
  chart: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5"/><path d="M4 19h16"/><path d="m7 15 4-4 3 3 5-6"/></svg>',
  gear: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
  back: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>',
  flag: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/></svg>',
};
function logo() { return `<span class="brand-mark"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.6" stroke-linejoin="round"><path d="M5 19 12 5l7 14z"/><circle cx="12" cy="14.5" r="1.6" fill="white" stroke="none"/></svg></span>`; }
function openModal(html) {
  $modal.innerHTML = `<div class="sheet" role="dialog" aria-modal="true">${html}<div class="row-actions" style="margin-top:18px"><button class="btn primary" data-close>Entendido</button></div></div>`;
  $modal.hidden = false;
  $modal.onclick = e => { if (e.target === $modal || e.target.closest('[data-close]')) closeModal(); };
}
function closeModal() { $modal.hidden = true; $modal.innerHTML = ''; }
function ytLink(t) { return `https://www.youtube.com/results?search_query=${encodeURIComponent(TIPOS[t].yt)}`; }
function ejemploHtml(t) {
  const b = BANK[t]; if (!b) return '';
  const L = Math.min(lvlOf(t), 1);
  const pool = b.filter(x => x.n === NIV[L] && !S.seen[x.i]);
  const it = (pool.length ? pool : b)[rnd(pool.length || b.length)];
  const q = { t, it, order: shuffle([0, 1, 2, 3, 4]), ans: null };
  const fig = isFigOpts(q);
  const opts = q.order.map((orig, pos) => `<button class="opt${orig === 0 ? ' right' : ''}" disabled><span class="letter">${LETRAS[pos]}</span>${optHtml(q, orig)}</button>`).join('');
  S.seen[it.i] = 1; save();
  return `<div class="worked"><p class="lvl" style="margin:0 0 8px">Ejemplo resuelto</p>${qBlock(q, true)}<div class="options${fig ? ' fig' : ''}">${opts}</div>
    <div class="why"><p><b>Solución paso a paso:</b></p>${it.e.map((x, k) => `<p>${k + 1}. ${esc(x)}</p>`).join('')}</div></div>`;
}
function showMetodo(t, first) {
  // ejemplo resuelto completo para principiantes; se retira al subir de nivel (efecto de inversión por experiencia)
  const conEjemplo = lvlOf(t) <= 1 && BANK[t];
  openModal(`<div class="lesson">${first ? '<p class="lvl" style="margin:0 0 8px">Tipo nuevo para ti</p>' : ''}<h3>Cómo resolver: ${TIPOS[t].n}</h3><ol>${METODO[t].map(x => `<li>${esc(x)}</li>`).join('')}</ol>
    ${conEjemplo ? ejemploHtml(t) : (BANK[t] ? '<button class="chip" id="ver-ej">Ver un ejemplo resuelto</button>' : '')}
    <div class="row-actions"><a class="chip" href="${ytLink(t)}" target="_blank" rel="noopener">▶ Ver videos que lo explican</a></div></div>`);
  const ve = document.getElementById('ver-ej'); if (ve) ve.onclick = () => { ve.outerHTML = ejemploHtml(t); };
}

// ------------------------------------------------------------------ vistas
let VIEW = 'home', TIMER = null, LAST = null;
function go(v) { VIEW = v; if (TIMER) { clearInterval(TIMER); TIMER = null; } render(); window.scrollTo(0, 0); }
function render() {
  if (VIEW === 'home') return renderHome();
  if (VIEW === 'quiz') return renderQuiz();
  if (VIEW === 'results') return renderResults();
  if (VIEW === 'progress') return renderProgress();
  if (VIEW === 'settings') return renderSettings();
}
function topBar(back = false, title = '') {
  return `<div class="top">${back ? `<button class="icon-btn" data-go="home">${ICON.back} Inicio</button><b>${title}</b><span style="width:80px"></span>` :
    `<div class="brand">${logo()}<span>Entrenador</span></div><div style="display:flex;gap:8px"><button class="icon-btn" data-go="progress" aria-label="Progreso">${ICON.chart}</button><button class="icon-btn" data-go="settings" aria-label="Ajustes">${ICON.gear}</button></div>`}</div>`;
}
function bindGo() { $app.querySelectorAll('[data-go]').forEach(b => b.onclick = () => go(b.dataset.go)); }

function renderHome() {
  const today = hoy();
  const dExam = diffDays(today, S.exam);
  const doneToday = S.sessions.filter(s => s.date === today && s.mode !== 'simulacro').reduce((a, s) => a + s.total, 0);
  const due = S.rev.filter(r => !r.done && r.due <= today).length;
  const streak = (() => { let n = 0, d = today; const days = new Set(S.sessions.map(s => s.date)); if (!days.has(d)) d = addDays(d, -1); while (days.has(d)) { n++; d = addDays(d, -1); } return n; })();
  const greet = S.sessions.length ? (doneToday >= S.daily ? '¡Meta de hoy cumplida!' : 'Sigamos entrenando') : 'Bienvenido, Julián';
  const resume = CUR && CUR.items ? `<button class="card action main" id="resume" style="margin-top:14px;border-color:var(--primary)"><span class="ico">${ICON.play}</span><div><b>Continuar ${CUR.mode === 'simulacro' ? 'el simulacro (el reloj sigue corriendo)' : 'donde ibas'}</b><span>${CUR.items.filter(x => x.ans !== null).length} de ${CUR.items.length} respondidas</span></div></button>` : '';
  const types = Object.entries(TIPOS).map(([t, info]) => {
    const a = accOf(t);
    return `<button class="type" data-tipo="${t}"><span class="lvl">${NIV_TXT[lvlOf(t)]}</span><b>${info.n}</b><div class="bar"><i style="width:${a === null ? 0 : Math.round(a * 100)}%"></i></div><small>${a === null ? 'Sin practicar' : Math.round(a * 100) + '% de acierto'}</small></button>`;
  }).join('');
  const anclaA = S.anchors.find(a => a.k === 'A');
  $app.innerHTML = topBar() + `
    <section class="hero">
      <svg class="hero-deco" width="180" height="180" viewBox="0 0 100 100"><path d="M10 90 50 10l40 80z" fill="none" stroke="currentColor" stroke-width="8" stroke-linejoin="round"/><circle cx="50" cy="62" r="9" fill="currentColor"/></svg>
      <h1>${greet}</h1>
      <p>${dExam > 0 ? `Faltan ${dExam} días para tu examen.` : dExam === 0 ? 'Hoy es tu examen. ¡Tú puedes!' : 'Sigue practicando para la próxima versión.'}</p>
      <div class="stats"><span class="pill">Hoy: ${Math.min(doneToday, 999)}/${S.daily} preguntas</span><span class="pill">🔥 Racha: ${streak} día${streak === 1 ? '' : 's'}</span></div>
    </section>
    ${resume}
    ${homeAvisos(dExam, doneToday)}
    <div class="grid2">
      <button class="card action main" id="practica"><span class="ico">${ICON.play}</span><div><b>Práctica de hoy</b><span>${S.daily} preguntas mezcladas, adaptadas a tu nivel · ~${Math.round(S.daily * 2.4)} min</span></div></button>
      <button class="card action" id="repaso"><span class="ico">${ICON.redo}</span><b>Repasar errores${due ? `<span class="badge">${due}</span>` : ''}</b><span>${due ? 'Preguntas nuevas sobre lo que fallaste' : 'No tienes repasos pendientes hoy'}</span></button>
      <button class="card action" id="simulacro"><span class="ico">${ICON.clock}</span><b>Simulacro</b><span>Completo (50 · 2 h) o corto (25 · 1 h), como el examen</span></button>
    </div>
    ${!anclaA ? `<div class="card" style="margin-top:12px"><b>${ICON.flag} Prueba ancla A (una sola vez)</b><p class="muted small" style="margin:6px 0 10px">Mide tu punto de partida con preguntas hechas por personas: descarga el <a href="${ANCLA_URL}" target="_blank" rel="noopener">PDF de 50 preguntas de RedOpositor</a>, haz solo las preguntas 1 a 25 en 60 minutos y anota aquí cuántas acertaste. Las 26 a 50 guárdalas para la prueba B, unos días antes del examen.</p><button class="chip" id="ancla">Anotar mi puntaje</button></div>` : ''}
    <div class="card" style="margin-top:12px"><b>👥 Practica también con preguntas hechas por personas</b>
      <p class="muted small" style="margin:6px 0 10px">Así compruebas que lo que aprendes aquí sirve fuera de esta app. Hazlas con cronómetro y anota tu puntaje.</p>
      <div class="row-actions" style="margin:0">
        <a class="chip" href="https://www.preparaoposiciones.com/blog/test-gratis/psicotecnicos/" target="_blank" rel="noopener">PreparaOposiciones (español)</a>
        <a class="chip" href="https://www.practiceaptitudetests.com/abstract-reasoning-tests/" target="_blank" rel="noopener">Practice Aptitude Tests (inglés)</a>
        <button class="chip" id="ext">✍ Anotar un test externo</button></div></div>
    <h2 class="section">Practicar un tipo</h2>
    <div class="types">${types}</div>
    <div class="row-actions" style="margin-top:18px"><button class="chip" id="proto2">📋 Protocolo del día del examen</button></div>
    <p class="muted small" style="margin-top:14px">Tu progreso se guarda en este dispositivo. Para no perderlo, descarga una copia desde Ajustes de vez en cuando.</p>`;
  bindGo();
  const start = async (mode, opts, ok) => {
    if (!ok && CUR && CUR.items && CUR.items.some(x => x.ans !== null)) {
      openModal(`<h3>Tienes una sesión a medias</h3><p class="muted">Si empiezas otra, se pierde la que llevas (${CUR.items.filter(x => x.ans !== null).length} de ${CUR.items.length} respondidas).</p><div class="row-actions"><button class="btn primary" id="keep">Continuar la que llevo</button><button class="btn" id="discard">Empezar la nueva</button></div>`);
      $modal.querySelector('[data-close]').textContent = 'Cancelar';
      document.getElementById('keep').onclick = () => { closeModal(); go('quiz'); };
      document.getElementById('discard').onclick = () => { closeModal(); start(mode, opts, true); };
      return;
    }
    $app.innerHTML = '<div class="spinner"></div>';
    const s = await buildSession(mode, opts);
    if (!s) { openModal('<h3>No hay repasos pendientes</h3><p class="muted">Cuando falles una pregunta, aquí aparecerán preguntas nuevas sobre esa misma regla al día siguiente, a los 3 días y a los 7 días.</p>'); return go('home'); }
    CUR = s; saveCur(); go('quiz');
  };
  document.getElementById('practica').onclick = () => start('practica');
  document.getElementById('repaso').onclick = () => start('repaso');
  document.getElementById('simulacro').onclick = () => {
    openModal(`<h3>Simulacro</h3><p class="muted">Como el examen: con reloj, sin pistas y con las explicaciones al final. Busca un lugar tranquilo, sin celular a la mano.</p><p class="muted small">Ritmo: ~2,4 min por pregunta. Si una te traba más de 3 minutos, sáltala y vuelve.</p><div class="row-actions"><button class="btn primary" id="go-sim">Completo · 50 preguntas · 2 h</button><button class="btn" id="go-sim-c">Corto · 25 preguntas · 1 h</button></div>`);
    $modal.querySelector('[data-close]').textContent = 'Cancelar';
    document.getElementById('go-sim').onclick = () => { closeModal(); start('simulacro'); };
    document.getElementById('go-sim-c').onclick = () => { closeModal(); start('simulacro', { corto: true }); };
  };
  const r = document.getElementById('resume'); if (r) r.onclick = () => go('quiz');
  const an = document.getElementById('ancla'); if (an) an.onclick = () => anclaDialog('A');
  const pr = document.getElementById('proto'); if (pr) pr.onclick = showProtocolo;
  const ex = document.getElementById('ext'); if (ex) ex.onclick = extDialog;
  const pr2 = document.getElementById('proto2'); if (pr2) pr2.onclick = showProtocolo;
  $app.querySelectorAll('[data-tipo]').forEach(b => b.onclick = () => start('tipo', { tipo: b.dataset.tipo }));
}
function homeAvisos(dExam, doneToday) {
  let h = '';
  if (S.plan && S.plan.h && doneToday === 0) h += `<div class="card note">📅 Tu plan: practicar a las <b>${esc(S.plan.h)}</b>${S.plan.l ? ` en <b>${esc(S.plan.l)}</b>` : ''}.</div>`;
  if (doneToday >= S.daily) h += `<div class="card note good">✅ Meta de hoy cumplida. Repartir la práctica en varios días rinde más que hacer mucho en uno: si quieres más, haz como máximo una sesión corta después de un descanso.</div>`;
  if (dExam >= 0 && dExam <= 3) h += `<div class="card note warn"><b>${dExam === 0 ? 'Hoy es el examen' : dExam === 1 ? 'Mañana es el examen' : 'Semana final'}</b>${dExam >= 2 ? ': menos cantidad y más repaso de errores. Haz la prueba ancla B.' : '.'} <button class="link-btn" id="proto">Ver protocolo del examen →</button></div>`;
  return h;
}
function showProtocolo() {
  openModal(`<div class="lesson"><h3>Protocolo del día del examen</h3><ol>
    <li><b>Duerme 7 a 9 horas</b> las dos noches antes: la falta de sueño afecta sobre todo la atención sostenida.</li>
    <li>El día antes, práctica suave o nada. No intentes aprender cosas nuevas.</li>
    <li>Computador cargado, buena conexión, cuarto en silencio y celular lejos.</li>
    <li><b>Lee las instrucciones</b>: ¿se puede volver atrás? ¿restan las malas?</li>
    <li>Ritmo de ~2,4 min por pregunta: la 10 al minuto 24, la 25 al minuto 60 y la 40 al minuto 96.</li>
    <li>Si una pasa de 3 minutos, márcala, sáltala y vuelve al final.</li>
    <li>Antes de marcar: relee la pregunta y comprueba que tu opción cumple <b>todas</b> las reglas (10 segundos).</li>
    <li>Si no restan las malas, no dejes ninguna en blanco.</li>
    <li>Si te bloqueas, respira lento unos segundos y pasa a la siguiente.</li></ol></div>`);
}
function extDialog() {
  openModal(`<h3>Test externo</h3><label class="field">¿Dónde lo hiciste?<input type="text" id="ex-n" placeholder="ej. PreparaOposiciones, matrices"></label><div class="grid2" style="margin-top:0"><label class="field">Acertadas<input type="number" id="ex-ok" min="0" inputmode="numeric"></label><label class="field">De cuántas<input type="number" id="ex-t" min="1" inputmode="numeric"></label></div>`);
  $modal.querySelector('[data-close]').textContent = 'Guardar';
  $modal.querySelector('[data-close]').addEventListener('click', () => {
    const ok = parseInt(document.getElementById('ex-ok').value, 10), t = parseInt(document.getElementById('ex-t').value, 10);
    if (t > 0 && ok >= 0 && ok <= t) { S.ext = S.ext || []; S.ext.push({ date: hoy(), n: document.getElementById('ex-n').value.trim(), ok, t }); save(); }
  }, { once: true });
}
function anclaDialog(k) {
  openModal(`<h3>Prueba ancla ${k}</h3><label class="field">¿Cuántas acertaste de 25?<input type="number" id="anc-v" min="0" max="25" inputmode="numeric"></label>`);
  const inp = document.getElementById('anc-v'); inp.focus();
  $modal.querySelector('[data-close]').textContent = 'Guardar';
  $modal.querySelector('[data-close]').addEventListener('click', () => {
    const v = parseInt(inp.value, 10);
    if (!isNaN(v) && v >= 0 && v <= 25) {
      S.anchors = S.anchors.filter(a => a.k !== k); S.anchors.push({ k, v, date: hoy() });
      if (k === 'A' && v >= 20 && !Object.keys(S.lvl).length) Object.keys(TIPOS).forEach(t => S.lvl[t] = 1);
      save(); render();
    }
  }, { once: true });
}

// ------------------------------------------------------------------ pregunta
const LOGICA = ['silogismo', 'condicional', 'ordenamiento', 'verdad_mentira', 'tabla_logica'];
function qParts(q) {
  const it = q.it;
  if (TIPOS[q.t].g === 'fig' && q.t !== 'cubo') return [it.q || PREG_FIG[q.t], ''];
  if (LOGICA.includes(q.t) && it.x && it.x.lines) {
    const set = new Set(it.x.lines);
    const rest = it.q.split('\n').filter(l => !set.has(l) && l !== 'Premisas:' && !l.startsWith('Se sabe que:'));
    const last = rest.pop() || '';
    return [rest.join('\n'), last];
  }
  return [it.q, ''];
}
function qText(q) { return qParts(q).filter(Boolean).join('\n'); }
function qBlock(q, small) {
  const [a, b] = qParts(q), st = small ? ' style="font-size:16px"' : '';
  return `${a ? `<div class="qtext"${st}>${esc(a)}</div>` : ''}${stemHtml(q)}${b ? `<div class="qtext"${st}>${esc(b)}</div>` : ''}`;
}
function stemHtml(q) {
  const t = q.t, it = q.it;
  if (TIPOS[t].g === 'fig' && t !== 'cubo') { if (t === 'intrusa') return ''; return `<div class="stem">${stemFig(t, it)}</div>`; }
  const x = it.x || {};
  let h = '';
  if (x.seq) h += `<div class="seq">${x.seq.map(v => `<span class="${v === '?' ? 'q' : ''}">${esc(v)}</span>`).join('')}</div>`;
  if (x.grid) h += `<table class="numgrid">${x.grid.map(r => `<tr>${r.map(v => `<td class="${v === '?' ? 'q' : ''}">${esc(v)}</td>`).join('')}</tr>`).join('')}</table>`;
  if (x.tri) h += triSvg(x.tri);
  if (x.lines) h += `<div class="lines">${x.lines.map(l => `<div>${esc(l)}</div>`).join('')}</div>`;
  if (x.code) h += `<pre class="code">${esc(x.code.join('\n'))}</pre>`;
  if (x.net) h += netSvg(x.net);
  return h ? `<div class="stem">${h}</div>` : '';
}
function optHtml(q, orig) {
  const t = q.t, it = q.it;
  if (TIPOS[t].g === 'fig' && t !== 'cubo') return optFig(t, it.o[orig], t === 'superposicion' ? it.s.n : (it.x && it.x.N) || 3);
  return `<span${t === 'cubo' ? ' class="big"' : ''}>${esc(it.o[orig])}</span>`;
}
function isFigOpts(q) { return TIPOS[q.t].g === 'fig' && q.t !== 'cubo'; }
function fmtTime(sec) { sec = Math.max(0, Math.round(sec)); const m = Math.floor(sec / 60), s = sec % 60; return `${m}:${String(s).padStart(2, '0')}`; }
function elapsed() { return CUR.mode === 'simulacro' ? (Date.now() - CUR.id) / 1000 : CUR.elapsed + (Date.now() - CUR.t0) / 1000; }

const CAUSAS = { regla: 'No conocía la regla', paso: 'Me equivoqué en un paso', descuido: 'Leí mal / descuido', adivine: 'Adiviné' };
function causeHtml(q) {
  return `<div class="cause"><p class="small" style="margin:0 0 6px"><b>¿Por qué fallaste?</b> Explicártelo ayuda a no repetirlo.</p><div class="row-actions" style="margin:0">${Object.entries(CAUSAS).map(([k, v]) => `<button class="chip${q.cause === k ? ' on' : ''}" data-cause="${k}">${v}</button>`).join('')}</div></div>`;
}
function hintText(q) {
  const it = q.it, x = it.x || {}, t = q.t;
  const num = v => +v;
  try {
    if (t === 'serie_num') { const v = x.seq.filter(a => a !== '?').map(num); return 'Las diferencias entre números seguidos son: ' + v.slice(1).map((a, i) => (a - v[i] >= 0 ? '+' : '') + (a - v[i])).join(', ') + '. ¿Qué patrón siguen?'; }
    if (t === 'serie_letras') {
      const A = it.q.includes('SIN Ñ') ? 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' : 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ';
      return 'Pasa las letras a números: ' + x.seq.filter(a => a !== '?').map(w => w.split('').map(ch => ch + (A.indexOf(ch) + 1)).join('')).join(', ') + '. Ahora busca el patrón.';
    }
    if (t === 'numeros_figura') { const f = (x.grid || x.tri)[0]; return `Mira la primera ${x.grid ? 'fila' : 'figura'}: ${f[0]} y ${f[1]} dan ${f[2]}. ¿Qué operación (suma, resta, producto, cuadrado…) lo logra? Compruébala en la segunda.`; }
    if (t === 'simbolos') return 'Empieza por esta igualdad: «' + x.lines[x.lines.length > 1 && /=\s*\d+$/.test(x.lines[0]) ? 0 : 0] + '». Despeja ese símbolo y reemplázalo en las demás.';
    if (t === 'operador') { const m = it.q.match(/(\d+)\s*\S\s*(\d+)/); return m ? `Copia la definición y reemplaza a = ${m[1]} y b = ${m[2]} (en ese orden). Si hay paréntesis, resuélvelos primero.` : 'Reemplaza a y b por los números en ese orden.'; }
    if (t === 'algoritmo') return `Haz una tabla con una columna por variable. Empieza con: ${x.code.filter(l => /^[a-z]\s*←\s*-?\d+$/.test(l)).join(', ')}. Luego ejecuta línea por línea.`;
    if (t === 'codificacion') { const m = it.q.match(/Si (\S+) se escribe (\S+),/); return m ? `Compara la primera letra: ${m[1][0]} → ${m[2][0]}. ¿Cuántas posiciones se movió? ¿Pasa lo mismo con la segunda (${m[1][1]} → ${m[2][1]})?` : ''; }
    if (t === 'verdad_mentira') { const n0 = x.lines[0].split(':')[0]; return `Supón que ${n0} dice la verdad. Si su frase es cierta, ¿qué sabes de los demás? Si llegas a una contradicción, entonces ${n0} miente.`; }
    if (t === 'tabla_logica') { const neg = x.lines.find(l => / no /.test(l)) || x.lines[0]; return `Haz una tabla (personas × opciones). Empieza marcando ✗ con: «${neg}»`; }
    if (t === 'ordenamiento') return `Dibuja una fila vertical (arriba el más alto). Empieza con «${x.lines[0]}» y ve agregando a los demás pista por pista.`;
    if (t === 'silogismo') return it.e[0];
    if (t === 'condicional') return 'Escribe la regla como «si P → Q». Ahora mira el dato: ¿afirma P, niega Q, afirma Q o niega P? Solo afirmar P o negar Q permiten concluir algo.';
  } catch (err) {}
  return METODO[t] ? METODO[t][0] + ' ' + (METODO[t][1] || '') : '';
}
function feedbackHtml(q) {
  const corrPos = q.order.indexOf(0);
  const f = !q.ok && q.ans !== null && q.it.f ? falloTxt(q.t, q.it.f[q.order[q.ans]]) : '';
  const head = q.ans === null ? '<p><b>La dejaste en blanco.</b></p>' : q.ok ? '<p><b>✓ ¡Correcto!</b></p>' : `<p><b>✗ Marcaste ${LETRAS[q.ans]}; la correcta es ${LETRAS[corrPos]}.</b> ${esc(f)}</p>`;
  const k = q.it.k ? `<div class="trap">⚠ La trampa más tentadora era la <b>${LETRAS[q.order.indexOf(q.it.k[0])]}</b>: ${esc(q.it.k[1])}.</div>` : '';
  const hyper = !q.ok && q.conf === 'seguro' ? '<div class="trap">⚡ Estabas seguro y fallaste: lee la explicación con calma. Los errores cometidos con seguridad son los que mejor se corrigen cuando se revisan.</div>' : '';
  return `<div class="why${q.ok ? ' good' : ''}">${head}${q.it.e.map(x => `<p>${esc(x)}</p>`).join('')}</div>${hyper}${k}`;
}
function renderQuiz() {
  if (!CUR) return go('home');
  CUR.t0 = Date.now();
  const q = CUR.items[CUR.i], n = CUR.items.length;
  q.v = 1; q.tIn = Date.now(); q.time = q.time || 0;
  const fig = isFigOpts(q);
  const sim = CUR.mode === 'simulacro';
  const fb = !sim && q.checked;
  if (fb) q.ok = q.ans !== null && q.order[q.ans] === 0;
  const corrPos = q.order.indexOf(0);
  const opts = q.order.map((orig, pos) => {
    let cls = q.ans === pos ? ' sel' : '';
    if (fb) cls = pos === corrPos ? ' right' : pos === q.ans ? ' wrong' : '';
    return `<button class="opt${cls}" data-pos="${pos}" ${fb ? 'disabled' : ''} aria-label="Opción ${LETRAS[pos]}"><span class="letter">${LETRAS[pos]}</span>${optHtml(q, orig)}</button>`;
  }).join('');
  const last = CUR.i === n - 1;
  const mainTxt = sim ? (last ? 'Terminar' : 'Siguiente') : (fb ? (last ? 'Ver resultados' : 'Siguiente') : 'Comprobar');
  $app.innerHTML = `
    <div class="top"><button class="icon-btn" id="exit">${ICON.back} Salir</button><div style="display:flex;gap:8px;align-items:center"><span class="timer" id="timer"></span><button class="icon-btn" id="map" aria-label="Ver todas las preguntas">▦</button></div></div>
    <div class="qhead"><div class="progress"><i style="width:${(CUR.items.filter(x => x.ans !== null).length) / n * 100}%"></i></div><span class="muted small" style="font-weight:700">${CUR.i + 1}/${n}</span></div>
    <div class="qmeta"><span>${sim ? `Pregunta ${CUR.i + 1}` : `${TIPOS[q.t].n} · ${NIV_TXT[NIV.indexOf(q.it.n)]}`}</span>${sim ? '' : `<button class="link-btn" id="how">¿Cómo se resuelve?</button>`}</div>
    <div id="pace" class="pace"></div>
    ${qBlock(q)}
    ${!sim && !fb && lvlOf(q.t) <= 1 ? (q.hint ? `<div class="why small"><p><b>💡 Primer paso:</b> ${esc(hintText(q))}</p><p class="muted">Ahora termina tú.</p></div>` : `<button class="link-btn" id="hint" style="margin:-4px 0 10px">💡 Ver el primer paso</button>`) : ''}
    ${!sim && !fb && S.thinkFirst !== false && !q.revealed && q.t !== 'intrusa' ? `<div class="think"><p><b>Primero piensa tu respuesta</b> sin mirar las opciones: ¿qué regla ves y cómo debería ser lo que falta?</p><button class="btn primary" id="reveal">Ya la pensé · ver opciones</button></div>` : `<div class="options${fig ? ' fig' : ''}">${opts}</div>
    ${!sim && !fb ? `<div class="checkrow"><span class="muted small">Comprobar:</span><button class="btn" id="dudo" ${q.ans === null ? 'disabled' : ''}>Tengo dudas</button><button class="btn primary" id="next" ${q.ans === null ? 'disabled' : ''}>Estoy seguro</button></div>` : ''}`}
    ${fb ? `<div id="fb">${feedbackHtml(q)}${q.ok ? '' : causeHtml(q)}<div class="row-actions"><a class="chip" href="${ytLink(q.t)}" target="_blank" rel="noopener">▶ Videos de este tipo</a></div></div>` : ''}
    <div class="navbar"><div class="in">
      <button class="btn ghost" id="prev" ${CUR.i === 0 ? 'disabled style="opacity:.4"' : ''} aria-label="Anterior">${ICON.back}</button>
      ${fb ? '' : `<button class="btn ghost" id="skip">${q.ans === null ? 'Saltar' : 'Después'}</button>`}
      ${!sim && !fb ? '' : `<button class="btn primary" id="next" ${!fb && q.ans === null ? 'disabled' : ''}>${mainTxt}</button>`}
    </div></div>`;
  if (!fb) $app.querySelectorAll('.opt').forEach(b => b.onclick = () => { q.ans = +b.dataset.pos; saveCur(); $app.querySelectorAll('.opt').forEach(o => o.classList.toggle('sel', +o.dataset.pos === q.ans)); const nb = document.getElementById('next'); if (nb) nb.disabled = false; const du = document.getElementById('dudo'); if (du) du.disabled = false; const sk = document.getElementById('skip'); if (sk) sk.textContent = 'Después'; });
  const nx = document.getElementById('next'); if (nx) nx.onclick = () => { if (!sim && !q.checked) q.conf = 'seguro'; next(); };
  const du = document.getElementById('dudo'); if (du) du.onclick = () => { q.conf = 'dudo'; next(); };
  const hb = document.getElementById('hint'); if (hb) hb.onclick = () => { q.hint = true; saveCur(); renderQuiz(); };
  const rv = document.getElementById('reveal'); if (rv) rv.onclick = () => { q.revealed = true; saveCur(); renderQuiz(); };
  $app.querySelectorAll('[data-cause]').forEach(b => b.onclick = () => { q.cause = b.dataset.cause; saveCur(); $app.querySelectorAll('[data-cause]').forEach(o => o.classList.toggle('on', o.dataset.cause === q.cause)); });
  const sk = document.getElementById('skip'); if (sk) sk.onclick = () => advance(true);
  document.getElementById('prev').onclick = () => { if (CUR.i > 0) { stopClock(); CUR.i--; saveCur(); renderQuiz(); window.scrollTo(0, 0); } };
  document.getElementById('exit').onclick = () => { stopClock(); saveCur(); go('home'); };
  document.getElementById('map').onclick = showMap;
  const how = document.getElementById('how'); if (how) how.onclick = () => showMetodo(q.t);
  if (fb) { const el = document.getElementById('fb'); if (el && !q._scrolled) { q._scrolled = true; setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50); } }
  const tick = () => {
    const el = document.getElementById('timer'); if (!el) return;
    if (CUR.limit) { const left = CUR.limit - elapsed(); el.textContent = '⏱ ' + fmtTime(left); el.classList.toggle('low', left < 600); if (left <= 0) finish(); }
    else el.textContent = '⏱ ' + fmtTime(elapsed());
    const w = document.getElementById('pace');
    if (w) {
      const tq = qTime(q);
      if (sim) {
        // ritmo del simulacro: 2,4 min por pregunta
        const done = CUR.items.filter(x => x.ans !== null).length, debe = Math.floor(elapsed() / 144);
        w.textContent = done >= debe ? '✓ Vas a buen ritmo' : `⚠ Vas ${debe - done} pregunta${debe - done > 1 ? 's' : ''} atrás del ritmo`;
        w.className = 'pace' + (done >= debe ? '' : ' warn');
      } else if (tq > 180 && q.ans === null) { w.textContent = '⏳ Llevas más de 3 min: en el examen conviene saltarla y volver al final.'; w.className = 'pace warn'; }
      else { w.textContent = ''; w.className = 'pace'; }
    }
  };
  tick(); if (TIMER) clearInterval(TIMER); TIMER = setInterval(tick, 1000);
  // la primera vez que aparece un tipo, mostrar cómo se resuelve
  S.intro = S.intro || {};
  CUR.intros = CUR.intros || 0;
  if (!sim && CUR.intros < 3 && !S.intro[q.t] && !(S.hist[q.t] && S.hist[q.t].tot)) { S.intro[q.t] = 1; CUR.intros++; save(); saveCur(); showMetodo(q.t, true); }
}
function stopClock() {
  if (!CUR) return;
  CUR.elapsed = elapsed(); CUR.t0 = Date.now();
  const q = CUR.items[CUR.i]; if (q && q.tIn) { q.time = (q.time || 0) + (Date.now() - q.tIn) / 1000; q.tIn = Date.now(); }
}
function qTime(q) { return (q.time || 0) + (q.tIn ? (Date.now() - q.tIn) / 1000 : 0); }
function showMap() {
  const cells = CUR.items.map((x, k) => `<button class="mapc${x.ans !== null ? ' done' : x.v ? ' skip' : ''}${k === CUR.i ? ' cur' : ''}" data-j="${k}">${k + 1}</button>`).join('');
  const blank = CUR.items.filter(x => x.ans === null).length;
  openModal(`<h3>Tus preguntas</h3><p class="muted small">Toca un número para ir a esa pregunta. ${blank ? `Te falta${blank > 1 ? 'n' : ''} ${blank}.` : 'Ya respondiste todas.'} <span style="white-space:nowrap">■ respondida · ◌ saltada</span></p><div class="mapgrid">${cells}</div>${blank === 0 || CUR.mode === 'simulacro' ? '<div class="row-actions"><button class="btn primary" id="fin-now">Terminar y ver resultados</button></div>' : ''}`);
  $modal.querySelector('[data-close]').textContent = 'Cerrar';
  $modal.querySelectorAll('[data-j]').forEach(b => b.onclick = () => { stopClock(); CUR.i = +b.dataset.j; saveCur(); closeModal(); renderQuiz(); window.scrollTo(0, 0); });
  const fn = document.getElementById('fin-now'); if (fn) fn.onclick = () => { closeModal(); finishConfirm(); };
}
function advance(skip) {
  stopClock();
  const n = CUR.items.length;
  const pend = k => CUR.items[k].ans === null && !(skip && k === CUR.i);
  // ir a la siguiente pregunta sin responder (después de esta; si no hay, la primera de antes)
  let j = -1;
  for (let k = CUR.i + 1; k < n; k++) if (pend(k)) { j = k; break; }
  if (j < 0 && !skip) for (let k = 0; k < CUR.i; k++) if (pend(k)) { j = k; break; }
  if (j >= 0) { CUR.i = j; saveCur(); renderQuiz(); window.scrollTo(0, 0); return; }
  finishConfirm();
}
function finishConfirm() {
  const blanks = CUR.items.map((x, k) => x.ans === null ? k : -1).filter(k => k >= 0);
  if (!blanks.length) return finish();
  openModal(`<h3>Te falta${blanks.length > 1 ? 'n' : ''} ${blanks.length} pregunta${blanks.length > 1 ? 's' : ''}</h3><p class="muted">Puedes volver a ${blanks.length > 1 ? 'ellas' : 'ella'} o terminar así (las que quedan en blanco cuentan como error).</p><div class="row-actions"><button class="btn primary" id="go-blank">Ir a la primera sin responder</button><button class="btn" id="fin-anyway">Terminar así</button></div>`);
  $modal.querySelector('[data-close]').textContent = 'Cancelar';
  document.getElementById('go-blank').onclick = () => { closeModal(); CUR.i = blanks[0]; saveCur(); renderQuiz(); window.scrollTo(0, 0); };
  document.getElementById('fin-anyway').onclick = () => { closeModal(); finish(); };
}
function next() {
  const q = CUR.items[CUR.i];
  if (CUR.mode !== 'simulacro' && !q.checked) {
    if (q.ans === null) return;
    q.checked = true; saveCur(); stopClock(); renderQuiz(); return;
  }
  if (CUR.mode === 'simulacro' && q.ans === null) return;
  advance(false);
}
document.addEventListener('keydown', e => {
  if (VIEW !== 'quiz' || !CUR || !$modal.hidden) return;
  const k = e.key.toUpperCase();
  const idx = '12345'.indexOf(k) >= 0 ? '12345'.indexOf(k) : LETRAS.indexOf(k);
  if (idx >= 0 && k.length === 1) { const b = $app.querySelector(`.opt[data-pos="${idx}"]`); if (b) b.click(); }
  if (e.key === 'Enter') { const b = document.getElementById('next'); if (b && !b.disabled) b.click(); }
});

function finish() {
  if (TIMER) { clearInterval(TIMER); TIMER = null; }
  stopClock();
  const today = hoy();
  const res = { id: CUR.id, date: today, mode: CUR.mode, total: CUR.items.length, correct: 0, mins: Math.round(CUR.elapsed / 60), byType: {}, conf: { seguro: [0, 0], dudo: [0, 0] }, causes: {}, secs: 0 };
  const made = new Set();
  CUR.items.forEach((q, idx) => {
    const ok = q.ans !== null && q.order[q.ans] === 0;
    q.ok = ok;
    if (ok) res.correct++;
    if (q.conf && res.conf[q.conf]) { res.conf[q.conf][1]++; if (ok) res.conf[q.conf][0]++; }
    if (!ok && q.cause) res.causes[q.cause] = (res.causes[q.cause] || 0) + 1;
    res.secs += q.time || 0;
    const bt = res.byType[q.t] || (res.byType[q.t] = [0, 0]); bt[1]++; if (ok) bt[0]++;
    // las preguntas en blanco (saltadas o abandonadas) no cuentan para tu nivel ni para los repasos
    if (q.ans === null) return;
    S.seen[q.it.i] = 1;
    // el simulacro mide, no ajusta: no cambia tu nivel ni tus porcentajes por tipo
    if (CUR.mode !== 'simulacro') {
      const h = histOf(q.t);
      // con pista cuenta como intento, pero no como acierto para subir de nivel
      h.n++; h.tot++; if (ok) { h.ok++; if (!q.hint) h.c++; }
      h.all.push(ok ? 1 : 0); if (h.all.length > 30) h.all.shift();
      if (h.n >= 8) {
        const acc = h.c / h.n, L = lvlOf(q.t);
        if (acc > 0.85 && L < 3) S.lvl[q.t] = L + 1;
        else if (acc < 0.7 && L > 0) S.lvl[q.t] = L - 1;
        h.n = 0; h.c = 0;
      }
    }
    if (q.revId) { const r = S.rev.find(x => x.id === q.revId); if (r) r.done = true; }
    // acertar dudando también merece un repaso (a 3 días), si esa regla no tiene uno pendiente
    if (ok && (q.conf === 'dudo' || q.hint) && !S.rev.some(r => !r.done && r.t === q.t && r.r === q.it.r)) {
      S.rev.push({ id: `${CUR.id}-${idx}-dudo`, src: `${CUR.id}-${idx}`, t: q.t, r: q.it.r, due: addDays(today, 3), done: false });
    }
    if (!ok) {
      const fallo = q.ans !== null ? (q.it.f ? q.it.f[q.order[q.ans]] : null) : null;
      const regla = (q.t === 'matriz' && fallo) ? fallo : q.it.r;
      q.revRegla = regla;
      // un solo calendario por regla y sesión (no se acumulan)
      const key = q.t + '|' + regla;
      if (made.has(key)) return;
      made.add(key);
      S.rev = S.rev.filter(r => r.done || !(r.t === q.t && r.r === regla));
      if (q.cause === 'descuido') { S.desc = S.desc || {}; S.desc[`${CUR.id}-${idx}`] = 1; S.rev.push({ id: `${CUR.id}-${idx}-d3`, src: `${CUR.id}-${idx}`, t: q.t, r: regla, due: addDays(today, 3), done: false }); return; }
      [1, 3, 7].forEach(d => S.rev.push({ id: `${CUR.id}-${idx}-${d}`, src: `${CUR.id}-${idx}`, t: q.t, r: regla, due: addDays(today, d), done: false }));
    }
  });
  S.sessions.push(res);
  S.rev = S.rev.filter(r => !r.done || r.due >= addDays(today, -30));
  save();
  LAST = CUR; CUR = null; saveCur();
  go('results');
}

// ------------------------------------------------------------------ resultados
function ring(p) {
  const r = 46, c = 2 * Math.PI * r, col = p >= 0.85 ? 'var(--ok)' : p >= 0.7 ? 'var(--primary)' : 'var(--bad)';
  return `<svg class="ring" viewBox="0 0 110 110"><circle cx="55" cy="55" r="${r}" fill="none" stroke="var(--surface-2)" stroke-width="12"/><circle cx="55" cy="55" r="${r}" fill="none" stroke="${col}" stroke-width="12" stroke-linecap="round" stroke-dasharray="${c * p} ${c}" transform="rotate(-90 55 55)"/><text x="55" y="62" text-anchor="middle" font-size="24" font-weight="800" fill="var(--ink)" font-family="Plus Jakarta Sans, sans-serif">${Math.round(p * 100)}%</text></svg>`;
}
const ATTR_TXT = { forma: 'la forma', cantidad: 'la cantidad', tamano: 'el tamaño', color: 'el color' };
const REGLA_TXT = { constante: 'se mantiene igual', progresion: 'progresión', aritmetica: 'suma o resta', distribucion: 'distribución de tres' };
function falloTxt(t, f) {
  if (!f) return '';
  if (t === 'matriz') return 'Tu opción fallaba en: ' + f.split(/;\s*/).map(p => { const [a, r] = p.split(':'); return `${ATTR_TXT[a] || a} (${REGLA_TXT[r] || r})`; }).join(', ') + '.';
  if (t === 'analogia') return 'Tu opción: ' + f.replace('analogia: ', '') + '.';
  return '';
}
function planHtml() {
  const p = S.plan || {};
  return `<div class="card" style="margin-top:12px"><b>📅 Tu plan para la próxima práctica</b><p class="muted small" style="margin:4px 0 8px">Decidir de antemano cuándo y dónde vas a practicar aumenta mucho la probabilidad de hacerlo.</p>
    <div class="grid2" style="margin-top:0"><label class="field" style="margin:0">Hora<input type="time" id="plan-h" value="${esc(p.h || '')}"></label><label class="field" style="margin:0">Lugar<input type="text" id="plan-l" value="${esc(p.l || '')}" placeholder="ej. mi escritorio"></label></div>
    <div class="row-actions"><button class="chip" id="plan-ok">Guardar plan</button></div></div>`;
}
function bindPlan() {
  const b = document.getElementById('plan-ok'); if (!b) return;
  b.onclick = () => { S.plan = { h: document.getElementById('plan-h').value, l: document.getElementById('plan-l').value.trim(), date: hoy() }; save(); b.textContent = '✓ Plan guardado'; };
}
let RTAB = 'mal';
function renderResults() {
  const s = LAST; if (!s) return go('home');
  const tot = s.items.length, ok = s.items.filter(x => x.ok).length, p = ok / tot;
  const msg = p >= 0.9 ? '¡Excelente!' : p >= 0.75 ? '¡Muy bien!' : p >= 0.55 ? 'Vas por buen camino' : 'Cada error es una lección';
  const list = s.items.map((q, idx) => ({ q, idx })).filter(({ q }) => RTAB === 'todas' || !q.ok);
  const cards = list.map(({ q, idx }) => {
    const corrPos = q.order.indexOf(0);
    const fig = isFigOpts(q);
    const opts = q.order.map((orig, pos) => {
      const cls = pos === corrPos ? ' right' : pos === q.ans ? ' wrong' : '';
      return `<button class="opt${cls}" disabled><span class="letter">${LETRAS[pos]}</span>${optHtml(q, orig)}</button>`;
    }).join('');
    const k = q.it.k ? `<div class="trap">⚠ La trampa más tentadora era la <b>${LETRAS[q.order.indexOf(q.it.k[0])]}</b>: ${esc(q.it.k[1])}.</div>` : '';
    const f = !q.ok && q.ans !== null && q.it.f ? falloTxt(q.t, q.it.f[q.order[q.ans]]) : '';
    const src = `${s.id}-${idx}`;
    const isDesc = !!(S.desc && S.desc[src]) && !q.ok;
    const n0 = list.findIndex(x => x.idx === idx);
    const resumen = q.ans === null ? 'en blanco' : q.ok ? 'correcta' : `marcaste ${LETRAS[q.ans]}, era ${LETRAS[corrPos]}`;
    return `<details class="card review" ${n0 < 2 ? 'open' : ''}>
      <summary class="rh"><span class="dot ${q.ok ? 'ok' : 'bad'}">${q.ok ? '✓' : '✗'}</span><span>${idx + 1}. ${TIPOS[q.t].n} <span class="muted small">· ${resumen}</span></span></summary>
      ${qBlock(q, true)}
      <div class="options${fig ? ' fig' : ''}">${opts}</div>
      <div class="why">${q.ans === null ? '<p><b>La dejaste en blanco.</b></p>' : q.ok ? '' : `<p><b>Marcaste ${LETRAS[q.ans]}; la correcta es ${LETRAS[corrPos]}.</b> ${esc(f)}</p>`}${q.it.e.map(x => `<p>${esc(x)}</p>`).join('')}</div>
      ${k}
      <div class="row-actions">
        <button class="chip" data-how="${q.t}">📘 Cómo se resuelve</button>
        <a class="chip" href="${ytLink(q.t)}" target="_blank" rel="noopener">▶ Videos</a>
        ${q.ok ? '' : `<button class="chip${isDesc ? ' on' : ''}" data-desc="${src}" data-t="${q.t}" data-r="${esc(q.revRegla || q.it.r)}">${isDesc ? '✓ Marcado como descuido' : 'Fue un descuido'}</button>`}
        ${q.time ? `<span class="chip" style="cursor:default">⏱ ${fmtTime(q.time)}</span>` : ''}
      </div></details>`;
  }).join('');
  const byT = Object.entries(s.items.filter(q => q.ans !== null).reduce((m, q) => { (m[q.t] = m[q.t] || [0, 0])[1]++; if (q.ok) m[q.t][0]++; return m; }, {}))
    .sort((a, b) => a[1][0] / a[1][1] - b[1][0] / b[1][1]).slice(0, 3);
  $app.innerHTML = topBar(true, 'Resultados') + `
    <div class="card"><div class="score">${ring(p)}<div><h1>${ok} de ${tot}</h1><p>${msg} · ${Math.round(s.elapsed / 60)} min</p>
      ${byT.length ? `<p class="small" style="margin-top:8px">A reforzar: ${byT.filter(x => x[1][0] < x[1][1]).map(x => TIPOS[x[0]].n).join(', ') || 'nada, ¡todo bien!'}</p>` : ''}</div></div>
      ${(() => {
        const avg = s.items.reduce((a, q) => a + (q.time || 0), 0) / tot;
        const seg = s.items.filter(q => q.conf === 'seguro'), dud = s.items.filter(q => q.conf === 'dudo');
        const pc = arr => arr.length ? Math.round(arr.filter(q => q.ok).length / arr.length * 100) + '%' : '—';
        return `<div class="kv"><span>Tiempo promedio por pregunta</span><span class="${avg > 144 ? 'bad-t' : ''}">${fmtTime(avg)} <span class="muted small">(meta ≤ 2:24)</span></span></div>` +
          (seg.length + dud.length ? `<div class="kv"><span>Acierto cuando estabas seguro</span><span>${pc(seg)} <span class="muted small">(${seg.length})</span></span></div><div class="kv"><span>Acierto cuando dudabas</span><span>${pc(dud)} <span class="muted small">(${dud.length})</span></span></div>` : '');
      })()}</div>
    ${s.mode !== 'simulacro' ? planHtml() : ''}
    <div class="tabs"><button data-tab="mal" class="${RTAB === 'mal' ? 'on' : ''}">Mis errores (${tot - ok})</button><button data-tab="todas" class="${RTAB === 'todas' ? 'on' : ''}">Todas (${tot})</button></div>
    ${cards || '<div class="empty">¡Ningún error! 🎉</div>'}
    <p class="muted small">${s.mode === 'simulacro' ? 'El simulacro no cambia tu nivel, pero tus errores también vuelven como repasos. ' : ''}Las preguntas que fallaste vuelven en versiones nuevas mañana, en 3 días y en 7 días. Si fallaste por leer rápido y no por no saber la regla, márcala como «descuido»: vuelve una sola vez y te recordamos leer con calma.</p>
    <div class="navbar"><div class="in"><button class="btn primary" data-go="home">Volver al inicio</button></div></div>`;
  bindGo();
  $app.querySelectorAll('[data-tab]').forEach(b => b.onclick = () => { RTAB = b.dataset.tab; renderResults(); });
  bindPlan();
  $app.querySelectorAll('[data-how]').forEach(b => b.onclick = () => showMetodo(b.dataset.how));
  $app.querySelectorAll('[data-desc]').forEach(b => b.onclick = () => {
    const src = b.dataset.desc;
    const mine = S.rev.filter(r => r.src === src && !r.done);
    const today = hoy();
    S.desc = S.desc || {};
    if (!S.desc[src]) { S.rev = S.rev.filter(r => r.src !== src || r.done); S.rev.push({ id: `${src}-d3`, src, t: b.dataset.t, r: b.dataset.r, due: addDays(today, 3), done: false }); S.desc[src] = 1; }
    else { S.rev = S.rev.filter(r => r.src !== src || r.done); [1, 3, 7].forEach(d => S.rev.push({ id: `${src}-${d}`, src, t: b.dataset.t, r: b.dataset.r, due: addDays(today, d), done: false })); delete S.desc[src]; }
    save(); const y = window.scrollY; renderResults(); window.scrollTo(0, y);
  });
}

// ------------------------------------------------------------------ progreso
function renderProgress() {
  const ss = S.sessions.slice(-20);
  let chart = '<div class="empty">Cuando hagas tu primera práctica, aquí verás cómo vas.</div>';
  if (ss.length) {
    const W = 300, H = 190, pad = 44, n = ss.length;
    const X = i => n === 1 ? W / 2 : pad + i * (W - 2 * pad) / (n - 1), Y = v => H - pad - v * (H - 2 * pad);
    let g = '';
    [0, .5, .7, .85, 1].forEach(v => { g += `<line x1="${pad}" x2="${W - pad}" y1="${Y(v)}" y2="${Y(v)}" stroke="var(--line)" ${v === .85 ? 'stroke-dasharray="6 5"' : ''}/><text x="${pad - 6}" y="${Y(v) + 5}" text-anchor="end" font-size="13" fill="var(--ink-3)">${v * 100}%</text>`; });
    const pts = ss.map((s, i) => [X(i), Y(s.correct / s.total)]);
    g += `<polyline points="${P(pts)}" fill="none" stroke="var(--primary)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>`;
    pts.forEach(([x, y], i) => { g += `<circle cx="${x}" cy="${y}" r="${ss[i].mode === 'simulacro' ? 6 : 4}" fill="${ss[i].mode === 'simulacro' ? 'var(--warn)' : 'var(--primary)'}"/>`; });
    chart = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Porcentaje de acierto por sesión">${g}</svg><p class="muted small" style="margin:6px 0 0">Cada punto es una sesión (los naranjas son simulacros). La línea punteada es 85%.</p>`;
  }
  const rows = Object.entries(TIPOS).map(([t, info]) => ({ t, info, a: accOf(t), h: S.hist[t] }))
    .sort((x, y) => (x.a ?? 2) - (y.a ?? 2))
    .map(({ t, info, a, h }) => `<div class="kv"><span>${info.n} <span class="lvl" style="margin-left:6px">${NIV_TXT[lvlOf(t)]}</span></span><span class="muted">${a === null ? '—' : Math.round(a * 100) + '%'} ${h ? `· ${h.tot}` : ''}</span></div>`).join('');
  const sims = S.sessions.filter(s => s.mode === 'simulacro');
  const tot = S.sessions.reduce((a, s) => a + s.total, 0), okT = S.sessions.reduce((a, s) => a + s.correct, 0);
  $app.innerHTML = topBar(true, 'Mi progreso') + `
    <div class="card chart">${chart}</div>
    <div class="grid2">
      <div class="card"><span class="muted small">Preguntas respondidas</span><h2 style="margin:4px 0 0">${tot}</h2></div>
      <div class="card"><span class="muted small">Acierto total</span><h2 style="margin:4px 0 0">${tot ? Math.round(okT / tot * 100) + '%' : '—'}</h2></div>
      <div class="card"><span class="muted small">Último simulacro</span><h2 style="margin:4px 0 0">${sims.length ? `${sims[sims.length - 1].correct}/${sims[sims.length - 1].total}` : '—'}</h2></div>
      <div class="card"><span class="muted small">Pruebas ancla</span><h2 style="margin:4px 0 0">${S.anchors.length ? S.anchors.map(a => `${a.k}: ${a.v}/25`).join(' · ') : '—'}</h2></div>
    </div>
    ${(() => {
      const c = {}; let sg = [0, 0], du = [0, 0];
      S.sessions.forEach(x => { Object.entries(x.causes || {}).forEach(([k, v]) => c[k] = (c[k] || 0) + v); if (x.conf) { sg[0] += x.conf.seguro[0]; sg[1] += x.conf.seguro[1]; du[0] += x.conf.dudo[0]; du[1] += x.conf.dudo[1]; } });
      const tc = Object.values(c).reduce((a, b) => a + b, 0);
      if (!tc && !sg[1] && !du[1]) return '';
      return `<h2 class="section">Cómo te equivocas</h2><div class="card">${Object.entries(CAUSAS).map(([k, v]) => `<div class="kv"><span>${v}</span><span class="muted">${c[k] || 0}${tc ? ` · ${Math.round((c[k] || 0) / tc * 100)}%` : ''}</span></div>`).join('')}
        ${sg[1] ? `<div class="kv"><span>Acierto cuando estabas seguro</span><span class="muted">${Math.round(sg[0] / sg[1] * 100)}% (${sg[1]})</span></div>` : ''}${du[1] ? `<div class="kv"><span>Acierto cuando dudabas</span><span class="muted">${Math.round(du[0] / du[1] * 100)}% (${du[1]})</span></div>` : ''}
        <p class="muted small" style="margin:8px 0 0">${(c.descuido || 0) / (tc || 1) >= 0.3 ? 'Muchos errores son por leer rápido: usa siempre la rutina de 10 segundos antes de marcar.' : (c.regla || 0) / (tc || 1) >= 0.4 ? 'La mayoría de errores son por no conocer la regla: abre «¿Cómo se resuelve?» y mira el ejemplo resuelto antes de practicar ese tipo.' : 'Sigue marcando por qué fallas: así la app y tú saben qué reforzar.'}</p></div>`;
    })()}
    ${(S.ext || []).length ? `<h2 class="section">Tests externos (hechos por personas)</h2><div class="card">${S.ext.slice(-8).reverse().map(e => `<div class="kv"><span>${esc(e.date)} · ${esc(e.n || 'Test')}</span><span class="muted">${e.ok}/${e.t} · ${Math.round(e.ok / e.t * 100)}%</span></div>`).join('')}</div>` : ''}
    <h2 class="section">Por tipo (de más débil a más fuerte)</h2>
    <div class="card">${rows}</div>
    <div class="row-actions" style="margin-top:14px">${!S.anchors.find(a => a.k === 'A') ? '<button class="chip" data-anc="A">Anotar prueba ancla A</button>' : ''}<button class="chip" data-anc="B">Anotar prueba ancla B</button></div>`;
  bindGo();
  $app.querySelectorAll('[data-anc]').forEach(b => b.onclick = () => anclaDialog(b.dataset.anc));
}

// ------------------------------------------------------------------ ajustes
function renderSettings() {
  $app.innerHTML = topBar(true, 'Ajustes') + `
    <div class="card">
      <label class="field">Fecha de tu examen<input type="date" id="exam" value="${S.exam}"></label>
      <label class="field">Preguntas por práctica diaria<input type="number" id="daily" min="5" max="60" value="${S.daily}"></label>
      <label class="field" style="flex-direction:row;align-items:center;gap:10px"><input type="checkbox" id="think" ${S.thinkFirst !== false ? 'checked' : ''} style="width:20px;height:20px"> Pensar mi respuesta antes de ver las opciones (en práctica)</label>
      <label class="field">Apariencia
        <div class="tabs" style="margin:0">${['auto', 'light', 'dark'].map(m => `<button data-theme="${m}" class="${S.theme === m ? 'on' : ''}">${{ auto: 'Automática', light: 'Clara', dark: 'Oscura' }[m]}</button>`).join('')}</div></label>
    </div>
    <h2 class="section">Tu progreso</h2>
    <div class="card">
      <p class="muted small" style="margin-top:0">Todo se guarda solo en este navegador. Descarga una copia para no perderla o para pasarla a otro dispositivo.</p>
      <div class="row-actions"><button class="chip" id="exp">⬇ Descargar copia</button><label class="chip">⬆ Cargar copia<input type="file" id="imp" accept="application/json" hidden></label><button class="chip" id="reset">Borrar todo</button></div>
    </div>
    <h2 class="section">Cómo funciona</h2>
    <div class="card small">
      <p style="margin-top:0"><b>Se adapta a ti.</b> Cada tipo de pregunta tiene su propio nivel (1 a 4). Después de 8 respuestas de un tipo, si aciertas más del 85% sube de nivel; si aciertas menos del 70%, baja.</p>
      <p><b>Repite tus errores.</b> Cada error vuelve con una pregunta nueva de la misma regla al día siguiente, a los 3 días y a los 7 días (repaso espaciado).</p>
      <p><b>Mezcla los tipos.</b> Practicar tipos mezclados ayuda a reconocer qué regla usar, como en el examen real.</p>
      <p><b>Corrige al instante y te pregunta por qué fallaste.</b> Explicarte el error y revisar con calma los errores que cometiste estando seguro ayuda a no repetirlos.</p>
      <p><b>Ejemplos resueltos al empezar.</b> En los primeros niveles te muestra un ejemplo resuelto paso a paso; al subir de nivel deja de mostrarlos, porque ya estorban.</p>
      <p><b>Preguntas comprobadas.</b> Las de figuras y las de lógica se comprueban por código para que solo una opción sea correcta; en las numéricas la respuesta se calcula. Las analogías verbales están escritas a mano. Si ves una pregunta que crees mal hecha, avísale a quien te ayuda a mantener la app.</p>
      <p style="margin-bottom:0" class="muted">Código abierto: <a href="https://github.com/lianmedicin-blip/entrenador-razonamiento" target="_blank" rel="noopener">github.com/lianmedicin-blip/entrenador-razonamiento</a></p>
    </div>`;
  bindGo();
  document.getElementById('exam').onchange = e => { S.exam = e.target.value || S.exam; save(); };
  document.getElementById('think').onchange = e => { S.thinkFirst = e.target.checked; save(); };
  document.getElementById('daily').onchange = e => { const v = parseInt(e.target.value, 10); if (v >= 5 && v <= 60) { S.daily = v; save(); } };
  $app.querySelectorAll('[data-theme]').forEach(b => b.onclick = () => { S.theme = b.dataset.theme; save(); applyTheme(); renderSettings(); });
  document.getElementById('exp').onclick = () => {
    const blob = new Blob([JSON.stringify(S)], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `progreso-entrenador-${hoy()}.json`; a.click();
  };
  document.getElementById('imp').onchange = e => {
    const f = e.target.files[0]; if (!f) return;
    f.text().then(t => { try { const d = JSON.parse(t); if (d && d.v === 1) { S = d; save(); applyTheme(); openModal('<h3>Copia cargada</h3><p class="muted">Tu progreso quedó restaurado.</p>'); } } catch (err) { openModal('<h3>No se pudo leer el archivo</h3>'); } });
  };
  document.getElementById('reset').onclick = () => {
    openModal('<h3>¿Borrar todo tu progreso?</h3><p class="muted">No se puede deshacer. Descarga una copia antes si la quieres guardar.</p><div class="row-actions"><button class="btn" id="really" style="background:var(--bad);color:#fff">Sí, borrar</button></div>');
    document.getElementById('really').onclick = () => { S = nuevoEstado(); CUR = null; save(); saveCur(); closeModal(); go('home'); };
  };
}

render();
