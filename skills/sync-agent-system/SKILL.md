---
name: sync-agent-system
description: Sync, install or publish the personal multi-agent system. IMPORTANT - this machine still has the retired three-branch layout. The system now lives in one canonical repo and this skill only explains how to migrate. Use when the user says to sync, update, install or publish the agent system / agents / orchestrator / skills.
---

# Este PC todavia no esta migrado

No ejecutes `~/.claude/install.ps1` ni intentes publicar con el: reinstalaria el sistema antiguo
desde ramas congeladas, y un push subiria estado de maquina a ellas.

El sistema se movio a una sola fuente de verdad, la rama `main` del mismo repo. `~/.claude`,
`~/.codex` y `~/.config/opencode` pasan a ser destinos de despliegue.

## Que decirle al usuario

Explicale que este PC usa el esquema retirado y que la migracion es de una sola vez. Ofrece correr
el ensayo en seco primero, que no toca nada:

```bash
git clone https://github.com/pma1999/agent-system.git ~/agent-system
cd ~/agent-system
python bin/agentsys.py install --dry-run
```

**Pon la salida delante del usuario antes de seguir.** Lo que importa son los *rechazados*:

- `cambio local sin publicar` - trabajo que este PC nunca subio. Enseñaselo con
  `git -C ~/.claude diff -- <fichero>` (o `.codex` / `.config/opencode`) y pregunta que hacer.
  No elijas por el.
- `nunca estuvo gestionado` - un fichero suyo que el sistema no puso ahi. Misma regla.

Cuando lo haya decidido:

```bash
python bin/agentsys.py install               # --force solo si ya reviso los rechazados
python bin/agentsys.py install --retire-legacy
python bin/agentsys.py verify
```

Despues: abrir `claude` una vez para que instale los plugins, `/repatch-codex` si el parche quedo
pendiente, y `codex login` para el lado Codex. En WSL hay que pasar `--home /mnt/c/Users/<usuario>`.

A partir de ese momento esta misma skill queda sustituida por la version buena, que documenta el
ciclo normal `pull` -> `install` -> `verify` -> `publish`. Guia completa en
`~/agent-system/docs/INSTALACION.md`.
