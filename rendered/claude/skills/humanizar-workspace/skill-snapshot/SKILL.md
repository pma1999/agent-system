---
name: humanizar
description: Reescribe un texto para que deje de dar positivo en un detector de IA, sin cambiar lo que dice, con un bucle medido contra Pangram y un manual de estrategias ordenado por rendimiento real. Úsala SIEMPRE que se pida humanizar, reescribir o arreglar un texto que da positivo en IA; que un ensayo, TFG, tesis, artículo, informe, post o memoria deje de parecer escrito por IA; que baje el porcentaje de IA de un texto; o que un texto pase como humano en Pangram, GPTZero, Turnitin o similar. También cuando alguien diga que su propio texto le sale marcado como IA, que "le sale positivo", o que quiere que un detector le dé humano. No la uses para detectar autoría sin reescribir (eso es la skill `pangram`), ni para pulir estilo cuando no hay un detector de por medio.
---

# Humanizar un texto frente a detectores de IA

El texto es del usuario y sigue siéndolo. Este trabajo es reescritura real: cambia cómo está
construido el texto, nunca lo que afirma.

Dos cosas que ahorran horas si se asumen desde el principio:

**Lo que detecta el detector es estructura, no vocabulario.** Cambiar palabras marcadas no mueve la
aguja. Lo que la mueve es el molde del párrafo, la densidad de referentes concretos y el perfil de
cadencia. En el caso que originó esta skill, seis redacciones distintas del mismo pasaje puntuaron
todas ~90% porque ninguna tocó la variable estructural.

**Medir, no adivinar.** El detector es la función objetivo. Cada iteración se mide, se atribuye a una
estrategia y se conserva o se descarta. Sin medición se avanza a ciegas y es fácil empeorar: en el
caso original, cuatro iteraciones seguidas de "mejoras" plausibles subieron la puntuación de IA.

## Qué no hacer nunca

Nada de esto está sobre la mesa, ni aunque el usuario lo pida:

- **Inventar hechos, cifras, fechas, fuentes o citas.** Se puede añadir una opinión o una reacción
  del autor si el texto tiene voz propia. Un dato, no. Un detector engañado con datos falsos deja un
  texto peor que el que había, y en un trabajo académico o firmado es un problema serio.
- **Meter erratas, sinónimos raros o caracteres unicode invisibles.** Pangram marca aparte el paso
  por un humanizador automático (`is_humanized`). Para un texto firmado, esa marca es peor que el
  positivo original. Compruébala siempre.
- **Recortar contenido para bajar el porcentaje.** Si algo sobra de verdad, dilo; no lo borres a
  escondidas.

## El bucle

### 1. Medir la base, gratis si se puede

Localiza el cliente: `pangram` en el PATH, o `<repo>/.venv/Scripts/pangram.exe`, o
`.venv\Scripts\python -m pangram_auto`. Comprueba sesión y saldo con `pangram whoami`.

Antes de gastar un crédito, busca si el texto ya se analizó:

```bash
pangram history -s "<una frase literal del texto>" --json
pangram history show <uuid> --json > base.json     # reabrirlo es gratis
```

Si no está, analízalo: `pangram check -f texto.txt --json > base.json`. Cuesta 1 crédito por cada
100 palabras. Por encima de 50 créditos, pide el visto bueno del usuario antes de lanzarlo.

### 2. Diagnosticar con el propio texto

Esta es la parte que más tiempo ahorra y la que casi nadie hace. Un texto mixto trae dentro su propia
muestra de estilo: los fragmentos que el detector marca como humanos son del autor y puntúan bien.
Son mejor referencia que cualquier regla general.

```bash
python <skill>/scripts/perfil.py segmentos base.json
```

Devuelve la tabla de fragmentos y, lo importante, **el perfil comparado**: cadencia de frase de los
tramos humanos frente a los de IA, y densidad de referentes de unos y otros. Eso convierte "varía la
longitud de frase" en un objetivo numérico y "sé más concreto" en un recuento.

Reproducir el perfil del autor es el objetivo, y **cuál es ese perfil cambia con cada texto**. En el
ensayo del primer caso, los tramos humanos tenían desviación 12,0 y un 20% de frases de ocho palabras
o menos, frente a 8,1 y 15% en los marcados: había que romper la meseta de 20 palabras. En el
capítulo de tesis del segundo caso, exactamente al revés, con los tramos humanos en desviación 14,7 y
cero frases cortas frente a 21,9 en los marcados: había que partir las frases de 87 palabras. Aplicar
ahí el número del ensayo habría empeorado el texto.

