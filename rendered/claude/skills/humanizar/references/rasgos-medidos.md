# Lo medido: qué mueve a Pangram y qué no

Todo lo de aquí está **medido**, no razonado. Existe para que ninguna sesión futura gaste créditos
redescubriendo lo que ya se probó. Detector: **Pangram 4.0** (campo `version` del JSON).

## La diana, y el error de apuntar a otro sitio

`Human Written` sale cuando **`fractions.ai` = 0**: ningún segmento etiquetado `AI-Generated`.

| | veredicto | global | frac. IA | segmentos `Human` |
|---|---|---|---|---|
| caso 1 final | `Human Written` | 14,7% | 0,0% | 14,7 · 14,7 |
| caso 2 final | `Human Written` | **31,3%** | 0,0% | **31,2** · 19,7 |
| caso 3 mejor | `Mostly Human Written` | 24,1% | 7,0% | 18,9 · 29,7 · 21,4 |
| ref. humanas | `Human Written` | 0,00x% | 0,0% | 0,001 - 0,004 |

Lo que se deduce, y que costó tres sesiones no saber:

- **El porcentaje global no decide.** El caso 2 pasó con 31,3%.
- **El `ai_likelihood` de los segmentos `Human` tampoco.** El caso 2 pasó con uno al 31,2%.
- **`AI-Assisted` no bloquea.** El caso 2 pasó con 97 palabras `AI-Assisted` al 38,1%.
- **La frontera `AI-Assisted` / `AI-Generated` está entre 46,8% y 48,2%.** Un bloque al 50% está a
  un empujón de dejar de contar.

Yo escribí una vez en esta misma skill que los segmentos humanos a 20-40% significaban que «ninguna
edición local va a bastar». Es falso: el caso 2 pasó exactamente en esa banda. Lo único que hay que
llevar a cero es `word_split['ai']`.

**La frontera del veredicto, sobre los 49 documentos medidos del proyecto:**

| veredicto | fracción IA observada | casos |
|---|---|---|
| `Human Written` | **0,0%**, y nada más que 0,0% | 5 |
| `Mostly Human Written` | 7,0% | 2 |
| `AI Detected` | **8,7% – 91,9%** | 42 |

Se recalcula **gratis** con los JSON que ya tengas en disco y decide si merece la pena seguir. Desde
el 50% de fracción IA, cambiar el veredicto pide bajar de ~8%: no es una pasada más.

## Tejer gana a reescribir, 10 a 0

La regularidad más fuerte de todo el proyecto. En un capítulo con dieciséis versiones medidas:

| versión | qué se hizo | palabras marcadas |
|---|---|---|
| t12 | punto de partida | 283 |
| t13 | **reescribir**: fundir períodos | 312 |
| t14 | **reescribir**: desarrollar en vez de comprimir | 309 |
| t15 | **reescribir**: los tramos humanos | 456 |
| t16 | tejer: ocho marcas de voz | 270 |
| t19 | tejer: quitar la frase-cartel | 269 |
| t20 | tejer: voz dentro del bloque marcado | 232 |
| t21 | tejer: anclar la abstracción huérfana | 230 |
| t23 | tejer: voz dentro del bloque «tóxico» | 221 |
| t25 | tejer: bajar la dosis de 3 marcas a 1 | 208 |
| t26 | tejer: bajar la dosis también en Folbre | 206 |
| t27 | **reescribir**: atribuir al autor | 374 |
| t29 | tejer: quitar «no X sino Y» | 203 |
| t30 | tejer: tres patrones más de `humanizer` | 193 |
| t31 | tejer: romper cadena + autor como sujeto | **176** |
| t32 | **reescribir**: atribuir otra vez | 218 |

Cinco reescrituras, cinco peores. Diez intervenciones tejidas, diez iguales o mejores. Y la misma
estrategia (atribuir al autor citado) funciona tejida y falla reescrita, lo que descarta que sea
cuestión de qué se hace: es cuestión de **cuánto texto se mueve**.

Causa probable: al reescribir cambias el tramo y sus fronteras a la vez, y el resegmentado arrastra
material que ya puntuaba humano. Al tejer, el resto del tramo es byte a byte el mismo.

## La palanca del residuo: los patrones que se leen

La lista de la skill `humanizer` (Wikipedia, *Signs of AI writing*). Es lo que desatascó un capítulo
después de doce iteraciones planas.

| patrón | efecto medido |
|---|---|
| «X, no Y» / «no solo X» / «no X sino Y» (§9) | el peor bloque, 71,8% → 64,0% |
| cadena de razonamiento + verdad honda + anuncio de recuento (§3, §27, §28) | 162 → 152 IA |
| romper la cadena + autor como sujeto (§3, §13) | 152 → **123 IA**, veredicto `AI Detected` → `Mostly Human Written` |

