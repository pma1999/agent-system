# Catálogo completo de marcas de escritura de IA

Referencia exhaustiva. Cubre **el catálogo entero** *Signs of AI writing* de Wikipedia (WikiProject
AI Cleanup, revisión de septiembre de 2026: todos sus apartados, incluidos los inútiles, los
históricos y los inversos) y **los 35 patrones** de la skill `/humanizer`, refundidos en **58 marcas
numeradas** más tres apartados finales, calcados al español y cruzados con lo que hemos medido
nosotros contra Pangram. Varios apartados del catálogo se agrupan en una sola marca cuando describen
la misma cosa: los cinco de artefactos de herramienta son la marca 50, los cinco de resúmenes de
edición son la 56.

No sustituye a `SKILL.md`. El procedimiento, las constantes y las operaciones están allí. Esto sirve
para **tres cosas concretas**:

1. **Localizar** qué falla dentro de un tramo que el detector ya ha marcado (§8.2 de `SKILL.md` trae
   las veintidós marcas rentables; aquí están todas, con el porqué).
2. **Calcar al español**: varias marcas del catálogo inglés no transfieren y **dos son peligrosas**
   aplicadas literalmente a prosa académica en español. Están señaladas.
3. **Barrer artefactos** con el bloque de `grep` del apartado F: inequívocos, gratis y sin gastar
   un crédito.

---

## Cómo se usa esto, y cómo no

> «**Please do not merely treat these signs as the problems to be fixed; that could just make
> detection harder.** The actual problems are those deeper concerns.»
> — *Wikipedia:Signs of AI writing*, párrafo de apertura

Esa advertencia es del propio catálogo y coincide con nuestras mediciones. Repasa antes de abrir
este fichero:

- **Una pasada de caza-marcas sobre todo el texto sale peor.** Medido cuatro veces. El mismo tramo
  de 47 palabras fue del 80,4 % al 88,9 % al reformularlo dos veces; la v7 de la tesis 5, reescrita
  entera a mano por patrones, dio **30 % IA** frente al 21,2 % de la v6 que sustituía. Lo que
  funcionó en ese mismo tramo fue **subordinar** el contenido: 0 % IA.
- **La reparación es estructural: poda, subordina o traslada, tejiendo.** No sustituyas palabras.
  Cambiar *subraya* por *pone de relieve* no mueve nada; borrar la oración que interpreta el dato,
  sí.
- **Añadir marcas no crea limpieza y quitarlas de un texto limpio lo rompe.** Sobre un bloque humano
  al 0 % IA, quitar las comas de especificación lo llevó al **100 % IA** conservando todas las
  afirmaciones. En sentido inverso, meter cifras y comas en prosa marcada la dejó igual o peor. Los
  rasgos son correlatos, no causas manipulables.
- **Una marca suelta no prueba nada.** Los textos humanos de referencia llegan a 3,0 «no X sino Y»
  por mil palabras. Lo que cuenta es la **acumulación dentro del mismo tramo marcado**.
- **Nunca dentro de una cita literal, un título o un nombre propio.** La marca ahí es del autor
  citado y tocarla es falsear la fuente.

### Etiquetas de fiabilidad

Cada marca lleva una. Sin ellas la referencia engaña: haría gastar créditos persiguiendo *subraya*
con la misma convicción que «no X sino Y», que es la única con separación limpia medida.

| Etiqueta | Qué significa |
|---|---|
| `[MEDIDA]` | Verificada en nuestro corpus con Pangram: al quitarla se movió la etiqueta o el porcentaje. Cada entrada dice **qué medición exacta** la respalda y si se midió sola o en lote con otras. |
| `[CONVERGENTE]` | El catálogo y la bibliografía la dan por buena y **coincide** con tramos que Pangram nos marcó, pero no la hemos aislado. Trátala como hipótesis fuerte, no como ley. |
| `[DELATA]` | No ha causado la etiqueta en ninguna medición de prosa académica, pero revela el origen a un lector humano y es gratis quitarla. |
| `[NO APLICA]` | Propia de Wikipedia o del inglés. Documentada por exhaustividad; en una tesis en español no existe. |
| `[TRAMPA]` | **Aplicarla literalmente en español degrada el texto.** Lee la entrada antes de tocar nada. |
| `[CONTEXTO]` | No es una marca que retirar: es algo que hay que saber al leer el resto. |

### El mecanismo, en una frase

Un LLM estima lo siguiente más probable sobre un corpus enorme, así que **regresa a la media**:
sustituye el hecho específico, raro y matizado por la descripción genérica y positiva que encaja en
el mayor número de casos. «El inventor del primer enganche ferroviario» se convierte en «un titán
revolucionario de la industria». El sujeto se vuelve a la vez **menos específico y más
exagerado**. Casi todas las marcas de los apartados A y B son manifestaciones de esa única cosa.

---

## A. Marcas de contenido

Las más rentables. Aquí es donde cae la etiqueta en prosa académica.

### 1. Importancia, legado y tendencias infladas · `[CONVERGENTE]`
`WP:AILEGACY` · `WP:AITREND` · `/humanizer §1`

**Qué es.** Se afirma que un detalle cualquiera marca un cambio de época, prueba un legado o refleja
una tendencia más amplia. Hay un repertorio corto y muy identificable de fórmulas para decirlo. El
modelo lo hace incluso con una etimología o un dato de población, y a veces añade un preámbulo que
reconoce que el asunto es menor **y habla de su importancia igualmente**.

**En español.** *marca un hito* · *supone un punto de inflexión* · *constituye un testimonio de* ·
*desempeña un papel crucial / decisivo / fundamental* · *subraya la importancia de* · *refleja una
tendencia más amplia* · *deja una huella indeleble* · *sienta las bases de* · *se inscribe en un
movimiento más amplio* · *abre un debate sobre* · *suscita interrogantes acerca de* · *panorama en
evolución* · *profundamente arraigado*.

**Arreglo.** Di el hecho y córtalo ahí.

> La creación del Instituto de Estadística de Cataluña en 1989 **marcó un momento decisivo en la
> evolución de la estadística regional en España** y **se inscribió en un movimiento más amplio** de
> descentralización administrativa.
>
> → El Instituto de Estadística de Cataluña se creó en 1989, dentro de la descentralización
> administrativa que España emprendió esos años.

**Qué la respalda, y qué no.** La reconocemos en casi todos los tramos que Pangram nos marcó, y el
catálogo la documenta con abundancia. Pero **no la hemos aislado nunca**: no hay ninguna medición
en la que quitar solo esto moviera un número. Por eso es `[CONVERGENTE]` y no `[MEDIDA]`. En la
práctica cae de todas formas, porque la frase que la contiene suele ser también un cierre
sentencioso (marca 7) o un marco de párrafo (marca 19), y esas dos sí están medidas.

### 2. Notabilidad, atribución y cobertura de catálogo · `[CONVERGENTE]`
`WP:OVERATTRIBUTION` · `WP:AIATTR` · `/humanizer §2`

**Qué es.** El modelo demuestra que algo importa **enumerando dónde se ha hablado de ello** y
clasificando esas fuentes, en vez de resumir qué dicen. El foco se desplaza de la afirmación a las
características de la fuente: su independencia, su alcance, su disponibilidad. Muy característico de
los modelos de 2025 en adelante.

**En español.** *cobertura independiente* · *medios locales / regionales / nacionales* ·
*publicaciones especializadas* · *ha sido citado / recogido / perfilado en* · *escrito por un
experto de referencia* · *mantiene una presencia activa en redes*.

**En una tesis se presenta así:** «La literatura ha prestado creciente atención a este fenómeno, con
trabajos publicados en revistas de primer nivel», sin decir qué sostiene ninguno de ellos.

**Arreglo.** Sustituye la lista por lo que la fuente afirma, con su atribución. Si no sabes qué
afirma, la frase no aporta y se va. **Esta operación es además la maestra de la skill**: entregar la
frase de la fuente en vez de anunciar que la fuente existe.

### 3. Análisis superficial en gerundio · `[MEDIDA]`
`WP:SUPERFICIAL` · `/humanizer §3`

**Qué es.** Se cuelga del final de una oración un participio de presente que dice qué significa el
dato. Suena a profundidad y no añade información. Es la marca con más respaldo bibliográfico
(Reinhart et al., *PNAS* 2025) y una de las que más veces hemos visto dentro de un tramo marcado.

**Qué la respalda.** Entró en dos intervenciones medidas, siempre **en lote con otras dos o tres
marcas, nunca sola**: con la cadena de razonamiento y el anuncio de recuento, **162 → 152** palabras
IA; después, rompiendo la cadena y devolviendo el autor como sujeto, **152 → 123** y el veredicto de
`AI Detected` a `Mostly Human Written`. No sabemos cuánto de esa mejora es suya.
Los modelos con búsqueda la atribuyen además a una fuente con nombre **diga esa fuente lo que
diga**.

