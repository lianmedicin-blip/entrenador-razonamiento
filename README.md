# Entrenador de razonamiento lógico y abstracto

**Úsalo aquí:** https://lianmedicin-blip.github.io/entrenador-razonamiento/

Página web de práctica para exámenes de razonamiento lógico y abstracto (psicotécnicos). Funciona en el celular y en el computador, sin cuenta y sin conexión a ningún servicio: el progreso se guarda en el propio navegador.

## Qué hace
- **25 tipos de pregunta**: matrices, espejos, girar figuras, papel doblado,, series de figuras, giros, superposición, dominós, figura que no pertenece, analogías de figuras, cubos y desarrollos, series de números y de letras, números en figuras, ecuaciones con símbolos, operadores inventados, seguir un procedimiento (pseudocódigo), silogismos, condicionales, ordenamiento, verdades y mentiras, tablas lógicas, codificación, problemas numéricos y analogías verbales.
- **Se adapta**: cada tipo tiene su nivel (1–4); sube con más de 85 % de acierto y baja con menos de 70 %.
- **Repaso espaciado**: cada error vuelve con una pregunta nueva de la misma regla a 1, 3 y 7 días.
- **Explicación de cada error**, la trampa más tentadora y enlace a videos.
- **Simulacro** de 50 preguntas en 2 horas.

## Preguntas verificadas
- Figuras: `examen.py` genera cada pregunta y comprueba por código que solo una opción cumple las reglas; las opciones incorrectas se construyen para que no se pueda adivinar sin razonar.
- Texto y lógica: `tools/textgen.py` calcula cada respuesta; ordenamientos, verdades y mentiras, tablas lógicas, silogismos y condicionales se verifican por fuerza bruta (una sola solución).

## Regenerar el banco
```bash
pip install matplotlib
python3 tools/banco_figuras.py 150
python3 tools/banco_texto.py 120
```
El generador de exámenes en PDF sigue disponible: `python3 examen.py --plan plan.json --salida hoy`.
