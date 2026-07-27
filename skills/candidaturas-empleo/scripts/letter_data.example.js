/**
 * letter_data.example.js — EJEMPLO de archivo de datos para una CARTA.
 * Copia y adapta por candidatura. Genera con: node build_cv.js letter_data.example.js
 * Mantiene la misma identidad visual que el CV (navy/azul/gris, Arial, A4).
 */

module.exports = {
  kind: "letter",
  meta: { filenameBase: "Carta_Pablo_Miguel_Argudo_Consultor_Sostenibilidad" },

  header: {
    name: "PABLO MIGUEL ARGUDO",
    contact: "pablomiguelargudo@gmail.com · 617556028 · linkedin.com/in/pma1999 · Valencia, España",
  },

  recipient: {
    org: "Equipo de Selección — [Nombre de la empresa]",
    ref: "Ref.: Candidatura a Consultor/a de Sostenibilidad (CSRD/ESRS)",
    date: "Valencia, 22 de julio de 2026",
  },

  salutation: "Estimado equipo de [empresa],",

  paragraphs: [
    [
      { text: "Me dirijo a ustedes para presentar mi candidatura al puesto de " },
      { text: "Consultor de Sostenibilidad", bold: true },
      { text: ". Llevo cerca de tres años trabajando en el marco europeo de reporting —CSRD, ESRS y doble materialidad— como referencia regulatoria interna de una consultora ESG, y creo que ese perfil encaja de lleno con lo que buscan." },
    ],
    [
      { text: "Mi trabajo consiste precisamente en " },
      { text: "traducir normativa compleja a criterios operativos, datos y herramientas", bold: true },
      { text: ": resuelvo los casos límite que escala el equipo consultor, sigo de cerca la evolución del marco (ESRS, VSME, Taxonomía UE, paquete Ómnibus) y llevo los requisitos —incluidas las emisiones de alcance 1, 2 y 3 del ESRS E1— hasta su implementación. A eso sumo un diferencial poco habitual en el sector: diseño y construyo soluciones digitales asistidas por IA que agilizan el propio trabajo ESG." },
    ],
    [
      { text: "Aporto además una base analítica sólida (Máster en Política Económica y Economía Pública, investigación europea) y una capacidad de comunicación escrita avalada por varios premios nacionales, útil para informes, memorias y presentaciones ante cliente. Me entusiasma la posibilidad de poner todo esto al servicio de su equipo." },
    ],
    [
      { text: "Les agradecería la oportunidad de comentarlo en persona. Gracias por su tiempo y consideración." },
    ],
  ],

  closing: "Atentamente,",
  signature: "Pablo Miguel Argudo",
};
