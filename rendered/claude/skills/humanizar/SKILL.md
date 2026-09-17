---
name: humanizar
description: Reescribe un texto para que deje de dar positivo en un detector de IA sin cambiar lo que dice, con un procedimiento medido contra Pangram que diagnostica cada tramo marcado y le aplica la operación que le corresponde. Úsala SIEMPRE que se pida humanizar, reescribir o arreglar un texto que da positivo en IA; que un ensayo, TFG, tesis, artículo, informe, post o memoria deje de parecer escrito por IA; que baje el porcentaje de IA de un texto; o que un texto pase como humano en Pangram, GPTZero, Turnitin o similar. También cuando alguien diga que su propio texto le sale marcado como IA, que "le sale positivo", o que quiere que un detector le dé humano. No la uses para detectar autoría sin reescribir (eso es la skill `pangram`), ni para pulir estilo cuando no hay un detector de por medio.
---

# Humanizar un texto frente a Pangram

El texto es del usuario y sigue siéndolo. Hay **tres requisitos simultáneos** y ninguno se sacrifica
por otro:

1. **Calidad igual o mayor** que la del original. Nada se vuelve confuso, impreciso ni peor
   argumentado.
2. **Tono del género de origen.** Si es académico, académico; si es ensayo, ensayo; si es informe,
   informe. No el tono del autor: el que el tipo de texto exige.
3. **Humano completo**, verificado por medición sobre el archivo final exacto.

Una versión que baja el porcentaje y estropea el texto es un fracaso. Una versión elegante que sigue
marcada, también.

Esta skill es autocontenida: incluye el catálogo de patrones, las constantes medidas, las
operaciones, el script de sonda y la lista de lo ya falsado. No necesitas consultar nada más.

---

## 1. La diana

`Human Written` sale cuando **`fractions.ai` llega a 0**, es decir cuando no queda ningún segmento
`AI-Generated`. Fronteras observadas sobre 49 documentos medidos:

| veredicto | fracción IA observada |
|---|---|
| `Human Written` | **0,0 %** y solo 0,0 % |
| `Mostly Human Written` | 2 % - 8 % |
| `AI Detected` | de 8,7 % a 97,7 % |

Tres consecuencias que cambian cómo se trabaja:

- **Un `ai_likelihood` global alto no impide el veredicto.** Hay pases con 31,3 % global. No uses el
  global para medir progreso; úsalo solo para elegir entre dos candidatas que ya pasan.
- **Los segmentos `Human` pueden estar al 31 % y no pasa nada.** No los toques.
- **`AI-Assisted` no bloquea el veredicto.** La frontera entre `AI-Generated` y `AI-Assisted` está
  medida entre el 46,8 % y el 48,2 %. **Degradar un bloque de `AI-Generated` a `AI-Assisted` vale
  casi tanto como borrarlo**, y un bloque al 50 % está a un empujón. Es a menudo el camino más corto.

Lo único que hay que llevar a cero es el recuento de palabras `AI-Generated` (`word_split['ai']`).
Métrica secundaria: total de palabras marcadas. El porcentaje global, para nada.

**Criterio de terminación completo** (las cinco):

1. veredicto `Human Written`;
2. `fractions.ai == 0` y ningún segmento con `is_humanized: true`;
3. margen: ningún segmento pegado al umbral (global ≤ ~15 % es cómodo; un `Human` por encima del
   35 % es frágil y volverá a caer);
4. auditoría de integridad y calidad en verde (§9);
5. **puerta de estabilidad**: 2-3 análisis consecutivos del archivo final exacto, sin islas (§10).

**Di la posición de salida al principio.** Un texto con dos bloques marcados y otro con el 73 %
marcado no son el mismo problema. Un caso que partía del 39,8 % llegó al 7,0 % en unas 30
mediciones; otro que partía del 73,5 % sobre un texto 2,4 veces más largo se quedó en el 50 % en
siete. Decirlo al principio evita que se confunda «no llegó» con «se hizo mal».

---

## 2. Lo primero: no busques una regla de estilo. No existe

Esto está medido en las dos direcciones y ahorra la mayor parte del tiempo que se pierde con esta
tarea.

**Asimetría fundamental.** Sobre un bloque limpio (1.157 palabras, 0 % AI, global 8,6 %), quitarle
rasgos lo rompe. Sobre un tramo marcado, añadirle esos mismos rasgos no lo arregla.

| Manipulación | Resultado |
|---|---|
| quitar las cifras exactas de un texto limpio | 0 % → **20 % AI** |
| quitar las comas de especificación de un texto limpio | 0 % → **100 % AI** (global 91,9 %) |
| **añadir** comas de especificación (9,33/100 palabras) a un tramo marcado | sigue en **87 % AI** |
| **añadir** cifras exactas e idiosincrásicas (4,92/100 palabras) a un tramo marcado | sigue en **100 % AI** |
| **añadir** registro verboso, marcos y matizadores a un tramo marcado | empeora: 76,6 % → **86,1 %** |
| reformular dos veces el mismo tramo de 47 palabras | empeora: 80,4 % → **88,9 %** |
| **subordinar** ese mismo contenido en lugar de reformularlo | **0 % AI** |

Los rasgos de superficie son **correlatos, no palancas**. Sobre 680 tramos escritos por modelo
(366 Human, 314 AI), controlando longitud, la densidad de cifras da AUC 0,62-0,82, las comas
sintácticas 0,69-0,76 y la diversidad léxica 0,12-0,28 (invertida). Son señales reales y no sirven
para construir. Pangram se entrena con espejos sintéticos emparejados por tema, tono y longitud, con
negativos difíciles y con salidas de humanizadores: imitar un perfil está dentro de su distribución
de entrenamiento.

**Regla de tres pruebas para cualquier rasgo que se te ocurra contar.** Es candidato solo si (a)
separa las clases *dentro del mismo documento*, (b) tu texto se aparta de un texto humano verificado
del mismo género y (c) la brecha supera **cuánto varían los humanos entre sí**, para lo cual hacen
falta tres o cuatro referencias, no una. Aun pasando las tres sigue siendo hipótesis: la longitud de
frase pasó las tres, con solapamiento cero entre cuatro autores, y empeoró 283 → 312.

**Cuenta poco, lee mucho.** Trece rasgos contables medidos contra textos humanos: ninguno resultó
palanca. Las palancas reales salieron de leer los bloques marcados y preguntarse *qué hace esta
prosa que la humana no hace*, no *cuántas comas tiene*.

---

## 3. Cómo funciona Pangram 4, y qué se sigue

Modelo causal de mezcla dispersa de expertos con ventana de inferencia de **512 tokens** (≈ 380
palabras en español). Cuatro cabezas sobre la representación compartida: grado de intervención de
IA, procedencia token a token en tres estados (Human / AI-Assisted / AI-Generated), autoría mixta y
una cabeza específica de humanización. En documentos largos las ventanas se solapan y se promedian
las observaciones de cada token; después un CRF y la decodificación de Viterbi imponen coherencia de
etiqueta; la interfaz traslada la etiqueta a oraciones por mayoría de tokens.

Cuatro consecuencias operativas. Gobiernan todo el procedimiento:

1. **No existe ningún rasgo global del documento.** El modelo nunca ve el texto entero de una vez.
   La ventana es más ancha que tu edición: puntúa tramos de doscientas o trescientas palabras, no
   frases. Por eso una frase impecable puede salir marcada por lo que la rodea, y por eso reescribir
   70 palabras de un tramo de 450 no cambia lo que la ventana ve. **Piensa en tramos.**
2. **El CRF arrastra los tramos dudosos hacia la etiqueta mayoritaria de su entorno.** De ahí que
   funcione el anclaje, y con radio corto. También de ahí que la **propagación al vecino** sea real y
   **reversible**: un bloque de 125 palabras idéntico byte a byte pasó a marcado cuando se rompieron
   sus dos vecinos y volvió a humano al repararlos.
3. **Solo los tokens escritos por un humano real son humanos por construcción.** Ninguna prosa que
   escribas puede serlo: la tarea del detector es puntuar verosimilitud de tokens. De aquí sale la
   operación maestra del §4.
4. **Hay una cabeza dedicada a detectar humanizadores.** Por eso reformular empeora de forma
   medible, y por eso `is_humanized` es peor que el positivo original para un texto firmado.
   **Compruébalo en cada medición.**

**Los cambios no son aditivos.** Cada medición resegmenta el documento entero, así que el efecto de
una edición depende de la configuración completa. El único cambio con evidencia positiva inequívoca,
aplicado solo, empeoró (451 → 490); dentro de una pasada coherente absorbió 118 palabras marcadas.

---

