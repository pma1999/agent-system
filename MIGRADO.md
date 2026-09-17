# Esta rama esta congelada

El sistema multiagentico ya no se sincroniza con tres ramas cuyos working trees eran las carpetas
de configuracion. Ahora hay **una sola fuente de verdad**, la rama `main` del mismo repo, y
`~/.claude`, `~/.codex` y `~/.config/opencode` son destinos de despliegue.

El motivo: con tres copias literales de los mismos prompts habia que editarlos tres veces a mano, y
acabaron divergiendo. Hoy los cuerpos de prompt existen una sola vez y `verify` demuestra en cada
ejecucion que los tres harnesses comparten el mismo texto.

## Migrar este PC

```bash
git clone https://github.com/pma1999/agent-system.git ~/agent-system
cd ~/agent-system

python bin/agentsys.py install --dry-run     # PARATE AQUI y lee los "rechazados"
```

Los rechazados vienen con motivo. `cambio local sin publicar` es trabajo que este PC nunca subio:
miralo con `git -C ~/.claude diff -- <fichero>` antes de seguir. Nada se toca hasta que decidas.

```bash
python bin/agentsys.py install               # --force solo si ya revisaste los rechazados
python bin/agentsys.py install --retire-legacy
python bin/agentsys.py verify
```

Tu configuracion de maquina (settings.json, config.toml, opencode.jsonc) se conserva: las
plantillas se fusionan de forma aditiva y nunca sobrescriben un valor existente.

Guia completa: `~/agent-system/docs/INSTALACION.md`. Vision general: `~/agent-system/README.md`.

## Que se conserva de esta rama

Nada se ha perdido. El estado exacto de antes de la migracion esta en los tags
`pre-unificacion-20260917-master`, `-codex` y `-opencode`, y el sistema de orquestacion del lado
Claude previo a su borrado, en `orchestrator-system-v1`.
