/**
 * cv_data.example.js — EJEMPLO de archivo de datos para un CV.
 * Copia este archivo por candidatura (p. ej. cv_data.js) y cámbialo entero
 * para adaptarlo a la oferta. Aquí va reproducido el ángulo "Consultor de
 * Sostenibilidad / ESG" (español) como ejemplo completo y real.
 *
 * Genera con:  node build_cv.js cv_data.example.js
 * Colores por nombre: "navy", "blue", "grey".
 */

module.exports = {
  kind: "cv",
  meta: { filenameBase: "CV_Pablo_Miguel_Argudo_Consultor_Sostenibilidad" },

  header: {
    name: "PABLO MIGUEL ARGUDO",
    tagline: "Consultor de Sostenibilidad · CSRD/ESRS · Doble Materialidad · Datos & Digitalización ESG con IA",
    contact: "pablomiguelargudo@gmail.com · 617556028 · linkedin.com/in/pma1999 · github.com/pma1999 · Valencia, España · Disponible para trabajo híbrido/remoto en España y UE",
  },

  sections: [
    {
      type: "profile",
      title: "Perfil profesional",
      body: [
        { text: "Consultor de sostenibilidad especializado en el marco europeo de reporting: " },
        { text: "CSRD, ESRS, doble materialidad y Taxonomía UE", bold: true },
        { text: ". Cerca de tres años en consultora ESG como referencia regulatoria interna: analizo la normativa, resuelvo los casos límite que escalan del equipo consultor y traduzco los requisitos —de las emisiones de alcance 1, 2 y 3 (ESRS E1) al resto de datapoints ambientales, sociales y de gobernanza— a metodología, datos y herramientas. Diferencial poco común en el sector: " },
        { text: "digitalizo el trabajo ESG", bold: true },
        { text: ", diseñando y construyendo soluciones de gestión y reporting asistidas por IA dentro del Data Intelligence Hub del grupo Attrim. Formación cuantitativa en economía pública y comunicación escrita premiada a nivel nacional." },
      ],
    },

    {
      type: "experience",
      title: "Experiencia profesional",
      items: [
        {
          role: "Consultor de Sostenibilidad — Análisis Regulatorio & Soluciones Digitales",
          org: "Ângela Impact Economy (Grupo Attrim) · Data Intelligence Hub",
          meta: "Valencia, España · sept. 2023 – actualidad",
          bullets: [
            [{ text: "Referencia regulatoria interna en CSRD/ESRS: ", bold: true }, { text: "resolución de consultas y casos límite del equipo de consultoría; seguimiento continuo de la evolución del marco europeo (ESRS, VSME, Taxonomía UE, paquete Ómnibus) y de tendencias del sector." }],
            [{ text: "Traducción de la normativa a datos: ", bold: true }, { text: "identificación, jerarquización y digestión de los datapoints obligatorios de los ESRS —incluidos los requisitos climáticos de E1 (emisiones de alcance 1, 2 y 3, objetivos y planes de transición)— a especificaciones para el software de gestión y reporting ESG del grupo." }],
            [{ text: "Doble materialidad: ", bold: true }, { text: "dominio metodológico del proceso completo de identificación y evaluación de impactos, riesgos y oportunidades (IRO) conforme a ESRS 1, aplicado al diseño de la solución digital interna que guía el proceso con asistencia de IA." }],
            [{ text: "Digitalización ESG: ", bold: true }, { text: "diseño y construcción, como desarrollador principal del Hub, de soluciones internas asistidas por IA — plataformas de gestión estratégica ESG (políticas, objetivos y acciones), herramientas de soporte a procesos ESRS y sistemas de monitorización con procesamiento diario y alertas automatizadas, en producción y en uso por el equipo." }],
            [{ text: "Automatización de la captura y el tratamiento de datos: ", bold: true }, { text: "ingesta de documentación corporativa (PDF) mediante APIs de IA generativa y patrones RAG, reduciendo el trabajo manual del equipo consultor." }],
            [{ text: "Stack de trabajo: ", bold: true }, { text: "Python · Excel/PowerPoint avanzado · APIs de LLMs (Gemini, OpenAI, Anthropic) · Flask · Angular · PostgreSQL." }],
          ],
        },
        {
          role: "Investigador — Proyecto europeo SeBI (Jean Monnet Chair)",
          org: "Universitat de València",
          meta: "Valencia, España · jun. 2020 – mar. 2022",
          bullets: [
            [{ text: "Investigación en el proyecto europeo “Securing the Best Interest of the Child (SeBI)”, representando a España bajo la dirección del Jean Monnet Chair Juan Antonio Ureña." }],
            [{ text: "Análisis documental y normativo comparado entre países europeos; elaboración de informes de soporte al diseño de políticas públicas." }],
          ],
        },
        {
          role: "Asesor — Evaluación de Políticas Públicas (prácticas)",
          org: "Generalitat Valenciana · Conselleria d'Habitatge i Arquitectura Bioclimàtica",
          meta: "Valencia, España · feb. 2021 – may. 2021",
          bullets: [
            [{ text: "Diseño de mecanismos de evaluación de políticas públicas y de estrategias de mejora organizativa en el ámbito de vivienda y arquitectura bioclimática." }],
            [{ text: "Análisis de procesos administrativos y de relaciones entre actores; elaboración de informes y dictámenes." }],
          ],
        },
        {
          role: "Propietario y operador",
          org: "Bueno Bueno (hostelería)",
          meta: "Valencia, España · dic. 2017 – ene. 2019",
          bullets: [
            [{ text: "Adquisición y gestión integral de un negocio junto a un socio: plena responsabilidad de P&L, operaciones, equipo y clientes antes de los 20 años." }],
          ],
        },
        {
          role: "Profesor particular (Matemáticas y Economía)",
          org: "Tusclasesparticulares",
          meta: "Valencia, España · sept. 2017 – jun. 2020",
          bullets: [
            [{ text: "Tres cursos académicos explicando conceptos cuantitativos a estudiantes de ESO, Bachillerato y preparación PAU." }],
          ],
        },
      ],
    },

    {
      type: "bullets",
      title: "Proyectos personales — evidencia de capacidad digital",
      bullets: [
        [{ text: "9+ aplicaciones full-stack desplegadas en producción", bold: true }, { text: ", construidas de forma autónoma con workflow asistido por IA: Prompter (mejorador de prompts, con tracción orgánica real), Explainer (explicaciones multimodelo paso a paso), MapMyLearn (generador de cursos con investigación online) y otras. Repositorios públicos en github.com/pma1999." }],
      ],
    },

    {
      type: "education",
      title: "Educación",
      items: [
        {
          title: "Máster en Política Económica y Economía Pública",
          uni: "Universitat de València", dates: "2021 – 2022",
          desc: [{ text: "Formación cuantitativa en evaluación de políticas, economía del sector público y métodos empíricos." }],
        },
        {
          title: "Grado en Ciencias Políticas y de la Administración",
          uni: "Universitat de València", dates: "2017 – 2021",
          desc: [
            { text: "Beca de Excelencia Académica del Ministerio de Educación (2020). ", bold: true },
            { text: "Políticas públicas, análisis institucional y derecho administrativo." },
          ],
        },
      ],
      extra: [
        { text: "Formación complementaria: ", bold: true, color: "navy" },
        { text: "AI Engineering & Full-Stack Development — autoformación continua con evidencia pública (2024 – act.) · Learn Python 3 — Codecademy (2024) · What is Data Science? — IBM (2024)." },
      ],
    },

    {
      type: "bullets",
      title: "Distinciones",
      bullets: [
        [{ text: "2.º premio, Ford Fund Smart Mobility Challenge (2021): ", bold: true }, { text: "NetCare, propuesta de aplicación para el cuidado de personas mayores en certamen de iniciativas sostenibles social y medioambientalmente." }],
        [{ text: "Cuatro premios en certámenes nacionales de relato (2024 – 2025), tres de ellos primeros premios: ", bold: true }, { text: "evidencia externa de capacidad de síntesis y comunicación escrita." }],
        [{ text: "Ganador de la Olimpiada de Economía (2017)", bold: true }, { text: ", Universitat de València / Universitat Politècnica de València." }],
      ],
    },

    {
      type: "paragraph",
      title: "Idiomas",
      body: [
        { text: "Español y valenciano (catalán): ", bold: true }, { text: "nativos · " },
        { text: "Inglés: ", bold: true }, { text: "competencia profesional (B2–C1), uso diario." },
      ],
    },

    {
      type: "skills",
      title: "Capacidades",
      rows: [
        ["Marco regulatorio", "CSRD; ESRS (ambiental —incl. E1: emisiones de alcance 1, 2 y 3—, social y gobernanza); doble materialidad (IRO); Taxonomía UE; VSME y paquete Ómnibus; familiaridad con GHG Protocol y SBTi a través de los requisitos de E1. Capacidad demostrada de incorporar marcos nuevos con rapidez."],
        ["Metodologías", "análisis de materialidad; análisis regulatorio comparado; evaluación de políticas y programas; investigación documental y síntesis rigurosa."],
        ["Datos y análisis", "Python aplicado a tratamiento y automatización de datos; gestión de datapoints ESG y trazabilidad de la información; Excel avanzado; construcción de dashboards y herramientas de visualización a medida."],
        ["Digitalización e IA", "desarrollo full-stack (Flask, Angular, React); APIs de LLMs (Gemini, OpenAI, Anthropic, OpenRouter); RAG e ingesta automatizada de documentos; automatización de flujos de trabajo."],
        ["Herramientas", "Microsoft Office avanzado (Excel, PowerPoint, Word); Git/GitHub; PostgreSQL; despliegue cloud."],
      ],
    },
  ],
};