## 4. La operación maestra: entregar en vez de sintetizar

**Es la de mayor rendimiento medido de toda la skill, y explica por qué.**

En prosa con fuentes, los tramos que puntúan `Human` son las **frases de entrega de fuente**: cita
literal más referencia, con andamiaje mínimo. Los tramos marcados son la **prosa de síntesis del
autor** entre una fuente y la siguiente. La razón es el §3.3: la cita es texto humano real; tu
síntesis no puede serlo.

Resultados medidos de aplicar esto:

| Intervención | Resultado |
|---|---|
| una sola pasada de «entregar en vez de sintetizar» sobre un capítulo | fracción IA **68 % → 15,7 %** |
| la misma pasada, efecto estructural | mayor tramo `Human` de 67 → **339** palabras; tramos Human >100 palabras de 0 → 5 |
| sustituir la paráfrasis de dos papers por sus palabras literales | región de **100 % AI → 19 % AI** |
| en esa región, el bloque de 408 palabras con las citas **y tu prosa alrededor** | pasó a `Human`, 21,4 % |
| dos regiones legales reconstruidas citando norma y sentencia | documento de 14 % → **8 % AI**, veredicto a `Mostly Human Written` |

**Cómo se hace:**

- La frase que anuncia una tesis antes de exponerla se **sustituye por la exposición directa**.
- **La fuente entra primero** y el juicio del autor viaja detrás, como subordinada de la misma frase.
- **La cita cierra la frase mejor que a mitad.**
- Autores, años, páginas, comillas y terminología técnica son **intocables**: son el anclaje.
- Longitud útil de la cita: **20-75 palabras**. Está medido que **dos citas de 21 y 23 palabras, separadas, rescatan más prosa propia (116 palabras) que una sola de 51 puesta en el centro (62)**, y con menos masa de cita. El suelo de segmentación de ~30 palabras describe lo que el CRF *emite* como segmento, no lo que puede *influir* en la etiqueta. Está medido que **una cita de 14 palabras no ancla
  nada**: dejó marcada su serie de 211 palabras.
- **Reparte**: una cita cada 100-150 palabras de prosa propia en la región difícil, no todas juntas.

**Si los tramos `Human` de tu base son todos frases de entrega de fuente, esta es la pasada que
toca**, y es la más rentable del género.

**Fuentes especialmente productivas** porque son texto humano verificable y pertinente: preámbulos y
articulado de normas, fundamentos de sentencias, resúmenes y conclusiones de papers, notas
metodológicas de organismos estadísticos, informes institucionales. Si el texto ya las cita, están
disponibles: ve al original y tráete sus palabras.

### La distinción que evita el error

**Sustituir tu paráfrasis por las palabras de la fuente: funciona.**
**Añadir citas encima de la paráfrasis para diluirla: no funciona.**

Está medido: en un caso, el capítulo ya tenía el 11,0 % de palabras entrecomilladas frente al 0,8 %
y 4,5 % de textos humanos verificados del género. Ya citaba el doble que textos que puntúan 0,002 %,
y seguir añadiendo no movió nada. No es «más cita»: es **cambiar quién habla en el tramo marcado**.

**Cuota global sana: 15-20 % del documento.** Referencias medidas: tesis humanas verificadas 17,8 %
y 21,5 %; una tesis nuestra ya aprobada 18,3 %. Localmente, una región difícil puede necesitar
30-40 % para sostenerse. Vigila la cuota **global**, no la local; si te acercas al 25 % global, deja
de añadir y resuelve por disposición (§6). **Nunca conviertas el texto en un collage de citas: eso
incumple el requisito 1.**

**Y jamás inventes una cita, una cifra, una página ni una fuente.** Verifica cada cita literal
contra el original, con su localizador. Si no puedes verificarla, no la uses. Añadir un localizador
de página a una paráfrasis tuya es inventarse una cita.

---

## 5. Tejer, no reescribir

La regla más rentable después de la anterior, y la que más cuesta obedecer, porque el instinto ante
un párrafo marcado es reescribirlo.

**Tejer** es intervenir dentro de las frases que ya existen: meter un inciso, romper una cadena
causal en dos frases, cambiar una construcción por otra equivalente, quitar un marco. La frase sigue
siendo la del autor. **Reescribir** es volver a redactar el tramo desde la idea.

En un capítulo con dieciséis versiones medidas la separación es total:

| | intentos | resultado (palabras `AI-Generated`) |
|---|---|---|
| **reescribir** un bloque marcado | 5 | **5 peores**: 283 → 312 · 309 · 456 · 374 · 218 |
| **tejer** dentro de él | 10 | **10 iguales o mejores**: 283 → … → **176** |

Incluye casos donde la reescritura era buena prosa y estaba bien motivada. La explicación es la
ventana: al reescribir cambias a la vez el tramo y sus fronteras, y el resegmentado se lleva por
delante material que ya puntuaba humano. Al tejer, el resto del tramo sigue siendo exactamente el
mismo texto.

**Corolario:** cuando un bloque se resista, no busques una redacción mejor. Busca **qué patrón
concreto** tiene dentro y quítalo sin tocar lo demás.

**Si un bloque resiste dos reescrituras, cámbiale el tipo de intervención.** Un párrafo aguantó
cuatro redacciones distintas y las cuatro arrastraron a su vecino; cedió a la primera tejiéndole dos
incisos dentro, sin reescribirlo (87 → 78 palabras). No era inmune a los cambios: era inmune a *ese*
cambio. Y **lo que pegues al lado de un bloque así lo revienta**: cambia dentro, no alrededor.

---

## 6. Constantes medidas

Todas obtenidas con texto idéntico palabra por palabra, variando solo lo indicado.

### Ley de dilución

Serie contigua de prosa propia **aún no verificada**, con ≥ 250 palabras de contexto ya `Human` a
cada lado y longitud total constante (~1.130 palabras):

| Serie contigua | Veredicto | AI |
|---:|---|---:|
| 113 palabras | `Human Written` | 0 % |
| 124 palabras | `Human Written` | 0 % |
| 153 palabras | `Human Written` | 0 % |
| 226 palabras | `Mostly Human` | 8 % |
| 406 palabras | `AI Detected` | 34 % |

El mismo párrafo puntuaba 66,4 % dentro del documento grande. **No se reescribió nada: cambió la
disposición.** La fracción del documento no lo explica: una serie de 381 palabras sigue siendo AI con
una fracción documental del 9 %.

**Regla:** cap de **150 palabras** de prosa propia no verificada en serie contigua; objetivo ≤ 120.

### Ley de anclaje: el ancla no protege, **parte**

Medido sobre 2.496 segmentos con posición (`geometria/HALLAZGOS.md` del proyecto). La formulación
anterior —"queda `Human` si está a menos de ~60-100 palabras de un ancla"— **era incorrecta**: no
hay radio de protección. Lo que hay es esto:

> Una racha contigua de prosa propia se etiqueta AI cuando es lo bastante larga para que al CRF le
> compense recortarla como segmento propio. Por debajo, la absorbe en la etiqueta del vecino: **eso
> te salva si el vecino es `Human` y te mata si el vecino es AI.**

Tres números medidos, no estimados:

| | valor |
|---|---|
| ventana del modelo | **329 palabras** (512 tokens / 1,557 tok por palabra) |
| **suelo de segmentación** | **~30 palabras** — por debajo, el CRF no emite segmento |
| umbral de recorte de racha | **130-230 palabras** |

**Un ancla no irradia protección: abre un corchete.** Dos anclas separadas abren y cierran, y
convierte **todo lo que queda dentro** — ver el corolario medido justo debajo. El suelo de ~30
palabras acota lo que el CRF *emite* como segmento, **no** lo que una cita puede *influir* en la
etiqueta: dos citas de 21 y 23 palabras rescatan más prosa propia que una sola de 51.
Eso explica la cita de 14 palabras que no ancló la racha de 211. *(Que la racha de 48 se marcara
por absorción hacia su vecina de 211 es **interpretación**, no medida: el efecto vecino a longitud
igualada es de sólo +0,043 y esa lectura descansa en una sola observación histórica.)*

**La confianza crece con la longitud del tramo, en las dos etiquetas.** Islas AI: 0,562 a 20-60
palabras → 0,867 a 640+. Tramos `Human`: 0,304 → 0,169. La frontera está en 0,47, así que **una
isla pequeña está a un pelo de caer del lado bueno y una grande ya no se mueve.**

> **Arregla siempre primero la isla grande.** No es solo que tenga más palabras: tiene más confianza
> que revertir y además absorbe a las pequeñas de alrededor, que se resuelven solas.

### El techo del metodo: la sintesis propia no se rescata