**En español.** *subrayando…* · *reflejando…* · *poniendo de manifiesto…* · *contribuyendo a…* ·
*garantizando…* · *simbolizando…* · *fomentando…* · *abarcando…* · *evidenciando…* · *lo que
permite…* · *aportando valiosas claves…*, colgado de un dato.

**Arreglo.** Corta el gerundio. Si lo que dice hace falta, ponlo como oración propia con su
atribución; casi nunca hace falta.

> La paleta de azul, verde y oro **resuena con la belleza natural de la región**, simbolizando las
> flores de Texas y el Golfo de México, **reflejando la profunda conexión de la comunidad con su
> tierra**.
>
> → El templo se pintó de azul, verde y oro, colores elegidos por las flores silvestres de Texas y
> el Golfo de México.

### 4. Lenguaje promocional · `[CONVERGENTE]`
`WP:AIPUFFERY` · `WP:AIPEACOCK` · `/humanizer §4`

**Qué es.** Aunque se le pida registro enciclopédico, el modelo deriva a texto de folleto. Ocurre
sin que nadie intente promocionar nada, y es peor con lugares, cultura, productos e instituciones.
Los modelos antiguos eran descaradamente positivos; los nuevos son positivos de forma más sutil y
evitan el superlativo abierto.

**En español.** *cuenta con* (por «tiene») · *vibrante* · *rico* (figurado) · *profundo* ·
*enclavado en* · *en el corazón de* · *de una belleza singular* · *revolucionario* (figurado) ·
*de renombre* · *un amplio abanico de* · *apuesta firme por* · *compromiso con* · *pone en valor*.

**Dos subtipos del catálogo.** (a) Cuando el asunto puede leerse como «patrimonio», el modelo
recuerda su importancia en cada párrafo. (b) Con personas y empresas adopta tono de nota de prensa:
*el consejero delegado destacó el compromiso de la compañía con la sostenibilidad*.

**En una tesis** se presenta como entusiasmo por el propio marco teórico: *un marco especialmente
fecundo*, *una aportación de enorme calado*.

**Arreglo.** Estado de cosas en indicativo, sin adjetivo evaluativo.

### 5. Fuentes vagas y opiniones generalizadas · `[CONVERGENTE]`
`WP:AIWEASEL` · `/humanizer §5`

**Qué es.** Se atribuye la afirmación a una autoridad sin nombre, y además se exagera cuántos la
sostienen: se presenta la opinión de uno o dos como generalizada, se habla de «varios autores»
citando a uno, o se sugiere que una lista de ejemplos es abierta cuando la fuente no dice tal cosa.

**En español.** *los expertos señalan* · *algunos críticos sostienen* · *diversos informes apuntan* ·
*se ha señalado que* · *la literatura coincide en* · *numerosos estudios demuestran* · *es
ampliamente aceptado que* · *tal y como* delante de una enumeración que se presenta como exhaustiva.

**Arreglo.** Nombra la fuente real, o retira la afirmación. **Nunca inventes una fuente ni una
cifra**: es la línea roja de la skill y del catálogo por igual.

### 6. Retos y perspectivas de futuro · `[MEDIDA]`
`WP:FACESCHALLENGES` · `/humanizer §6`

**Qué es.** Un apartado de fórmula que empieza «Pese a su [algo positivo], X afronta varios retos…»
y termina en una valoración vagamente optimista o en especulación sobre iniciativas en marcha.
Aparece al final de textos con estructura rígida de esquema, a veces con un «Perspectivas de futuro»
aparte.

**En español.** *Pese a estos avances, subsisten importantes retos* · *No obstante estas
dificultades* · *Retos y perspectivas* · *De cara al futuro* · *queda un largo camino por recorrer*.

**Ojo:** la marca es **la fórmula**, no mencionar dificultades. Una tesis tiene que discutir sus
límites; lo que no puede es cerrar con el molde.

**Arreglo.** Poda. Conserva únicamente la afirmación concreta que no esté ya en otro sitio, y
termina en el último dato útil.

**Qué la respalda.** En la tesis 5, el apartado doméstico pasó de **311 a 132** palabras IA en una
intervención que hizo **dos cosas a la vez**: anclar en el preámbulo literal del RD-ley 16/2022 y
podar esta recapitulación final. Por lo medido en el resto del proyecto, casi toda esa mejora es del
ancla; la poda es la parte pequeña. No la vendas como palanca por sí sola.

### 7. Recapitulaciones y cierres de apartado · `[MEDIDA]`
`WP:CONCLUSION` · `WP:INCONCLUSION` · histórico en el catálogo · `/humanizer §25`

**Qué es.** El modelo cierra párrafos y secciones repitiendo su idea central, y en textos largos
añade un «Conclusión» que no concluye nada. Wikipedia lo clasifica como indicador histórico
(2022-2024) porque los modelos nuevos lo hacen menos; **en nuestros datos sigue vivo y es el residuo
más frecuente**.

**En español.** *En síntesis* · *En resumen* · *En definitiva* · *En conclusión* · *Con todo* ·
*Como se ha visto* · y sobre todo **la frase lapidaria sin marcador** que resume el párrafo que
acabas de leer.

**Arreglo.** Quítala, o sustitúyela por la consecuencia atada a la evidencia.

**Qué la respalda.** Dos cosas distintas, ninguna de ellas un experimento aislado. Una: en el
recuento de residuos de nuestros tramos marcados, el cierre sentencioso es **lo que más veces
queda** cuando ya se ha reparado todo lo demás. Dos: la poda de recapitulaciones formó parte de las
intervenciones tejidas de la serie t16-t31, que bajaron un capítulo de **283 a 176** palabras
marcadas — pero repartidas entre diez operaciones. Es fiable como **dónde mirar**, no como cuánto
rinde.

**Corolario del cierre optimista genérico** (`/humanizer §25`): *el futuro se presenta prometedor*,
*un paso en la dirección correcta*. Fuera el párrafo; el texto termina en el último hecho.

### 8. Encabezado tratado como nombre propio y secciones «X e Y» · `[NO APLICA]`
Wikipedia: leads que definen el título de una lista como si fuera una entidad real («*La «Lista de
canciones sobre México» es una recopilación…*»), y la ubicuidad de apartados titulados «Premios y
reconocimientos» o cualquier «X e Y». En una tesis el equivalente laxo sería un epígrafe genérico
del tipo «Retos y oportunidades»; se trata por la marca 6.

---

## B. Marcas de lengua y gramática

Estas son consistentes con independencia del tema, y es lo que da a la prosa generada una «voz»
reconocible.

### 9. Densidad de vocabulario de IA · `[CONVERGENTE]`
`WP:AIVOCAB` · `WP:AIWORDS` · `/humanizer §7`

**Qué es.** Hay palabras que los modelos usan mucho más que la gente, y **coocurren**: donde hay
una, suele haber más. Está documentado en varios estudios (Juzek & Ward 2025; Kobak et al.,
*Science Advances* 2025; Kousha & Thelwall 2025) sobre resúmenes científicos, y se dispara en los
textos posteriores a 2022. Una o dos son casualidad; un párrafo lleno de ellas es de las señales más
fuertes que existen.

**Léxico por época** (útil para saber si un texto se generó antes o después, no como norma):

| Época | Palabras que se agrupan |
|---|---|
| 2023 – mediados 2024 (GPT-4) | *además*, *cuenta con*, *impulsado*, *crucial*, *ahondar*, *destacando*, *perdurable*, *obtener*, *intrincado*, *interacción*, *clave*, *panorama*, *meticuloso*, *decisivo*, *subrayar*, *tapiz*, *testimonio*, *valioso*, *vibrante* |
| Mediados 2024 – mediados 2025 (GPT-4o) | *alinearse con*, *impulsado*, *crucial*, *destacando*, *potenciar*, *perdurable*, *fomentando*, *decisivo*, *mostrando*, *subrayar*, *vibrante* |
| Mediados 2025 en adelante (GPT-5) | *destacando*, *potenciar*, *poniendo de relieve*, *mostrando*, más el repertorio de la marca 2 |
| Grok, en cualquier época | *causal*, *empírico*, *correlato*, y sigue abusando de *subrayar* en 2026 |

**Cómo se lee esta entrada.** «Tómese lo más literalmente posible», dice el catálogo: que un modelo
abuse de una palabra **no implica que abuse de sus sinónimos**. Y cuenta el contexto: *subrayar* una
línea con un lápiz no es la marca.

**Arreglo.** Palabra llana. Pero lee la marca 30 antes de tocar nada: sustituir léxico **no** ha
movido la etiqueta en ninguna de nuestras mediciones. Esto se arregla al reescribir la frase por
otro motivo, no como pasada propia.

