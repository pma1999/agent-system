# Caso 3: segundo capítulo de tesis (el que rompió el método)

Tercer caso medido y el más instructivo, porque **refutó cuatro instrucciones que la propia skill
daba** y porque terminó en un techo que no se movía por reescritura. 1.734 palabras, castellano
académico, economía política feminista, denso en citas con autor, año y página.

Los dos casos anteriores llegaron a `Human Written`. Este llegó a **80% humano, veredicto todavía
`AI Detected`**, y saber por qué vale más que el resultado.

## Resultados

| ver. | qué se hizo | alcance | veredicto | IA | asist. | humano | palabras marcadas |
|---|---|---|---|---|---|---|---|
| v0 | — | — | AI Detected | 39,8% | 19,3% | 40,9% | 1.030 |
| t1 | manual entero | **ancho** (15) | AI Detected | 36,2% | 7,1% | 56,7% | **755** |
| t2 | fuente como agente, disolver | **ancho** (6) | AI Detected | 25,6% | 0,0% | 74,4% | **451** |
| t3 | 5 retoques finos | fino | AI Detected | 27,5% | 2,9% | 69,6% | 532 |
| t4 | el mejor retoque de t3, aislado | fino (1) | AI Detected | 27,4% | 0,0% | 72,6% | 490 |
| t5 | conectores de discurso | fino (8) | AI Detected | 30,6% | 0,0% | 69,4% | 548 |
| t6 | manual entero otra vez | **ancho** (5) | AI Detected | 28,3% | 0,0% | 71,7% | 492 |
| t7 | t6 sin su edición tóxica | **ancho** (4) | AI Detected | 23,5% | 0,0% | 76,5% | **405** |
| **t8** | **recombinación t7 + t2** | recomb. | AI Detected | **20,0%** | **0,0%** | **80,0%** | **345** |
| t9 | recombinación de más | recomb. | AI Detected | 25,6% | 0,0% | 74,4% | 453 |

Once análisis (≈200 créditos). 1.734 → 1.698 palabras (−2,1%). Las 21 citas literales y los 15
localizadores de página, intactos uno por uno; ninguno añadido. Las 25 afirmaciones del original,
comprobadas una a una, siguen presentes.

## Lo que este caso refutó del manual

### 1. «Una variable por iteración» no vale aquí

Las tres pasadas anchas ganaron (−275, −304, −46). Las cuatro finas perdieron, **incluida la que
aislaba el único cambio con evidencia positiva inequívoca**: aplicado dentro de una pasada ancha
absorbió 118 palabras marcadas en un bloque humano de 221; aplicado solo sobre la mejor versión,
empeoró (451 → 490).

La razón es la ventana deslizante. Cada medición resegmenta el documento entero, así que el efecto
de una edición depende de la configuración completa y **no es aditivo**. Aislar variables supone
separabilidad, y no la hay. Cuando quede residuo, la respuesta no es afinar más fino: es volver a
hacer una pasada ancha y coherente.

### 2. Desnominalizar va en dirección contraria en prosa académica

Sustantivos abstractos (`-ción`, `-miento`, `-dad`, `-ismo`) por 100 palabras:

| | referencia humana 1 | referencia humana 2 | mis zonas humanas | mis zonas marcadas |
|---|---|---|---|---|
| nominalizaciones | 7,5 | 8,2 | 4,4 | 5,5 |

Las dos referencias son capítulos académicos verificados al 0,002% de IA. **Nominalizan más que
mi texto, no menos.** La estrategia venía de un ensayo periodístico y no se transfiere.

### 3. Un marco no es lo mismo que un conector, y la lista de la skill los mezclaba

«En este sentido», «Así», «Además», «Es importante destacar que» aparecen constantemente en las
dos referencias humanas. En una, el **71% de las frases abre con conector**; en la otra, el 53%.

- Un **marco** es una frase entera que anuncia o interpreta en vez de entregar: «Esta distinción es
  clave, ya que…», «Los datos reflejan…», «Su argumento es que…». Esa sobra.
- Un **conector** es una palabra o dos que ordenan el discurso y dejan la frase entregando lo mismo.
  Es prosa académica normal.

Al aplicar el manual, t1 borró los dos a la vez y dejó las zonas marcadas en **0% de frases con
conector**. Añadirlos después (t5) no lo arregló: 451 → 548.

### 4. La propagación al vecino está establecida, y es reversible

Un bloque de 125 palabras (Carrasco et al.), **byte a byte idéntico en las diez versiones y nunca
tocado**:

- v0, t2 → `Human` High, 26,9% y 20,3%, entero
- t1 → partido en Human 54 / **AI-Generated 54,5% 35 palabras** / Human 36, tras romperle los dos vecinos
- t2 → entero y humano otra vez, tras repararlos

De ahí la regla operativa: **no persigas un fragmento marcado que no has escrito tú. Arregla sus
vecinos y vuelve a medir.**

## El hallazgo central: el residuo no era prosa de IA