Construir una unidad desde la fuente **si funciona** — la asimetria «destruir funciona, construir
no» describia la reparacion de texto ya generado, no la escritura desde fuente. Una unidad de ~350
palabras escrita desde el BOE dio **70 % `Human` a la primera** y **92 % afinada**, donde prosa
propia equivalente sin cita daba 100 % AI.

Pero tiene un techo, y esta medido. El residuo final fueron **32 palabras a 0,751**, rodeadas de
anclas literales **a los dos lados y a corta distancia**, y subordinadas:

> «Ese tope, al convertir en escalón contable lo que la sentencia había planteado como igualdad de
> trato, sigue midiendo la desventaja en número de hijos y no en carrera de cotización perdida.»

Es la única frase de la unidad que **no procede de ninguna fuente**: la aportación propia.

> **Lo que el detector marca de forma irreducible es la frase que lleva la síntesis del autor.** No
> es disposición, ni longitud, ni registro, y por eso **ningún anclaje lo arregla**. El techo del
> método lo fija cuánta tesis propia tiene el texto: un documento que pasara al 100 % sería un
> documento sin tesis.

**Estatus: dos observaciones, no una ley medida.** Este residuo de 32 palabras, y la apertura
abstracta de 77 palabras del paso 1, que con un ancla pegada bajó de 0,946 a 0,665 y ahí se paró.
Apuntan las dos al mismo sitio, pero son dos. **Lo que lo rompería:** una afirmación sintética
abstracta que sí cruce a `Human` bajo corchete. Si la encuentras, esta entrada se cae.

**Consecuencias operativas, todas medidas:**

- **La paráfrasis se marca; la cita, no.** Sustituir una cita literal por tu resumen del mismo
  contenido, en la misma posición, dio ese tramo AI a 0,633; restituir el literal lo pasó a `Human`
  y extendió la región limpia a 217 palabras seguidas. **Si vas a decir lo que dice la fuente,
  cítala.**
- **En prosa argumentativa el umbral de recorte está entre 77 y 103.** Lo recortado fue siempre
  la racha larga (110, 110, 103) y todo lo de ≤ 77 sobrevivió, pero **entre 78 y 102 no se ha
  medido nada**: 77 es el extremo bajo de un hueco, no la frontera. Los 113-127 que pasaban en
  la serie de dilución tenían texto humano verificado al lado. **Sin ese vecindario usa 77 como
  conservador, y mide el hueco antes de gastar cita de más en respetarlo** — la masa de cita es
  precisamente lo que empuja al collage.
- **No pongas el ancla al final.** Al 93 % del texto, el bloque AI se tragó la propia cita y el
  resultado fue el peor de cuatro versiones. Al 88 %, con 19 palabras detrás, recortó un segmento
  `Human`.
- **Conoce el precio.** Llegar al 92 % costó **37,4 % de masa de cita**, contra el 17,8-21,5 % de
  las tesis humanas de referencia: eso ya es collage. El óptimo practicable fue **78 % `Human` con
  24,4 %**. De ahí en adelante cada punto se paga con cita que un tribunal no aceptaría.

### Corolario medido: el ancla es un **corchete**, no un radio

Batería causal sobre un sujeto de 243 palabras de prosa propia pura, basal 94,6 % IA, con literal
verificado del BOE. **Mismas 311 palabras y la misma cita de 51 en las tres primeras; solo cambia
dónde está:**

| | segm. | palabras `Human` | **prosa propia rescatada** |
|---|---:|---:|---:|
| cita **al medio** | 3 | 124 | **62** |
| cita **al final** | 2 | 63 | **1** |
| cita **al principio** | 2 | 63 | **1** |
| **dos citas de 21 y 23** a 1/3 y 2/3 | 3 | **160** | **116** |

Tres consecuencias operativas:

1. **Un ancla en un borde no sirve de nada.** Solo alcanza hacia un lado. Al medio rescata 62
   veces más con el mismo texto.
2. **Dos anclas cortas y separadas baten a una larga y central**, con menos cita. Abren y cierran
   un corchete y convierte **todo lo que queda dentro**. Es además mejor escritura académica que
   el citado en bloque.
3. **El ancla se lleva la prosa concreta y deja la abstracta.** Lo que cruzó la línea fue el pasaje
   de cifras con fuente; lo que se quedó marcado fueron la apertura y el cierre abstractos (0,868 y
   0,920). **Pégala a tus frases con datos, no a tus frases de tesis.**

> **Y mide `word_split` / `fractions`, no `ai_likelihood`.** Las variantes de arriba se diferencian
> en un solo punto de probabilidad global (0,684 vs 0,694) mientras duplican las palabras
> rescatadas. Lo que se mueve es la segmentación.

### Qué hace y qué no hace mover texto

- **Mover un párrafo o una frase dentro de su propio vecindario: cero efecto** (230 → 230 sin
  cambiar una palabra). La ventana es deslizante; si la composición de la ventana no cambia, nada
  cambia.
- **Cambiar cuánta prosa no verificada comparte ventana, o traer un ancla dentro del radio: efecto
  grande** (tabla de dilución). 
- **Lo que rinde en un cierre es cambiar con qué termina, no reubicarlo.** El cierre es la posición
  más rentable porque solo está rodeado por un lado: un cierre reescrito para nombrar a sus autores
  pasó de 68,1 % a 18,0 %.
- **Mover prosa abstracta a una zona concreta contamina la zona sana** y no arregla el original.

### Bandas humanas de referencia (para no salirte, no para apuntar)

- Anclajes concretos (nombre propio, fecha, cifra con fuente, cita): separan las clases *dentro* del
  documento (8,6 vs 4,8 por 100 palabras; 13,4 vs 7,3; 11,1 vs 5,9), pero **los capítulos humanos
  anclan menos** que el texto que se estaba humanizando (0,55-1,70 frente a 2,09). El nivel absoluto
  no es la diana.
- Comas sintácticas y cifras: los textos que pasan están en ~6 comas y ~3,5-5,5 cifras por 100
  palabras. Sirve para detectar que **has destruido** especificación, no para perseguir un número.
- Voz / metadiscurso: banda humana **0,9-2,0 marcas por 1.000 palabras**.
- Longitud de frase: capítulos académicos humanos de 35,2 a 48,7 palabras. **No es diana**: llevar un
  texto a 40,0 fundiendo periodos empeoró 283 → 312.
- Nominalización académica (`-ción`, `-miento`, `-dad`, `-ismo`): 6,4-8,2 por 100 palabras en
  capítulos humanos verificados. En prosa académica **desnominalizar aleja del objetivo**; en prosa
  divulgativa la dirección es la contraria.

---

## 7. El bucle

### Fase 0 — Preparar

1. Copia canónica intacta del original. Nunca se edita.
2. **Inventario antes de tocar nada**: cifras, años, porcentajes, importes, citas textuales, autores,
   referencias, títulos, encabezados y referencias cruzadas.
3. Identifica el **género** y su registro. Es el tono que hay que conservar (§8).
4. Localiza las **fuentes reales que el texto ya cita**: son tu reserva de anclas (§4).
5. Busca si el texto ya se analizó (`pangram history -s "<frase literal>"`; reabrir es gratis). Si
   no, analízalo y guarda JSON y HTML. Anota `word_split['ai']`.
6. **Pide una muestra al usuario, una sola vez:** «¿tienes otro texto tuyo, del mismo registro, que
   pase por humano?». Si tiene tres o cuatro, pídeselos todos: el denominador de la variación humana
   cambia las conclusiones. Lo que **no** es: una lista de rasgos que copiar.
7. Determina el **régimen**:
   - **mixto** — hay prosa `Human` suficiente para anclar → Fase 1;
   - **homogéneo** — ≥ ~90 % AI, sin anclas internas → arranque del §7bis, y luego Fase 1.

### Fase 1 — Mapear y ordenar

Del JSON, lista las islas `AI-Generated` con palabras, `ai_likelihood` y coordenadas. Ordena por
masa de palabras, de mayor a menor.

**Ataca primero las islas grandes.** Reducen más masa y, por el CRF, las pequeñas y los tramos
`Human` frágiles (los que están al 35-50 %) pueden resolverse solos. **Vuelve a medir antes de tocar
las pequeñas**: a menudo ya no están.

**No toques los fragmentos que puntúan humanos.** Reescribir dos párrafos dentro del mayor tramo
humano, sin tocar una afirmación ni una cita, dio el peor resultado registrado (283 → **456**). Y no
hace falta: un tramo `Human` al 31 % no impide el veredicto.

### Fase 2 — Reparar cada isla: tabla de decisión

