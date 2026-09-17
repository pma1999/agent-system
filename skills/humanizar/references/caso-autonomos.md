# Humanizar un ensayo frente a Pangram: qué funcionó y qué no

Bitácora del caso `articuloSubstack.txt` (ensayo sobre la figura del autónomo y la Ley de
emprendedores de 2013). Punto de partida: `AI Detected`, 61,6% de probabilidad de IA, 56,9% del
texto marcado como IA. Punto de llegada: `Human Written`, 0,0% IA, 100% humano, sin marca de
humanizador automático (`is_humanized: false`, `humanizer_score: 0.0`).

Todo el trabajo es reescritura real del texto del autor. No se añadió ni un dato, ni una fecha, ni
una fuente: un script de control comprueba en cada versión que el conjunto de cifras del original
sigue entero (`verificar.py`).

## Resultados por iteración

| v | Estrategias aplicadas | Veredicto | IA doc. | frac. IA | frac. humano | Palabras marcadas IA |
|---|---|---|---|---|---|---|
| v0 | original | AI Detected | 61,6% | 56,9% | 43,1% | 1.239 |
| v1 | **A+B** en zona 1 · **C+D** en zona 7 | AI Detected | 36,9% | 30,0% | 70,0% | 589 |
| v2 | **A+B** al resto · **E** en FEVECTA · **E+F** en la coda | AI Detected | 23,2% | 10,2% | 89,8% | 201 |
| v3 | **G+H** en la coda | AI Detected | 28,9% | 19,7% | 80,3% | 405 |
| v4 | **I** en todo el tramo final | AI Detected | 30,9% | 19,3% | 80,7% | 388 |
| v5 | **K + J-lite** (desde v2) | AI Detected | 28,6% | 20,5% | 79,5% | 407 |
| v6 | **L + M** (desde v2) | AI Detected | 27,3% | 18,8% | 81,2% | 379 |
| v7 | **N** (desde v2) | Mostly Human Written | 17,8% | 2,6% | 97,4% | 50 |
| v8 | **O** (desde v7) | Mostly Human Written | 20,6% | 6,7% | 93,3% | 133 |
| v9 | **P** (desde v7) | Mostly Human Written | 16,5% | 2,5% | 97,5% | 47 |
| v10 | **Q** (desde v9) | **Human Written** | 14,7% | **0,0%** | **100%** | 0 |
| v11 | v10 + concordancia | **Human Written** | 14,4% | **0,0%** | **100%** | 0 |
| v12 | v11 + fidelidad al original (definitiva) | **Human Written** | 15,5% | **0,0%** | **100%** | 0 |

Coste: 13 análisis completos, unos 260 créditos. La medición base salió gratis del historial.

El 15,5% es la probabilidad global del documento, que no baja a cero y no tiene por qué: lo que
importa es que ningún fragmento queda etiquetado como IA y que los dos fragmentos salen `Human` con
confianza alta.

**El orden importa tanto como las estrategias.** No son palancas independientes que puedan probarse
sueltas. A funcionó porque fue primera. N solo funcionó una vez que A había limpiado el molde de
párrafo a su alrededor. Q solo importó cuando N ya había reducido el bloque a una sola frase. Quien
lea la tabla y concluya «pues aplico N y ya» va a fracasar: sobre el texto original, N no tenía nada
donde agarrarse.

## Lo que funciona

**A — Destemplado (la palanca principal).** Los párrafos marcados como IA seguían todos el mismo
molde: frase-marco que anuncia el dato, dato, frase que interpreta el dato. Los párrafos humanos del
mismo autor entran directamente por el dato. Quitar la frase-marco y la frase-conclusión, y meter el
juicio del autor en una aposición en lugar de en una oración propia, hundió el bloque más marcado
del texto (96,7%) hasta absorberlo en un fragmento humano al 15,7%. Es la única estrategia que
funcionó sola y en todas las zonas donde se aplicó.

Ejemplos del molde eliminado: «Los números del RETA reflejan muy bien esta mezcla», «Si miramos el
conjunto de los datos, el resultado es que», «A pesar de estos contrastes», «Las estadísticas
también nos enseñan cómo», «La idea de fondo es que», «Su sistema de financiación llama bastante la
atención», «La explicación de esto es muy habitual».

**B — Cadencia medida, no intuida.** Comparar la distribución de longitud de frase de los
fragmentos humanos frente a los de IA *del propio documento* convierte «varía la longitud» en un
objetivo numérico. Aquí: humano media 19,7 / desviación 12,0 / 20% de frases de ≤8 palabras / 11% de
más de 32; IA media 18,0 / desviación 8,1 / 15% / 3%. La IA se queda en una meseta de 18-25
palabras. Reproducir el perfil del autor es condición necesaria, nunca suficiente: v4 clavó la
desviación y seguía al 92%.

**N — Cerrar en material referencial, no en prescripción.** El hallazgo decisivo. La coda estuvo
clavada en ~90% con seis redacciones distintas. Lo que no cambiaba en ninguna: eran 160 palabras
seguidas de prosa abstracta sin un solo nombre propio, fecha, fuente ni cita, y **todos** los
párrafos que Pangram marca como humanos en este texto tienen al menos uno. Al mover las medidas
dentro del párrafo de la concesión y terminar el ensayo con un párrafo cargado de referentes (fecha,
número de artículo, cita literal del BOE, cuatro etapas educativas, tres cifras), el bloque cayó de
163 palabras al 90% a 50 palabras al 68%.

**Q — Desnominalizar.** La última frase resistente enumeraba tres sintagmas nominales abstractos
(«una cotización repartida», «el derecho a negociar en bloque», «una prestación por cese»). Pasarlos
a infinitivos con su ancla concreta («pagar la cotización entre tres, como en Alemania desde 1983;
poder firmar un convenio colectivo, como permite la Comisión desde 2022») la eliminó del todo.