Si el texto es homogéneo y no hay fragmentos humanos con los que comparar, usa como muestra otro
texto del mismo autor. Si tampoco lo hay, aplica el manual a ciegas y mide.

**Pide una muestra al usuario, al principio y una sola vez:** «¿tienes otro texto tuyo, del mismo
registro, que pase por humano?». Cuesta una frase y puede ahorrar varias iteraciones. En el caso
original, el artículo de referencia que aportó el usuario a mitad de trabajo fue lo que destrabó el
pasaje que llevaba seis intentos fallidos. Léelo antes de reescribir y trátalo como autoridad sobre
cualquier regla genérica de estilo, incluida la de las rayas.

### 3. Reescribir aplicando el manual entero de golpe

Aquí está el atajo, y es lo que separa esta skill de improvisar. Las estrategias de la sección
siguiente ya están validadas y son compatibles entre sí: aplícalas todas a la vez, a todas las zonas
marcadas, en la primera pasada. El método de una variable por iteración es para investigar, y esa
investigación ya está hecha; solo se vuelve a él si queda residuo que no cede.

Por cada zona marcada, en este orden:

1. Borra los marcos de párrafo y las frases-conclusión que localizó el diagnóstico. Abre por el hecho,
   o por la cita si el texto cita.
2. Busca las frases y los tramos que son abstracción tuya sin anclaje y sin compañía. Anclarlos,
   atribuirlos o disolverlos en la frase contigua que sí lleva el referente, con material que ya esté
   en el texto. Nunca inventando uno.
3. Mira si el tramo termina el documento. Si es así, revísalo con especial cuidado: es la posición
   más expuesta, porque solo puede estar rodeada por un lado.
4. Acerca la cadencia al perfil objetivo **en la dirección que marque el diagnóstico**, que según el
   género será meter extremos o partir monstruos.
5. Pasa a verbos las enumeraciones de sustantivos abstractos, y deshaz las cadenas de aposiciones que
   glosan el mismo concepto dos y tres veces.
6. Relee lo escrito buscando el patrón nuevo que acabas de introducir sin querer: frases consecutivas
   con la misma estructura, o una frase huérfana recién creada al partir otra. Este paso se salta con
   facilidad y es el que más caro sale.

No toques los fragmentos que puntúan humanos. Funcionan; cualquier cambio ahí es riesgo puro.

### 4. Verificar antes de pagar

```bash
python <skill>/scripts/verifica.py original.txt nueva.txt --base base.json
```

Comprueba en segundos que los fragmentos humanos siguen intactos, que no falta ni sobra ninguna
cifra, que no hay rayas ni guiones largos (salvo que el autor los use), que la cadencia sigue en el
perfil objetivo y qué frases del original han desaparecido. Un análisis lanzado con la cadencia
desviada es un crédito tirado.

### 5. Medir, atribuir, decidir

```bash
pangram check -f nueva.txt --json > v1.json
python <skill>/scripts/perfil.py segmentos v1.json
```

Compara con la versión anterior tres cosas: el veredicto, `fraction_ai` y **cuántas palabras quedan
marcadas**. La última es la que mejor indica el progreso, porque el porcentaje global se mueve poco
mientras el bloque marcado se encoge.

Si mejora, sigue desde ahí. Si empeora, **vuelve a la mejor versión, no a la última**. Encadenar
ediciones sobre una versión que empeoró es la forma más rápida de perder una tarde.

Con el manual aplicado entero desde el principio, lo normal son dos o cuatro mediciones. Si llevas
tres intentos sobre el mismo bloque y no se mueve, deja de afinar la redacción: el problema es de
otra clase. Vuelve al diagnóstico y pregúntate qué variable no has tocado todavía, que casi siempre
es la densidad referencial o la longitud del tramo abstracto.

## Las estrategias, por orden de rendimiento

### 1. Destemplar el párrafo

La palanca más grande, con diferencia. Los párrafos generados siguen un molde: frase que anuncia el
dato, dato, frase que interpreta el dato. Los párrafos humanos entran directos por el dato y meten el
juicio dentro de una aposición o una subordinada, no en oración propia.

Quita la frase-marco y la frase-conclusión. Abre por el hecho. Si el autor opina, que opine dentro de
un sintagma.

> «Los números del RETA reflejan muy bien esta mezcla. Julio de 2026 cerró con 3.472.357 afiliados.
> (…) Si miramos el conjunto de los datos, el resultado es que solamente uno de cada siete encaja
> con la idea clásica del creador de empleo.»
>
> → «Julio de 2026 cerró con 3.472.357 afiliados al RETA. (…) Juntad las dos cosas y solo uno de
> cada siete afiliados encaja de verdad con la idea clásica del creador de empleo.»