Diagnostica y aplica **la operación que le corresponde**. No pruebes al azar y no empieces
reescribiendo.

| Diagnóstico de la isla | Operación | Coste |
|---|---|---|
| Parafrasea en tus palabras lo que dice una fuente | **§4** Sustituye tu paráfrasis por sus palabras (≥ 40 palabras), deja tu análisis alrededor | 1 sonda |
| Ejecuta un movimiento retórico (§8) | **Poda o subordina** tejiendo. Nunca reformules | 1 unidad |
| Repite algo ya dicho en otro sitio | **Poda**, o **traslada** el dato único al punto donde se usa | 1 unidad |
| Es una abstracción huérfana (sin anclaje, sin autor) | **Ancla, atribuye o disuelve**, tejiendo (§7ter) | 1 unidad |
| Ha perdido precisión numérica respecto de la fuente | **Restaura las cifras exactas** con su precisión real | 1 unidad |
| Está a más de ~100 palabras de cualquier ancla | **Redispón**: mete un ancla dentro o parte la serie | 1 sonda |
| Es una región contigua nueva de más de ~150 palabras | **Trocea** en unidades ≤ 120 y constrúyela por Fase 3 | varias |
| Está entre el 46,8 % y el 50 % | **Un empujón cualquiera** de los anteriores: cae a `AI-Assisted` y deja de bloquear | 1 unidad |
| Nada de lo anterior aplica | **Batería de 3 variantes**, mide las tres, elige por margen | 3 créditos |

Cuando la marca **cruza una frontera** y alcanza el párrafo anterior, no ensayes más variantes del
párrafo nuevo: reescribe junta la **unidad completa de solapamiento**. Insistir en la adición aislada
dejó entre 42 % y 51 % AI donde tratar el solapamiento completo dio 100 % `Human`.

**Y antes de perseguir un fragmento marcado que no has escrito tú: arregla sus vecinos y vuelve a
medir** (propagación reversible, §3.2).

### Fase 3 — Construir regiones largas: la regla crítica

Una región larga de prosa propia **sí puede** quedar 100 % `Human`: hay una de 1.157 palabras con
0,7 % de cita que puntúa 8,6 % medida sola. Pero solo se consigue de una forma.

**Crece de izquierda a derecha, en la disposición final, y verifica cada paso en su sitio.** En el
paso *k* la sonda es:

```
contexto izquierdo real  +  unidades 1..k  +  contexto derecho real ya Human
```

Nunca incluyas a la derecha material aún sin verificar: contaminaría la medición.

> **Prohibido: verificar dos mitades por separado y concatenarlas.** Dos mitades de 220 palabras que
> dieron 0 % AI cada una, unidas en 441 palabras, dieron **196 palabras AI en el centro**: la ventana
> interior no tenía ancla. Es el error más caro de todo el procedimiento.

Tamaño de unidad: 60-120 palabras. Amplía a 150 solo cuando el contexto acumulado ya sea estable.

### Fase 4 — Recombinar

Cuando tengas dos o tres versiones buenas, ninguna será la mejor en todas las regiones.
**Recombina sin redactar nada nuevo**: coge la mejor versión y devuelve una región a la redacción de
otra versión ya medida. Eso bajó de 405 a 345 sin escribir una frase.

- Para en cuanto la recombinación empiece a perder: una buena configuración es un paquete, y al
  sacarle otra pieza el mismo caso se derrumbó de 345 a 453.
- **La recombinación va sola.** Mezclada con nueve anclajes nuevos empeoró +63 y no hubo forma de
  saber de quién fue la culpa.

### Fase 5 — Cerrar

Integra, escanea el documento completo, repara lo que reaparezca empezando por las uniones,
auditoría de integridad (§9) y puerta de estabilidad (§10). Si el mapa trae varias islas
pendientes, no cierres una por una: acumula antes un lote de candidatas verificadas en sonda
y valida el conjunto en un solo integral (§13, «Lotes»).

---

## 7bis. Régimen homogéneo: el arranque

Si el documento es casi todo AI no hay anclas y el método de islas no puede empezar. Una reescritura
completa en una pasada **no** resuelve: 97,2 % → 97,7 % AI.

1. Reúne 2-4 muestras de texto humano verificado del mismo género y tema (capítulos reales, no
   generados).
2. Reconstruye el documento **transfiriendo el registro completo** de esas muestras: atribución menos
   comprimida, periodos acumulativos, transiciones funcionales, desarrollo de la fuente antes de la
   conclusión. Esto llevó 97,7 % → **64,8 %** y creó ocho tramos `Human` de 1.781 palabras.
3. Congela literalmente todo lo que ya pase.
4. A partir de ahí, Fases 1-5 normales.

Es un **arranque para generar anclas**, no un método de acabado. No lo repitas sobre un documento
que ya tiene prosa `Human`.

### Ancho contra fino: cuál toca

No es contradicción, es régimen:

- **Régimen homogéneo o alta fracción AI:** una pasada **ancha y tejida** sobre todo el documento,
  aplicando a la vez el destemplado, los patrones del §8 y el anclaje. Ganó −275, −304 y −46 donde
  las pasadas finas perdieron +81, +39, +97 y +108.
- **Régimen mixto con pocas islas:** **operaciones dirigidas** de la tabla de decisión. Aquí la
  pasada ancha **falla**: reescribir varias secciones a la vez dio 21,4 % → 21,2 % (0,2 puntos por
  más de mil palabras cambiadas) y reescribir cuatro solapamientos dio 21,2 % → **30 %**.

Lo que nunca funciona en ningún régimen es **re-redactar**; lo que funciona ancho es **tejer ancho**.

---

## 7ter. La abstracción huérfana

> **La prosa que el detector marca es la abstracción del propio autor cuando va sola y sin anclaje.**

Redactar mejor una frase huérfana no la salva (una reescritura con mejor sintaxis subió del 72,6 % al
80,5 %). Las tres salidas, **todas tejidas**:

- **Anclarla.** Meterle un referente concreto que ya esté en el texto. En prosa académica el
  referente tiene que ser una **cita autor-año o una cita literal**: un sintagma concreto o un eco de
  las palabras de una cita vecina no ancla nada (78,6 % → 78,1 %).
- **Atribuirla.** Que el autor citado aparezca dentro de la propia frase, como sujeto o inciso.
  «Marshall hace de ese elemento social un principio igualador» bajó veinte puntos respecto a «Ese
  elemento social opera como principio igualador». Tejido: *ocupa, para Fraser, una fase…*. Como
  reescritura del párrafo, la misma estrategia empeoró dos veces.
- **Disolverla.** Que pase a ser subordinada o aposición de la frase contigua que lleva la cita. Es
  la más eficaz, **pero solo dentro de la zona marcada**: hacia fuera contamina el bloque sano.

**Dos errores comprobados:** nunca arregles una huérfana **partiéndola en dos** (creas otra) ni
**fundiéndola con la de al lado** (alargas la racha abstracta, que es lo que se castiga).

**Dos corolarios sobre rachas:** un tramo abstracto contiguo se marca por serlo, y cuanto más largo
peor; y una frase corta bien anclada pegada a una racha marcada se la traga la racha. Primero encoge
la racha, después ancla la apertura.

**El anclaje tiene suelo.** Disolver funciona donde hay una frase vecina con cita. La apertura y el
cierre de una sección son arquitectura del propio texto y no hablan de ningún autor: ahí no hay nada
a lo que disolverse. Deja de gastar mediciones anclando esos dos y trátalos por §6 (cambiar con qué
termina).

---

## 8. Qué se marca, y cómo se arregla

Esto predice **dónde** cae la marca. Confirmado por dos vías independientes: nuestras mediciones y el
catálogo *Signs of AI writing* de Wikipedia, que coincide justo en sus apartados retóricos y no en
los ortográficos.

> **La reparación es estructural: poda, subordina o traslada, tejiendo. No sustituyas palabras.**

Las veintidós marcas que rinden están en la tabla de §8.2 y con eso trabajas. Cuando un tramo se
resista y no reconozcas qué falla, abre **`references/marcas-de-ia.md`**: el catálogo entero *Signs
of AI writing* y los 35 patrones de `/humanizer` en 58 marcas calcadas al español, cada una
etiquetada según si la hemos medido aquí, si solo converge, si delata sin causar, si no aplica al
género o si **aplicarla en español estropea el texto** (las comillas curvas y el relleno lo hacen).
Trae además el bloque de `grep` de artefactos de herramienta y la lista inversa de lo que los
humanos hacen *más*. No la necesitas para el bucle normal.

### 8.1 El molde del párrafo generado — destemplar

