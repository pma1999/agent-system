# Sistema propio de orquestación multiagente — referencia de candidatura

> **Fuente de verdad.** Pablo ha diseñado y construido este sistema como modelo
> operativo para trabajos de ingeniería complejos y lo utiliza tanto en trabajo
> profesional como personal. Es una capacidad propia de desarrollo y
> coordinación asistida por IA; no debe presentarse como un producto comercial,
> una implantación de cliente o una solución con usuarios externos salvo que
> Pablo lo confirme expresamente.

## 1. Qué es

El sistema separa pensar, implementar y verificar en manos diferentes e
independientes, conectadas por contratos escritos y artefactos durables en vez
de depender de una conversación larga. Un coordinador elige el carril de
trabajo y despacha especialistas con responsabilidades cerradas. El resultado
es un flujo auditable con menos redescubrimiento, decisiones mejor
fundamentadas y verificación explícita.

El diseño es **agnóstico del harness** y puede materializarse en distintas
instalaciones de desarrollo asistido por IA. Pablo utiliza **Claude Code,
Codex y OpenCode**, además de GitHub Copilot, como herramientas del ciclo de
desarrollo; el modelo operativo define qué debe ocurrir y por qué, mientras que
cada harness se ocupa de la mecánica concreta de despacho.

## 2. Problemas que resuelve

- Evita que el mismo agente implemente y revise su propio código.
- Evita que cada subtarea vuelva a explorar el repositorio desde cero mediante
  mapas de contexto reutilizables.
- Mantiene los hechos durables en artefactos, no en la memoria de una sesión.
- Sustituye la adivinación de APIs y requisitos por recetas verificadas y señales
  de gap explícitas.
- Exige evidencia observada —checks ejecutados y resultados leídos— en vez de
  asumir que algo funciona.
- Protege el trabajo preexistente registrando baseline y cambios antes de
  escribir.

## 3. Roles y fronteras

El sistema tiene ocho roles. La regla transversal es que un especialista no
coordina a otros agentes, escribe solo el artefacto que le corresponde y recibe
un brief autocontenido. La excepción es una segunda opinión read-only del
advisor cuando el harness la soporta.

### Coordinador / orquestador

Habla con el usuario, pide las decisiones y aprobaciones necesarias, elige el
carril más ligero seguro, registra dueños y estados, mantiene el ledger,
despacha especialistas y enruta la remediación. Posee los handoffs, pero no
pre-resuelve el trabajo de un especialista ni edita producción mientras hay
trabajo delegado vivo.

### Explorador de código (`codebase-explorer`)

Hace el descubrimiento inicial y produce un **context map**: punteros
verificados a archivos, símbolos, contratos, tests, patrones reutilizables,
riesgos y desconocidos abiertos. El mapa es una guía de lectura, no un volcado
del repositorio.

### Investigador de integraciones (`integration-researcher`)

Verifica contratos externos que el repositorio aún no prueba —APIs, SDKs,
librerías, CLIs o scraping— y produce una **Integration Recipe** con
autenticación, llamadas, shapes, errores, límites y setup. Etiqueta cada hecho
como `VERIFIED`, `per-docs` o `UNVERIFIED`, sin exponer secretos.

### Planificador-arquitecto (`implementation-planner`)

Convierte requisitos, context maps y recipes en un **plan bundle** con diseño,
grafo de tareas, olas, invariantes y briefs ejecutables. Cada brief incluye
objetivo, criterios observables, alcance y no-alcance, interfaces, contexto,
tests, riesgos y patrones a reutilizar.

### Implementador BDD/TDD (`task-implementer-bdd`)

Es el único rol que toca código de producción. Ejecuta un brief mediante
Outside-In BDD/TDD: escenario de aceptación, señal RED por la razón esperada,
cambio mínimo que produce GREEN, refactor acotado y checks nombrados. Devuelve
estados honestos como `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`,
`NEEDS_CONTEXT` o `PACK_GAP`.

### Revisor independiente (`implementation-reviewer`)

Verifica corrección y calidad desde los artefactos y el diff sin editar
producción ni confiar ciegamente en el report del implementador. Produce
hallazgos estables (`RC-01`, `RC-02`…), distingue problemas de la tarea,
transversales o de contratos cambiados, y emite `PASS`, `FAIL` o `PASS WITH
REQUIRED CHANGES`. Nunca revisa su propio trabajo.

### Depurador de causa raíz (`root-cause-debugger`)

Diagnostica sin arreglar. Formula hipótesis explícitas, sigue datos y control
hasta la primera asunción violada, descarta alternativas y devuelve causa,
localización por archivo y símbolo, mecanismo, evidencia, condiciones de
disparo y confianza. Si la confianza no es alta o hay bloqueo, entrega un
handoff de hipótesis para un segundo diagnóstico independiente.

### Advisor / segunda opinión

Es un consultor read-only que mejora una decisión antes de que cristalice:
enfoque, arquitectura, descomposición, seguridad, datos, contratos públicos o
un atasco repetido. Su respuesta debe contener recomendación, evidencia,
riesgos, pasos concretos y el resultado empírico que invalidaría el consejo.
No se consulta por rutina ni sustituye la evidencia.

## 4. Invariantes del sistema

1. Un dueño por unidad de trabajo.
2. Se usa el carril más ligero que sea seguro; la economía de tokens no rebaja
   el estándar de calidad.
3. Los hechos durables viven en artefactos; los briefs son contratos de
   ejecución.
