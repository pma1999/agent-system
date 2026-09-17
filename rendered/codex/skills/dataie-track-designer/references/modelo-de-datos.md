# Modelo de datos: obligatoriedad, contratos, metadatos y calidad

Cómo tratar los datos en cualquier diseño: qué acompaña a un dato, cuándo es
obligatorio, qué pasa si falta, y cómo se documenta el contrato de datos de un
componente.

## Índice

1. Todo dato con contexto (metadatos obligatorios)
2. Estados del ciclo de vida del dato
3. Obligatoriedad: clases de datos dentro de un componente
4. Consecuencias de la ausencia de un dato
5. Niveles de datos de un track (iniciar / ejecutar / cerrar)
6. La fórmula de solicitud y la secuencia dinámica
7. El contrato de datos por componente
8. Dimensiones de calidad del dato
9. Vocabulario de entidades del modelo común

---

## 1. Todo dato con contexto (metadatos obligatorios)

Un dato ESG sin contexto puede ser técnicamente correcto y completamente
inútil. `Emisiones: 12.500` no dice nada sin saber: 12.500 **qué**, de qué
periodo, de qué sociedad, con qué perímetro, con qué metodología, de qué
fuente, si es real/calculado/estimado, quién lo aprobó y en qué outputs se ha
usado.

Todo dato relevante lleva estos metadatos:

- Propietario (quién responde por él)
- Fuente (sistema, documento, persona, proveedor, cálculo, estimación, externa)
- Periodo y perímetro
- Organización/entidad a la que pertenece
- Metodología o método de obtención (real / calculado / estimado)
- Estado y fecha de actualización
- Evidencia(s) que lo respaldan
- Nivel de calidad
- Versión e historial de cambios
- Usos posteriores (en qué outputs se ha utilizado)

Y debe poder responder a las preguntas incómodas: ¿quién lo aportó?, ¿de dónde
procede?, ¿qué versión está vigente?, ¿qué ocurre si cambia?

## 2. Estados del ciclo de vida del dato

Ciclo común recomendado:

1. Solicitado → 2. En preparación → 3. Introducido → 4. Validado
automáticamente → 5. Pendiente de revisión → 6. Revisado → 7. Aprobado →
8. Publicado → 9. Sustituido → 10. Archivado

No todo dato necesita pasar por los diez: el diseño indica qué estados aplican
a cada tipo de dato (un catálogo de referencia no necesita el mismo ciclo que
una medición crítica).

## 3. Obligatoriedad: clases de datos dentro de un componente

Al definir el contrato de datos, cada dato de entrada se clasifica en una de
estas clases:

| Clase | Qué es | Ejemplo |
|---|---|---|
| **Obligatorio bloqueante** | Sin él, el componente no puede ejecutarse | Identificador y tipo del IRO para evaluarlo |
| **Obligatorio derivado** | Necesario, pero lo genera otro componente: no se pide al usuario | La puntuación final que necesita "Determinar materialidad" procede de "Evaluar IRO" |
| **Condicional** | Solo se exige si se cumple una condición | Probabilidad solo para impactos potenciales; posición en cadena de valor solo si el IRO afecta a la cadena; escenarios solo si se cuantifica financieramente |
| **Opcional** | Mejora el análisis; no impide terminar | Comentarios, benchmark, segunda evidencia |
| **De referencia** | Procede de catálogos comunes; lo mantiene el administrador, no el usuario del track | Lista de temas ESG, escalas, unidades, requisitos |
| **Calculado** | Lo genera el sistema; jamás se solicita como dato primario | Severidad, valor consolidado, nivel de materialidad, variación interanual |

Regla de oro: el sistema distingue con claridad **"no disponible"** de
**"no necesario"**. De lo contrario, los cuadros de mando terminan decorados
con alarmas rojas que nadie entiende.

## 4. Consecuencias de la ausencia de un dato

No todos los datos faltantes bloquean, y el diseño debe decir cuál es la
consecuencia de cada ausencia:

| Consecuencia | Significado | Ejemplo |
|---|---|---|
| **Bloqueante** | No se puede continuar | Falta el valor que debe evaluarse |
| **Bloqueante para aprobación** | Se trabaja en borrador, pero no se aprueba/publica | Falta una evidencia obligatoria |
| **Advertencia** | Se completa, con menor calidad declarada | Falta un dato comparativo |
| **No aplicable** | La configuración hace que no se necesite | No se pide probabilidad para un impacto real si la metodología no la exige |
| **Pendiente** | Se aportará después; el proceso sigue | Dato comprometido para una fase posterior |
| **Estimado** | Se permite valor provisional identificado como estimación | Medición estimada a la espera del dato real |
| **Calculado** | El sistema lo obtiene automáticamente | Severidad |

## 5. Niveles de datos de un track

Cada track define tres niveles — así puede ponerse en marcha aunque falte
información:

1. **Para iniciar**: crear y configurar el recorrido (organización, periodo,
   perímetro, usuarios, metodología seleccionada).
2. **Para ejecutar**: completar los componentes principales (objetos,
   evaluaciones, evidencias, indicadores).
