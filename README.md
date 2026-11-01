# Entrenador de razonamiento lógico y abstracto

Genera exámenes de práctica tipo psicotécnico en PDF: preguntas de texto (escritas por quien arma el examen) y preguntas de figuras generadas automáticamente.

**Tipos de figuras:** matrices 3×3, series de figuras, rotación (flecha que gira y punto que se mueve), superposición de puntos, dominós, figura que no pertenece y analogías.

**Cada pregunta de figuras se verifica por código:** solo una opción cumple las reglas del tipo. Además, las letras correctas quedan repartidas por igual y las opciones están construidas para que no se pueda adivinar sin razonar.

```bash
pip install matplotlib
python3 examen.py --autotest 200          # prueba de estrés
python3 examen.py --plan plan.json --salida hoy
```

Salida: `examen.pdf` (preguntas), `respuestas.pdf` (clave con explicaciones) y `clave.json`.
