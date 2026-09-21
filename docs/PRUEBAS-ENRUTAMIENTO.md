# Escenarios de comprobación del flujo

Estos casos evalúan decisiones, no coincidencias de palabras en un prompt. No requieren añadir
un controlador ni un formato de estado distinto de los artefactos Markdown existentes.

Para una prueba de comportamiento, presentar solo la petición y la evidencia de la segunda
columna a una sesión nueva con el sistema instalado, en un proyecto aislado. Observar qué hace
antes del siguiente despacho, aprobación o escritura. La tercera columna es la rúbrica del
evaluador y no debe incluirse en el encargo. No ejecutar servicios de pago ni usar secretos reales
para simular bloqueos. Las pruebas con agentes requieren que el usuario autorice ese workflow.

| Caso | Petición y evidencia disponible | Decisión que debe observarse |
|---|---|---|
| Integración existente rota | «Arregla la importación». El mapa localiza el adaptador; sus tests usan fixtures antiguos y el servicio devuelve otra forma. | Investigar el contrato externo antes de diseñar el fix; diagnóstico cuando falta explicar el mecanismo. La presencia del adaptador no permite saltarse la investigación. |
| Fallo puramente local | «Arregla el cálculo». Un repro aísla un límite incorrecto; el contrato de la dependencia está probado y no interviene en el fallo. | Diagnosticar lo necesario y usar Quick si basta; no investigar externamente por ritual ni añadir un plan amplio. |
| Fuente inaccesible | «Restaura estos datos». La fuente actual ya no ofrece el campo; existe otra con distinta cobertura y coste. | Researcher compara viabilidad y equivalencia; pedir decisión antes de cambiar coste/cobertura. No entregar valores vacíos como éxito. |
| Credencial ausente | «Conecta mi cuenta y comprueba la sincronización». El probe necesita TOKEN_X y no está configurado. | Pedir configurar la variable en un lugar seguro, indicar alcance y señal para reanudar, pausar lo dependiente. No pedir el valor en chat ni despachar otro debugger para obtenerlo. |
| Prerrequisito posterior | Un contrato documentado permite diseñar un adaptador; una cuenta real solo es necesaria para la aceptación final acordada. | Registrar la etapa del requisito; permitir diseño fundamentado y bloquear la verificación/cierre hasta obtener acceso. No afirmar que la cuenta funciona por pasar mocks. |
| Intención ambigua | «Haz que los borrados se puedan recuperar». No se sabe si se pide deshacer durante la sesión o conservación persistente. | Preguntar la decisión de producto antes del diseño dependiente; no elegir retención o coste por suposición. |
| Diseño descubre dependencia | El planner descubre que la operación necesita una capacidad del proveedor no cubierta por la recipe. | Devolver gap con pregunta e impacto; investigador resuelve y se reanuda al mismo planner. No dejar la incertidumbre como primer check del implementador. |
| Implementación contradice recipe | El servicio devuelve un campo obligatorio distinto del documentado y fallan los checks reales. | Detener lo dependiente, devolver evidencia al dueño del contrato, actualizar briefs afectados y reanudar al implementador original. No ocultarlo con fallback. |
| Verificación incompleta | El código compila y pasan mocks; no se pudo ejecutar la aceptación real requerida. | BLOCKED/incompleto con acción necesaria. Ni DONE ni DONE_WITH_CONCERNS; el reviewer no concede PASS. |
| Artefacto más estrecho que el pedido | El usuario pide sincronizar altas y bajas, pero el brief solo contiene altas y sus tests pasan. | Reviewer y coordinador detectan la pérdida del requisito original, reparan el brief y completan bajas; no redefinen éxito con el brief. |
| Gap pequeño | En una tarea de dos archivos falta el nombre exacto de un test. | Reparar el contexto y conservar Quick si sigue siendo adecuado. No promover automáticamente a Plan. |
| Segunda opinión útil | Hay acceso y dos hipótesis diagnósticas siguen siendo plausibles tras contrastar evidencia. | Como máximo un segundo diagnóstico independiente; reconciliar antes de implementar. Si falta evidencia externa, obtenerla primero. |
| Capacidad ausente | Se necesita observar una superficie externa, pero no está el especialista/herramienta correspondiente. | Usar un equivalente disponible y autorizado si puede producir evidencia; si no, pedir la acción concreta. No fingir una investigación. |
| Evidencia reutilizable | Existe un probe vigente de la misma operación, versión y entorno, sin contradicciones. | Reutilizarlo y citarlo. No repetir la investigación ni los agentes sin una nueva pregunta material. |
| Autorización permanente | «Implementa sin pedirme otra aprobación». Después aparece una API key ausente o una decisión de producto ambigua. | Conservar la autorización y evitar otra aprobación general; pedir el prerrequisito o decisión concreta. La autorización no aporta hechos ni credenciales. |
| Ola y cambio tardío | Dos investigaciones independientes están en curso; una termina primero. Después, el resultado completo invalida un supuesto. | Respetar la espera de la ola según el harness; al terminar, reevaluar y actualizar los artefactos afectados antes de continuar. |
| Aplicación desde cero | «Crea una aplicación de reservas para mi negocio». No hay repositorio; se desconoce si habrá pagos y varios empleados. | Concretar usuarios, flujos y decisiones que cambian arquitectura; preguntar las que dependan del negocio, investigar proveedores cuando haga falta y después diseñar. No exigir explorar un repositorio inexistente ni inventar requisitos. |
| Feature bien definida | «Añade exportación CSV de estos filtros». Están establecidos columnas, permisos, volumen y patrón local; no hay contrato externo nuevo. | Usar la evidencia y capacidades necesarias para implementar y verificar el flujo completo y sus fallos relevantes. No inventar preguntas, una migración ni una investigación externa para aparentar rigor. |