3. **Para aprobar/publicar**: considerar el resultado completo (evaluaciones
   revisadas, datos críticos validados, evidencias mínimas, aprobaciones,
   incidencias resueltas).

## 6. La fórmula de solicitud y la secuencia dinámica

> **Datos a solicitar = datos requeridos por componentes activos − datos
> existentes y válidos − datos calculables**

Secuencia: track seleccionado → configuración del alcance → componentes
activos → cada componente declara sus datos → la plataforma comprueba qué
existe y está vigente → reutiliza → calcula lo derivable → solicita solo lo
que falta → los componentes generan nuevos datos → los requisitos se
recalculan si cambia el alcance.

Nunca diseñes un track como "formulario largo al inicio": los datos aparecen y
se generan progresivamente conforme se ejecutan los componentes.

## 7. El contrato de datos por componente

Cada dato relevante del componente se documenta con esta tabla. Es lo que
impide que cada equipo interprete distinto qué necesita el sistema.

| Campo | Contenido |
|---|---|
| Componente | A qué componente pertenece |
| Dato | Nombre del dato |
| Tipo | Entrada / entrada derivada / salida |
| Obligatoriedad | Bloqueante / derivado / condicional / opcional / referencia / calculado |
| Condición | Cuándo aplica (si es condicional) |
| Fuente | Usuario, componente origen, integración, catálogo, cálculo |
| Momento | Cuándo se aporta o genera |
| Calidad mínima | Qué requisitos debe cumplir |
| Si falta | Consecuencia (bloqueante / bloqueante para aprobación / advertencia / no aplicable / pendiente / estimado) |
| Salida relacionada | Qué output o dato depende de él |

### Ejemplos

| Campo | Ejemplo 1 | Ejemplo 2 | Ejemplo 3 |
|---|---|---|---|
| Componente | Evaluar impactos | Evaluar impactos | Determinar materialidad |
| Dato | Severidad | Probabilidad | Puntuación total |
| Tipo | Entrada | Entrada | Entrada derivada |
| Obligatoriedad | Obligatorio | Condicional | Obligatorio derivado |
| Condición | Siempre | Solo impactos potenciales | — |
| Fuente | Usuario experto | Usuario experto | Componente "Evaluar IRO" |
| Momento | Durante la evaluación | Durante la evaluación | Automático |
| Calidad mínima | Escala completa y justificación | Escala completa | Evaluación aprobada |
| Si falta | Bloquea la aprobación | Bloquea solo si aplica la condición | No puede determinarse materialidad |
| Salida relacionada | Puntuación del impacto | Puntuación total | Estado material / no material |

## 8. Dimensiones de calidad del dato

La calidad se mide, no se describe con expresiones tranquilizadoras. Seis
dimensiones por dato:

1. **Completitud** — ¿está toda la información necesaria?
2. **Validez** — ¿cumple formato, unidad y reglas?
3. **Consistencia** — ¿es coherente con los datos relacionados?
4. **Trazabilidad** — ¿se identifica su origen y transformaciones?
5. **Actualidad** — ¿corresponde al periodo requerido y está al día?
6. **Fiabilidad** — ¿tiene evidencia suficiente y revisión?

La puntuación de calidad se puede agregar por dato, indicador, entidad, track,
output y cliente — y usarse como funcionalidad y argumento (p. ej. gaps de
calidad como recomendación de mejora).

## 9. Vocabulario de entidades del modelo común

Entidades canónicas para nombrar datos de forma consistente en los diseños
(no es un esquema físico; es vocabulario compartido):

- **Organización** (grupo, sociedad, unidad, centro, instalación, activo,
  departamento, cadena de valor)
- **Periodo** (año, trimestre, mes, fecha de referencia, vigencia, comparativo)
- **Perímetro** (corporativo, financiero, operativo, geografías, actividades,
  cadena de valor, criterios de consolidación)
- **Fuente** (sistema interno, documento, persona, proveedor, cálculo,
  estimación, externa)
- **Evidencia** (tipo, propietario, fecha, vigencia, relación con el dato,
  estado de revisión, nivel de confianza)
- **Indicador** (definición: nombre, unidad, fórmula, metodología,
  periodicidad, dimensiones, responsable, requisitos asociados)
- **Medición** (valor concreto de un indicador para un periodo y perímetro,
  con fuente, estado, evidencia, metodología, calidad y versión)
- **IRO** (impacto, riesgo u oportunidad; relacionado con tema, actividad,
  geografía, stakeholder, horizonte, cadena de valor, evaluaciones,
  evidencias, indicadores, acciones, requisitos)
- **Evaluación** (criterio, escala, puntuación, justificación, evaluador,
  fecha, versión, aprobación — siempre separada del objeto evaluado)
- **Política / Acción / Objetivo** (compromisos, iniciativas con responsable y
  calendario, metas con línea base y valor objetivo)
- **Requisito** (obligación, marco o solicitud de información; se vincula con
  indicadores, IRO, políticas, acciones, objetivos, evidencias y outputs)
- **Output** (resultado generado, con relación a los datos y versiones usados)

La distinción **Indicador vs Medición** y **Objeto vs Evaluación** son las dos
separaciones que más errores evitan: la definición es estable y compartida;
los valores y valoraciones son contextuales y versionados.