### 10. Huida de la cópula · `[CONVERGENTE]`
`WP:AINOCOPULA` · `WP:AIREPRESENTS` · `/humanizer §8`

**Qué es.** Se sustituye *ser*, *estar* o *tener* por perífrasis más largas y con aire de marketing.
Está observado en modelos GPT y Gemini, y hay un estudio que midió una caída de más del 10 % en el
uso de *is*/*are* en la escritura académica de 2023, sin variación previa. Se ve especialmente en
las «mejoras de estilo» hechas con IA. En los modelos recientes la perífrasis es más elaborada:
*inició su trayectoria como* en vez de *fue*.

**En español, la lista que sí sirve.** *constituye* · *supone* · *representa* · *se erige en* ·
*se configura como* · *funciona como* · *opera como* · *desempeña el papel de* · *viene dado por* ·
*cuenta con* / *presenta* / *ofrece* (por *tiene*) · *hace referencia a* (por *es*, al definir).

**Arreglo.** *es*, *está*, *tiene*, *hay*.

> El artículo 4 **constituye la piedra angular** del régimen y **cuenta con** tres apartados.
> → El artículo 4 es la norma central del régimen y tiene tres apartados.

**Nota.** El *ha sido* del pretérito perfecto no es esta marca. Y *constituye* es correcto y
frecuente en prosa jurídica: la marca es la **acumulación** en un mismo tramo, no una aparición.

### 11. Conexión o asociación vaga · `[CONVERGENTE]`
`WP:AICONNECT` · `WP:AIASSOCIATION` · no está en `/humanizer`

**Qué es.** En vez de decir la relación, se alude a que dos cosas están «relacionadas» o
«vinculadas». «En 2017, fuentes identificaron a X como asociado a la dirección de la empresa» en
lugar de «en 2017, X fue consejero delegado de la empresa». Suele venir acompañada del léxico de las
marcas 4 y 9, y a veces se repite en cada párrafo.

**En español.** *en relación con* · *vinculado a* · *asociado a* · *en conexión con* ·
*particularmente asociado a* · *material relacionado con* · *en el marco de*.

**Arreglo.** Di el verbo y el papel: quién hizo qué, cuándo. Si no lo sabes, la frase no puede
sostenerse.

### 12. Paralelismos negativos · `[MEDIDA]`
`WP:AIPARALLEL` · `/humanizer §9`

**Qué es.** El texto parece corregir un malentendido que nadie ha planteado, o contrasta un rasgo
con otro para dar profundidad. El catálogo distingue tres formas:

- **«no solo X, sino también Y»** — *no solo constituye un instrumento de gestión, sino también un
  mecanismo de control*.
- **«no X, sino Y»** — niega el primer término por completo: *no es un espejo, sino un portal*;
  *no una carrera, no una obra, no una relevancia sostenida: solo un instante algorítmico*.
- **«X más que Y»** — la inversión, típica de Grok: *priorizando la consolidación efectiva del poder
  más que la pureza ideológica*.

**Qué la respalda — es el mejor caso que tenemos.** Dentro de un mismo documento: **0 apariciones en
1.561 palabras de tramos etiquetados humanos frente a 2 en 164 palabras de tramos marcados**.
Separación perfecta. Quitarlos, sin tocar nada más, bajó el peor bloque del **71,8 % al 64,0 %**.
Es lo primero que hay que buscar en un tramo marcado.

**Arreglo.** Afirma el término que sí sostienes y suelta el otro.

> ocupa una fase transitoria, **no** un estado natural → ocupa una fase histórica transitoria

**Aviso de umbral.** Los textos humanos de referencia llegan a **3,0 por mil palabras**. No es un
patrón prohibido: es un patrón que **no puede acumularse** en el tramo que quieres desmarcar.

### 13. Tríadas · `[CONVERGENTE]`
`WP:RO3` · `/humanizer §10`

**Qué es.** Abuso de la regla de tres, del «adjetivo, adjetivo, adjetivo» al «frase corta, frase
corta y frase corta». Se usa sobre todo para que un análisis superficial (marca 3) parezca completo.

**En español.** *un proceso complejo, dinámico y multidimensional* · *el encuentro reúne ponencias,
mesas redondas y espacios de trabajo* · *innovación, inspiración e ideas*.

**Arreglo.** Dos términos si dos bastan, o desarrolla los tres con contenido y atribución propios.
La variante peor es **la enumeración anunciada y no desarrollada**: *el estudio distingue tres
elementos: A, B y C*, y ahí acaba.

### 14. Ciclo de sinónimos (variación elegante) · `[CONVERGENTE]`
`WP:AIELEVAR` · histórico en el catálogo · `/humanizer §11`

**Qué es.** Los modelos con penalización de repetición renombran el mismo referente una y otra vez:
*el protagonista* → *el personaje principal* → *la figura central* → *el héroe*. Está observado
comparando Wikipedia de antes y después de 2023, y en artículos generados con GPT-4o-mini y
Gemini-1.5-Flash.

**Arreglo.** Un nombre estable para cada cosa. En prosa académica española esto importa: llamar
*la norma*, *el texto legal*, *la disposición* y *el precepto* a la misma cosa en cuatro frases
seguidas confunde al lector además de delatar.

**Salvedad del catálogo.** Quien escribe en una lengua que no es la suya también evita repetir; en
la escuela italiana, por ejemplo, se enseña a hacerlo. No es prueba por sí sola.

### 15. Aperturas de frase repetidas · `[CONVERGENTE]`
`/humanizer §11`

**Qué es.** Varias oraciones seguidas empiezan por el mismo sujeto. El modelo gestiona la repetición
por regla, no de oído.

**Arreglo.** Fusiona oraciones, cambia el sujeto o empieza por la acción. **Arregla el patrón, no la
palabra**: la frase resultante puede seguir empezando igual. Y si la repetición tiene función
rítmica deliberada, se queda.

### 16. Rango falso «de X a Y» · `[CONVERGENTE]`
`/humanizer §12`

**Qué es.** *de X a Y* cuando X e Y no forman un rango real, solo dos ejemplos sueltos.

> *desde la singularidad del Big Bang hasta la enigmática danza de la materia oscura*
> → *el Big Bang, la formación estelar y las teorías actuales sobre la materia oscura*

**Arreglo.** Enumera.

### 17. Pasiva y sujetos que desaparecen · `[MEDIDA]`
`/humanizer §13`

**Qué es.** Se oculta quién actúa. En prosa académica española la variante propia es la **pasiva
refleja con sujeto abstracto**: *se observa que*, *el fallo excede a*, *cabe concluir que*.

**Arreglo.** Devuelve el agente, que casi siempre es el autor citado.

> el fallo excede a la redistribución → **Fraser** sitúa el fallo más allá de la redistribución

**Qué la respalda.** Entró, **en lote** con la ruptura de la cadena de razonamiento (marca 18), en
la intervención que llevó un capítulo de **152 a 123** palabras IA y cambió el veredicto de
`AI Detected` a `Mostly Human Written`. Aislada no se ha medido.

**El matiz que decide si funciona.** Devolver el autor como sujeto **tejido** dentro de la frase
rinde; **reescribiendo el párrafo para atribuirlo**, falla, y dos veces: 230 → 374 y 203 → 218
palabras marcadas. Es la misma idea con dos resultados opuestos según cuánto texto muevas.

**No la conviertas en regla ciega.** La pasiva refleja es normativa y frecuentísima en español
académico; erradicarla saca el texto de la banda humana.

### 18. Cadena de razonamiento encadenada · `[MEDIDA]`
Nuestra, no está en ninguno de los dos catálogos

**Qué es.** Una sola oración larga que ensarta premisa, contraste y conclusión con bisagras
lógicas: *…, porque A, mientras B, de modo que C*.

**Arreglo.** Pártela en dos o tres oraciones.

**Qué la respalda.** Dos intervenciones medidas, las dos **en lote**: con el gerundio y el anuncio
de recuento, **162 → 152**; después, rompiendo la cadena y devolviendo el autor como sujeto,
**152 → 123** y cambio de veredicto. Está en la tabla de operaciones de `SKILL.md` §8.2 y aparece en
casi todos los tramos marcados de prosa argumentativa.

---

## C. Molde del párrafo y movimientos retóricos

### 19. El molde del párrafo generado · `[MEDIDA]`
Nuestra

**Qué es.** *Frase que anuncia el dato · dato · frase que interpreta el dato.* Los párrafos humanos
entran directos por el dato y meten el juicio dentro de una aposición o una subordinada, no en
oración propia. Es la marca estructural con más rendimiento que hemos encontrado.

**Marcos que se borran enteros.** *los datos reflejan / muestran* · *si miramos* · *las estadísticas
nos enseñan* · *la idea de fondo es* · *esto pone de manifiesto* · *lo que demuestra que* · y en
registro académico *aquí radica el problema* · *su argumento es que* · *esta distinción es clave*.

**Arreglo.** Destemplar: fuera la frase que anuncia, el dato abre el párrafo, el juicio entra
subordinado.

**Qué la respalda.** El cierre de la tesis 4. Quedaba una isla de 56 palabras al **47,8 %**, justo
en la frontera. Una sola operación tejida — borrar el marco *La pobreza de las mujeres permite
observar la diferencia:* y dejar que el contenido abriera la frase — la llevó a **`Human Written`,
0 % IA**, con puerta de estabilidad 3/3. Es lo más cerca que tenemos de una marca aislada con efecto
limpio, aunque la misma edición deshizo también una alternativa balanceada (marca 12).

### 20. Revelar una verdad honda · `[CONVERGENTE]`
`/humanizer §27`

**Qué es.** Se presenta una observación corriente como si fuera un fondo que el lector no había
visto. La fórmula anuncia profundidad y después dice lo mismo que ya decía la frase anterior.

**En español.** *la verdadera cuestión es* · *en el fondo* · *en esencia* · *en realidad* · *lo que
de verdad importa* · *el problema de fondo* · *el núcleo del asunto* · *queda como lo que es*.

**Arreglo.** La afirmación directa, sin el anuncio.

> queda **como lo que es**, una fase transitoria → es una fase histórica transitoria

**Por qué importa en una tesis.** Es la marca que más se confunde con voz propia: suena a que el
autor toma partido. Pero si al quitar el marco la frase dice exactamente lo mismo, el marco no era
voz, era relleno. Comprueba eso antes de defenderlo.

**Coincide con la marca 7**: casi siempre está en la frase que cierra el párrafo. Si encuentras las
dos juntas, la operación es una sola.

### 21. Frase-cartel que anuncia lo que viene · `[MEDIDA]`
`/humanizer §28`

**Qué es.** Una oración entera cuyo único contenido es avisar de lo que se va a decir. No aporta
información: **ocupa el sitio de la información**. En registro divulgativo aparece como *vamos a
verlo*; en registro académico, disfrazada de método.

**En español.** *Conviene retener esta objeción, porque reaparece más adelante:* · *Veamos ahora* ·
*Analicemos* · *Cabe detenerse en* · *Antes de continuar, conviene precisar* · *Merece la pena
examinar* · *A continuación se expone*.

**Qué la respalda.** Una frase de estas se convirtió en **su propio segmento de 26 palabras al
76,9 %**: el detector la aisló sola y la marcó. Ese es el hallazgo. **Quitarla, en cambio, rinde
poco**: en la serie medida, la versión que solo hacía eso fue de 270 a 269 palabras marcadas. Sirve
para no **crear** tramos marcados nuevos, no para desatascar uno existente.

**Arreglo:** fuera; empieza por el contenido.

### 22. Anunciar el recuento · `[CONVERGENTE]`
Nuestra · emparentada con las marcas 13 y 21

**Qué es.** Antes de enumerar, se dice cuántos elementos vienen. Es la versión en miniatura de la
frase-cartel: gasta palabras en anunciar una estructura que el lector va a ver de todas formas.

**En español.** *de dos maneras a la vez: A y B* · *cabe distinguir tres planos* · *por un doble
motivo* · *responde a dos lógicas*, cuando las dos van justo después.

**Arreglo.** Enumera y ya está.

> gestionada **de dos maneras a la vez**: por A y por B → gestionada por A y por B

**Cuándo se queda.** Si los elementos vienen separados por párrafos o páginas, el anuncio es una
ayuda real al lector y se conserva. La marca es anunciar lo que viene **en la misma frase**.

**Qué la respalda.** Formó parte del lote de tres marcas (con el gerundio y la cadena) que llevó un
capítulo de **162 a 152** palabras IA. Nunca aislada.

### 23. Sentencias formularias · `[CONVERGENTE]`
`/humanizer §32`

**Qué es.** Una afirmación corriente convertida en aforismo mediante una metáfora de molde. Suena
memorable y no aporta ningún detalle nuevo; a menudo sustituye al detalle que faltaba.

**En español.** *X es el Y de Z* · *X se convierte en una trampa* · *el lenguaje de* · *la gramática
de* · *la moneda de cambio de* · *la arquitectura de* · *el reverso de*.

**Arreglo.** La afirmación concreta, con su sujeto y su verbo.

> La simetría es el lenguaje de la confianza. → Las composiciones simétricas suelen resultar más
> predecibles al usuario.

**Ojo con la cita.** En humanidades, la sentencia puede ser **del autor citado**: si la metáfora es
de Fraser o de Bourdieu, es suya, va entre comillas y no se toca.

### 24. Remates dramáticos en serie · `[CONVERGENTE]`
`/humanizer §31`

**Qué es.** Cada oración construida como cierre de efecto, o una ráfaga de fragmentos cortos sin
verbo. Una frase corta enfatiza; una hilera suena a guion.

> Entonces llegó AlphaEvolve. Sin preferencia por la simetría. Sin apriorismo estético. Sin
> nostalgia del gusto humano. Las viejas reglas habían muerto.
>
> → AlphaEvolve cambió la búsqueda porque no favorecía la simetría ni los diseños de aspecto humano,
> lo que restó utilidad a algunos supuestos anteriores.

**Arreglo.** Reúnelos en una oración con contenido.

**Cuándo se queda.** Una sola frase corta para enfatizar, y la repetición con función rítmica
deliberada. Solo cuenta **la hilera**.

### 25. Responder objeciones que nadie ha hecho · `[CONVERGENTE]`
`/humanizer §34`

**Qué es.** El texto se defiende de un reproche que no aparece en ninguna parte. La señal es una
declaración **sin atribuir** sobre lo que el autor *no* quiere decir, sobre todo si ese tema no
vuelve a salir.

**En español.** *no se trata tanto de* · *no estoy diciendo que* · *que quede claro* · *no es que* ·
*conviene no confundir esto con* · *cabría enfocarlo de otro modo, pero*.

**Arreglo.** Retira solo la defensa sin apoyo. Si dentro hay una afirmación real, dila de frente.

**Cuándo se queda — importante en una tesis.** Se conserva la objeción cuando el texto **nombra su
fuente** («frente a lo sostenido por Todolí…») o cuando la responde de verdad. Eso no es la marca:
es discusión académica, y quitarla empobrece el trabajo. Distinguir una de otra es la parte
delicada, y ante la duda **se queda**.

**No confundir** con una afirmación negativa normal: *la norma no es aplicable a los cuidados* es un
hecho, no una defensa.

### 26. Descartar alternativas ficticias · `[CONVERGENTE]`
`/humanizer §35`

**Qué es.** Se introduce una opción que ningún lector se habría planteado, se descarta en una
subordinada y no vuelve a mencionarse. Suele ser el resto fosilizado de un borrador anterior: la
frase registra una decisión de escritura, no una idea.

**En español.** *una opción tentadora sería… pero* · *cabría pensar que…, sin embargo* · *sería
fácil suponer* · *podría objetarse que…, ahora bien* · *un enfoque evidente pasaría por*.

**Arreglo.** La restricción real, dicha de frente.

> Los tokens rotan cada 24 horas. **Una opción tentadora sería** reiniciar el servicio por cron,
> **pero** eso tiraría todas las sesiones. La rotación ocurre en caliente.
>
> → Los tokens rotan cada 24 horas en caliente, y los clientes se refrescan de forma transparente.

**Cómo distinguirla.** Pregunta qué información nueva aporta cada oración. Una sola alternativa
rechazada puede ser legítima — en un apartado metodológico lo es casi siempre —; **varias, cortas y
sin relación entre sí**, es la marca.

### 27. Apertura de falsa franqueza · `[NO APLICA]` en registro académico
`/humanizer §33`

**Qué es.** Una pausa teatral o una declaración de sinceridad antes de decir algo corriente. El
gesto promete confidencia y después no la hay.

**En español.** *Sinceramente…* · *Mira* · *La cosa es que* · *Seamos honestos* · *Vamos a ser
claros* · *Te lo digo de verdad*, usados como gancho aislado.

**Arreglo.** El punto, directo.

> ¿Merece la pena por ese precio? ¿**Sinceramente**? Depende de cuánto lo uses.
> → Que merezca la pena depende de cuánto vayas a usarlo.

**Por qué aquí pone `[NO APLICA]`.** En una tesis no aparece; en un ensayo o un artículo en primera
persona **sí puede ser voz del autor**, y entonces se respeta. Lo que delata es el arranque teatral
aislado, no la palabra: un *sinceramente* en mitad de una frase es prosa normal.

### 28. Relleno · `[TRAMPA]` — lee la nota
`/humanizer §23`

*con el fin de lograr este objetivo* → *para* · *debido al hecho de que* → *porque* · *en este
momento* → *ahora* · *tiene la capacidad de* → *puede* · *es importante señalar que los datos
muestran* → *los datos muestran*.

**La trampa.** El apartado *Signs of human writing* del propio catálogo dice lo contrario: sobre
25 años de Wikipedia, las construcciones **largas y algo torpes** (*como resultado de*, *con el fin
de*, *todos los*, *el hecho de que*) son **más frecuentes en lo escrito por humanos** que en lo
generado. Ambas cosas son verdad y se resuelven así: lo que delata es **el marco formulario**
completo (*es importante señalar que…*) y **el apilamiento**; un *con el fin de* suelto es prosa
humana normal. Nosotros medimos el precio de erradicarlos: la zona quedó en **0 marcas por mil
palabras**, un extremo que no tiene ningún texto humano, y volver a meterlos después **no lo
arregló** (451 → 548 palabras marcadas). **Quita el marco, deja el conector.**

### 29. Matizadores apilados · `[TRAMPA]` — misma nota
`/humanizer §24`

*podría posiblemente argumentarse que* · *cabría sostener, hasta cierto punto, que* · *en algunos
casos podría* · *es igualmente posible*. La marca es la **cadena** de cautelas que repara una
afirmación anterior demasiado fuerte.

**La trampa.** El catálogo registra los matizadores e intensificadores (*muy*, *quizá*, *tiende a*)
como **más frecuentes en escritura humana**. Conserva el matiz que la fuente sostiene; elimina solo
la cadena.

### 30. Escribir sobre la versión anterior · `[NO APLICA]`
`/humanizer §30`

Documentación y comentarios que describen lo que había antes en vez de lo que hay. Solo tiene
sentido en un registro de cambios. En una tesis no aparece; en el `SKILL.md` sí importa cuando el
agente redacta informes.

---

## D. El dial de la voz

### 31. Metadiscurso: se mide y se ajusta en los dos sentidos · `[MEDIDA]`
Nuestra

Los dos casos donde más rindió apuntan en direcciones **contrarias**, así que no hay regla: hay
dial.

| Texto | Voz medida | Qué funcionó | Resultado |
|---|---|---|---|
| capítulo sin nadie dentro | 0,00 marcas/1000 | **meterla** | 283 → 206 palabras marcadas |
| sección ahogada en metadiscurso | **20,90**/1000 (banda 1,62-5,51) | **quitarlo** | 3081 → 2020 IA en una pasada |