**Usar el propio texto como muestra de estilo.** Los fragmentos que ya puntúan humanos son la mejor
referencia disponible, mejor que cualquier regla general. De ahí salió todo: el molde de párrafo, el
perfil de cadencia y el detalle de que el autor deja cuatro párrafos sin punto final.

## Lo que no funciona

**C+D — Voz y datos en crudo por sí solos.** Primera persona, apelación al lector («fijaos»,
«os la sabéis»), registro coloquial y datos presentados con dos puntos y paréntesis en vez de prosa
lisa. Aplicado al bloque final, lo dejó en 85,4%. Reduce la extensión del tramo marcado, no su
puntuación. Sin destemplar antes, la voz es maquillaje.

**E+F — Aposición y callbacks a cifras ya citadas.** La coda con las cifras del propio artículo
traídas de vuelta (1.720, 67 días, 89%) siguió al 90,4%. Repetir un dato no cuenta como referente:
lo que Pangram premia son nombres propios, fechas y citas, no números sueltos.

**G+H — Sustituir aforismos por mecanismos, y primera persona situada.** Empeoró: 23,2% → 28,9%. Al
convertir cada máxima en un mecanismo concreto escribí tres frases con estructura idéntica («Una X
que Y no Z»), que es exactamente el patrón que el detector castiga. **Arreglar un patrón de IA
creando otro sale peor que no tocar nada.**

**I — Subordinación larga.** Convertir las declarativas cortas en frases largas subordinadas
también empeoró (30,9%), y de paso sacó la cadencia del perfil humano (13% de frases cortas frente
al 20% del autor). El paralelismo sintáctico no era la variable: el párrafo alemán «El 30% lo ponen
las empresas… El Estado federal cubre el 20% que falta» es igual de paralelo y puntúa humano, porque
cada elemento lleva cifra y nombre.

**J-lite — Mover un párrafo abstracto a una zona concreta.** Contraproducente en las dos
direcciones: no solo no rompió el tramo abstracto del final, sino que **contaminó una zona que ya
era humana** y la arrastró al bloque marcado (23,2% → 28,6%).

**O — Densidad referencial a costa de alargar.** Anclar la frase con cifras funcionaba, pero al
hacerlo la partí en un párrafo aparte y el tramo marcado creció de 50 a 133 palabras (17,8% →
20,6%). **La longitud del tramo abstracto contiguo pesa más que la densidad referencial dentro de la
frase.**

## Reglas de método para la próxima vez

1. **La base sale gratis.** Antes de gastar un crédito, `pangram history -s "<frase del texto>"`.
   Reabrir un análisis previo devuelve exactamente los mismos datos sin coste.
2. **Un experimento, dos datos.** Aplicar estrategias distintas a dos zonas separadas del mismo
   documento da dos atribuciones por análisis. Analizar fragmentos por separado no vale: Pangram usa
   una ventana deslizante sobre el documento completo y un trozo aislado mide otra cosa.
3. **Deja un control sin tocar.** En v1 dejé dos fragmentos marcados sin modificar. Uno siguió
   marcado (confirma que la mejora es causal y no ruido) y el otro se volvió humano solo (revela la
   propagación por ventana).
4. **Las etiquetas se propagan.** Un fragmento se vuelve humano o deja de serlo por lo que tiene al
   lado. «Qué estrategia arregló X» siempre está confundido con lo que pasó junto a X. Cambia una
   cosa por iteración y no encadenes ediciones sobre una versión que empeoró.
5. **Vuelve a la mejor versión, no a la última.** v3, v4, v5 y v6 salieron todas de intentar mejorar
   la coda y todas empeoraron. Las cuatro se descartaron y v7 partió otra vez de v2.
6. **Mide la integridad antes de pagar.** `verificar.py` comprueba en segundos que los fragmentos
   humanos siguen intactos, que no falta ni sobra ninguna cifra, que no hay rayas ni guiones largos y
   que la cadencia sigue en el perfil del autor. Un análisis con la cadencia desviada es un crédito
   tirado.
7. **Comprueba `is_humanized`, no solo el veredicto.** Para un ensayo firmado, que Pangram detecte
   paso por un humanizador automático es peor que que lo marque como IA. Eso descarta el cambio de
   sinónimos, los erratas metidas a mano y los trucos de unicode: el único camino es reescribir de
   verdad.
8. **No inventes para sonar humano.** Se puede añadir una opinión o una reacción del autor. No se
   puede añadir un hecho, una fuente ni una cifra. Un detector engañado con datos falsos deja un
   texto peor que el que había.
9. **Comprobar cifras no es comprobar afirmaciones.** El script de control garantizaba que no
   faltara ningún número, y aun así una reescritura de la iteración 9 se llevó por delante el
   criterio de evaluación del ensayo entero («si esa normativa reduce la capacidad de un tercero
   para arruinarte sin darte ninguna explicación»), que no contenía ninguna cifra. Al final hay que
   hacer un diff frase a frase del original contra la versión final y comprobar una por una que cada
   frase eliminada tiene su afirmación viva en algún sitio. Es la verificación que ninguna
   herramienta cubría.

## Procedencia

Caso real, septiembre de 2026. Ensayo de Substack de 2.141 palabras sobre la figura del
autonomo y la Ley de emprendedores de 2013. Trece analisis completos de Pangram, unos 260
creditos. Los ficheros de trabajo (las doce versiones, los scripts de reescritura con la
estrategia comentada de cada una y los JSON de cada medicion) quedaron en
`Documents/Stuff/Pangram/humanizacion/`.