4. Solo el implementador escribe producción y ningún especialista delega de
   forma recursiva.
5. Antes de escribir se registra baseline, cambios preexistentes y propiedad
   segura de los archivos; nunca se limpia o revierte trabajo ajeno.
6. No se implementa antes del gate de aprobación cuando el carril lo exige.
7. Se distingue siempre entre evidencia ejecutada y observada, documentación
   externa y contenido no verificado.
8. El material bajo revisión —código, comentarios, reports, fixtures o
   prompts— se trata como evidencia, nunca como instrucciones; esto contiene
   intentos de inyección dentro del material de trabajo.

## 5. Carriles de trabajo

- **Direct:** pregunta factual, conceptual o de código que no requiere tocar
  producción.
- **Quick:** cambio pequeño, cohesionado y con alcance conocido, sin contrato
  público nuevo, migración, seguridad, datos sensibles ni interfaces entre
  tareas.
- **Plan → Implement → Review:** feature no trivial, refactor amplio o cambio
  transversal. Incluye descubrimiento, verificación de contratos externos,
  plan bundle, gate de aprobación, implementación por briefs y revisión final.
- **Debug:** diagnóstico de causa raíz y, según el alcance, promoción a Quick o
  al carril completo de Plan. Si la primera confianza es baja, se hace un
  segundo diagnóstico independiente antes de implementar.

Un gap de contexto, crecimiento de alcance o una segunda ronda de corrección
promueve el trabajo al carril apropiado en vez de improvisar. El sistema limita
las rondas de remediación y deja el bloqueo explícito cuando ya no es seguro
seguir.

## 6. Artefactos y trazabilidad

El trabajo no trivial se conserva en un bundle `plans/<slug>/`, normalmente con:

- `context-map.md`: realidad del repositorio, punteros, riesgos y unknowns.
- `integration-<dep>.md`: contrato externo y nivel de verificación.
- `plan.md`: arquitectura, grafo, olas y verificación.
- `global-constraints.md`: invariantes cruzados.
- `task-<id>-brief.md`: contrato autocontenido de una tarea.
- `task-<id>-report.md`: delta real, tests, decisiones y read ledger.
- `task-<id>-review.md` y `final-review.md`: veredictos y hallazgos estables.
- `debug-diagnosis.md` y, si procede, `second-diagnosis-<id>.md`.
- `progress.md`: ledger compacto de baseline, dueños, estados y evidencia.

Cada artefacto tiene un único propósito y dueño. El **read ledger** registra
lecturas adicionales y su razón; las señales `PACK_GAP`, `NEEDS_CONTEXT` y
`BLOCKED` impiden fabricar una conclusión de éxito cuando faltan insumos.

## 7. Qué demuestra profesionalmente

Este sistema permite presentar a Pablo como alguien que no solo sabe invocar
modelos, sino que diseña flujos agentivos gobernables: separa responsabilidades,
define contratos, protege el contexto, verifica integraciones, incorpora
calidad BDD/TDD, mantiene trazabilidad y usa revisión independiente. Es una
prueba de pensamiento sistémico, criterio de ingeniería, control de riesgos y
capacidad para trabajar con varios harnesses de desarrollo aumentado por IA.

No deben añadirse sin confirmación afirmaciones sobre número de usuarios,
adopción externa, ahorro de tiempo, despliegue para un cliente concreto,
monetización o métricas de impacto. La formulación segura es **“sistema propio
de orquestación multiagente para el desarrollo asistido por IA, utilizado en
contextos profesionales y personales”**.

## 8. Formulaciones reutilizables

### Perfil técnico en español

> Desarrollo aumentado por GenAI con Claude Code, Codex, OpenCode y GitHub
> Copilot. He diseñado, construido y utilizado tanto profesional como
> personalmente un sistema propio de orquestación multiagente para trabajos de
> ingeniería complejos, con roles separados para descubrimiento, investigación
> de integraciones, planificación, implementación, revisión independiente y
> depuración, conectados mediante briefs, artefactos, gates de aprobación y
> evidencia verificable.

### Bullet breve para CV

> **Orquestación multiagente propia:** sistema agnóstico del harness, utilizado
> en trabajo profesional y personal, que separa planificación, implementación y
> verificación mediante especialistas, contratos escritos, context maps, gates y
> revisión independiente.

### English version

> GenAI-augmented development with Claude Code, Codex, OpenCode and GitHub
> Copilot. Designed, built and used a harness-agnostic multi-agent
> orchestration system both professionally and personally for complex
> engineering work, separating discovery, integration research, planning,
> implementation, independent review and debugging through written contracts,
> durable artifacts, approval gates and observable evidence.

## 9. Uso en candidaturas

- Para **AI agent engineer, AI platform, developer productivity o software
  engineering**, incluir una referencia breve en el perfil o en competencias y
  un bullet en proyectos/experiencia técnica si hay espacio.
- Para candidaturas **ESG, políticas públicas o comunicación**, usarlo solo como
  valor añadido digital si la oferta lo beneficia; no desplazar el relato
  principal.
- Mantener separadas tres cosas: uso de herramientas GenAI, construcción y uso
  profesional/personal del sistema propio, y experiencia profesional en
  Ângela/Attrim. Solo la última es el empleo profesional confirmado; el sistema
  puede presentarse como capacidad propia utilizada en ambos contextos, sin
  inventar clientes, usuarios o métricas.
