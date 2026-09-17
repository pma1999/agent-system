# Proceso de diseño: track, componente, normativa y checklist

Los pasos para producir diseños completos y consistentes, las preguntas de
encuadre, la conversión de normativa en track y el checklist final que todo
diseño debe pasar antes de entregarse.

## Índice

1. Preguntas de encuadre
2. Pasos para definir un track (10)
3. Pasos para definir un componente (10)
4. De normativa a track
5. Checklist de consistencia (obligatorio antes de entregar)

---

## 1. Preguntas de encuadre

Antes de diseñar, reúne esta información. Pregunta **solo** lo que cambie el
diseño; el resto decláralo como supuesto explícito y sigue — un buen diseño
con supuestos claros es más útil que un interrogatorio.

Críticas (preguntar si no se deducen de la petición):

- **Necesidad y cliente objetivo**: ¿qué problema resuelve y para qué tipo de
  cliente (tamaño, sector, madurez)?
- **Catálogo existente**: ¿qué tracks, componentes o datos ya existen o ya se
  han diseñado? (Determina qué se reutiliza y evita duplicar. Si el usuario no
  tiene catálogo aún, se declara "diseño sin catálogo previo".)
- **Normativa o marco aplicable**: ¿hay texto normativo que adjuntar o una
  base regulatoria concreta (y versión)?
- **Outputs esperados**: ¿qué debe recibir el cliente al final?

Secundarias (asumir con criterio si no hay respuesta):

- Alcance típico (entidades, geografías, cadena de valor sí/no).
- Nivel de acompañamiento experto previsto.
- Variantes de cliente que deben soportarse (mono-entidad vs grupo, datos
  manuales vs integrados).

## 2. Pasos para definir un track

Sigue los diez pasos en orden. El diseño de arriba abajo evita empezar por
las funcionalidades existentes y acabar justificándolas.

1. **Identificar la necesidad.** Completar: "El cliente necesita…". Empezar
   por el problema, nunca por las funcionalidades.
2. **Definir el resultado prometido.** Completar: "Al finalizar, el cliente
   tendrá…" (lista de outputs concretos).
3. **Definir alcance y límites.** Qué incluye, qué no, entidades, periodos,
   metodologías, profundidad. Las exclusiones explícitas valen tanto como las
   inclusiones.
4. **Dibujar el recorrido end-to-end.** Fases desde el inicio hasta los
   outputs, como recorrido de negocio (aún sin componentes).
5. **Identificar los componentes necesarios.** Traducir cada fase a
   componentes reutilizables. No convertir automáticamente cada tarea en
   componente: aplicar los tests de `criterios-dimensionamiento.md`. Comprobar
   contra el catálogo existente: reutilizar > configurar > extender > crear.
6. **Clasificar los componentes.** Obligatorio / condicional (con su
   condición) / opcional.
7. **Definir los datos mínimos.** Por niveles (iniciar / ejecutar / aprobar) y
   por clase (bloqueante, derivado, condicional, opcional, referencia,
   calculado, reutilizado). Aplicar la fórmula de solicitud.
8. **Definir configuración y metodología.** Perímetro, escalas, umbrales,
   workflows, roles, evidencias mínimas, perfiles metodológicos, outputs
   seleccionables.
9. **Definir el criterio de finalización.** Condiciones exactas para
   considerar el track completado (evaluaciones aprobadas, evidencias
   disponibles, outputs generados…).
10. **Validar el tamaño.** ¿Podría dividirse en dos soluciones contratables
    por separado? ¿Alguna parte no contribuye al mismo resultado? ¿Es
    demasiado pequeño para venderse? Aplicar el test de 7 preguntas y la
    frase de validación; ajustar si falla.

## 3. Pasos para definir un componente

1. **Formular el propósito.** "Este componente sirve para…" — un único
   propósito principal.
2. **Nombrarlo**: verbo de negocio + objeto.
3. **Definir inputs**: datos que recibe, obligatoriedad de cada uno, fuentes
   posibles.
4. **Definir reglas**: metodología, criterios, fórmulas, umbrales,
   validaciones, condiciones. Los criterios pequeños viven aquí, no como
   componentes.
5. **Definir proceso y estados**: solo los estados necesarios. Añadir estados
   sin necesidad es una forma sorprendentemente eficiente de fabricar trabajo.
6. **Definir outputs**: datos, evaluaciones, resultados, alertas, evidencias,
   estados.
7. **Identificar reutilización**: en qué tracks y outputs puede participar;
   qué parte es común y qué parte depende de la metodología.
8. **Separar configuración de lógica común**: la función estable queda en el
   componente; escalas, fórmulas, campos obligatorios, evidencias, umbrales y
   metodologías van a perfiles configurables.
9. **Revisar el tamaño**: ¿más de un propósito? → dividir. ¿Solo una fórmula
   o campo? → integrarlo como regla. Aplicar el test de 8 preguntas.