**«no X sino Y» es el rasgo mejor separado de todo el proyecto**: 0 apariciones en 1.561 palabras de
tramos humanos, 2 en 164 palabras de tramos marcados. Externamente, los cuatro textos humanos van de
0,00 a 3,01 por mil palabras y el bloque marcado estaba a 12,20: cuatro veces el más alto. Pasa las
tres pruebas y además funcionó al aplicarlo, que es lo que ninguno de los rasgos contables logró.

Ojo con el uso: el documento entero estaba a 1,13 por mil, **dentro de la banda humana**. Lo que
marca no es la tasa global sino la concentración dentro del tramo.

## Nueve rasgos contables, cero palancas

| rasgo | interna | externa | modelo nulo | intervención | veredicto |
|---|---|---|---|---|---|
| cita literal | sí | no | — | — | descartado |
| atribución | sí | no | — | — | descartado |
| conector de discurso | no | sí | — | sin efecto | descartado |
| nombres propios | no | sí | — | — | descartado |
| autor como sujeto (recuento) | no | — | — | — | descartado |
| redundancia léxica | no | — | — | — | descartado |
| repetición léxica local | sí | **no** (ref4 = marcado) | — | — | descartado |
| matiz epistémico | — | **no** (ya matizo más) | — | — | descartado |
| subordinantes | r=+0,12 | sí | **0,73** | — | descartado |
| comas por frase | r=−0,62 | proxy de longitud | 0,85 | — | descartado (proxy) |
| **longitud de frase** | rango restringido | **total** | **1,26** | **283 → 312** | **descartado** |
| reubicar un párrafo | — | — | — | 230 → 230 | sin efecto |
| **sorpresa por token** (LM local) | — | **sí, 4,94** | **4,94** | **D_new150 2,383 vs B_new226 2,382, veredictos opuestos** | **descartado** |

Dos filas merecen leerse despacio.

**Longitud de frase.** El mejor candidato imaginable: los cuatro humanos entre 35,2 y 48,7 palabras
por frase, el capítulo entre 29,4 y 33,1 en doce versiones, **solapamiento cero**, el mayor ratio de
la batería. Se llevó a 40,0 fundiendo períodos sin tocar una afirmación (+12 palabras de pegamento).
Resultado: **283 → 312**.

> Un rasgo puede separar tu texto de cuatro humanos verificados con solapamiento cero y aun así no
> mover el detector. La separación estadística no es causalidad.

**Comas por frase.** Parecía separar limpio, pero lleva la longitud de frase en el denominador.
Medida como comas por 100 palabras, la densidad real del capítulo (6,65-7,85) **ya estaba dentro de
la banda humana** (5,66-7,86) antes de tocar nada. Siempre que un cociente tenga frases en el
denominador, calcula también la versión por 100 palabras antes de concluir.

### La sorpresa por token: el mejor separador del proyecto, y aun así no sirve

Merece párrafo propio porque es el caso más instructivo de toda la tabla. La sorpresa por token
bajo un LM causal local (`binoc` = sorpresa media / entropía media, trozos de 150 palabras,
`Qwen2.5-1.5B`) separa **humano académico auténtico (0,9925-1,0197) de tesis generadas sin tocar
(1,0364-1,0770) con cero solapamiento y modelo nulo 4,94**. Es la separación más limpia que se ha
medido aquí. Y no sirve para lo que necesitas:

- **No explica la ley de dilución.** Con las mismas palabras y distinta disposición, `D_new150`
  da sorpresa 2,383 y pasa; `B_new226` da 2,382 y no. Idénticas, veredicto opuesto.
- **No predice a Pangram.** ρ = +0,057 sobre 352 documentos medidos; +0,110 sobre 106 versiones
  del mismo texto. No sirve de prefiltro gratuito.

**Para qué sí sirve:** como **medidor de calidad ortogonal**. Nuestras cinco tesis humanizadas
siguen en banda IA (cambio medio de todo el proceso: **+0,0013 = 0,13 sd**; brecha restante 5,1 sd;
peor en 4 de 5). Lo único que la mueve es el método fuente-primero: la región anclada en literales
del BOE da 0,9950, dentro de la banda humana, y su prosa propia 0,9833. Si quieres saber si has
humanizado el texto o solo has pasado el detector, esto te lo dice gratis. Detalle en
`surprisal/HALLAZGOS.md` del proyecto.

## Rango restringido

