# Caso 2: capítulo de tesis (prosa académica)

Segundo caso medido, y el que sirvió para comprobar que el manual se transfiere de género. Capítulo
2 de una tesis sobre economía política feminista, 1.497 palabras, castellano académico, denso en
citas literales con autor, año y página.

Este caso existe porque la primera versión de la skill se validó lanzándola sobre este texto y **no
alcanzó el objetivo**: se quedó en `AI Detected` con la fracción de IA en 35,9%. Aquella ejecución
destapó tres fallos de herramienta y dos supuestos falsos del manual. Corregidos, una segunda
ejecución llegó a `Human Written` en cuatro mediciones.

## Resultados

| Versión | Veredicto | IA global | frac. IA | frac. asistida | frac. humana | Palabras marcadas |
|---|---|---|---|---|---|---|
| v0 | AI Detected | 59,5% | 68,0% | 14,4% | 17,6% | 1.261 |
| h1 | AI Detected | 36,0% | 15,7% | 12,3% | 71,9% | 403 |
| h2 | AI Detected | 34,7% | 6,7% | 4,7% | 88,5% | 177 |
| h3 | Mostly Human Written | 31,0% | 2,9% | 4,1% | 93,0% | 107 |
| **h4** | **Human Written** | 30,9% | **0,0%** | 4,0% | **96,0%** | 58 |
| h5 | Human Written | 31,3% | 0,0% | 6,6% | 93,4% | 97 (peor, descartada) |

Cuatro mediciones. El texto encogió un 5,7% y no se perdió ni una cita, ni un autor, ni un año, ni
una página, ni un término técnico. Ninguna cifra nueva: en un texto con referencias, una cifra
inventada es una referencia falsa.

Compárese con la ejecución fallida previa: tres mediciones para llegar a 802 palabras marcadas. La
diferencia no fue esfuerzo, fue diagnóstico.

## El discriminador de este texto

Los fragmentos que Pangram marcaba como humanos eran, uno por uno, las frases de **entrega de cita**:
cita literal más referencia, con andamiaje mínimo alrededor. Los marcados eran la prosa de
**síntesis** del autor, la que va entre una cita y la siguiente. Tres formas concretas:

1. El molde «no es X, sino Y», siete veces en el capítulo: «Esta crítica, por lo tanto, no opera como
   un apéndice añadido a posteriori, sino como condición necesaria»; «El género, aquí, no es un
   epígrafe más, sino lo que nos permite…»; «no se mide por el volumen de su gasto sino por la
   medida en que…»; «El paradigma laboralista, por tanto, no es un dispositivo neutro…».
2. Frases que anuncian la tesis antes de exponerla: «Aquí radica el problema central de este
   desanclaje», «Su argumento es que», «Este concepto revela su sesgo en cuanto se examina desde la
   perspectiva de género», «La crítica feminista reconstruye el concepto desde esa grieta».
3. Frases monstruo de 80 a 90 palabras, con la cita enterrada en una subordinada de síntesis.

La primera pasada atacó las tres a la vez y se llevó por delante el 77% de las palabras marcadas.

## Los dos supuestos del manual que este caso rompió

**La cadencia no tiene una dirección universal.** El manual venía del ensayo, donde los tramos
humanos tenían más varianza y más frases cortas que los marcados, y por eso recomendaba meter frases
de 3-6 y de 40-55 palabras. Aquí era al contrario: los tramos humanos tenían media 32,6 y desviación
14,7 con **cero** frases de menos de ocho palabras, y los marcados desviación 21,9 con la mitad de
frases de más de 32 y una de 87. Lo que funcionaba era partir monstruos, no añadir extremos. Seguir
el número del otro texto habría empeorado el resultado. El objetivo sale siempre del propio
documento.

**«¿Tiene este párrafo algún anclaje?» no discrimina en prosa académica.** Aquí todo párrafo cita por
convención disciplinar. El bloque de 594 palabras más marcado del capítulo (72,7%) citaba a Weeks
cuatro veces, a Marshall cuatro y a Lister tres, con página y cita literal. Aun así la densidad sí
discriminaba en términos relativos (13,4 anclajes por 100 palabras en los tramos humanos frente a
7,3 en los marcados), y la pregunta que de verdad separaba era **cómo llega la cita**: entregada casi
literal cuenta, parafraseada dentro de una subordinada de síntesis no.

## Los tres fallos de herramienta que este caso destapó

Vale la pena tenerlos presentes porque los tres daban resultado en verde mientras no comprobaban
nada, que es la peor clase de fallo:

1. `parrafos()` separaba solo por línea en blanco. Un .txt exportado de Word trae los párrafos con un
   solo salto de línea, así que las 1.497 palabras colapsaron en un único párrafo y todo el
   diagnóstico por párrafo quedó inutilizado sin aviso. Ahora hay respaldo por salto simple.
2. `frases_humanas()` descartaba la primera y la última frase de cada fragmento humano para evitar
   los bordes cortados a mitad de palabra. Con fragmentos de una o dos frases, frecuentes en prosa
   densa en citas, no quedaba nada que comprobar: protegía 1 frase de 3 bloques y reportaba verde.
   Ahora mapea cada frase del original al fragmento donde cae su punto medio.
3. La lista de marcos de párrafo era de registro divulgativo y no detectó ni uno de los seis marcos
   académicos que el texto tenía a la vista. Ahora hay dos familias de patrones.

## La regla que unifica los dos casos

Los dos textos, tan distintos, resistían por lo mismo: **la abstracción del propio autor cuando va
sola y sin anclaje**. En el ensayo era una coda de 160 palabras de prescripciones sin un nombre
propio; en la tesis, frases de síntesis suelta entre citas. En los dos, redactarlas mejor no servía
de nada: una reescritura con mejor sintaxis subió del 72,6% al 80,5%.

Las tres salidas, por orden de eficacia medida: disolverla en la frase citada contigua, atribuirla
nombrando al autor dentro de la frase, o anclarla con un referente que ya esté en el texto. Y el
error a evitar, comprobado en los dos casos: **partir una frase huérfana en dos crea otra huérfana y
empeora**. La h5 de este capítulo lo hizo y la fracción asistida subió del 4,0% al 6,6%.

## Procedencia

Septiembre de 2026. Cinco análisis de Pangram para las cuatro versiones más un descarte, unos 75
créditos, más 75 de la ejecución fallida previa. Ficheros de trabajo en
`Documents/Stuff/Pangram/validacion-skill/`.
