# Skills

## 1. ticket-documenter

- **Nombre:** `ticket-documenter`
- **Descripción:** Transforma información vaga o parcial sobre una tarea en un ticket de trabajo completo, claro y accionable.
- **Trigger/uso:** Cuando el usuario pide documentar una tarea, issue o funcionalidad a implementar.
- **Instrucciones clave:**
  - Solicitar contexto, objetivo, problema a resolver, alcance, fuera de alcance, criterios de aceptación, dependencias, riesgos, prioridades y subtareas.
  - Aprovechar la conversación, archivos existentes (`README`, `CONTRIBUTING`, issues relacionados) y código relevante.
  - Detectar ambigüedad y hacer preguntas específicas antes de generar el ticket.
  - Mantener lenguaje técnico pero claro, siguiendo convenciones del proyecto si existen.
- **Herramientas a usar:** `read`, `grep`, `glob`, `websearch`
- **Salida esperada:** 
  - `docs/tickets/ticket-<id>.md` con estructura: Título, Estado, Prioridad, Tipo, Descripción, Alcance/Fuera de alcance, Criterios de aceptación (testables), Dependencias, Riesgos/mitigaciones, Subtareas, Referencias.
  - Resumen breve en consola con checklist generado.
- **Notas:** Generar criterios de aceptación en formato verificable (Dado/Cuando/Entonces) cuando aplique.

## 2. implementer

- **Nombre:** `implementer`
- **Descripción:** Genera, modifica y valida código para implementar un ticket, priorizando cambios mínimos, correctos y mantenibles.
- **Trigger/uso:** Cuando hay un ticket definido y se requiere implementar la solución.
- **Instrucciones clave:**
  - **Explorar contexto:** Leer archivos afectados, tests existentes, configuración (`package.json`, `tsconfig.json`, etc.) y convenciones.
  - **Planificar:** Descomponer en pasos pequeños antes de editar.
  - **Implementar:** Cambios mínimos, seguir estilo existente, reutilizar utilidades, evitar duplicación.
  - **Probar:** Escribir/actualizar pruebas unitarias/integración según corresponda. Priorizar cobertura de casos borde.
  - **Validar:** Ejecutar `lint`, `typecheck`, `build`, `test` si existen scripts definidos. Solo usar comandos válidos del repo.
  - **Seguridad:** No introducir secretos, logs sensibles o dependencias innecesarias.
  - **Iterar:** Si falla validación, corregir sin sobreescribir lógica no relacionada.
- **Herramientas a usar:** `read`, `edit`, `glob`, `grep`, `bash`, `todowrite`
- **Salida esperada:** 
  - Archivos modificados/creados con cambios coherentes.
  - Pruebas actualizadas/añadidas.
  - Log de validación (comandos ejecutados + resultados).
  - Checklist de tareas completadas vs plan.
- **Notas:** Nunca asumir framework de testing; detectar automáticamente (`jest`, `vitest`, `pytest`, `go test`, etc.).

## 3. work-explainer

- **Nombre:** `work-explainer`
- **Descripción:** Genera un informe HTML autocontenido que documenta y explica detalladamente el trabajo realizado.
- **Trigger/uso:** Después de implementar cambios, para compartir evidencia, revisión o trazabilidad.
- **Instrucciones clave:**
  - Detectar archivos modificados/creados/eliminados mediante `git diff --name-status` o comparación contextual.
  - Incluir resumen ejecutivo (qué, por qué, alcance).
  - Para cada cambio relevante: explicación técnica, motivación, alternativas consideradas, decisiones.
  - Añadir snippets con syntax highlighting por lenguaje.
  - Mostrar validación: comandos, resultados, capturas conceptuales de tests.
  - Listar breaking changes, migraciones o configuración requerida.
  - Sugerir follow-ups, deuda técnica y riesgos residuales.
  - Mantener tono objetivo y orientado a revisión de código.
- **Herramientas a usar:** `read`, `glob`, `grep`, `bash`, `write`
- **Salida esperada:** `docs/reports/work-explanation-<timestamp>.html` autocontenido (CSS inline, sin dependencias externas). Debe ser navegable por secciones y legible.
- **Notas:** Incluir enlaces a archivos con ruta relativa al repo para facilitar navegación.

## 4. requirements-extractor

- **Nombre:** `requirements-extractor`
- **Descripción:** Extrae, estructura y valida requerimientos desde documentos provistos (PDF, TXT, MD, JSON), identificando ambigüedad y gaps.
- **Trigger/uso:** Cuando se sube/provee documentación (PRD, especificación, reunión, correo) para convertirla en requisitos accionables.
- **Instrucciones clave:**
  - Parsear contenido completo preservando contexto.
  - Extraer: requerimientos funcionales (RF), no funcionales (RNF), actores, reglas de negocio, entidades, restricciones, interfaces, flujos, criterios de aceptación.
  - Clasificar por módulo/componente si se infiere.
  - Detectar ambigüedades, contradicciones, términos no definidos, información faltante.
  - Formular preguntas concretas y priorizables para clarificación.
  - Priorizar (Must/Should/Could/Won't) y estimar complejidad si solicitada.
  - Mapear a user stories (Como [actor], quiero [acción], para [beneficio]) cuando aplique.
- **Herramientas a usar:** `read`, `grep`, `glob`
- **Salida esperada:**
  - `docs/requirements/requirements.md` - versión humana: índice, glosario, requisitos detallados, matriz trazabilidad básica.
  - `docs/requirements/requirements.json` - versión estructurada con schema claro (id, tipo, prioridad, fuente, criterios, dependencias, estado).
  - `docs/requirements/clarifications.md` - preguntas abiertas con justificación.
- **Notas:** Mantener trazabilidad (fuente + línea/párrafo) cuando sea posible.