Prueba de 3 créditos. Las tres redacciones del mismo pasaje de 58 palabras, medidas **solas**:

| redacción | sola | dentro del documento |
|---|---|---|
| v0 | 69,7% `AI Generated` | 73,8% |
| t2 | **4,4% `Human Written`** | **78,1%** |
| t7 | **0,5% `Human Written`** | 68,9% |

Las mismas palabras: 4,4% solas y 78,1% dentro. **74 puntos de diferencia sin cambiar una letra.**
Y no es un artefacto de la longitud: la versión v0, del mismo tamaño y tema, da 69,7% sola.

Dos consecuencias:

1. **Medir un fragmento aislado no sirve para elegir entre redacciones**: ordena al revés.
2. **Los bloques que resistían ya estaban bien escritos.** Lo que los marcaba era la densidad local
   de entrega de cita. En ventanas de 250 palabras, la cita literal ocupaba el 5-10% en la primera
   mitad (760 palabras seguidas, humanas), el 21-31% en el tramo Carrasco, y **2,7% en el tramo que
   resistía**. La ventana del detector es más ancha que la edición: reescribir 70 de 450 palabras no
   cambia lo que la ventana ve.

Por eso el techo no se rompía. El déficit era de material de entrega en 450 palabras, y ese material
o lo aporta la fuente o no existe.

## Bloques tóxicos

El párrafo de Folbre se reescribió dos veces con tácticas distintas. Las dos veces arrastró el tramo
de su izquierda y creó un bloque marcado de **246 y de 286 palabras**, tragándose frases intactas que
ya puntuaban humanas. Dejarlo como estaba costaba 78.

**Si reescribir un bloque empeora su entorno dos veces, deja de tocarlo.** No es que no encuentres la
redacción buena: ese tramo es el que sostiene la frontera.

## La recombinación, que es el movimiento de cierre

Al final había varias configuraciones medidas y ninguna dominaba en todas las regiones. t8 no
contiene ni una redacción nueva: es t7 con una región devuelta a la redacción de t2, elegida porque
en t2 esa región dejaba humano un párrafo de 49 palabras que en t7 se perdía. Bajó de 405 a **345**.

t9 sacó otra pieza del paquete y se derrumbó a 453: la cascada de absorciones río abajo desapareció
entera. **Una buena configuración es un paquete, no una suma de aciertos.**

## Correlación no es palanca

Dos veces en este caso, y conviene recordarlo antes de gastar una medición:

- **Conectores.** La diferencia más marcada que encontré (0% frente a 71%), causada por mí. Añadirlos
  sin tocar nada más: peor.
- **El autor como sujeto gramatical.** Parecía explicar seis aciertos seguidos. Medido: 0,8 por 100
  palabras en las zonas humanas y 0,9 en las marcadas. No discrimina. Y la referencia humana está en
  0,5, por debajo de las dos. Los seis «aciertos» cambiaban también el marco, la apertura y la
  longitud: la variable nunca estuvo aislada.

Antes de construir una pasada sobre un rasgo, comprueba que separa las dos clases **dentro del
documento**. Un rasgo del texto de referencia no sirve: dice en qué género estás, no qué mover.

## Lo que sí funcionó

- **Cerrar el capítulo nombrando a sus autores**: 68,1% → **18,0%**, el segundo bloque más limpio.
  Cada constructo devuelto a la atribución que el propio capítulo ya establecía. Ni una cita nueva.
- **Disolver la síntesis dentro de la frase que lleva la referencia**, siempre que sea dentro de la
  zona marcada. Hacia fuera, colgándola de una frase que ya puntuaba humana, contaminó el bloque sano
  (+18 puntos).
- **El nombre del autor en la primera frase del párrafo**, cuando sustituye a un marco. Pero solo si
  la racha marcada que tiene detrás es corta: una frase anclada breve pegada a una racha larga se la
  traga la racha.

## Dos fallos de herramienta que este caso destapó

1. `parrafos()` trataba cada línea como párrafo cuando no había líneas en blanco. Un texto con salto
   duro (copiado de un PDF) daba **141 «párrafos» de doce palabras** y un diagnóstico sin sentido.
   Ahora distingue por longitud media de línea y agrupa en bloques de ~120 palabras si hace falta.
2. `verifica.py` buscaba las frases protegidas literalmente en el texto crudo, así que **cada fila de
   una tabla salía como MODIFICADA** aunque fuera byte a byte idéntica. Reportaba 26/33 cuando eran
   33/33. Un falso positivo recurrente es tan dañino como un falso negativo: enseña a ignorar el
   aviso. Ahora la búsqueda tolera cualquier espaciado.

## Procedencia

Septiembre de 2026. Once análisis de Pangram más tres pruebas de fragmento aislado, ≈200 créditos.
Ficheros de trabajo, con el guion de reescritura de cada versión y su JSON, en
`Documents/Stuff/Pangram/tesis2/`. La bitácora de decisiones, con la atribución de cada cambio, en
`tesis2/PLAN.md`.