Los párrafos generados siguen un molde: **frase que anuncia el dato, dato, frase que interpreta el
dato**. Los párrafos humanos entran directos por el dato y meten el juicio dentro de una aposición o
una subordinada, no en oración propia.

> «Los números del RETA reflejan muy bien esta mezcla. Julio de 2026 cerró con 3.472.357 afiliados.
> (…) Si miramos el conjunto de los datos, el resultado es que solamente uno de cada siete encaja
> con la idea clásica del creador de empleo.»
>
> → «Julio de 2026 cerró con 3.472.357 afiliados al RETA. (…) Juntad las dos cosas y solo uno de cada
> siete afiliados encaja de verdad con la idea clásica del creador de empleo.»

**Marcos que se borran** (frases enteras): *los datos reflejan / muestran*, *si miramos*, *las
estadísticas nos enseñan*, *la idea de fondo es*, *esto pone de manifiesto*, *lo que demuestra que*;
y en registro académico *aquí radica el problema*, *su argumento es que*, *esta distinción es clave*.

**Conectores que NO se tocan** (bisagras de una o dos palabras): *así*, *además*, *sin embargo*, *no
obstante*, *en este sentido*, *por su parte*, *en consecuencia*, *por ello*, *frente a*. Cuatro
capítulos académicos verificados como humanos van llenos de ellos: en dos, el 71 % y el 53 % de las
frases abren con conector. Borrarlos junto con los marcos deja las zonas reescritas en 0 %, un
extremo que no tiene ningún texto humano, y volver a meterlos después no lo arregla (451 → 548).

### 8.2 Los movimientos retóricos

| Patrón | Ejemplo → arreglo |
|---|---|
| **«no X sino Y»**, «X, no Y», «no solo X» | *ocupa una fase transitoria, **no** un estado natural* → *ocupa una fase histórica transitoria* |
| **cadena de razonamiento** encadenada | *…, porque A, mientras B, **de modo que** C* → dos o tres frases |
| **revelar una verdad honda** | *queda **como lo que es**, una fase transitoria* → *es una fase transitoria*; también *la verdadera cuestión es*, *en el fondo*, *lo que de verdad importa* |
| **anunciar el recuento** | *gestionada **de dos maneras a la vez**: A y B* → *gestionada por A y por B* |
| **frase-cartel** que anuncia lo que viene | *«Conviene retener esta objeción, porque reaparece más adelante:»* → fuera |
| **sujeto ausente o abstracto** | *el fallo excede a…* → *Fraser sitúa el fallo más allá de…* |
| **tríada forzada** o enumeración anunciada sin desarrollo | *el estudio separa tres elementos: A, B y C* → desarrolla cada uno con su contenido y su atribución, o reduce |
| **cierre sentencioso / aforístico** | la frase lapidaria que resume el párrafo. Es el residuo más frecuente: sustitúyela por la consecuencia atada a la evidencia, o quítala |
| **importancia inflada** | *marca un hito*, *subraya la importancia de*, *refleja una tendencia más amplia*, *punto de inflexión*, *deja una huella* → di el hecho |
| **análisis superficial en gerundio** | *subrayando…*, *reflejando…*, *contribuyendo a…*, *garantizando…* colgado de un dato |
| **recapitulación** y apartados de «retos y perspectivas» | poda; conserva solo la afirmación que no esté en otro sitio |
| **fragmentos dramáticos** en serie y frases-remate encadenadas | reúnelos en una oración con contenido |
| **sentencias formularias** | *X es el Y de Z*, *X se convierte en una trampa*, *el lenguaje de*, *la arquitectura de* → la afirmación concreta |
| **responder objeciones que nadie ha hecho** | *no se trata tanto de*, *no estoy diciendo que*, *que quede claro* → la afirmación directa |
| **descartar alternativas ficticias** | *una opción tentadora sería… pero*, mencionada una vez y nunca más → la restricción real |
| **fuentes vagas** | *los expertos señalan*, *algunos críticos*, *diversos informes* → nombra la fuente real o retira la afirmación |
| **relleno** | *con el fin de lograr este objetivo* → *para*; *debido al hecho de que* → *porque*; *es importante señalar que los datos muestran* → *los datos muestran* |
| **matizadores apilados** | *podría posiblemente argumentarse que* → conserva el matiz que la fuente sostiene |
| **ciclo de sinónimos** y aperturas de frase repetidas | usa un nombre estable; arregla el patrón, no la palabra |
| **rango falso** *de X a Y* | cuando X e Y no forman un rango, enumera |
| **final de optimismo genérico** | termina en el último dato útil |
| **encabezado repetido** en la primera frase del apartado | fuera la frase |

El **«no X sino Y»** merece mención aparte porque es el caso mejor medido: **0 apariciones en 1.561
palabras de tramos humanos frente a 2 en 164 palabras de tramos marcados** — separación perfecta
dentro del documento. Quitarlos, sin tocar nada más, bajó el peor bloque del 71,8 % al 64,0 %.

Aplicados en cadena y siempre tejidos, estos patrones llevaron un capítulo de 165 a 123 palabras
`AI-Generated` y cambiaron el veredicto de `AI Detected` a `Mostly Human Written`.

**Dos avisos:**

- **Un patrón suelto no prueba nada.** Un *sin embargo* es prosa normal, y un *no X sino Y* también:
  los textos humanos de referencia llegan a 3,0 por mil palabras. Lo que cuenta es la **acumulación
  dentro del mismo tramo**.
- **No toques el patrón dentro de una cita literal**, de un título o de un nombre propio.

### 8.3 El dial de la voz: en los dos sentidos

**Es un dial, no una receta.** Los dos casos donde más rindió apuntan en direcciones contrarias:

| Texto | Voz medida | Qué funcionó | Resultado |
|---|---|---|---|
| capítulo sin nadie dentro | 0,00 marcas/1000 | **meterla** | 283 → 206 palabras marcadas |
| sección ahogada en metadiscurso | **20,90**/1000 (banda 1,62-5,51) | **quitarlo** | 3081 → 2020 IA en **una** pasada |

**Mide antes de decidir la dirección.** Se persigue la banda humana (0,9-2,0 marcas por 1.000
palabras), nunca el extremo.

**Cómo medirlo sin engañarte.** Un regex escrito después de leer el texto recoge *sus* modismos:
mide tu lectura, no el texto. Usa **clases gramaticales cerradas**: posesivos de primera persona ·
clíticos `nos`/`me` · verbos en `-amos`/`-emos`/`-imos` · autorreferencia al texto (`este apartado`,
`el capítulo 8`) · andamiaje ordinal (`en primer lugar`, `por último`). Medido así un texto daba
20,90; con el regex amañado a mano, 11,16. **La medida honesta separaba casi el doble.**

**Descuenta lo que el género de la referencia no puede tener.** Una tesis dice «como se verá en el
capítulo 8»; un capítulo de libro publicado no puede decirlo nunca. Descontado, un texto pasaba de
7,70 (fuera de banda) a **5,58** (dentro). Sin el descuento habrías seguido recortando hasta salirte
por abajo, que es el error que costó 451 → 548.

**Dosis y forma:**

- **Tejida dentro de una frase que además dice algo.** *Ningún país, conviene precisarlo, encarnó el
  modelo puro.*
- **Nunca como frase suelta que anuncia lo que viene.** «Conviene retener esta objeción, porque
  reaparece más adelante:» se convirtió en su propio segmento de 26 palabras al 76,9 %.
- **Dosis, no cantidad.** Tres marcas en 100 palabras salieron peor que una.
- **Al quitar, quita el anuncio y deja la referencia cruzada.** Fuera «El objetivo no es… Se trata
  de…»; se quedan «lo abordaremos en el capítulo 8», «introducido en el apartado 2.1»: llevan
  información y el lector de una tesis los necesita.
- **En el registro del propio texto.** Si la tesis usa «conviene», «cabe», «este trabajo», mete eso.
  Lo que no cabe es cambiarle el registro al autor.

### 8.4 Higiene ortográfica

No fue la causa en ningún caso medido de prosa académica, pero delata y es gratis: rayas y guiones
largos donde el original no los usa, negritas sin motivo, listas con etiqueta en negrita y dos
puntos, títulos con mayúscula en cada palabra, emojis, restos de conversación (*espero que te
sirva*, *¿quieres que…?*), avisos de límite de conocimiento (*hasta mi última actualización*), tono
complaciente, restos de Markdown (`##`, `**`) y separadores `----` entre apartados.
**Ajústate a lo que hace el documento original**, no a una norma abstracta.