**Banda objetivo: 0,9-2,0 marcas por 1.000 palabras.** Mide antes de decidir la dirección, y nunca
apuntes al extremo.

**Qué la respalda.** Es la marca mejor medida del proyecto junto con la 12, y la de mayor palanca
absoluta. El modelo nulo (brecha entre clases dividida por dispersión entre humanos) da **7,90**,
frente al umbral de 1,5 y al 1,26 de la longitud de frase, que separaba con solapamiento cero y aun
así no movió nada. Los cuatro capítulos humanos de referencia caen en 1,62-5,51 por mil palabras; el
capítulo marcado, en 20,90. Y las dos intervenciones de la tabla se midieron aisladas.

**Cómo medirlo sin engañarte.** Un regex escrito después de leer el texto recoge *sus* modismos:
mide tu lectura, no el texto. Usa **clases gramaticales cerradas**: posesivos de primera persona ·
clíticos *nos*/*me* · verbos en `-amos`/`-emos`/`-imos` · autorreferencia al texto (*este apartado*,
*el capítulo 8*) · andamiaje ordinal (*en primer lugar*, *por último*). Medido así, un texto daba
20,90; con el regex amañado a mano, 11,16. **La medida honesta separaba casi el doble.**

**Descuenta lo que el género de la referencia no puede tener.** Una tesis dice «como se verá en el
capítulo 8»; un capítulo de libro publicado no puede decirlo nunca. Descontado, un texto pasaba de
7,70 (fuera de banda) a 5,58 (dentro).

**Dosis y forma.** Tejida dentro de una frase que además dice algo (*Ningún país, conviene
precisarlo, encarnó el modelo puro*), nunca como frase suelta (marca 21). Tres marcas en 100
palabras salieron peor que una. Al quitar, quita el anuncio y **deja la referencia cruzada**: *lo
abordaremos en el capítulo 8* lleva información y el lector de una tesis la necesita.

### 32. La trampa del conector · `[MEDIDA]` · **la más importante de este fichero**

El catálogo pone *Additionally* entre las palabras que más abusa la IA, y es cierto **en inglés y al
principio de frase**. Trasladado a *además* como norma de borrado, hace daño medible.

**No se tocan las bisagras de una o dos palabras:** *así* · *además* · *sin embargo* · *no obstante*
· *en este sentido* · *por su parte* · *en consecuencia* · *por ello* · *frente a* · *asimismo*.

**Por qué.** Cuatro capítulos académicos verificados como humanos van llenos de ellos: en dos, el
**71 % y el 53 % de las frases abren con conector**. Borrarlos junto con los marcos de la marca 19
dejó las zonas reescritas en 0 marcas por mil palabras, un extremo que no tiene ningún texto humano,
y **reponerlos después no lo arregló** (451 → 548).

Se borra **el marco de oración entera** (marca 19), no la bisagra.

**Qué la respalda.** Tres medidas independientes. Una: el conector de discurso como rasgo contable
quedó **descartado** en la batería — separaba en la comparación externa, pero la intervención no
tuvo efecto. Dos: los cuatro capítulos humanos verificados van llenos de ellos, y en dos el **71 % y
el 53 %** de las frases abren con conector. Tres: la pasada que los borró junto con los marcos dejó
la zona en 0 por mil, fuera de la banda humana por abajo, y reponerlos después **no lo arregló**:
451 → 548 palabras marcadas.

---

## E. Estilo, formato y ortografía

Nada de esto ha causado la etiqueta en ninguna medición nuestra de prosa académica. Pero delata a un
lector humano y es gratis. **La regla es ajustarse a lo que hace el documento original**, no a una
norma abstracta.

### 33. Rayas y guiones largos · `[DELATA]`
`WP:AIDASH` · `/humanizer §14`

El catálogo lo marca en septiembre de 2026 como candidato a pasar a indicadores históricos: OpenAI
las suprimió expresamente en GPT-5.1, y un estudio de julio de 2026 encontró que **de los modelos
actuales solo Claude las usa más que los escritores profesionales, y ChatGPT menos**. Es decir:
delata según modelo y época, y no es causa de nada. La pista fina que da el catálogo: las rayas
generadas suelen ir **rodeadas de espacios**, contra la norma tipográfica que conoce quien las usa
de verdad.

**Qué hacer.** Si el original no las usa, fuera: coma, punto, dos puntos o paréntesis. **Si el
original sí las usa, se quedan al mismo ritmo** — y dentro de una cita literal, siempre. En la
tesis 4 las dos rayas que quedaron estaban dentro de una cita de Fraser cuyo original tiene ocho:
conservarlas era lo correcto.

### 34. Comillas curvas · `[TRAMPA]`
`WP:AICURLY` · `/humanizer §19`

ChatGPT y DeepSeek usan “...” y ’ donde el formato pide "..." y '. Gemini y Claude, no.

**Por qué es trampa.** `/humanizer §14` y §19 están escritas para el inglés y para wikitexto. **En
español académico las comillas correctas son las angulares « »**, y las curvas son lo normal en
cualquier texto compuesto profesionalmente: Word, macOS y iOS las ponen solas, y el *Chicago Manual
of Style* las prescribe. Una regla «endereza las comillas» **destruiría** la tipografía de una
tesis. Aquí la única comprobación válida es la **coherencia interna**: que el documento no mezcle
« » con “ ” con " " sin motivo.

### 35. Negrita sin motivo · `[DELATA]`
`WP:AIBOLD` · `/humanizer §15`

Resaltado mecánico de cada aparición de un término, al estilo «ideas clave», heredado de los
`readme`, los wikis de aficionados y las presentaciones de venta. Algunos modelos nuevos ya llevan
instrucción de evitarlo. En una tesis: la negrita se reserva a lo que el documento reserve.

### 36. Listas con etiqueta en negrita y dos puntos · `[DELATA]`
`WP:AILIST` · `/humanizer §16`

`- **Experiencia de usuario:** se ha mejorado…`. El catálogo añade dos detalles útiles: la viñeta
puede aparecer como `•`, `-`, `–`, `#` o un emoji en vez de la marca de lista real, y las numeradas
como `1.` literal; y al copiar como texto plano **se pierden los saltos de línea**, con lo que
quedan etiquetas en negrita seguidas sin puntuación en medio de un párrafo. Eso último es lo que hay
que buscar en un documento de texto.

**Arreglo.** Prosa. En una tesis, además, mejora la calidad.

### 37. Mayúscula en cada palabra del título · `[NO APLICA]` tal cual
`WP:AITITLECASE` · `/humanizer §17`

El *title case* es un problema del inglés. El español ya usa mayúscula de oración, así que la marca
real es **el calco**: «Negociaciones Estratégicas y Alianzas Globales» → «Negociaciones estratégicas
y alianzas globales».

### 38. Emojis como formato · `[DELATA]`
`WP:AIEMOJI` · `/humanizer §18`

Emojis delante de epígrafes o de viñetas. Casi siempre en conversación y resúmenes de edición, y hoy
más raro. En un texto académico, cero.

### 39. Título repetido como encabezado · `[DELATA]`

El modelo pone un encabezado con el nombre del documento antes de todo el contenido, porque no
«ve» que el título ya está ahí. En un fichero entregado, sobra.

### 40. Encabezado repetido en la primera frase · `[CONVERGENTE]`
`/humanizer §29`

Un epígrafe seguido de una línea que solo lo reformula, antes de que empiece el contenido de verdad.
**Arreglo:** fuera esa línea.

### 41. Encabezados que solo contienen encabezados · `[DELATA]`
Un nivel de título sin texto propio, solo subtítulos debajo. En una tesis es un índice mal pegado.

### 42. Saltos de nivel de encabezado y abuso del nivel 1 · `[NO APLICA]`
El modelo empieza en `===` saltándose `==`, o pone todo en nivel 1, normalmente por traducir
Markdown. Es propio de wikitexto. El equivalente en un documento: jerarquía de epígrafes
incoherente.

### 43. Separadores temáticos entre secciones · `[DELATA]`
`----` o `---` entre cada apartado, muy típico de salida en Markdown. Fuera.

### 44. Tablas innecesarias · `[DELATA]`
`WP:AITABLE`

Tablas pequeñas para dos o tres datos que irían mejor en prosa. En una tesis, además, una tabla sin
título ni fuente es un defecto formal.

### 45. Markdown donde no toca · `[DELATA]`
`WP:MARKDOWN` · `WP:AIMARKDOWN`

`##` como encabezado, `**` como negrita, `*` como cursiva, ` ``` ` de bloque de código, `1.`
literal. **Restos que hay que buscar siempre en un texto que va a entregarse en Word o PDF.** El
catálogo advierte: el Markdown **por sí solo** no prueba nada — lo usa a diario media industria del
software —, pero **Markdown mezclado con sintaxis mal formada del formato de destino** es un
indicador fuerte.

### 46. Pares con guion · `[NO APLICA]`
`/humanizer §26`

*third-party*, *data-driven*, *client-facing*. El español no apila compuestos con guion; no
transfiere.

---

## F. Restos de conversación y artefactos de herramienta

Aquí no hay juicio que hacer: o está o no está. **Es la única ganancia gratis del catálogo.**

### 47. Texto dirigido al usuario · `[DELATA]` · inequívoco
`WP:CERTAINLY` · `WP:COLLABCOMM` · `/humanizer §20` · `/humanizer §22`

*Espero que te sirva* · *Por supuesto* · *Desde luego* · *Tienes toda la razón* · *¿Quieres que…?* ·
*¿Te gustaría que…?* · *avísame* · *aquí tienes un…* · *un desglose más detallado* · *Excelente
pregunta*. Incluye el tono complaciente que alaba al usuario antes de responder, y los textos que
explican **para qué** se ha escrito el documento o qué normas cumple.

### 48. Avisos de límite de conocimiento y especulación sobre lagunas · `[DELATA]`
`WP:AICUTOFF` · `WP:AIDISCLAIMER` · `/humanizer §21`

*Hasta mi última actualización* · *A fecha de mi último entrenamiento* · *Si bien los detalles son
limitados* · *no está ampliamente documentado* · *según la información disponible* · *en los
resultados de búsqueda proporcionados*.

**La parte peligrosa** no es el aviso, es lo que viene detrás: el modelo rellena el hueco con una
conjetura presentada como hecho — *probablemente estudió*, *cabe suponer que*, *mantiene un perfil
bajo* —. **Incluso la afirmación «no está documentado» es especulativa.** En un texto académico esto
es una afirmación sin fuente y hay que retirarla o sustituirla por lo que la fuente sí diga.

### 49. Plantillas y texto de relleno sin rellenar · `[DELATA]` · inequívoco
`WP:AIPLACEHOLDER`

Huecos de tipo *Mad Libs* que el usuario olvidó completar: `[Tema específico]`, `[Su nombre]`,
`[enlace al artículo revisado]`, `(Añade aquí la URL)`. Y en el aparato de citas: `2025-XX-XX` en
las fechas de consulta, `INSERT_SOURCE_URL_30`, `SOURCE_PUBLISHER`, `PASTE_SPOTIFY_TRACK_URL_HERE`,
`URL` como valor literal.

**Fecha de consulta desfasada** (histórico en el catálogo): citas cuya fecha de acceso es
llamativamente anterior a la fecha del texto — un documento de diciembre de 2025 con varios
`consultado el 12 de diciembre de 2024`. Los modelos nuevos lo hacen poco y hay explicaciones
legítimas (citas copiadas, trabajo sin conexión), así que corrobora, no prueba.

### 50. Artefactos internos de cada herramienta · `[DELATA]` · **prueba inequívoca de origen**
`WP:OAICITE` · `WP:STARTSPAN` · `WP:GROKCARD`

Código interno del generador que se escapa al texto. El catálogo los llama «un indicador
inequívoco». Búscalos siempre; cuestan cero.

| Herramienta | Qué aparece |
|---|---|
| ChatGPT | `:contentReference[oaicite:0]{index=0}` · `oai_citation` · `oaicite` · `Ejemplo+1` · `citeturn0search0` (con caracteres de área de uso privado) · `turn0image0turn0image1` · `citeturn0news0` · `citeturn1file0` · `({"attribution":{"attributableIndex":"1009-1"}})` |
| Gemini | `[cite: 1]` · `[cite: 3, 12, 13]` · `[span_1](start_span)` · `[span_1](end_span)` |
| Grok | `<grok-card data-id="e8ff4f" data-type="citation_card">` · `[](grok_render_citation_card_json={"cardIds":["3bb883"]})` |
| DeepSeek | corchetes lenticulares con daga: `【85†L261-269】` |
| Perplexity | `[attached_file:1]` · `[web:1]` · URLs con `ppl-ai-file-upload` |
| Sin clasificar | `:::writing{variant="document" id="68427"}` y sus tres dos puntos de cierre (visto desde junio de 2026, también traducido: `:::écriture{variante=...}`) |
| Cualquiera | `utm_source=chatgpt.com` · `utm_source=openai` · `utm_source=copilot.com` · `referrer=grok.com` · el carácter `↩` alrededor de notas |

**Barrido de una sola orden** (POSIX; en PowerShell, `Select-String` con el mismo patrón):

```bash
grep -nE 'contentReference|oai_?citation|oaicite|turn[0-9](search|image|news|file)[0-9]|attributableIndex|\[cite: *[0-9]|span_[0-9]\]\((start|end)_span|grok-card|grok_render_citation_card_json|【[0-9]+†|\[attached_file:[0-9]|\[web:[0-9]|ppl-ai-file-upload|utm_source=(chatgpt|openai|copilot)|referrer=grok|:::(writing|écriture)\{|20[0-9]{2}-(XX|xx)-(XX|xx)|INSERT_[A-Z_]+|PASTE_[A-Z_]+|↩' fichero.txt
```

Un solo acierto aquí basta para saber que el fragmento salió de una herramienta, y hay que quitarlo
antes de cualquier medición: `utm_source=chatgpt.com` en una URL de la bibliografía sobrevive al
PDF.

### 51. Corte abrupto · `[DELATA]`
Histórico en el catálogo

El texto se detiene a media frase porque se agotaron los tokens de la respuesta. No es concluyente
—un copiado mal hecho hace lo mismo—, pero en un fichero entregado es un defecto en cualquier caso.

### 52. Rechazo de instrucción · `[DELATA]`
Histórico en el catálogo

*Como modelo de lenguaje…* · *Como IA, no puedo…* · *Lo siento*. Hoy es raro. Coste de comprobación:
un `grep`.

### 53. Advertencias didácticas · `[CONVERGENTE]`
`WP:DIDACTIC` · histórico (nov. 2022 – 2024)

*es importante señalar / recordar / tener en cuenta* · *conviene destacar* · *puede variar*. Consejo
a un lector imaginario sobre seguridad o sobre asuntos que cambian según el país. El catálogo apoya esa
observación en el informe técnico de Pangram (Spero y Emi, 2024); no dice, y nosotros tampoco
podemos saber, qué aprendió ese clasificador.
Aparecen en la tarjeta de sistema de GPT-4 como ejemplos de «negativas parciales». **Arreglo:** la
afirmación, sin el envoltorio; es un caso particular de la marca 19.

---

## G. Marcas propias de Wikipedia

No aplican a una tesis. Van aquí porque el catálogo las trae y la referencia debía ser completa; y
porque si algún día se humaniza texto **para** una wiki, hacen falta.

### 54. Wikitexto roto y plantillas inexistentes · `[NO APLICA]`
`WP:AIREDCAT`

Sintaxis de plantilla mal formada; plantillas e *infoboxes* alucinados con nombre verosímil;
parámetros que no existen y por tanto no hacen nada; categorías inventadas o renombradas que salen
como enlaces rojos; plantillas borradas después del corte de entrenamiento del modelo. Ninguno
prueba nada por sí solo — los editores humanos se equivocan igual —, pero corroboran.

### 55. Fallos en el aparato de citas · `[NO APLICA]` como marca de estilo · **crítico como problema de integridad**
`WP:AIFICTREF` · `WP:AICITESTYLE`

El catálogo enumera: varios enlaces externos rotos en un texto nuevo y que tampoco están en el
Internet Archive; ISBN con dígito de control inválido; DOI que no resuelven; **DOI que resuelven a
un artículo distinto del citado**; citas de libro sin número de página ni URL; citas de libro con
página que **no verifica** lo que sostiene el texto; referencias con nombre declaradas y no usadas;
reutilización de referencias con sintaxis incorrecta.

**Por qué importa aquí de todas formas.** Esto no es una marca estilística: es **una cita
inventada**. La skill lo prohíbe y una tesis con una referencia falsa es un problema de integridad
académica, no de detección. Si en el texto de partida hay una cita que no puedes verificar,
verifícala o retírala; nunca la conserves porque «suena bien».

### 56. Indicadores de comentario y de resumen de edición · `[NO APLICA]`
`WP:AICOMMENT` · `WP:AISUMMARY`

Comentarios largos divididos en apartados; políticas mal citadas y atajos inventados; plantillas
transcluidas al mencionarlas; minimizar el uso de IA enumerando el esfuerzo puesto en cumplir las
normas; pedir a los críticos que digan exactamente qué mejorar; descartar las sospechas como
«especulación» frente a hechos «concretos»; pedir que se centren en el contenido.

En los resúmenes de edición, cuatro fórmulas: **garantía enlatada de cumplimiento** («revisado para
asegurar la neutralidad y el cumplimiento del manual de estilo»); **mención de lo que se ha
preservado, retenido o evitado** — inusual en un humano, exactamente lo que se espera de un modelo
al que se le pidió cambiar X conservando Z —; **énfasis en que las fuentes son independientes y
secundarias** en vez de decir qué se añadió; e **itemización de nombres de parámetros y plantillas**.

**Lo aprovechable para nosotros:** cuando redactes el informe final de la skill, di **qué cambió y
por qué**, no cuánto cuidado pusiste. Las mismas fórmulas delatan a un agente.

### 57. Señales de contexto, no de texto · `[NO APLICA]`
`WP:AIUSERPAGE` · `WP:AIDECLINE` · `WP:PGAME`
Cambio brusco de estilo respecto a lo que la misma persona escribía antes (sobre todo si es anterior
a noviembre de 2022), y el desajuste de variedad de lengua: quien escribe desde la India sobre una
universidad india no usaría inglés americano, y varios modelos lo hacen por defecto. Añade:
declaraciones de presentación dirigidas al revisor, plantillas de mantenimiento pre-colocadas,
páginas de usuario enlatadas, y acumulación de ediciones para subir de nivel de permisos. También
que quien lleva años usando IA cambia de estilo **en paralelo** a los modelos de cada año.

### 58. Diferencias entre modelos y sesgos · `[CONTEXTO]`
Cada modelo tiene su idiolecto (Rudnicka 2025; Sun et al. 2025): centrarse en el contexto amplio
—marca 1— es más de ChatGPT y Grok que de Gemini y Claude; Gemini y Claude son más concisos. Y el
catálogo registra un **sesgo pro-autoritario** en modelos punteros, más acusado en respuestas en
chino, por entrenarse con internet entera sin excluir propaganda estatal. Relevante para el
contenido de una tesis sobre asuntos políticos: **verifica las afirmaciones, no solo el estilo**.

---

## H. La lista inversa: qué hacen los humanos *más*

El catálogo tiene un apartado *Signs of human writing* que es exactamente lo que la skill necesita
para el dial de la voz: **lo que hay que meter o dejar en paz**, no lo que hay que quitar. Sobre 25
años de Wikipedia se ha observado que estas cosas son **más frecuentes en lo escrito por personas**:

- **Frases simples con verbo llano:** *hay un*, *tiene un*, *es*. (Inverso de la marca 10.)
- **La palabra corta en vez de su sinónimo rígido o eufemístico:** *escribió* y no *procedió a la
  redacción de*; *se trasladó* y no *fue reubicado*; *usó* y no *utilizó*; *intentó* y no *acometió
  el intento de*; *murió* y no *falleció* / *nos dejó*.
- **Afirmaciones superlativas o definitivas:** *uno de los mejores*, *el único*, *el primero*. El
  modelo las evita por prudencia entrenada; una persona las escribe.
- **Matizadores e intensificadores:** *muy*, *quizá*, *tiende a*. (Inverso de la marca 29.)
- **Construcciones largas y algo torpes:** *como resultado de*, *con el fin de*, *todos los*,
  *parte de*, *el hecho de que*. (Inverso de la marca 28.)

Y de `/humanizer`, los detalles que llevan la voz y **se conservan** aunque parezcan mejorables:

- **El detalle específico y raro.** Una dirección real, una cita rara, «el abogado que tenía el
  despacho encima de mi dentista». Es lo primero que la regresión a la media borra.
- **El sentimiento mezclado sin resolver.** «Creo que está bien, pero me incomoda y no sé decir por
  qué.»
- **La referencia atada a una época.** Jerga, memes, chistes internos de un año concreto: los
  modelos van con retraso.
- **La variedad de longitud de frase.** La escritura real alterna corta y larga; la generada tiende
  a una cadencia media y uniforme.
- **El paréntesis, la digresión y la autocorrección genuinas.** «(Me sale decir "casi", pero fue
  seguro.)» Un modelo casi nunca se interrumpe así.
- **La decisión en primera persona que el autor sabe justificar.** El catálogo lo pone como señal
  humana por sí misma: quien escribe puede explicar por qué hizo un corte o eligió una palabra, y
  puede explicar también un error como error. Si el usuario justifica una elección, esa elección se
  queda.
- **La antigüedad del texto.** ChatGPT se abrió al público el **30 de noviembre de 2022**. Lo
  escrito antes de esa fecha no puede ser generado, por muchas marcas que acumule. Si el usuario
  aporta material propio anterior, es la mejor muestra de voz que existe.
- **Las manías del autor.** Cifras repetidas en letra, comillas angulares, apelación directa al
  lector, paréntesis con datos en crudo. **Si el usuario aporta otro texto suyo, ese texto manda
  sobre cualquier regla de este fichero, incluida la de las rayas.**

---

## I. Indicadores inútiles y falsos positivos

Ninguno de estos prueba nada, y «arreglarlos» degrada el texto. El catálogo los recoge para evitar
acusaciones falsas; a nosotros nos sirve para no gastar iteraciones.

- **Gramática impecable.** Mucha gente escribe bien o ha sido editada. Pulido no es IA.
- **Mezcla de registro coloquial y formal**, o prosa a la vez «clínica» y «emotiva». Puede indicar
  un campo técnico, juventud, gusto por mezclar, o simplemente varias manos en el mismo texto.
- **Prosa «sosa» o «robótica».** La generada tiene marcas *concretas*; la sequedad sin ellas es solo
  sequedad.
- **Prosa «culta», «académica» o «elegante».** La marca 9 lista **palabras concretas**. La
  correlación no se extiende a todo el léxico formal.
- **Un conector de transición aislado.** Un *sin embargo* no es nada. Ver marca 32.
- **Comillas curvas por sí solas.** Ver marca 34.
- **Una sola raya.** Ver marca 33.
- **Una frase corta para enfatizar.** Solo cuenta la hilera (marca 24).
- **Repetición deliberada con función rítmica.** «Llegó. Vio. Venció.»
- **Límites, advertencias y objeciones reales.** Alcance, avisos legales, correcciones, objeciones
  con fuente, respuestas. En una tesis son obligatorios.
- **Alternativas reales** que un lector sí consideraría, en un apartado metodológico o
  argumentativo. Ver marca 26.
- **Falta de citas.** Más de 570.000 artículos de Wikipedia están marcados por eso y la mayoría son
  anteriores a los LLM. Y al revés: los modelos actuales sí ponen citas (inexactas, pero las ponen).
- **Formato complejo correcto.** Los editores visuales y las plantillas dan salida limpia sin IA.
- **Errores de marcado extraños e inexplicables.** El catálogo señala que los modelos **no**
  producen fallos aleatorios de ese tipo (etiquetas HTML sueltas, cursiva a medio cerrar): esos
  vienen de extensiones de navegador y de editores visuales. En un documento de texto, un formato
  roto de forma arbitraria apunta a copiado y pegado humano, no a IA.
- **Texto de segunda mano.** No reescribas una expresión marcada **dentro** de una cita, un título,
  un nombre propio o un ejemplo que se está discutiendo en vez de usando.

### Y sobre los detectores, del propio catálogo
`WP:AIDETECTION` · `WP:AIDETECTOR` · `WP:AIDETECTIVE`

El apartado *Caveats* dice tres cosas que conviene tener presentes:

1. **No hay que apoyarse solo en un detector.** Cita a GPTZero y a **Pangram** por su nombre:
   funcionan mejor que el azar, pero tienen tasas de error no triviales, y son **sensibles a
   modificaciones del texto** —paráfrasis, marcado, cambios de espaciado— y a modelos que no vieron
   al entrenarse. Un porcentaje alto **no** basta para borrar una página.
2. **Los humanos somos malísimos distinguiendo.** Un estudio de 2025 encuentra acierto **igual al
   azar**; otro, sobre **tesis alemanas**, un 57 % con textos de IA y un 64 % con textos humanos.
   Quien usa mucho LLM acierta ~90 %.
3. **Nos estamos pareciendo.** Está medida la influencia de los LLM en el habla y en la escritura
   académica humanas desde 2024. La frontera se mueve, y con ella el detector.

Traducido a nuestro procedimiento: **Pangram es el instrumento de evaluación, no la prueba de la
autoría**, y esa es exactamente la razón por la que la skill exige la puerta de estabilidad de tres
escaneos y no acepta un pase al filo.

---

## J. Barrido de una pasada

Orden de trabajo dentro de **un tramo que el detector ya ha marcado**. No sobre el documento
entero: eso está medido y sale peor.

1. **`grep` de artefactos** (marca 50) y de restos de conversación (47, 48, 49, 51, 52). Coste cero,
   inequívoco. Hazlo siempre y primero.
2. **«No X sino Y»** y sus dos variantes (marca 12). Único caso con separación limpia medida. Si hay
   dos en el tramo, empieza por aquí.
3. **El cierre** (marca 7) y **la frase-cartel de apertura** (marca 21). El residuo más frecuente
   está en los bordes del tramo, no en el medio.
4. **Destemplar el molde** (marca 19): fuera el marco de oración entera, el dato abre. Y respeta la
   marca 32: la bisagra se queda.
5. **Gerundios colgados** (marca 3) y **tríadas sin desarrollar** (marca 13).
6. **Importancia inflada** (1), **verdad honda** (20), **sentencias** (23), **remates** (24).
7. **Fuentes vagas** (5) y **conexión vaga** (11) → sustituye por lo que la fuente dice, con su
   atribución. Ésta es además la operación maestra: mete tokens humanos reales.
8. **Cadena de razonamiento** (18) y **sujeto ausente** (17) → parte y devuelve el agente.
9. **Mide el metadiscurso** (31) y decide la **dirección** del dial antes de tocarlo.
10. **Higiene** (33-46) solo al final y solo **ajustándose a lo que hace el original**.
11. **Repasa la lista inversa** (apartado H) y los falsos positivos (I) antes de aceptar la
    candidata. Si la zona reescrita se ha quedado en 0 marcas por mil palabras o sin un solo
    conector, has ido demasiado lejos: eso está medido y no se arregla reponiéndolos.

---

## K. Índice de correspondencia

Cada apartado del artículo de Wikipedia, contra la marca que lo recoge. Sirve para auditar que no
falta nada y para volver al original cuando quieras el ejemplo en inglés.

| Apartado del artículo | Aquí |
|---|---|
| *Caveats* → AI detection tools · Your detection ability | I, «Y sobre los detectores» |
| Undue emphasis on significance, legacy, and broader trends | 1 |
| Canned emphasis on notability, attribution, and media coverage | 2 |
| Superficial analyses | 3 |
| Promotional and advertisement-like language (+ *Subtypes*) | 4 |
| Vague attributions and overgeneralization of opinions | 5 |
| Outline-like conclusions about challenges and future prospects | 6 |
| Leads treating Wikipedia lists or broad titles as proper nouns | 8 |
| "Awards and recognition" section | 8 |
| High density of "AI vocabulary" words | 9 |
| Avoidance of basic copulatives | 10 |
| Vague expression of connection or association | 11 |
| Negative parallelisms (+ *Not just X but also Y* · *Not X, but Y* · *X rather than Y*) | 12 |
| Rule of three | 13 |
| Title heading | 39 |
| Title case | 37 |
| Headings only containing other headings | 41 |
| Overuse of boldface | 35 |
| Inline-header vertical lists | 36 |
| Overuse of em dashes | 33 |
| Emoji as formatting | 38 |
| Unusual use of tables | 44 |
| Curly quotation marks and apostrophes | 34 |
| Skipping heading levels · Overuse of level 1 headings | 42 |
| Thematic breaks between sections | 43 |
| Collaborative communication | 47 |
| Knowledge-cutoff disclaimers and speculation about gaps | 48 |
| Phrasal templates and placeholder text | 49 |
| Use of Markdown | 45 |
| Broken wikitext · Non-existent categories · Non-existent templates | 54 |
| Internal formatting and reference markup bugs (ChatGPT · Gemini · Grok · DeepSeek · Perplexity · `:::writing`) | 50 |
| `utm_source=` | 50 |
| Broken external links · Invalid DOI/ISBN · DOIs to unrelated articles · Book citations without pages · Incorrect use of references · Named references unused | 55 |
| Comment-specific indicators | 56 |
| Edit summaries (los cinco subapartados) | 56 |
| Pronounced shift in writing style · Submission statements · Pre-placed maintenance templates · Canned user pages · Permissions gaming | 57 |
| Differences between LLMs · Biases in content (pro-authoritarian) | 58 |
| *Signs of human writing* → Age of text · Ability to explain choices · Syntax | H |
| *Ineffective indicators* | I |
| *Historical* → Didactic disclaimers | 53 |
| *Historical* → Section summaries | 7 |
| *Historical* → Prompt refusal | 52 |
| *Historical* → Abrupt cut offs | 51 |
| *Historical* → Outdated *access-date* | 49 |
| *Historical* → Lexical diversity / elegant variation | 14 |

**Marcas que no vienen del artículo.** La 18 (cadena de razonamiento), la 19 (el molde del
párrafo), la 22 (anunciar el recuento), la 31 (el dial de la voz) y la 32 (la trampa del conector)
son nuestras, salidas de medición. Las 20, 21, 23-30 y 40 vienen de `/humanizer`, que a su vez las
derivaba del artículo o las añadía por su cuenta.

**La 7 es un caso mixto** y por eso aparece arriba: su mitad explícita (*en resumen*, *en
conclusión*) es el apartado *Section summaries*, que el catálogo archiva como histórico; su mitad
útil — **la frase lapidaria sin marcador que cierra el párrafo** — no está en el catálogo y sale de
nuestros datos, donde sigue viva.

**Los 35 patrones de `/humanizer`** están citados uno por uno en la cabecera de la marca que los
absorbe. Para comprobarlo:

```bash
grep -oE '/humanizer §[0-9]+' marcas-de-ia.md | sort -u | wc -l   # 35
```

---

## Procedencia

- **Wikipedia:Signs of AI writing**, WikiProject AI Cleanup — <https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing>.
  Leído íntegro en la revisión del 3 de septiembre de 2026 (1.891 líneas de wikitexto, 63 apartados,
  incluidos *Caveats*, *Signs of human writing*, *Ineffective indicators* e *Historical indicators*).
  Es **descriptivo, no prescriptivo**: son observaciones, no reglas.
- **Skill `humanizer` v2.11.2** (MIT), 35 patrones — un destilado de la anterior. Absorbida entera
  aquí; no hace falta consultarla.
- **Nuestras mediciones**, en `references/rasgos-medidos.md`, los cuatro `caso-*.md` y
  `APRENDIZAJES_VIVOS.md` del proyecto. Son la fuente de toda etiqueta `[MEDIDA]` y de las cifras
  citadas.

Bibliografía que el catálogo apoya y que conviene conocer: Reinhart et al., *PNAS* 2025 (estilo
gramatical y retórico); Kobak et al., *Science Advances* 2025 (vocabulario en exceso en publicación
biomédica); Juzek & Ward 2025 (por qué «delve»); Russell et al., ACL 2025 (los usuarios intensivos
de LLM detectan bien); Spero & Emi 2024 (informe técnico del clasificador de Pangram).