Marcos típicos que hay que borrar: *los datos reflejan / muestran*, *si miramos / si repasamos*, *a
pesar de estos contrastes*, *las estadísticas nos enseñan*, *la idea de fondo es*, *la explicación es
sencilla*, *conviene señalar*, *cabe destacar*, *resulta llamativo*, *en este sentido*, *como
veremos*, *esto pone de manifiesto*, *lo que demuestra que*.

### 2. La abstracción huérfana

Esta es la regla que explica los dos casos medidos, y la que más iteraciones ahorra:

> **La prosa que el detector marca es la abstracción del propio autor cuando va sola y sin
> anclaje.** No importa cómo esté redactada.

Los anclajes concretos (nombre propio, fecha, cifra con fuente, cita literal) separan los dos lados
de forma consistente: en un ensayo, 8,6 anclajes por 100 palabras en los tramos humanos frente a 4,8
en los marcados; en un capítulo de tesis, 13,4 frente a 7,3, con los nombres propios casi
cuadruplicando (3,4 frente a 0,8). Dos géneros muy distintos, la misma proporción.

Lo que está medido es que **redactar mejor una frase huérfana no la salva**. En el caso de la tesis,
una frase de síntesis sin anclaje se reescribió con mejor sintaxis y subió del 72,6% al 80,5%. Solo
hay tres salidas, y todas consisten en que la frase deje de estar huérfana:

- **Anclarla.** Meterle un referente concreto que ya esté en el texto: una fecha, un nombre, una cita.
- **Atribuirla.** Que el autor citado aparezca dentro de la propia frase. «Marshall hace de ese
  elemento social un principio igualador» bajó veinte puntos respecto a «Ese elemento social opera
  como principio igualador».
- **Disolverla.** Que pase a ser subordinada o aposición de la frase contigua que sí lleva la cita.
  Es la más eficaz de las tres: aplicada a las dos últimas frases resistentes, llevó el documento de
  `Mostly Human Written` a `Human Written` con la fracción de IA a cero.

Y el error que hay que evitar: **nunca arregles una frase huérfana partiéndola en dos.** Creas otra
huérfana y empeora. Comprobado dos veces, en los dos textos.

Dos corolarios sobre los tramos largos:

- **Un tramo abstracto contiguo se marca por serlo, y cuanto más largo, peor.** Partir en dos un
  párrafo abstracto alargó el tramo y subió la puntuación.
- **El final del texto es el sitio más expuesto**, porque solo puede estar rodeado por un lado. Si la
  conclusión resiste, cierra con material referencial (una fecha, una cita, un dato que vuelve) en
  lugar de con prescripciones o moralejas en abstracto. Eso desbloqueó el caso del ensayo: de 90% a
  absorberse en el bloque humano.
- **Repetir una cifra ya citada no cuenta como anclaje.** Lo que puntúa son nombres propios, fechas y
  citas, no números sueltos traídos de vuelta.

### 3. Cadencia, con el número del propio documento delante

Ajusta la distribución de longitud de frase al perfil que devolvió el diagnóstico, y **solo a ese**.

No existe un perfil humano universal, y suponerlo lleva en dirección contraria. Medido: en un ensayo
periodístico los tramos humanos tenían más varianza que los marcados (desviación 12,0 frente a 8,1) y
más frases cortas, así que había que romper la meseta de 20 palabras metiendo frases de 4 y de 50. En
un capítulo de tesis del mismo usuario, los tramos humanos tenían **menos** varianza (14,7 frente a
21,9), ninguna frase de menos de 8 palabras y la mitad de frases monstruo; ahí lo que funcionaba era
partir las frases de 80 palabras, no añadir extremos.

Si el lado humano tiene menos de una docena de frases, el perfil es orientativo: sigue la dirección,
no persigas el decimal. Y en cualquier caso es condición necesaria y nunca suficiente: hubo una
versión que clavó la desviación del autor y seguía al 92%. Cuando la cadencia y el destemplado
compiten, gana el destemplado.

### 4. Desnominalizar

Las enumeraciones de sintagmas nominales abstractos son un imán. Pásalas a verbos y cuélgale a cada
elemento su anclaje concreto.

> «Una cotización repartida, el derecho a negociar en bloque y una prestación por cese…»
>
> → «pagar la cotización entre tres, como en Alemania desde 1983; poder firmar un convenio
> colectivo, como permite la Comisión desde 2022; y que cerrar el negocio deje de presumirse culpa
> tuya»