**Las comillas son la excepción y va en sentido contrario.** En español las correctas son « », y
Word y macOS curvan solas: aquí solo se comprueba **coherencia interna**. No las «endereces» nunca
— estropearías la tipografía de una tesis. Igual con los pares con guion (*data-driven*): eso es
del inglés y en español no existe. Ver marcas 33, 34 y 46 de `references/marcas-de-ia.md`.

### 8.5 No toques esto (falsos positivos)

Gramática impecable, estilo consistente, palabras formales o técnicas, un solo conector de
transición, una sola raya, comillas curvas por sí solas, una frase corta para enfatizar, una
repetición deliberada con función rítmica, límites y advertencias reales, alternativas que un lector
sí consideraría, afirmaciones sin cita cuando el género lo admite, formato complejo correcto, y
cualquier expresión **dentro de una cita, un título o un nombre propio**. Nada de esto prueba nada
por sí solo y «arreglarlo» degrada el texto.

**Las manías del autor se respetan.** Cifras repetidas en letra, comillas angulares, apelación
directa al lector, paréntesis con datos en crudo. Si el usuario aporta otro texto suyo, manda sobre
cualquier regla de estilo genérica, incluida la de las rayas.

---

## 9. Integridad y calidad

Antes de aceptar cualquier candidata y otra vez antes de entregar:

- **Inventario numérico**: diff automático de cifras, años, porcentajes e importes contra el
  original. Cero pérdidas.
- **Afirmaciones, una por una.** **Comprobar cifras no es comprobar afirmaciones**: en un caso el
  control de cifras estaba en verde y una reescritura se había llevado por delante el criterio
  central del ensayo, que no contenía ningún número.
- **Citas y referencias**: todas las fuentes del original siguen presentes; los localizadores son
  correctos; las citas nuevas son **literales y verificadas contra el original**.
- **Fronteras**: ninguna palabra partida, frase truncada ni oración duplicada en los empalmes. Los
  límites de segmento que da Pangram **cortan palabras**: son diagnóstico, nunca líneas de corte
  editoriales. Recomponerlos mecánicamente ya produjo una frase truncada y otra duplicada.
- **Estructura**: encabezados, numeración y referencias cruzadas («Capítulo 4», «apartado 3.1»)
  intactos y correctos.
- **Ninguna afirmación nueva, ninguna reforzada, ninguna relación causal introducida.** Repasa
  denominadores y poblaciones: al comprimir es fácil hacer que un porcentaje parezca referirse a otro
  grupo del que se calculó.
- **`is_humanized: false`** en todos los segmentos.
- **Lectura seguida** de las uniones como prosa, no como ensamblaje.
- **Tono** del género de origen.
- Normaliza espacios y puntuación **solo** antes del escaneo final.

**Nada de esto está sobre la mesa, ni aunque el usuario lo pida:**

- **Inventar** hechos, cifras, fechas, fuentes, páginas o citas.
- **Meter erratas, sinónimos raros o caracteres unicode invisibles** (homoglifos, ancho cero). Es
  manipulación oculta para burlar un control de integridad, no escritura que se lea con naturalidad;
  se destruye con una normalización o un copiar-pegar; activa `is_humanized`, que para un texto
  firmado es peor que el positivo original; y en un trabajo académico expone al usuario a un problema
  mucho mayor que el que resuelve. Si lo pide, dilo en una frase y ofrece el procedimiento legítimo.
- **Artefactos de extracción de PDF** (números de página sueltos, notas con URL roto, cortes de
  línea). Comprobado que los textos humanos de referencia siguen dando humano una vez limpios: no
  aportan y dañan la calidad.
- **Recortar contenido para bajar el porcentaje.** Si algo sobra de verdad, dilo; no lo borres a
  escondidas.
- **Convertir el texto en un collage de citas.**

Si al verificar una fuente descubres que el original la representa mal, **corrígelo y dilo al usuario
de forma explícita y separada del informe de progreso**: es una mejora de calidad, pero cambia el
contenido y la decisión es suya.

---

## 10. Puerta de estabilidad

**Pangram no es determinista.** El mismo fichero, sin cambiar un byte, alternó entre `Human Written`
con 0 % AI y `Mostly Human Written` con una isla de 27 palabras; y un bloque limpio repetido dio
8,5 % y 8,6 %. Además, 23 sustituciones de sinónimos triviales movieron un bloque limpio de 0 % a
2 % AI: eso es ruido de frontera, no una palanca.

Por tanto un solo aprobado no cierra nada:

1. Guarda el texto definitivo con su **nombre final**.
2. Analiza **ese** archivo, no una variante enviada por otro canal.
3. Repite el análisis **2-3 veces seguidas**.
4. Si aparece una isla en alguna repetición, repárala y **vuelve a empezar la puerta**.
5. Entre dos candidatas equivalentes en calidad, quédate con la de **menor probabilidad global**:
   margen es lo que sobrevive al ruido.
6. **Cualquier edición posterior invalida el pase.** Vuelve a medir.

---

## 11. Cuando un bloque se resiste

Si aguanta tres pasadas, antes de intentar una cuarta redacción **mide ese bloque solo**, en un
fichero aparte. Cuesta 1-2 créditos frente a 45 del documento.

- **Si sale alto solo**, la prosa tiene firma propia: sigue trabajándola. Un bloque puede puntuar más
  alto solo que dentro (93,1 % frente a 83,0 %).
- **Si sale humano solo**, ya está bien escrita y lo que la marca es el entorno: 58 palabras que
  daban 4,4 % solas puntuaban 78,1 % dentro. **Arregla los vecinos, no el bloque.**

**Es diagnóstico, no cribado.** No lo uses para elegir entre redacciones: las ordena al revés que el
documento. Y la doble medición engaña en los dos sentidos — una región dio **0 % AI anclada y 92,9 %
sola**, y una unidad de 65 palabras pasó sola y quedó marcada dentro de una serie de 183. Usa el
solitario como **filtro barato** y **valida siempre en la posición final**.

### Antes de declarar un techo

Declarar un techo mal es el error más caro de esta skill, porque cierra el trabajo a medias. Antes:

1. **Contrasta la teoría del techo con un texto humano verificado del mismo género.** Si tu
   explicación dice «le falta X» y un texto humano del género tiene **menos** X que el tuyo, la
   explicación es falsa. Ocurrió: «falta material citado» cuando el capítulo ya citaba el doble que
   textos que puntúan 0,002 %. Con la teoría corregida el residuo bajó de 345 a 283, y luego a 123.
2. **Comprueba a qué apuntas.** Si miras el global o el `ai_likelihood` de los tramos humanos, no
   estás mirando el veredicto. Cuenta `word_split['ai']`.
3. **Pasa los bloques restantes por el §8**, uno por uno. Es lo que más veces queda sin hacer, porque
   no se ve contando.
4. **Comprueba que has tejido en vez de reescribir.** Tres reescrituras seguidas no son evidencia de
   techo: son evidencia de que usas la herramienta equivocada.
5. **Comprueba disposición y anclas** (§6) antes de concluir que el problema es la redacción.

Solo entonces la salida es del usuario: explícale dónde está el límite con los números y déjale
decidir. Si dice que no, reporta con honestidad y sin adornar.

---

## 12. El género manda sobre el manual

Las palancas son propiedades del texto y funcionan en cualquier género. Los **números no se
transfieren**, y algunas tácticas tampoco:

- **Ensayo, columna, post.** Cabe la voz: primera persona, apelación al lector, registro coloquial.
  El destemplado se hace quitando la frase que anuncia el dato. La palanca de la cita rinde menos:
  apóyate en §5, §6 y §8.
- **Tesis, paper, informe técnico, memoria.** Aquí manda **§4, entregar en vez de sintetizar**, y es
  la pasada más rentable del género. Autores, años, páginas y terminología son intocables.
  Desnominalizar **aleja** del objetivo.
- **Texto legal, contractual o normativo.** Casi todo lo anterior sobra: manda la fidelidad. Si el
  texto tiene que decir lo que dice, dilo y no lo humanices.
- **Sin fuentes citables** (ensayo personal, divulgación sin referencias): no fuerces la cita. Quedan
  la disposición, las operaciones estructurales y las baterías baratas. **Dilo al usuario y no
  prometas el mismo resultado.**

Mantener el registro no es una concesión estética. Un capítulo de tesis que suena a columna de
opinión está peor que antes, aunque el detector diga humano.

---

## 13. Economía de la medición: aquí está la velocidad

**1 crédito por cada 100 palabras empezadas**, mínimo 50 palabras, máximo 100.000 caracteres.

| Qué mides | Palabras | Créditos |
|---|---:|---:|
| una **unidad** (párrafo) | 65-130 | **1-2** |
| una **sonda** con contexto real a ambos lados | 900-1.400 | 9-14 |
| el **documento** completo | 4.500-5.000 | 45-50 |

