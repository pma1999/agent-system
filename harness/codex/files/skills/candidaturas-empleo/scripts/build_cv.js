/**
 * build_cv.js — Motor de CV y carta de presentación de Pablo Miguel Argudo
 * =========================================================================
 *
 * QUÉ ES ESTO
 * -----------
 * Un ESQUELETO reutilizable. El "motor" (design tokens + helpers + render) es
 * ESTABLE y no se toca entre candidaturas. Lo que cambia en cada oferta es
 * ÚNICAMENTE el ARCHIVO DE DATOS que le pasas. Así los CVs salen visualmente
 * idénticos (misma identidad: navy/azul/gris, Arial, A4) pero el contenido se
 * adapta por completo a cada puesto para maximizar las opciones.
 *
 * Es el mismo sistema de diseño de los CVs reales de Pablo (build_cvs_v2.js /
 * build_parlament.js), refactorizado para separar diseño de contenido.
 *
 * CÓMO SE USA
 * -----------
 *   1. npm install docx        (una sola vez, en esta carpeta)
 *   2. Escribe un archivo de datos, p. ej. cv_data.js (copia cv_data.example.js)
 *   3. node build_cv.js cv_data.js                 -> genera <filenameBase>.docx
 *      node build_cv.js cv_data.js Salida.docx     -> nombre de salida explícito
 *   4. Para PDF:  bash to_pdf.sh <archivo.docx>     (LibreOffice headless)
 *
 * El archivo de datos exporta un objeto con `kind: "cv"` o `kind: "letter"`.
 * Ver el ESQUEMA completo más abajo y los ejemplos cv_data.example.js /
 * letter_data.example.js.
 *
 * =========================================================================
 * ESQUEMA DE DATOS
 * =========================================================================
 *
 * -- Runs de texto enriquecido (se usan en muchos campos) --
 *   Un "run" es { text, bold?, italics?, color? }. Un campo "richtext" es un
 *   array de runs, p. ej.:  [{ text: "Referente regulatorio: ", bold: true },
 *                            { text: "resuelvo casos límite del equipo." }]
 *   Colores disponibles por nombre: "navy", "blue", "grey" (o un hex de 6).
 *
 * -- kind: "cv" --
 *   {
 *     kind: "cv",
 *     meta:   { filenameBase: "CV_Pablo_Miguel_Argudo_Puesto" },   // sin extensión
 *     header: {
 *       name:    "PABLO MIGUEL ARGUDO",
 *       tagline: "Titular en una línea, a medida de la oferta",
 *       contact: "email · teléfono · linkedin · github · ubicación · disponibilidad",
 *     },
 *     sections: [ ...bloques... ]   // ver tipos de bloque abajo
 *   }
 *
 *   Tipos de bloque (cada uno lleva su `title`, salvo que se indique):
 *     { type: "profile",  title, body: richtext }                 // párrafo justificado
 *     { type: "paragraph",title, body: richtext }                 // idéntico a profile
 *     { type: "experience", title, items: [
 *         { role, org, meta, bullets: [ richtext, richtext, ... ] }, ...
 *     ]}
 *     { type: "bullets",  title, bullets: [ richtext, ... ] }     // lista suelta
 *     { type: "education",title, items: [
 *         { title, uni, dates, desc: richtext }, ...
 *       ], extra?: richtext }                                     // "extra": párrafo final opcional
 *     { type: "skills",   title, rows: [ [label, text], ... ] }   // "Label: texto"
 *
 * -- kind: "letter" --
 *   {
 *     kind: "letter",
 *     meta:   { filenameBase: "Carta_Pablo_Miguel_Argudo_Puesto" },
 *     header: { name: "PABLO MIGUEL ARGUDO", contact: "email · tel · ..." },
 *     recipient: {                     // todos opcionales
 *       org:  "Nombre de la empresa / oficina",
 *       ref:  "Ref.: Candidatura a ...",
 *       date: "Valencia, 22 de julio de 2026",
 *     },
 *     salutation: "Estimado equipo de ...,",
 *     paragraphs: [ richtext, richtext, ... ],
 *     closing:   "Atentamente,",
 *     signature: "Pablo Miguel Argudo",
 *   }
 *
 * =========================================================================
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat, BorderStyle,
} = require("docx");

// ---------- Design tokens (idénticos a los CVs reales de Pablo) ----------
const COLORS = { navy: "1F3A5F", blue: "2E5C8A", grey: "5A6470" };
const NAVY = COLORS.navy, BLUE = COLORS.blue, GREY = COLORS.grey;
const BODY = 20;      // 10pt
const SMALL = 18;     // 9pt
const NAME = 36;      // 18pt
const TAGLINE = 21;   // 10.5pt
const SECTION = 22;   // 11pt
const ROLE = 21;      // 10.5pt

// Resuelve un nombre de color ("navy"/"blue"/"grey") o hex a hex.
const col = (c) => (c == null ? undefined : (COLORS[c] || c));

// Comillas tipográficas, como en los CVs originales.
const fix = (s) => (s == null ? s : String(s).replace(/'/g, "’"));

// Convierte un "run" del esquema en un TextRun de docx, respetando color por nombre.
const toRun = (r, base) => new TextRun({ ...base, ...r, color: col(r.color) || base.color, text: fix(r.text) });
const mkRuns = (runs, base) => (runs || []).map((r) => toRun(r, base));

// ---------- Numbering (viñetas) ----------
const bulletsConfig = {
  config: [{
    reference: "bullets",
    levels: [{
      level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 340, hanging: 200 } } },
    }],
  }],
};

// ---------- Helpers de párrafo (mismos que en los scripts originales) ----------
const pName = (txt) => new Paragraph({
  spacing: { after: 40 },
  children: [new TextRun({ text: fix(txt), bold: true, size: NAME, color: NAVY })],
});

const pTagline = (txt) => new Paragraph({
  spacing: { after: 60 },
  children: [new TextRun({ text: fix(txt), size: TAGLINE, color: BLUE, bold: true })],
});

const pContact = (txt) => new Paragraph({
  spacing: { after: 60 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY, space: 4 } },
  children: [new TextRun({ text: fix(txt), size: SMALL, color: GREY })],
});

const pSection = (txt, first = false) => new Paragraph({
  keepNext: true,
  spacing: { before: first ? 120 : 170, after: 70 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 2 } },
  children: [new TextRun({ text: fix(txt).toUpperCase(), bold: true, size: SECTION, color: NAVY })],
});

const pBody = (runs, opts = {}) => new Paragraph({
  alignment: opts.justify === false ? AlignmentType.LEFT : AlignmentType.JUSTIFIED,
  spacing: { after: opts.after ?? 60, line: 250 },
  children: mkRuns(runs, { size: BODY }),
});

const pPosition = (role, org, meta) => [
  new Paragraph({
    keepNext: true,
    spacing: { before: 110, after: 20 },
    children: [
      new TextRun({ text: fix(role), bold: true, size: ROLE, color: NAVY }),
      new TextRun({ text: "   |   ", size: ROLE, color: GREY }),
      new TextRun({ text: fix(org), bold: true, size: BODY, color: BLUE }),
    ],
  }),
  new Paragraph({
    keepNext: true,
    spacing: { after: 40 },
    children: [new TextRun({ text: fix(meta), italics: true, size: SMALL, color: GREY })],
  }),
];

const pBullet = (runs, opts = {}) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  alignment: AlignmentType.JUSTIFIED,
  spacing: { after: opts.after ?? 30, line: 250 },
  children: mkRuns(runs, { size: BODY }),
});

const pSkillRow = (label, txt) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  spacing: { after: 40, line: 250 },
  children: [
    new TextRun({ text: fix(label) + ": ", bold: true, size: BODY, color: NAVY }),
    new TextRun({ text: fix(txt), size: BODY }),
  ],
});

const pEdu = (title, uni, dates, desc) => [
  new Paragraph({
    keepNext: true,
    spacing: { before: 90, after: 20 },
    children: [
      new TextRun({ text: fix(title), bold: true, size: BODY, color: NAVY }),
      new TextRun({ text: " — " + fix(uni) + " · " + fix(dates), size: BODY, color: GREY }),
    ],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 40, line: 250 },
    children: mkRuns(desc, { size: BODY }),
  }),
];

const makeDoc = (children) => new Document({
  numbering: bulletsConfig,
  styles: { default: { document: { run: { font: "Arial", size: BODY } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4
        margin: { top: 800, right: 850, bottom: 800, left: 850 },
      },
    },
    children,
  }],
});

// =========================================================================
// RENDER: CV
// =========================================================================
function renderCV(data) {
  const h = data.header || {};
  const out = [];
  if (h.name) out.push(pName(h.name));
  if (h.tagline) out.push(pTagline(h.tagline));
  if (h.contact) out.push(pContact(h.contact));

  const sections = data.sections || [];
  sections.forEach((s, i) => {
    const first = i === 0;
    const type = s.type || "paragraph";
    if (s.title) out.push(pSection(s.title, first));

    switch (type) {
      case "profile":
      case "paragraph":
        out.push(pBody(s.body, { after: 40 }));
        break;

      case "experience":
        (s.items || []).forEach((it, j) => {
          out.push(...pPosition(it.role, it.org, it.meta));
          const bullets = it.bullets || [];
          bullets.forEach((b, k) => {
            const last = k === bullets.length - 1;
            out.push(pBullet(b, { after: last ? 40 : 30 }));
          });
        });
        break;

      case "bullets": {
        const bullets = s.bullets || [];
        bullets.forEach((b, k) => {
          const last = k === bullets.length - 1;
          out.push(pBullet(b, { after: last ? 40 : 30 }));
        });
        break;
      }

      case "education":
        (s.items || []).forEach((it) => {
          out.push(...pEdu(it.title, it.uni, it.dates, it.desc || []));
        });
        if (s.extra) out.push(pBody(s.extra, { after: 40 }));
        break;

      case "skills":
        (s.rows || []).forEach(([label, txt]) => out.push(pSkillRow(label, txt)));
        break;

      default:
        throw new Error(`Tipo de sección desconocido: "${type}" (sección "${s.title || i}")`);
    }
  });

  return makeDoc(out);
}

// =========================================================================
// RENDER: CARTA DE PRESENTACIÓN
// =========================================================================
function renderLetter(data) {
  const h = data.header || {};
  const r = data.recipient || {};
  const out = [];

  if (h.name) out.push(pName(h.name));
  if (h.contact) {
    out.push(new Paragraph({
      spacing: { after: 80 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: NAVY, space: 4 } },
      children: [new TextRun({ text: fix(h.contact), size: SMALL, color: GREY })],
    }));
  }

  if (r.org) {
    out.push(new Paragraph({
      spacing: { before: 60, after: 40 },
      children: [new TextRun({ text: fix(r.org), bold: true, size: BODY, color: NAVY })],
    }));
  }
  if (r.ref) {
    out.push(new Paragraph({
      spacing: { after: 40 },
      children: [new TextRun({ text: fix(r.ref), size: BODY, color: GREY })],
    }));
  }
  if (r.date) {
    out.push(new Paragraph({
      spacing: { after: 170 },
      children: [new TextRun({ text: fix(r.date), italics: true, size: SMALL, color: GREY })],
    }));
  }

  const lp = (runs, opts = {}) => new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: opts.after ?? 130, line: 264 },
    children: mkRuns(runs, { size: BODY }),
  });

  if (data.salutation) out.push(lp([{ text: data.salutation }]));
  const paras = data.paragraphs || [];
  paras.forEach((p, i) => lp && out.push(lp(p, { after: i === paras.length - 1 ? 150 : 130 })));

  if (data.closing) {
    out.push(new Paragraph({
      spacing: { after: 20 },
      children: [new TextRun({ text: fix(data.closing), size: BODY })],
    }));
  }
  if (data.signature) {
    out.push(new Paragraph({
      children: [new TextRun({ text: fix(data.signature), bold: true, size: BODY, color: NAVY })],
    }));
  }

  return makeDoc(out);
}

// =========================================================================
// CLI
// =========================================================================
async function main() {
  const dataArg = process.argv[2];
  const outArg = process.argv[3];

  if (!dataArg) {
    console.error("Uso: node build_cv.js <archivo-datos.js> [salida.docx]");
    console.error("     El archivo de datos debe exportar { kind: 'cv' | 'letter', ... }");
    process.exit(1);
  }

  const dataPath = path.resolve(process.cwd(), dataArg);
  if (!fs.existsSync(dataPath)) {
    console.error(`No encuentro el archivo de datos: ${dataPath}`);
    process.exit(1);
  }

  const data = require(dataPath);
  const kind = data.kind || "cv";
  const doc = kind === "letter" ? renderLetter(data) : renderCV(data);

  const base = (data.meta && data.meta.filenameBase) || path.basename(dataArg).replace(/\.[^.]+$/, "");
  const outPath = path.resolve(process.cwd(), outArg || `${base}.docx`);

  fs.writeFileSync(outPath, await Packer.toBuffer(doc));
  console.log(`OK -> ${outPath}`);
}

// Permite importar los helpers/render desde otros scripts, o ejecutar como CLI.
module.exports = {
  renderCV, renderLetter, makeDoc,
  helpers: { pName, pTagline, pContact, pSection, pBody, pPosition, pBullet, pSkillRow, pEdu, mkRuns, fix },
  COLORS,
};

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}
