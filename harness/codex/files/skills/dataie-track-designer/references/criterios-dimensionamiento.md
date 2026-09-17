# Criterios de definición y dimensionamiento

Cómo decidir qué es un track, qué es un componente, de qué tamaño, y cuándo
configurar en lugar de crear algo nuevo. El principio rector: **el tamaño se
decide por sentido de negocio, no por pantallas, campos o tareas**. "Más
pequeño" no es "más modular": la modularidad excesiva fabrica burocracia
técnica (cientos de piezas diminutas, dependencias por todas partes).

## Índice

1. Criterios de un track
2. Tamaño correcto de un track (señales)
3. Test de 7 preguntas del track
4. Criterios de un componente
5. Tamaño correcto de un componente (señales)
6. Test de 8 preguntas del componente
7. Test de coste de separación
8. Configuración vs componente nuevo vs extensión especializada
9. Política de personalización en 4 niveles
10. Tabla de clasificación de ejemplos

---

## 1. Criterios de un track

Una propuesta es un track cuando cumple:

1. **Resuelve una necesidad completa.** El cliente entiende qué problema
   resuelve. Ni "gestionar toda la sostenibilidad de la empresa" (demasiado
   amplio) ni "calcular la severidad de un impacto" (demasiado pequeño).
2. **Produce un resultado con valor propio.** Genera outputs que el cliente
   reconoce como valiosos por sí mismos. Si el resultado solo sirve como paso
   interno de otro proceso, no es un track.
3. **Puede contratarse o activarse de forma independiente.** Puede tener
   dependencias (datos o configuraciones previas), pero representa una unidad
   de valor comprensible en una propuesta comercial.
4. **Tiene principio y final claros.** Condiciones de entrada, fases, criterio
   de finalización y exclusiones definidos. Lo que nunca puede darse por
   terminado suele ser una capacidad continua o la plataforma, no un track.
5. **Alcance configurable pero coherente.** Admite variantes (entidades,
   geografías, metodologías, profundidad, outputs) pero todas resuelven la
   misma necesidad principal. Si al configurarlo resuelve problemas distintos,
   es demasiado grande.
6. **Combina varias funciones de negocio.** Habitualmente entre 3 y 10
   componentes principales (referencia orientativa para detectar extremos, no
   dogma).
7. **Destinatario y responsable principal claros.** Quién lo compra, quién lo
   lidera, quién aprueba. Si sus partes tienen compradores y objetivos
   totalmente distintos, probablemente son varios tracks.
8. **Métricas propias.** Completitud, calidad del resultado, esfuerzo, tiempo,
   reutilización de datos, valor y margen medibles.

## 2. Tamaño correcto de un track

### Demasiado grande cuando

- Resuelve varias necesidades independientes.
- Tiene compradores o responsables principales distintos por partes.
- Genera outputs que se contratarían por separado.
- Su alcance no cabe en una frase.
- No admite un criterio único de finalización.
- Acumula variantes y excepciones para cubrirlo todo.

Ejemplo: "Gestión ESG integral" — eso es una suite o cartera de tracks.

### Demasiado pequeño cuando

- Resuelve una tarea parcial o produce solo un dato intermedio.
- El cliente no lo contrataría por separado.
- No tiene valor sin otros procesos; se ejecuta siempre dentro de otro track.
- Equivale a una sola función operativa.

Ejemplo: "Evaluación de probabilidad de impactos" — es una regla o parte de un
componente.

### Frase de validación

Todo track debe poder expresarse así, con claridad y de forma vendible:

> Ayudamos a **[tipo de cliente]** a **[resolver una necesidad concreta]**
> mediante **[recorrido principal]**, generando **[outputs principales]**.

Si la frase sale forzada, ambigua o con dos necesidades unidas por "y además",
el tamaño está mal.

## 3. Test de 7 preguntas del track

1. ¿Resuelve una necesidad concreta del cliente?
2. ¿Genera un output con valor propio?
3. ¿Puede explicarse en una frase?
4. ¿Tiene principio, recorrido y final?
5. ¿Puede contratarse o activarse de forma independiente?
6. ¿Combina varias funciones de negocio relacionadas?
7. ¿Puede medirse su calidad, esfuerzo y resultado?

Interpretación: 7 síes → track claro. 5-6 → probablemente track, ajustar. 3-4 →
capacidad o track mal definido. <3 → no es un track.

Al aplicarlo en un diseño, indica el resultado (p. ej. "7/7") y, si no llega a
7, qué falla y cómo se corrige.

## 4. Criterios de un componente

Una pieza es un componente cuando cumple:

1. **Un único propósito principal.** Realiza una función clara ("evaluar
   impactos", "consolidar indicadores"). Ni "gestionar impactos, riesgos,
   estrategia y reporting" ni "introducir la puntuación de alcance".
2. **Produce un resultado propio.** Salida identificable y con valor fuera de
   sí mismo. Si solo genera una parte mínima, es una regla o cálculo interno.
3. **Inputs y outputs claros.** Qué datos necesita, de dónde proceden, qué
   reglas aplica, qué genera, quién usa su resultado.
4. **Reutilizable.** Útil en más de un track, variante, output o caso de uso.
5. **Lógica de negocio coherente.** Sus reglas internas pertenecen a la misma
   operación (escala, alcance, carácter irremediable y severidad conviven bien
   dentro de "evaluar impactos").
6. **Configurable y versionable** mediante metodologías, escalas, umbrales,
   reglas, campos y workflows — sin crear copias.
7. **Probable de forma aislada.** Se puede verificar sin ejecutar el track
   completo.
8. **Responsable funcional claro.** Un tipo de usuario, rol o equipo. Varias
   funciones con responsables totalmente distintos = probablemente demasiado
   grande.

### Nomenclatura

> **Verbo de negocio + objeto principal**: Identificar impactos, Evaluar
> riesgos, Consolidar indicadores, Aprobar evaluaciones, Generar tabla de
> reporting, Gestionar evidencias.

Dos verbos principales en el nombre = dos componentes. Nombres nebulosos tipo
"Gestión integral avanzada ESG 360" informan poco y fatigan bastante.

## 5. Tamaño correcto de un componente

### Demasiado grande cuando

- Contiene varios propósitos principales o varios workflows independientes.
- Produce outputs no relacionados o exige responsables distintos.
- Parte de su funcionalidad se reutiliza y otra parte no.
- Cuesta definir sus inputs y outputs.
- Cambiar una regla afecta a funcionalidades que no deberían tocarse.

Ejemplo: "Identificar, evaluar, aprobar y reportar riesgos" → dividir en
Identificar riesgos / Evaluar riesgos / Aprobar evaluaciones / Generar
reporting de riesgos.

### Demasiado pequeño cuando

- Equivale a un campo, una fórmula o una puntuación parcial.
- Siempre se ejecuta dentro de otro componente.
- No necesita estado, permisos ni versionado propios.
- No tiene valor reutilizable por sí solo.
- Separarlo genera más dependencias que beneficios.

Ejemplos: evaluar escala, evaluar alcance, calcular severidad, aplicar umbral,
introducir justificación → **reglas o criterios internos**, no componentes.
Si el track tuviera que orquestar cada puntuación individual, la arquitectura
se convierte en una caja de piezas microscópicas derramada por el suelo.

### Regla práctica de granularidad

> Un componente es la unidad más pequeña que conserva sentido de negocio y
> puede reutilizarse, configurarse, probarse y gobernarse de forma
> independiente. Representa una decisión, transformación o gestión de negocio
> completa, con output reutilizable y contrato de datos propio.

## 6. Test de 8 preguntas del componente

1. ¿Tiene un propósito de negocio único?
2. ¿Genera un resultado con sentido propio?
3. ¿Tiene inputs y outputs claramente definidos?
4. ¿Puede reutilizarse?
5. ¿Puede configurarse o versionarse?
6. ¿Puede probarse por separado?
7. ¿Tiene un responsable o workflow coherente?
8. ¿Separarlo aporta más valor que complejidad?

Interpretación: 7-8 síes → componente adecuado. 5-6 → probablemente, revisar
frontera. 3-4 → subcomponente o agrupación poco clara. <3 → regla, tarea o
dato.

Al aplicarlo en un diseño, indica el resultado por componente (p. ej. "8/8").

## 7. Test de coste de separación

Que una pieza *pueda* separarse no significa que *convenga*. Comparar:

- **Separar aporta:** reutilización, flexibilidad, versionado, testabilidad,
  claridad.
- **Separar cuesta:** más dependencias, más contratos de datos, más estados,
  más errores potenciales, más coordinación, más complejidad de interfaz.

Solo se separa cuando el beneficio supera el coste. En caso de duda, empezar
unido y separar cuando aparezca una segunda reutilización real es más barato
que empezar separado y mantener dependencias que nadie usa.

## 8. Configuración vs componente nuevo vs extensión especializada

La pregunta más frecuente del ecosistema: "este track necesita X, ¿reutilizo o
creo?". Orden de preferencia:

### a) Mismo componente + alcance + perfil (caso por defecto)

Mantener el mismo componente cuando comparte: el mismo objeto principal, el
mismo ciclo de vida, el mismo workflow y estados, la misma lógica básica de
revisión, el mismo tipo de output y gran parte de los datos.

> Si cambia principalmente **"qué criterios aplico"** → es configuración
> (perfil metodológico + filtro de alcance).

Ejemplo: evaluar solo riesgos climáticos en un track de Taxonomía → componente
"Evaluar riesgos" + filtro `tipo = climático ∧ perímetro del track` + perfil
metodológico de Taxonomía. El componente no sabe por qué recibe ese
subconjunto; recibe los objetos y ejecuta la metodología configurada.

### b) Extensión especializada (componente base + motor)

Cuando la lógica común se mantiene pero aparece un cálculo o proceso
técnicamente distinto: proyecciones geoespaciales, escenarios científicos,
cruce con mapas de amenazas, modelos de vulnerabilidad, integración con
proveedores especializados.

Estructura: el **componente base** conserva workflow, estados, evidencias,
revisión, aprobación y versionado; el **motor especializado** aporta el
cálculo específico. El track combina ambos. Así se separa solo la lógica
verdaderamente específica.

### c) Componente nuevo

Cuando cambia sustancialmente la naturaleza del proceso: el tipo de input, el
workflow, el responsable, las herramientas, el tipo de resultado o la lógica
de negocio.

> Si cambia **"qué proceso ejecuto y qué tecnología necesito"** → extensión o
> componente nuevo.

Cuidado con el extremo contrario: un componente tan genérico que acumula
condiciones incomprensibles se convierte en un pequeño monstruo metodológico.
Si los perfiles empiezan a contradecirse entre sí o el 80 % del componente son
ramas condicionales, es señal de dividir.

## 9. Política de personalización en 4 niveles

Toda petición de adaptación de un cliente se clasifica antes de diseñarla:

| Nivel | Qué es | Tratamiento |
|---|---|---|
| 1. Configuración estándar | Se resuelve con opciones existentes (escala, plantilla, workflow, responsables) | La opción habitual; sin diseño nuevo |
| 2. Configuración reutilizable | No existe aún, pero puede incorporarse como opción estándar (variante sectorial, nueva regla, nueva plantilla) | Diseñar como configuración del catálogo común |
| 3. Extensión de producto | Nueva capacidad con valor estratégico y potencial comercial | Pasa por priorización de producto |
| 4. Desarrollo específico | Solo sirve para un cliente, lógica exclusiva | Excepcional: precio y mantenimiento diferenciados, no compromete el núcleo |

Señal de salud del modelo: que la gran mayoría de una implantación (~80 % como
referencia, no como religión corporativa) se resuelva en niveles 1-2.

La pregunta que guía todas las decisiones:

> ¿Esta nueva necesidad aumenta la capacidad reutilizable del ecosistema o
> introduce una excepción que habrá que mantener indefinidamente?

## 10. Tabla de clasificación de ejemplos

| Elemento | Clasificación | Por qué |
|---|---|---|
| Doble materialidad completa | Track | Necesidad completa, vendible, con outputs finales |
| Análisis contextual | Capacidad | Agrupa varias funciones (perfil organizativo, cadena de valor, stakeholders, contexto externo) |
| Datos generales de la empresa | Datos maestros | Información, no función; el componente sería "Configurar perfil organizativo" |
| Configurar perfil organizativo | Componente | Función con resultado propio y reutilizable |
| Identificación de impactos | Componente | Tamaño adecuado; valorar unificar con riesgos/oportunidades en "Identificar IRO" si comparten interfaz, workflow, datos y validaciones |
| Evaluación de impactos | Componente | Objetivo, metodología, resultado y revisión propios |
| Evaluación de riesgos | Componente (separado de impactos) | Metodología distinta (magnitud, probabilidad, horizonte vs escala, alcance, irremediabilidad) |
| Evaluación de severidad | Regla interna | Derivada de escala + alcance + irremediabilidad; sin ciclo de vida propio |
| Evaluación de probabilidad | Regla condicional | Solo aplica a impactos potenciales; sin reutilización aislada |
| Puntuación de severidad | Dato derivado | Lo calcula el sistema |
| Determinación de materialidad | Componente | Aplica reglas/umbrales y produce un resultado aprobable |
| Aplicar un umbral | Regla | Cálculo interno |
| Evaluación de riesgos climáticos (en otro track) | Ejecución específica | Componente "Evaluar riesgos" + filtro climático + perfil del track (no un componente nuevo) |