De aquí sale la estrategia de pocas iteraciones, y no es «acertar a la primera»: es **probar
barato**. Una batería de 3 variantes de unidad cuesta 3 créditos. Escribe 3, mide las 3, quédate con
la que pase con mejor margen. Ejemplo real: tres variantes de un párrafo dieron `Human 10,7 %`,
`100 % AI` y `100 % AI`; se aceptó la primera por 3 créditos.

**Reglas de gasto:**

- **Nunca `batch` ni comodines** sobre carpetas: ya se gastaron créditos analizando ficheros ajenos a
  la tarea. Solo `check -f <fichero>` explícito.
- No vuelvas a escanear el documento completo después de cada frase. Escaneo integral solo en hitos
  de ensamblaje. Por encima de 50 créditos, pide el visto bueno del usuario.
- Guarda siempre `--format json`: los segmentos con coordenadas son gratis después y son el
  diagnóstico.
- Reutiliza un resultado solo si el texto es idéntico byte a byte.
- `pangram history` y `history show <uuid>` son gratis: reabrir un análisis previo no cuesta nada.

### Lotes: varias islas por integral

El integral (≈45 créditos) es lo más caro del bucle; la sonda (≈10), lo más barato. Cuando el
mapa trae muchas islas, el ciclo «una isla → un integral» quema un integral por isla. El régimen
de trabajo es el inverso: **lote de islas por integral**. Ordena por masa y empieza por las
grandes (Fase 1), que son las que más palabras liberan y las que más arrastran por CRF.

1. Para cada isla del lote, edita **tejiendo** (§5) y verifica **en sonda, no en integral**:
   construye su probe con `step.py`, mídelo y solo cuando la candidata pase en su sitio repite
   con `--commit`. Lo que no pase en sonda no entra en el lote.
2. Commitea en el documento todas las candidatas verificadas del lote y lanza **un solo
   integral** para validar el conjunto en su posición final. Son regiones independientes y cada
   commit mueve pocas palabras, así que el resegmentado apenas se desplaza.
3. Lee el integral con el mapa completo (§14): si mejora, sigue desde ahí; si empeora,
   **vuelve a la mejor versión, no a la última**, y parte el lote por la mitad hasta aislar la
   pieza culpable. Nunca mezcles el lote con recombinación: la Fase 4 va sola.

Límite medido: esto es un lote de ediciones tejidas y verificadas una por una, no una pasada
masiva a ciegas. Reescribir varias secciones a la vez sin sonda previa dio 21,4 % → 21,2 % y
21,2 % → **30 %**. Dos o tres islas por integral es el ritmo que ha funcionado (−132 y −138 en
la misma serie); por encima de tres, el riesgo de resegmentado supera al ahorro. Y la sonda
ordena mal a veces —una candidata que pasa en sonda puede ir plana en integral si sus vecinos
siguen AI—, por eso el integral valida y por eso las islas del lote se eligen independientes
entre sí y sin tocar tramos `Human`.

### Comandos

```bash
pangram whoami                                                  # plan y creditos
pangram history -s "<frase literal del texto>" --json           # gratis
pangram history show <uuid> --json > base.json                  # gratis
pangram check -f unidad.txt   --yes --format json      --out informes
pangram check -f documento.txt --yes --format json,html --out informes
```

Localiza el cliente: `pangram` en el PATH, o `<repo>/.venv/Scripts/pangram.exe`, o
`.venv\Scripts\python -m pangram_auto`.

Del JSON usa `verdict`, `ai_likelihood`, `fractions.{ai,ai_assisted,human}`, `word_count` y sobre
todo `segments[]` con `start`, `end`, `label`, `ai_likelihood`, `word_count`, `is_humanized`.

### Sonda de unidad en su posición final

Guarda esto como `scripts/step.py`. Empalma una candidata en el documento y construye la sonda con
contexto real a ambos lados, respetando fronteras de oración.

```python
# -*- coding: utf-8 -*-
"""Mide una unidad donde va a vivir: contexto real izquierdo + candidata + contexto real derecho."""
import re, argparse

def sent_left(txt, n):
    sub = ' '.join(txt.split()[-n:])
    m = re.search(r'[.!?]\s+([A-ZÁÉÍÓÚÑ¿¡"“])', sub)
    return sub[m.start(1):] if m else sub

def sent_right(txt, n):
    sub = ' '.join(txt.split()[:n])
    m = list(re.finditer(r'[.!?](?=\s|$)', sub))
    return sub[:m[-1].end()] if m else sub

a = argparse.ArgumentParser()
a.add_argument('--doc',   required=True)   # documento de trabajo
a.add_argument('--cand',  required=True)   # candidata
a.add_argument('--start', required=True)   # marca literal donde empieza lo que sustituye
a.add_argument('--end',   required=True)   # marca literal donde termina, o EOF
a.add_argument('--probe', required=True)
a.add_argument('--left',  type=int, default=520)
a.add_argument('--right', type=int, default=300)
a.add_argument('--commit', action='store_true')
o = a.parse_args()

doc  = open(o.doc,  encoding='utf-8').read()
cand = open(o.cand, encoding='utf-8').read().strip()
i = doc.index(o.start)
j = len(doc) if o.end == 'EOF' else doc.index(o.end, i)

probe = (sent_left(doc[:i], o.left).strip() + "\n\n" + cand + "\n\n"
         + sent_right(doc[j:], o.right).strip())
open(o.probe, 'w', encoding='utf-8').write(probe)

run, tot = len(cand.split()), len(probe.split())
print(f"sustituye {len(doc[i:j].split())}w -> {run}w | sonda {tot}w "
      f"| serie {100*run/tot:.1f}% | ~{-(-tot//100)} creditos")
if o.commit:
    open(o.doc, 'w', encoding='utf-8').write(doc[:i] + cand + "\n\n" + doc[j:])
    print("COMMIT")
```

Mide sin `--commit`; cuando pase, repite con `--commit`.

### Métricas de control (no son objetivos)

Sirven para detectar que una edición ha **destruido** especificación, nunca para perseguir un número:

```python
import re
t = open(f, encoding='utf-8').read(); n = len(t.split())
clean = re.sub(r'(?<=\d),(?=\d)', '', t)                 # fuera comas decimales
figs = [x for x in re.findall(r'\d[\d.,]*', t)
        if not re.fullmatch(r'(?:19|20)\d{2}', x)]
print(100*clean.count(',')/n, 100*len(figs)/n)            # comas y cifras por 100 palabras
```

Si tras una edición caes muy por debajo de ~6 comas y ~3,5 cifras por 100 palabras, has borrado
especificación y vas a romper el tramo. **Estar por encima no arregla nada.**

**No metas scripts de análisis en `python -c "..."` desde bash**: las barras invertidas se pierden,
`\b` llega como carácter de retroceso y el regex devuelve cero en silencio. Ha falseado una medición
dos veces. **Escribe el script a fichero.**

---

## 14. Lo que NO funciona

Cada línea está medida. Consultar esta lista antes de improvisar ahorra sesiones enteras.

**Sobre el estilo y los rasgos contables**

- **Igualar métricas agregadas** de un texto humano (longitud de frase, densidad de anclajes):
  igualando 23,4 vs 23,9 y 11,5 vs 10,2 el resultado **empeoró** de 346 a 448 palabras AI.
- **Convertir sujetos nominales abstractos en agentes humanos**: plano entre el 7 % y el 36 % de
  fracción AI; las tesis humanas auténticas puntúan *más alto* en sujeto abstracto (13-23 %).
- **Registro verboso** (marcos iniciales, matizadores apilados, reformulación redundante, gerundios,
  perífrasis): empeoró 76,6 % → 86,1 %.
- **Subir densidad de datos** en un tramo marcado: 100 % AI. **Subir densidad de comas**: 87 % AI.
- **Variar solo la cadencia** o las longitudes: 91,8 % AI. Fundir periodos hasta la media humana:
  283 → 312.
- **Unir oraciones** masivamente: de 42,4 % a ~53 %.
- **Primera persona o metadiscurso** sin destemplar antes: la voz es maquillaje, 85 %.
- **Tabla de datos**: 100 % AI, global 96,4 %.
- **Calcar un esqueleto sintáctico humano**: 100 % AI, global 99,8 %.
- **Perseguir el paralelismo sintáctico**: no es la variable; tres declarativas paralelas puntúan
  humano si cada una lleva cifra y nombre.
- **Sinónimos**: 23 sustituciones triviales movieron un bloque limpio de 0 % a 2 % AI. Ruido.

**Sobre la intervención**