### 5. Las manías del autor

Sácalas de sus fragmentos humanos y respétalas: cifras repetidas en letra («son más de cuarenta y
siete mil casos»), párrafos que terminan sin punto, comillas angulares, apelación directa al lector,
paréntesis con datos en crudo, coletillas redundantes («y eso contando solo los que se descubrieron»).
Si el usuario aporta otro texto suyo como referencia, léelo antes de reescribir: manda sobre
cualquier regla de estilo genérica, incluida la de las rayas.

## El género manda sobre el manual

Las cinco palancas son propiedades del texto y funcionan en cualquier género. Los **números** no se
transfieren, y las tácticas concretas tampoco. Antes de reescribir, sitúa el texto:

- **Ensayo, columna, post.** Cabe la voz: primera persona, apelación al lector, registro coloquial,
  párrafos que terminan sin punto. Ahí el destemplado se hace quitando la frase que anuncia el dato.
- **Tesis, paper, informe técnico, memoria.** La voz no cabe y forzarla estropea el texto. Aquí el
  destemplado tiene una forma propia y muy productiva: **entregar en vez de sintetizar**. En un
  capítulo de tesis medido, los fragmentos que puntuaban humanos eran exactamente las frases de
  entrega de cita (cita literal más referencia, andamiaje mínimo) y los marcados eran la prosa de
  síntesis del autor entre una cita y la siguiente. Así que: las frases que anuncian una tesis antes
  de exponerla («aquí radica el problema central», «su argumento es que», «X, por tanto, no es un
  dispositivo neutro sino…») se sustituyen por la exposición directa; la cita entra primero y el
  juicio del autor viaja detrás, como subordinada de la misma frase; y la cita cierra la frase mejor
  que a mitad. Una sola pasada con esto bajó la fracción de IA del 68% al 15,7%.
  Autores, años, páginas, comillas y terminología técnica son intocables: son el anclaje. No añadas
  una referencia ni un localizador de página para dar anclaje a una paráfrasis tuya: eso es
  inventarse una cita.
- **Texto legal, contractual o normativo.** Casi todo lo anterior sobra. Aquí manda la fidelidad;
  si el texto tiene que decir lo que dice, dilo y no lo humanices.

Mantener el registro no es una concesión estética. Un capítulo de tesis que suena a columna de
opinión está peor que antes, aunque el detector diga humano.

## Errores que cuestan iteraciones

Todos estos se probaron y todos empeoraron el resultado:

- **Voz y coloquialismos sin destemplar antes.** Primera persona, apelación al lector y registro
  coloquial aplicados a un bloque con el molde intacto lo dejaron en 85%. Sin destemplar, la voz es
  maquillaje.
- **Arreglar un patrón de IA creando otro.** Al sustituir aforismos por mecanismos concretos salieron
  tres frases con estructura idéntica («Una X que Y no Z»), que es justo lo que el detector castiga.
  Subió de 23% a 29%. Antes de dar por buena una reescritura, léela buscando el patrón nuevo que
  acabas de introducir.
- **Perseguir el paralelismo sintáctico.** No era la variable. Un párrafo con tres declarativas
  paralelas puntúa humano si cada una lleva cifra y nombre; el mismo paralelismo en abstracto se
  marca.
- **Mover prosa abstracta a una zona concreta.** Contamina la zona sana y la arrastra al bloque
  marcado, además de no arreglar el original.
- **Alargar por subordinar.** Convertir declarativas cortas en frases largas subordinadas empeoró y
  además sacó la cadencia del perfil del autor.

## Reglas de método para el residuo

Cuando el manual completo no limpia un bloque, se pasa a experimentar. Ahí:

- **Una variable por iteración.** Si cambias dos cosas y mejora, no sabes cuál fue.
- **Mira el mapa completo en cada medición, no solo la zona que editaste.** Cada análisis resegmenta
  el documento entero, así que un fragmento puede cambiar de etiqueta por lo que tiene al lado. Todas
  las regresiones observadas hasta ahora se explicaron por texto realmente editado; una ejecución
  reportó además un cambio de etiqueta a distancia, en un párrafo intacto, y **ese caso no se ha
  reproducido**, así que trátalo como posible y no como establecido. Sea como sea, mirar el mapa
  entero es gratis: `perfil.py comparar antes.json después.json` señala qué fragmentos cambiaron y
  cuáles caen fuera de lo que tocaste.
