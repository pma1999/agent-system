# Carpeta gestionada

Este directorio es un **destino de despliegue**, no un repositorio.

Los ficheros de orquestacion (`agents/`, la skill orquestadora), las skills y las plantillas de
configuracion se generan desde la fuente canonica:

    ~/agent-system            (repo pma1999/agent-system, rama main)

Editar cualquiera de ellos aqui se pierde en el siguiente despliegue. Para cambiar algo, lee
`~/agent-system/README.md`: dice exactamente que fichero del canon toca.

    cd ~/agent-system
    python bin/agentsys.py status     # que hay gestionado y que ha derivado
    python bin/agentsys.py install    # regenera y despliega
    python bin/agentsys.py adopt      # recupera al canon un cambio hecho aqui a mano

Lo que NO se gestiona desde ahi (credenciales, sesiones, historial, caches, y los valores reales de
settings.json / config.toml / opencode.jsonc) es estado de esta maquina y se queda aqui.