- **Reescribir un bloque en vez de tejer dentro:** cinco de cinco peores.
- **Tocar los tramos que puntúan humanos:** 283 → 456, el peor resultado registrado.
- **Reformular un residuo repetidamente:** 80,4 % → 88,9 %; en otro caso 96 palabras AI con
  probabilidad local del 81 %.
- **Arreglar un patrón creando otro:** al sustituir aforismos por mecanismos salieron tres frases con
  estructura idéntica, de 23 % a 29 %. **Relee buscando el patrón nuevo que acabas de introducir.**
- **Mover prosa abstracta a una zona concreta:** contamina la zona sana.
- **Reubicar un párrafo dentro de su vecindario:** cero efecto, 230 → 230.
- **Quitar los conectores junto con los marcos:** 451 → 548.
- **Partir una huérfana en dos** o **fundirla con la de al lado**.
- **Añadir citas encima de la paráfrasis** para diluirla, o subir la cuota de cita como métrica.
- **Reescritura completa en una pasada:** 97,2 % → 97,7 %.
- **Pasada masiva multisección en régimen mixto:** 21,4 % → 21,2 % (0,2 puntos por más de mil
  palabras), y en otro intento 21,2 % → **30 %**.
- **Verificar dos mitades por separado y concatenarlas:** 0 % + 0 % → 196 palabras AI en el centro.
- **Mezclar recombinación con edición nueva:** +63 y sin atribución posible.

**Sobre el método**

- **Una correlación nula no dice nada si la variable nunca salió de su franja.** La longitud de frase
  daba r=+0,03 en doce versiones, pero las doce vivían en una franja de 3,7 palabras enteramente por
  debajo del mínimo humano.
- **Antes de escribir «X empeoró», comprueba en qué versión entró X.** Si el texto de un bloque no ha
  cambiado ni una letra y su porcentaje sí, no ha sido ese bloque: es propagación del vecino.
- **Mira el mapa completo en cada medición**, no solo la zona que editaste.
- Si mejora, sigue desde ahí. Si empeora, **vuelve a la mejor versión, no a la última**.
- Cuidado con confundir un bloque que baja de porcentaje con uno que mejora: del 59,6 % al 54,5 %
  creciendo de 39 a 72 palabras es **peor**.

**Lo que no debe inferirse.** Una oración larga no es humana por serlo ni una corta artificial. Los
conectores académicos no se eliminan por sistema. La puntuación, la desviación de longitud y la
riqueza léxica son controles de calidad, no objetivos. Un texto que pasa y no se entiende no vale.

---

## 15. Sin detector disponible

Si no hay sesión, créditos o conexión, el manual se aplica igual, a ciegas: el §8 completo, el §4,
el destemplado y el §7ter no necesitan medición. **Dilo claramente: sin medición no hay garantía.**

Si el detector que le importa al usuario es otro (GPTZero, Turnitin, ZeroGPT, Copyleaks), el manual
vale igual porque las palancas son propiedades del texto. Lo que cambia es el bucle: pídele que pase
cada versión por su herramienta y te traiga el resultado.

---

## 16. Al terminar

Entrega el texto y, en el mismo mensaje, lo que el usuario necesita para publicarlo:

- **Veredicto y reparto, leídos con honestidad.** «Veredicto `Human Written`, 0 % del texto marcado
  como IA, 31 % de probabilidad global, sin marca de humanizador». Decir «100 % humano» exagera.
- Cuánto ha cambiado la extensión y qué se ha eliminado.
- Cualquier **cambio estructural o editorial**, y por separado cualquier **corrección de contenido**
  (una fuente mal representada, un denominador equivocado): esa decisión es del usuario.
- Las afirmaciones del original que no aparecen literales en la versión final, comprobando una por
  una que su contenido sigue vivo.
- La **cuota de cita** resultante, para que vea que está en banda.

Si te quedas por debajo, dilo sin adornarlo: veredicto real, reparto real, cuántas palabras siguen en
`AI-Generated` y **por qué** se ha parado ahí. «7,0 % de IA, `Mostly Human Written`, y lo que queda
son dos bloques de paráfrasis que han resistido diez intervenciones» es útil; «ya casi está» no.

Guarda cada versión (`v0-original.txt`, `v1.txt`, …) con su JSON y una **bitácora** con una línea por
medición: unidad, operación aplicada, palabras, serie contigua, veredicto, fracción AI, global y qué
se aprendió. Anota también las mediciones fallidas: son la mitad del valor. Sin las versiones no se
puede volver atrás y sin la bitácora no se puede recombinar.

---

## 17. Alcance honesto

Pangram es un **instrumento de evaluación, no una prueba de autoría**. Trátalo así al informar.

**No prometas un pase a la primera ni un método universal.** Está medido que ninguna redacción fija
fuerza una salida determinista y que el mismo fichero puede cambiar de etiqueta. Lo que este
procedimiento garantiza es distinto y es real:

- **minimiza el número de iteraciones** — diagnóstico que elige la operación en lugar de probar al
  azar, unidades de 1-2 créditos, baterías de 3 variantes, disposición calculada de antemano;
- **cierra con una puerta** que detecta y repara hasta que el artefacto exacto sea estable frente al
  modelo actual.

Si un tramo resiste después de agotar la tabla de decisión y el §11, dilo. Es preferible entregar
`Mostly Human Written` con la calidad intacta y el residuo localizado que un texto degradado.

---

## 18. Calibración: qué cabe esperar

Caso real completo, tesis académica en español, para ajustar expectativas y detectar si vas por mal
camino:

| Hito | Palabras | Fracción AI | Global | Qué lo produjo |
|---|---:|---:|---:|---|
| original | 6.251 | 97,2 % | 92,9 % | — |
| reescritura completa en una pasada | 5.077 | 97,7 % | — | **no funciona** |
| transferencia de registro humano | 5.141 | 64,8 % | 66,0 % | arranque §7bis |
| poda de los dos bloques grandes | 4.535 | 58,6 % | 55,1 % | |
| bloque construido por incrementos | 4.743 | 35,6 % | 37,0 % | Fase 3 |
| segundo bloque por solapamientos | 4.698 | 21,4 % | 28,8 % | Fase 3 |
| reescritura extensa multisección | 4.430 | 21,2 % | 27,9 % | **0,2 puntos: no funciona** |
| reescritura de cuatro solapamientos | 4.343 | 30,0 % | 34,9 % | **empeora** |
| región reconstruida con §4 y anclaje | 4.499 | 14,0 % | 23,0 % | tabla de decisión |
| dos regiones legales con cita verificada | 4.719 | **8,0 %** | 17,5 % | `Mostly Human Written` |

Otro capítulo del mismo lote cerró en `Human Written`, 0 % AI, 4,8 % asistido, global 15,5 %, con
cuota de cita del 18,3 %. Otro caso, ensayo periodístico, fue del 39,8 % al 7,0 % en unas 30
mediciones.

**Lectura:** el progreso viene de **operaciones dirigidas sobre islas** y de **§4**. Cada pasada
masiva que aparece en la tabla está plana o empeora. Si llevas tres intervenciones sin bajar la masa
de palabras `AI-Generated`, no insistas en reescribir: vuelve al diagnóstico y comprueba **§4,
disposición y anclas**.

---

## 19. Ficheros del directorio

Todo lo necesario está en este SKILL.md. Lo demás es material de apoyo, opcional:

- `scripts/step.py` — la sonda del §13, ya extraída a fichero.
- `scripts/perfil.py` — `perfil <texto>` (cadencia, anclajes por párrafo, marcos) · `segmentos <json>`
  (tabla de fragmentos y perfil humano-vs-IA) · `comparar <antes.json> <despues.json>`.
- `scripts/verifica.py` — integridad: tramos humanos intactos, cifras, rayas, cadencia y diff de
  frases desaparecidas.
- `references/marcas-de-ia.md` — catálogo exhaustivo: *Signs of AI writing* (Wikipedia) entero y los
  35 patrones de `/humanizer` en 58 marcas calcadas al español, con etiqueta de fiabilidad
  (`[MEDIDA]`, `[CONVERGENTE]`, `[DELATA]`, `[NO APLICA]`, `[TRAMPA]`), bloque de `grep` de
  artefactos, lista inversa de rasgos humanos y falsos positivos. Se consulta; no se recorre.
- `references/rasgos-medidos.md` — los trece rasgos contables falsados, con lo que costó cada
  comprobación. Útil si te tienta medir un rasgo nuevo.
- `references/caso-autonomos.md`, `caso-tesis.md`, `caso-tesis-2.md`, `caso-tesis-3.md` — las
  mediciones completas de donde salen las constantes de esta skill.

Los scripts usan solo la biblioteca estándar.