- **Si aparece un cambio lejos de tu edición, vuelve a una variable por iteración.** «Dos zonas, dos
  datos» sirve mientras las atribuciones salen limpias; en cuanto una no lo es, desenredarla cuesta
  más mediciones de las que ahorró.
- **Deja un control sin tocar.** Un fragmento marcado que no modificas confirma si la mejora es
  causal o ruido.
- **El detector es determinista.** Medir dos veces el mismo texto da el mismo resultado bit a bit
  (comprobado). No gastes un análisis de control para descartar ruido: si cambió, lo cambiaste tú.

## Criterio de aceptación

El objetivo es `verdict: Human Written`, `fraction_ai` a 0, todos los fragmentos etiquetados `Human`
y `is_humanized: false`.

La probabilidad global (`ai_likelihood`) no baja a cero y no tiene por qué. Repórtala como lo que es:
«veredicto Human Written, 0% del texto marcado como IA, 15% de probabilidad global, sin marca de
humanizador». Decir solo «100% humano» exagera.

Si el usuario pidió un mínimo (por ejemplo 90% humano) y ya está alcanzado pero queda un fragmento
etiquetado como IA, dilo y pregunta si quiere seguir: cada iteración cuesta créditos.

## Cuando hay que tocar la estructura

Puede llegar un punto en que lo único que queda por cambiar sea cómo está organizado el texto: con
qué termina, en qué orden van las secciones. En el caso original ese fue el paso decisivo.

Eso ya no es reescritura, es edición. Explícale al usuario qué cambio propones y por qué, y déjale
decidir. Lo demás se puede hacer sin consultar; esto no.

## Sin detector disponible

Si no hay sesión de Pangram, créditos o conexión, el manual se aplica igual, solo que a ciegas.
`perfil.py perfil texto.txt` calcula sin coste la cadencia, marca los párrafos sin ningún anclaje
referencial y localiza los marcos de párrafo típicos. Es un sustituto razonable del diagnóstico.
Dilo claramente: sin medición no hay garantía de resultado.

Si el detector que le importa al usuario es otro (GPTZero, Turnitin, ZeroGPT, Copyleaks), el manual
vale igual, porque las tres palancas son propiedades del texto y no de un modelo concreto. Lo que
cambia es el bucle: pídele que pase cada versión por su herramienta y te traiga el resultado, y usa
`perfil.py perfil` para decidir dónde tocar mientras tanto.

## Al terminar

Entrega el texto y, en el mismo mensaje, lo que el usuario necesita saber para publicarlo:

- Veredicto y reparto, con la lectura honesta de la sección de aceptación.
- Cuánto ha encogido el texto y qué se ha eliminado.
- Cualquier cambio estructural o editorial que hayas hecho.
- Las afirmaciones del original que no aparecen literales en la versión final, comprobando una por
  una que su contenido sigue vivo en algún sitio. **Comprobar cifras no es comprobar afirmaciones**:
  en el caso original el control de cifras estaba en verde y aun así una reescritura se había llevado
  por delante el criterio central del ensayo, que no contenía ningún número. `verifica.py` lista las
  frases desaparecidas; recórrelas.

Guarda cada versión (`v0-original.txt`, `v1.txt`, …) y su JSON. Si hay que volver atrás, y suele
haberlo, sin las versiones no se puede.

## Ficheros

- `scripts/perfil.py` — `perfil <texto>` (cadencia, anclajes por parrafo, marcos) · `segmentos <json>` (tabla de fragmentos y perfil humano-vs-IA comparado) · `comparar <antes.json> <despues.json>` (que fragmentos cambiaron de etiqueta, y cuales lejos de lo que editaste).
- `scripts/verifica.py` — integridad: tramos humanos intactos, cifras, rayas, cadencia y diff de frases desaparecidas.

Los dos usan solo la biblioteca estandar, asi que sirve cualquier Python 3. Si `python` no esta en
el PATH, tira del interprete del entorno donde este instalado `pangram-auto`.

Dos bitacoras con la evidencia detras de cada recomendacion. Leelas si el texto se resiste y quieres
ver que se probo ya, o si dudas de una recomendacion y quieres los numeros:

- `references/caso-autonomos.md` — ensayo periodistico de 2.141 palabras, 13 mediciones. De donde
  salen las cinco palancas, y las estrategias que se probaron y fallaron.
- `references/caso-tesis.md` — capitulo de tesis de 1.497 palabras, prosa academica densa en citas,
  4 mediciones. Que se transfiere entre generos y que no, y la regla de la abstraccion huerfana.