10. **Probarlo (conceptualmente) en dos contextos.** Todo componente
    reutilizable debe funcionar en al menos dos tracks/casos distintos
    cambiando solo alcance y perfil. Si la función común deja de ser
    reconocible entre ambos, la frontera está mal puesta.

## 4. De normativa a track

Cuando el usuario aporta una normativa (o la necesidad tiene una detrás), el
texto normativo se procesa **antes** de diseñar, con esta disciplina:

### Principio

> La normativa define **requisitos y outputs**, nunca la arquitectura. Una
> norma entra al modelo como entidad Requisito vinculada a datos, componentes
> y outputs. No se crea un componente por artículo ni un track por capítulo.

### Pasos

1. **Extraer del texto**: sujetos obligados y condiciones de aplicabilidad
   (umbrales de tamaño, sector, fechas); obligaciones y requisitos de
   información (datapoints); outputs exigidos (informes, matrices,
   desgloses, formatos); metodologías impuestas o permitidas (criterios,
   escalas, escenarios); condicionalidades internas ("si X aplica, entonces
   divulgar Y"); definiciones propias de la norma; y versión/fecha del texto.
2. **Convertir a modelo**: cada obligación → uno o más Requisitos; cada
   requisito → datos necesarios (con su clase de obligatoriedad — las
   condicionalidades de la norma se convierten en datos/componentes
   condicionales, no en obligatorios universales) → outputs del track.
3. **Mapear a componentes**: para cada grupo de requisitos, ¿qué función de
   negocio los satisface? Buscar primero componentes existentes que se
   configuren (perfil metodológico con los criterios de la norma); crear
   extensiones o componentes nuevos solo según las reglas de
   `criterios-dimensionamiento.md` §8.
4. **Construir la matriz de trazabilidad**: requisito → dato(s) →
   componente(s) → output(s). Todo requisito debe quedar cubierto; todo
   componente debe justificar qué requisitos sirve (lo que no sirve a ningún
   requisito ni a la operación del track, sobra).
5. **Versionar la metodología**: anotar la versión de la norma usada. Si la
   norma cambia, cambian perfiles y requisitos — no la arquitectura.

### Si no hay texto adjunto

Usar el conocimiento propio del marco regulatorio, declarándolo: "Base
normativa asumida: [norma, versión aproximada, fecha de conocimiento]", y
recomendar validar contra el texto vigente. Nunca presentar como cita textual
lo que es reconstrucción de memoria.

## 5. Checklist de consistencia (obligatorio antes de entregar)

Recorre la lista completa. Si algo no pasa, corrige o declara la excepción
justificada en el entregable. Un diseño entregado sin este checklist no es un
diseño terminado.

**Track**

- [ ] Pasa el test de 7 preguntas (indicar resultado) y la frase de validación.
- [ ] Alcance con inclusiones y exclusiones explícitas.
- [ ] Componentes clasificados en obligatorios / condicionales (con condición) / opcionales.
- [ ] Criterio de finalización definido y verificable.
- [ ] Outputs listados y con valor reconocible por el cliente.

**Componentes**

- [ ] Cada componente pasa el test de 8 preguntas (indicar resultado).
- [ ] Nombres verbo + objeto; un solo verbo principal por componente.
- [ ] Ningún criterio, cálculo o campo modelado como componente (severidad,
      escala, umbral… son reglas).
- [ ] Ningún componente duplicado: si dos hacen la misma función de negocio,
      es uno con perfiles/alcances distintos.
- [ ] Cada componente probado conceptualmente en un segundo contexto.

**Datos**

- [ ] Contrato de datos por componente con obligatoriedad, condición, fuente,
      momento y consecuencia de ausencia.
- [ ] Datos clasificados: reutilizados / nuevos de entrada / generados /
      calculados / de referencia.
- [ ] Fórmula de solicitud respetada: nada que exista, esté vigente o sea
      calculable se pide al cliente.
- [ ] Niveles definidos: iniciar / ejecutar / aprobar-publicar.
- [ ] Metadatos y evidencias previstos para los datos críticos.
- [ ] Separación objeto ↔ evaluación respetada (ninguna puntuación como
      propiedad del objeto).

**Reutilización**

- [ ] Declarado qué consume el track que ya existe o que otros tracks generan.
- [ ] Declarado qué genera este track que otros podrán reutilizar.
- [ ] Perfiles metodológicos usados en lugar de componentes duplicados.
- [ ] Peticiones de personalización clasificadas en los 4 niveles.

**Normativa (si aplica)**

- [ ] Matriz de trazabilidad requisito → dato → componente → output completa.
- [ ] Condicionalidades de la norma modeladas como condicionales, no como
      obligatorios universales.
- [ ] Versión de la norma anotada; base normativa asumida declarada si no
      hubo texto adjunto.

**Entregable**

- [ ] Estructura de `plantillas.md` respetada.
- [ ] Supuestos y preguntas abiertas listados (nunca vacío si hubo huecos).
- [ ] Terminología exactamente conforme a `marco-conceptual.md`.