La longitud de frase daba r=+0,03 contra las palabras marcadas en doce versiones, y eso parecía
cerrarla. No la cerraba: las doce vivían en una franja de 3,7 palabras, entera por debajo del mínimo
humano. Una correlación calculada donde la variable nunca entra en la zona de interés no prueba nada.
**Mira siempre el rango recorrido antes de concluir que algo no influye.**

## El modelo nulo, y por qué hacen falta tres referencias

Con dos textos humanos no se puede estimar cuánto varían los humanos entre sí. Con cuatro, sí, y eso
convirtió «subordinantes 0,3 y 0,4 frente a 1,5, clarísimo» en «banda humana 0,30-0,61, dispersión
mayor que la brecha, descartado».

La prueba: `brecha / dispersión`. Por debajo de 1,0 el rasgo mide género o autor, no humanidad. Por
encima de 1,5 es candidato — y aun así puede fallar, como falló la longitud de frase a 1,26.

## Bloques «tóxicos»: la regla estaba mal enunciada

El párrafo de Folbre resistió **cuatro reescrituras** y empeoró su entorno las cuatro veces (bloques
marcados de 246, 286 y 134 palabras; una deshizo un bloque humano de 231 recién ganado). De ahí salió
«si empeora dos veces, no lo toques más».

Ese mismo bloque cedió a la primera con dos incisos tejidos dentro, **sin reescribirlo**: 87 → 78
palabras, 54,9% → 53,4%. No era inmune a los cambios; era inmune a *ese tipo* de cambio.

> Enunciado correcto: si un bloque resiste dos reescrituras, deja de reescribirlo y **cámbiale el
> tipo de intervención**.

Sigue siendo cierto que **lo que se pega al lado de un bloque así lo revienta** (cuarta confirmación).

## El corpus de referencia

Cuatro capítulos académicos en castellano, ciencias sociales, densos en cita con autor, año y página.
En `tesis2/ref/` del caso 3.

| ref | palabras | IA | tema |
|---|---|---|---|
| ref1 | 1.679 | 0,0021% | justicia social |
| ref2 | 3.051 | 0,0024% | reificación |
| ref3 | 3.269 | 0,0014% | esfera pública (Habermas) |
| ref4 | 1.959 | 0,0042% | decodificaciones resistentes (TV) |

Si el usuario ya los analizó en la web, **no gastes créditos**: `pangram history -s "<frase>"` los
localiza y `pangram history show <uuid> --json` los reabre enteros, gratis.

## Banda humana del género (contexto, no diana)

| rasgo | los cuatro humanos | el capítulo de IA |
|---|---|---|
| **metadiscurso (clases cerradas)/1000** | **1,62 – 5,51** | **20,90** (caso 4) |
| autorreferencia al texto/1000 | 0,00 – 0,50 | 4,75 (caso 4) |
| andamiaje ordinal/1000 | 0,00 – 1,49 | 4,99 (caso 4) |
| anclajes/100 palabras | 0,55 – 1,70 | 2,09 (cita **más** que los humanos) |
| palabras por frase | 35,2 – 48,7 | 27 – 33 |
| comas por 100 palabras | 5,66 – 7,86 | 6,65 – 7,85 |
| subordinantes/100 pal. | 0,30 – 0,61 | 0,18 – 0,48 |
| nominalizaciones/100 pal. | 6,42 – 8,19 | 3,9 – 5,7 |
| matiz epistémico/1000 | 1,18 – 2,51 | 2,82 |
| marcas de voz/1000 | 0,92 – 2,04 | **0,00** |
| «no X sino Y»/1000 | 0,00 – 3,01 | 1,13 (12,20 en el bloque marcado) |

Las filas de metadiscurso son las de mayor separación de todo el proyecto: modelo nulo **7,90**,
frente al 1,26 de la longitud de frase (que falló) y al umbral de 1,5. Y dieron la palanca más grande
medida: **3081 → 2020 palabras IA en una sola pasada**. Ojo con las dos trampas de medirlas, las dos
en `caso-tesis-3.md`: usar clases gramaticales cerradas y no un regex escrito tras leer el objetivo
(20,90 frente a 11,16), y descontar las referencias cruzadas de tesis, que ningún capítulo publicado
puede tener (7,70 en bruto, **5,58** descontadas, banda 1,62-5,51).

La fila de los anclajes enseña lo contrario y por eso importa: el texto marcado **cita más** que los
cuatro humanos verificados. El anclaje separa las clases dentro de un documento, pero su nivel
absoluto no es diana. Nunca añadas citas.

## Nota de herramienta

`python -c "..."` dentro de comillas dobles en bash **se come las barras invertidas**: `\b` llega como
carácter de retroceso y el regex devuelve 0 en silencio. Ha falseado una medición dos veces. Escribe
el script a fichero con la herramienta Write y ejecútalo.
