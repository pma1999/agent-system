# Marco conceptual del ecosistema DATAIE

Definición oficial de cada concepto y de sus relaciones. Todo diseño y toda
respuesta deben usar estos términos exactamente con este significado.

## 1. La idea general

> El cliente contrata un track para resolver una necesidad.
> El track activa una serie de componentes.
> Los componentes utilizan y generan datos aplicando reglas.
> Los datos permiten producir uno o varios outputs.

La cadena básica es **Track → componentes → datos → outputs**, pero la
estructura real es una **red, no una línea**:

- Un track utiliza varios componentes.
- Un componente puede utilizarse en varios tracks.
- Un componente consume unos datos y genera otros.
- Un dato puede alimentar varios componentes y varios outputs.
- Un mismo objeto (p. ej. un riesgo) puede recibir varias evaluaciones según
  el track y la metodología.

El valor del ecosistema aparece en esa reutilización: cuanto más usa un
cliente la plataforma, menos esfuerzo requiere cada nueva necesidad.

## 2. Plataforma

Infraestructura común que almacena, organiza y gobierna los datos: modelo de
datos común, seguridad, usuarios y permisos, trazabilidad, workflows,
integraciones, evidencias, versionado y reglas de calidad. No se vende como
funcionalidad aislada, pero sostiene todas las soluciones. La arquitectura de
la plataforma **no depende del catálogo comercial**: un track puede cambiar de
nombre, alcance o precio sin obligar a rediseñar el modelo de datos.

## 3. Track

### Definición

Solución completa, configurable y comercializable que resuelve una necesidad
concreta del cliente mediante la combinación ordenada de componentes.