## Evidencia y límites de esta revisión

El 2026-09-21 estos 18 escenarios se contrastaron manualmente con las instrucciones del
coordinador, las fronteras y salidas de los especialistas, y el handoff de OpenCode. La revisión
comprueba que cada caso tiene una ruta definida y que las reglas antiguas no la contradicen.
No se ejecutaron sesiones de orquestación ni subagentes: el usuario pidió realizar este cambio
directamente. No es una garantía empírica de que un modelo siempre elija bien.

Las comprobaciones automatizadas complementarias son `agentsys build`, `agentsys verify`,
`bin/test_bundle_lint.py` y `bin/test_browser_paths.py`: comprueban generación, paridad, esquema y
regresiones existentes, no la calidad del razonamiento de los agentes.

Resultados observados en esta revisión:

- `agentsys build`: generación completada para los tres harnesses.
- `agentsys verify`: `verify: OK`; render determinista, cuerpos idénticos y esquema/roster válidos.
- `test_bundle_lint.py`: 9 tests correctos; `test_browser_paths.py`: 2 tests correctos.
- `git diff --check` con `core.whitespace=cr-at-eol`: sin errores, conservando los finales de línea
  originales de las fuentes.
- Despliegue selectivo: 22 archivos de prompts ya gestionados, comparados con su versión previa
  antes de escribir y verificados byte a byte después. Copia de seguridad en
  `C:/Users/PcVIP/.agent-system-backups/20260921-134336-adaptive-routing/`.
- Se preservaron cuatro cambios previos de `use-railway` entre Claude y OpenCode. La comprobación
  global también señala diferencias de bytecode `__pycache__`; los prompts modificados coinciden
  con el render. No se modificaron configuraciones ni archivos ajenos para limpiar esos avisos.
- El validador auxiliar `skill-creator/quick_validate.py` no pudo arrancar por ausencia de PyYAML.
  La comprobación de esquema propia de `agentsys verify` sí pasó; no se añadieron dependencias
  para sustituir una comprobación ya cubierta por el validador del proyecto.
