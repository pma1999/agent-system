# Plantillas de entrega

Estructuras estándar para que todos los diseños tengan la misma forma. Usa
estas plantillas tal cual (añade secciones si el caso lo exige; no quites las
que apliquen). El objetivo: que dos diseños hechos en meses distintos parezcan
hechos por la misma cabeza.

## Índice

1. Estructura del entregable completo (diseño de track)
2. Ficha de track
3. Ficha de componente
4. Contrato de datos
5. Perfil metodológico
6. Matriz de trazabilidad normativa
7. Formato de respuesta en Modo Consulta

---

## 1. Estructura del entregable completo (diseño de track)

Cuando el encargo es un track con sus componentes, el entregable (chat y, si
es extenso, documento `.md` adicional) sigue esta estructura:

1. **El track en una frase** (la frase de validación).
2. **Ficha de track** (plantilla §2).
3. **Mapa de capacidades y componentes**: lista jerárquica
   capacidad → componentes, marcando cada componente como
   [obligatorio] / [condicional: …] / [opcional], y anotando
   ♻ si reutiliza uno existente o ✚ si es nuevo.
4. **Fichas de componentes** (plantilla §3), cada una con su contrato de
   datos (§4). Para componentes reutilizados basta indicar el perfil y el
   alcance con que se ejecutan.
5. **Perfiles metodológicos** (plantilla §5).
6. **Datos del track**: resumen clasificado — reutilizados / nuevos de
   entrada / generados / calculados / de referencia — y niveles
   iniciar / ejecutar / aprobar.
7. **Matriz de trazabilidad normativa** (§6), si hay normativa.
8. **Reutilización**: qué consume de otros tracks y qué aporta a otros
   (nunca vacío sin justificación).
9. **Verificación de consistencia**: resultado de los tests (7 preguntas del
   track, 8 preguntas por componente) y del checklist.
10. **Supuestos, preguntas abiertas y siguientes pasos.**

Para encargos menores (un componente suelto, un contrato, un perfil), usa
solo las plantillas correspondientes más supuestos y preguntas abiertas.

## 2. Ficha de track

```markdown
## Track: [Nombre orientado a la necesidad]

**En una frase:** Ayudamos a [tipo de cliente] a [necesidad concreta]
mediante [recorrido principal], generando [outputs principales].

| Campo | Definición |
|---|---|
| Necesidad | Qué problema resuelve |
| Cliente objetivo | Para quién está pensado |
| Resultado prometido | Qué tendrá el cliente al finalizar |
| Alcance | Qué incluye |
| Exclusiones | Qué NO incluye |
| Condiciones de entrada | Qué debe existir para empezar |
| Base normativa | Norma(s) y versión, o "sin base normativa específica" |
| Roles | Quién compra, lidera, participa, aprueba |
| Configuración | Qué puede variar sin perder coherencia |
| Criterio de finalización | Cuándo se considera completado |
| Métricas | Cómo se mide calidad, esfuerzo, reutilización y valor |
| Tracks relacionados | Qué consume de otros y qué aporta a otros |

**Componentes**
- Obligatorios: …
- Condicionales: … (condición: …)
- Opcionales: …

**Outputs**
- …

**Datos mínimos por nivel**
- Para iniciar: …
- Para ejecutar: …
- Para aprobar/publicar: …
```

## 3. Ficha de componente

```markdown
### Componente: [Verbo + objeto]  [♻ existente | ✚ nuevo | ⚙ extensión]

| Campo | Definición |
|---|---|
| Propósito | Este componente sirve para… (uno solo) |
| Capacidad | A qué capacidad pertenece |
| Tracks donde se usa | Dónde se reutiliza (actuales y previsibles) |
| Responsable funcional | Quién lo ejecuta / revisa / aprueba |
| Estados | Solo los necesarios |
| Dependencias | Qué debe existir antes; quién consume su resultado |
| Configuración | Qué varía por perfil (escalas, umbrales, campos, evidencias…) |
| Criterio de completitud | Cuándo se considera terminado |

**Reglas internas** (no son componentes)
- …

**Inputs** → ver contrato de datos.
**Outputs**: …

**Test de 8 preguntas:** [n/8 — si <7, qué se ajustó]
```

## 4. Contrato de datos

Una fila por dato relevante del componente:

```markdown
| Dato | Tipo | Obligatoriedad | Condición | Fuente | Momento | Si falta | Salida relacionada |
|---|---|---|---|---|---|---|---|
| … | Entrada / Entrada derivada / Salida | Bloqueante / Derivado / Condicional / Opcional / Referencia / Calculado | … | Usuario / Componente X / Integración / Catálogo / Cálculo | … | Bloquea / Bloquea aprobación / Advertencia / No aplicable / Pendiente / Estimado | … |
```

## 5. Perfil metodológico

```markdown
### Perfil: [Nombre — p. ej. "Evaluación de riesgos · clima · Taxonomía"]

| Campo | Definición |
|---|---|
| Componente al que aplica | … |
| Contexto / track | Dónde se usa |
| Objetos aplicables | Filtro de alcance (p. ej. riesgos tipo climático) |
| Criterios y escalas | … |
| Fórmulas y umbrales | … |
| Campos obligatorios adicionales | … |
| Condiciones | Reglas si/entonces |
| Evidencias mínimas | … |
| Resultado esperado | Qué produce la ejecución con este perfil |
| Versión metodológica | Norma/metodología y versión |
```

## 6. Matriz de trazabilidad normativa

```markdown
| Requisito (ref. norma) | Datos necesarios | Componente(s) | Output(s) | Condición de aplicabilidad |
|---|---|---|---|---|
| … | … | … | … | … |
```

Cierre obligatorio de la matriz: "Todos los requisitos extraídos quedan
cubiertos" o lista de huecos con propuesta.

## 7. Formato de respuesta en Modo Consulta

Para preguntas sobre el sistema, responde en prosa clara con esta lógica
interna (sin necesidad de encabezados si la respuesta es corta):

1. **Criterio aplicable**: qué regla/test del marco responde a la pregunta.
2. **Aplicación al caso**: la respuesta concreta.
3. **Ejemplo**: si aclara.
4. **Matiz o límite**: cuándo la respuesta cambiaría (p. ej. "si el proceso o
   la tecnología cambian sustancialmente, entonces extensión en lugar de
   perfil").

Si la pregunta expone un hueco del marco, dilo y propón la extensión más
consistente, marcada como propuesta.