Es la unidad principal de la propuesta comercial: el cliente contrata un
resultado comprensible ("hacer la doble materialidad", "evaluar el
alineamiento con Taxonomía"), no piezas técnicas.

### Qué define un track

- El problema o necesidad que resuelve y para quién.
- El alcance y sus límites (qué incluye y qué no).
- Los componentes que activa, con su orden y dependencias.
- Cuáles son núcleo obligatorio, cuáles condicionales y cuáles opcionales.
- Los datos mínimos por nivel (iniciar / ejecutar / aprobar-publicar).
- Las reglas y perfiles metodológicos aplicables.
- Los roles participantes y los workflows de revisión/aprobación.
- Los outputs que genera.
- El criterio de finalización (cuándo se considera completado).
- Las opciones de configuración admitidas.

### Qué NO es un track

Un módulo de software, una pantalla, un conjunto fijo de formularios, un
proyecto totalmente personalizado, un único informe, ni una copia de
funcionalidades existentes. El track **orquesta y configura** capacidades
comunes; no las reimplementa.

### Estructura interna recomendada

- **Núcleo obligatorio**: componentes imprescindibles para el resultado principal.
- **Componentes condicionales**: se activan según tipo de cliente, metodología,
  complejidad, outputs contratados, disponibilidad de datos o marco normativo.
- **Componentes opcionales o premium**: añaden valor adicional.

### Fórmula

> **Track = necesidad + alcance + componentes + configuración + outputs + criterio de finalización**

## 4. Capacidad

Conjunto coherente de componentes que cubre una función amplia (p. ej.
"gestión de IRO", "gestión de indicadores", "reporting"). Sirve para organizar
y agrupar; **no** es la unidad de orquestación (eso es el componente) ni la
unidad comercial (eso es el track). Cuando una pieza parece "componente" pero
contiene varias funciones con propósitos distintos, suele ser una capacidad
que hay que descomponer.

## 5. Componente

### Definición

Unidad funcional reutilizable que realiza **una** operación de negocio
concreta, con datos y reglas definidos, y genera un resultado con sentido
propio.

### Contrato que todo componente debe declarar

- Propósito (uno solo).
- Datos de entrada: cuáles, de dónde, cuáles obligatorios/condicionales.
- Reglas y configuración que admite.
- Proceso y estados (si los necesita).
- Datos de salida.
- Validaciones.
- Dependencias (qué debe existir antes; quién consume su resultado).
- Condiciones de ejecución.

### Propiedades esperadas

- Propósito de negocio comprensible sin detalles técnicos.
- Resultado propio identificable.
- Ciclo de vida propio (pendiente, en curso, completado, revisado, aprobado)
  cuando lo necesite — sin inventar estados que no hagan falta.
- Reutilizable en más de un track, output o recorrido.
- Configurable y versionable sin crear copias.
- Probable de forma aislada.
- Responsable funcional claro.

### Qué NO es un componente

- Una pantalla o formulario: una pantalla puede ejecutar varios componentes y
  un componente puede aparecer en varias pantallas.
- Un microservicio: primero se definen componentes funcionales y contratos de
  datos; la implementación técnica se decide después.
- Un criterio o cálculo interno (eso es una regla).
- Un conjunto de datos maestros (eso son datos; el componente sería, p. ej.,
  "configurar perfil organizativo").

### Fórmula

> **Componente = propósito + inputs + reglas + proceso + outputs**

## 6. Regla y perfil metodológico

### Regla

Define **cómo** funciona una parte de un componente: un criterio, una fórmula,
una escala, un umbral, una validación, una condición de activación.

Ejemplos: "severidad = combinación de escala, alcance y carácter
irremediable"; "la probabilidad solo se solicita para impactos potenciales";
"una puntuación extrema exige justificación adicional".

### Perfil metodológico (o perfil de evaluación)

Agrupación con nombre de las reglas aplicables en un contexto: tipos de objeto
aplicables, criterios, escalas, fórmulas, campos obligatorios, condiciones,
evidencias mínimas, umbrales y resultado esperado.

El perfil es el mecanismo que permite que **un mismo componente** sirva a
varios tracks y metodologías sin duplicarse: el componente aporta la función
estable (workflow, estados, evidencias, revisión, versionado); el perfil
aporta la metodología del contexto.

Ejemplo: el componente "Evaluar riesgos" puede ejecutarse con perfiles
distintos — materialidad financiera, riesgo climático para Taxonomía
(exposición, sensibilidad, vulnerabilidad, escenario, adaptación, riesgo
residual), riesgo de cadena de suministro — sin que exista más que un
componente.

### Fórmula

> **Ejecución específica = componente común + alcance + perfil metodológico + configuración**

Donde el **alcance** es el filtro de selección de objetos (p. ej. "solo
riesgos de tipo climático dentro del perímetro del track"). El componente no
necesita saber por qué recibe ese subconjunto; recibe los objetos y ejecuta la
metodología configurada.

## 7. Dato

### Definición

Cualquier información estructurada que la plataforma utiliza, genera, almacena
o relaciona. No solo números o campos: también son datos los **objetos** (una
empresa, un riesgo, una evaluación, una evidencia, una acción, un requisito).

### Tipos

| Tipo | Qué es | Ejemplos |
|---|---|---|
| Maestros | Elementos estables del cliente | Organización, sociedad, instalación, actividad, geografía, stakeholder |
| De entrada | Aportados o conectados desde una fuente | Valor de emisiones, descripción de un riesgo, documento |
| Generados | Creados durante un proceso | Un IRO identificado, una evaluación, una acción |
| Calculados/derivados | Obtenidos aplicando reglas sobre otros | Severidad, puntuación de riesgo, valor consolidado, nivel de calidad |
| De configuración | Determinan cómo funciona un componente | Escala, umbral, fórmula, metodología, workflow |
| De referencia | Catálogos comunes mantenidos centralmente | Lista de temas ESG, tipos de stakeholder, unidades, requisitos |
| Evidencias | Respaldan datos, decisiones o cálculos | Facturas, informes, estudios, archivos de cálculo |

### Propiedad clave

Los datos **no pertenecen a un track**: pertenecen al cliente y se reutilizan
cuando contexto, periodo, perímetro y metodología son compatibles. El detalle
completo (metadatos obligatorios, estados, obligatoriedad, calidad, contratos)
está en `modelo-de-datos.md`.

## 8. Output

Resultado generado para el cliente o para otro proceso: registro de IRO,
matriz de materialidad, informe, cuadro de mando, plan de acción, tabla de
indicadores, paquete de evidencias, exportación.

Un output puede ser **final** (se entrega al cliente), **intermedio**
(alimenta otro componente) o **reutilizable** (sirve a varios tracks). Todo
output conserva la relación con los datos, versiones y evidencias utilizados.

## 9. Producto de datos

Activo de información reutilizable generado a partir de datos agregados,
anonimizados o enriquecidos (benchmarks sectoriales, bibliotecas sectoriales
de IRO, patrones, indicadores de calidad del dato, modelos). Se plantean como
productos de **insights**, nunca como venta de datos individuales de clientes;
exigen derechos contractuales, anonimización, agregación mínima y gobierno.

## 10. Objeto común, evaluaciones múltiples

Regla estructural para todo el modelo. Se separa siempre:

- **El objeto que se analiza** — información estable: identificador,
  descripción, categoría, causa, consecuencia, activos afectados, geografía,
  responsable.
- **Las evaluaciones sobre ese objeto** — cada una registra: perfil
  metodológico, track de origen, periodo, perímetro, escenario, puntuaciones,
  evidencias, resultado, estado y versión.

```text
Riesgo: inundación de una planta      ← objeto común (se registra una vez)
 ├── Evaluación para doble materialidad
 ├── Evaluación climática para Taxonomía
 ├── Evaluación financiera
 └── Evaluación de riesgo residual
```

Consecuencias prácticas:

- Nunca se guarda una puntuación como propiedad universal del objeto.
- Un nuevo track no duplica el objeto: añade su evaluación y reutiliza
  descripción, activo, evidencias y responsable.
- Las evaluaciones quedan relacionadas entre sí a través del objeto, lo que
  permite comparar metodologías y detectar incoherencias.

## 11. La secuencia dinámica (cómo se ejecuta un track)

1. El cliente selecciona o contrata un track.
2. Se configura el alcance (entidades, periodo, perímetro, metodología, outputs).
3. La configuración activa determinados componentes (no todos siempre).
4. Cada componente declara sus requisitos de datos.
5. La plataforma comprueba qué datos ya existen y están vigentes.
6. Reutiliza los disponibles; calcula los derivables.
7. Solicita únicamente lo que falta.
8. Los componentes generan nuevos datos que alimentan a los siguientes.
9. Solo bloquea cuando falta un dato realmente imprescindible.
10. Si cambia el alcance, los requisitos se recalculan dinámicamente.

> **Datos a solicitar = datos requeridos por componentes activos − datos existentes y válidos − datos calculables**

Esta es la fórmula funcional más importante del modelo. Elegir un track **no**
significa pedir al cliente todos los datos posibles de todos sus componentes
desde el primer día.

## 12. Reglas de diseño del ecosistema

1. Los tracks se diseñan desde las necesidades del cliente.
2. Los componentes se diseñan desde las funciones reutilizables.
3. Los datos no pertenecen a un track: pertenecen al cliente y se reutilizan
   cuando contexto, periodo, perímetro y metodología son compatibles.
4. Un componente no se duplica porque cambie el track: se configura mediante
   alcance y perfil metodológico mientras la función principal sea la misma.
5. Se crea un componente (o extensión) nuevo cuando cambia sustancialmente el
   proceso, el tipo de input, el workflow, la tecnología necesaria, el
   resultado, el responsable o la lógica de negocio.
6. Los criterios pequeños son reglas internas, no componentes, salvo que
   tengan ciclo de vida y reutilización propios.
7. El sistema pide únicamente datos necesarios, no disponibles y no calculables.
8. Todo output conserva trazabilidad hasta sus datos y evidencias de origen.

## 13. Distinciones rápidas

### Track vs componente

| Pregunta | Track | Componente |
|---|---|---|
| ¿Qué resuelve? | Una necesidad completa | Una función concreta |
| ¿Quién lo entiende? | Cliente y negocio | Producto, conocimiento y tecnología |
| ¿Puede venderse? | Sí, normalmente | No necesariamente |
| ¿Genera valor final? | Sí | A menudo intermedio |
| ¿Qué combina? | Componentes | Reglas y datos |
| ¿Cómo se reutiliza? | Se repite entre clientes | Se comparte entre tracks |

### Componente vs regla vs dato (test de una pregunta)

- ¿El cliente reconocería esto como una solución completa que resuelve una
  necesidad y produce un resultado final? → **track**.
- ¿Realiza una función de negocio completa, reutilizable, con inputs y outputs
  propios? → **componente**.
- ¿Solo define cómo se calcula, valida o ejecuta una parte del componente? →
  **regla**.
- ¿Representa información consumida o generada? → **dato**.

## 14. Ejemplo ilustrativo mínimo (no es catálogo oficial)

Track "Doble materialidad" (ejemplo): su componente "Evaluar impactos" consume
impacto, actividad, stakeholder, periodo, perímetro y evidencias; aplica las
reglas escala, alcance, carácter irremediable, probabilidad (condicional a
impactos potenciales) y fórmula de severidad; y genera severidad, resultado de
evaluación, justificación y estado. Ese resultado alimenta el componente
"Determinar materialidad", cuyo resultado alimenta a su vez estrategia y
reporting. Ni "evaluar escala" ni "calcular severidad" son componentes: son
reglas dentro de "Evaluar impactos".

## 15. Resumen operativo

> **El track decide qué debe lograrse.**
> **Los componentes realizan el trabajo.**
> **Las reglas y perfiles determinan cómo.**
> **Los datos alimentan y registran el proceso.**
> **Los outputs materializan el resultado.**

> **Un dato común alimenta varios componentes. Un componente común participa
> en varios tracks. Un mismo objeto tiene distintas evaluaciones según la
> metodología. Un track no copia funcionalidades: las configura y las
> orquesta.**
