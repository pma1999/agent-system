# -*- coding: utf-8 -*-
"""Diagnostico de un texto frente a detectores de IA.

    python perfil.py perfil    texto.txt          # cadencia, anclajes y marcos de parrafo
    python perfil.py segmentos informe.json       # fragmentos de Pangram + perfil humano vs IA
    python perfil.py comparar  antes.json despues.json   # que etiquetas cambiaron y donde

El valor de `segmentos` es que un texto mixto trae dentro su propia muestra de estilo: los
fragmentos que el detector marca como humanos son del autor. Comparar su perfil con el de los
fragmentos marcados como IA da los objetivos numericos de ese documento concreto.

Los objetivos SIEMPRE salen del propio documento. No hay un perfil humano universal: en un ensayo
periodistico medido, los tramos humanos tenian mas varianza y mas frases cortas que los marcados;
en un capitulo de tesis medido, exactamente lo contrario. Aplicar el numero de otro texto lleva en
direccion equivocada.
"""
import difflib
import io
import json
import re
import statistics as st
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

MAY = 'A-ZÁÉÍÓÚÑÜ'
MIN = 'a-záéíóúñü'

MESES = (r'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|'
         r'noviembre|diciembre|january|february|march|april|june|july|august|september|'
         r'october|november|december')

# Aperturas y bisagras que anuncian o interpretan el contenido en lugar de darlo. Es el molde de
# parrafo que separa la prosa generada de la humana. Hay dos familias porque el molde cambia de
# vestido segun el genero: en prosa divulgativa anuncia datos, en prosa academica anuncia tesis.
MARCOS_DIVULGATIVO = [
    r'(?:los |las |estos |estas )?(?:datos|números|numeros|cifras|estadísticas|estadisticas)\b[^.]{0,40}\b(?:reflejan|muestran|revelan|indican|enseñan|apuntan|dibujan)',
    r'si (?:miramos|repasamos|analizamos|observamos|atendemos|nos fijamos|echamos)',
    r'(?:a pesar de|pese a) (?:est[eoa]s?|ello|todo)',
    r'(?:resulta|es) (?:llamativo|significativo|revelador|interesante|clave)',
    r'(?:esto|ello|lo cual) (?:pone de manifiesto|demuestra|evidencia|refleja|revela|confirma|subraya)',
    r'(?:como|tal y como) (?:veremos|hemos visto|se ha visto|se puede observar)',
    r'(?:no|nada) (?:es|resulta) (?:casual|casualidad|baladí|baladi)',
    r'(?:el|un) (?:análisis|analisis|examen|estudio|repaso) (?:de |detallado )?[^.]{0,30}(?:revela|muestra|permite)',
    r'(?:todo |)(?:esto|ello) (?:se traduce|se explica|tiene que ver|responde a)',
]
MARCOS_ACADEMICO = [
    r'(?:aquí|ahí|en esto|en ello|en esta tensión) radica',
    r'(?:el|un) (?:problema|núcleo|nudo|punto) (?:central|de fondo|clave)\b[^.]{0,30}(?:es|radica|reside|está|esta)',
    r'su (?:argumento|tesis|planteamiento|propuesta|aportación|aportacion) (?:central |principal |)es que',
    r',\s*por (?:lo )?tanto,\s*no (?:es|opera|funciona|constituye|se trata)',
    r'no (?:es|opera|funciona|constituye|se trata de)\b[^.]{0,60}\bsino\b',
    r'(?:est[ae]|es[ae]) (?:crítica|critica|distinción|distincion|noción|nocion|categoría|categoria|perspectiva|enfoque|lectura|operación|operacion)\b[^.]{0,30}(?:no |)(?:opera|funciona|permite|nos permite)',
    r'(?:lo que|esto|ello) (?:nos |)(?:permite|obliga a|invita a|abre|exige)',
    r'en (?:definitiva|síntesis|sintesis|suma|resumen)',
    r'dicho (?:de otro modo|de otra forma|de otra manera|en otros términos)',
    r'(?:conviene|cabe|merece la pena|es importante|es preciso|es necesario|hay que) (?:señalar|senalar|destacar|subrayar|recordar|notar|mencionar|apuntar|advertir|matizar|tener en cuenta)',
    r'(?:el|un) objetivo de (?:est[ae]|la presente) (?:sección|seccion|apartado|capítulo|capitulo|tesis)',
    r'(?:esa|esta) es la (?:tarea|función|funcion|finalidad) de (?:esta|este)',
    r'(?:sistematiza|articula|desarrolla|formula|acuña|acuna|conceptualiza|plantea),\s*(?:por último|por ultimo|además|ademas|asimismo|en este sentido|a su vez),',
    r'(?:la|una) (?:clave|cuestión|cuestion|pregunta) (?:aquí |aqui |)(?:es|está en|esta en|reside en)',
    r'desde (?:esta|esa) (?:perspectiva|óptica|optica|clave|lente|mirada)',
    r'de ahí que',
    r'(?:it is|it\'s) (?:important|worth) (?:to note|noting|mentioning)',
    r'(?:this|these) (?:highlights?|underscores?|demonstrates?|reflects?|reveals?)',
]
MARCOS_RE = [re.compile(p, re.I) for p in MARCOS_DIVULGATIVO + MARCOS_ACADEMICO]


def frases(txt):
    txt = re.sub(r'\s+', ' ', txt)
    return [f.strip() for f in re.split(r'(?<=[.!?])\s+', txt) if len(f.strip()) > 3]


def parrafos(txt):
    """Devuelve los parrafos del texto, eligiendo entre dos particiones posibles.

    Hay tres formas de que un texto marque sus parrafos y las tres aparecen en la practica:
    linea en blanco entre parrafos, un solo salto de linea por parrafo (lo que produce Word al
    exportar a .txt), y salto duro cada 80 caracteres (lo que produce copiar de un PDF).
    Elegir mal arruina el diagnostico sin avisar: por linea en blanco, un .txt de Word cae en
    dos o tres bloques de cientos de palabras; por linea, un PDF cae en decenas de "parrafos"
    de doce palabras.

    El criterio es el tamano resultante. Un parrafo real anda entre 20 y 300 palabras.
    """
    ps = [p.strip() for p in re.split(r'\n\s*\n', txt) if p.strip()]
    lineas = [l.strip() for l in txt.split('\n') if l.strip()]

    def media(xs):
        return sum(len(x.split()) for x in xs) / float(len(xs)) if xs else 0.0

    m_ps, m_li = media(ps), media(lineas)

    # Las lineas sueltas son parrafos plausibles y los bloques por linea en blanco son
    # demasiado grandes: el texto separa por salto simple y las lineas en blanco son sueltas.
    if len(lineas) > len(ps) and 20 <= m_li <= 300 and m_ps > 300:
        return lineas
    if len(ps) >= 2 and m_ps <= 300:
        return ps
    if len(lineas) <= 2:
        return ps
    if m_li >= 20:
        return lineas

    # Lineas cortas: salto duro, sin marca de parrafo que recuperar. Se agrupa en bloques de
    # ~120 palabras, que es lo mas parecido a un parrafo que se puede reconstruir.
    bloques, actual, n = [], [], 0
    for l in lineas:
        actual.append(l)
        n += len(l.split())
        if n >= 120:
            bloques.append(' '.join(actual))
            actual, n = [], 0
    if actual:
        bloques.append(' '.join(actual))
    return bloques

def cadencia(txt):
    L = [len(f.split()) for f in frases(txt)]
    if not L:
        return None
    return {
        'n': len(L), 'media': st.mean(L), 'desv': st.pstdev(L), 'max': max(L),
        'cortas': 100.0 * sum(1 for x in L if x <= 8) / len(L),
        'medias': 100.0 * sum(1 for x in L if 9 <= x <= 19) / len(L),
        'largas': 100.0 * sum(1 for x in L if 20 <= x <= 32) / len(L),
        'muylargas': 100.0 * sum(1 for x in L if x > 32) / len(L),
    }


def fmt_cadencia(c, etiqueta):
    if not c:
        return '  %-8s (sin frases)' % etiqueta
    return ('  %-8s n=%-4d media=%4.1f  desv=%4.1f  max=%-3d | <=8: %2.0f%%  9-19: %2.0f%%  '
            '20-32: %2.0f%%  >32: %2.0f%%' % (etiqueta, c['n'], c['media'], c['desv'], c['max'],
                                              c['cortas'], c['medias'], c['largas'], c['muylargas']))


def anclajes(txt):
    """Referentes concretos: nombres propios, anios, fechas, cifras y citas literales."""
    propios = set()
    for f in frases(txt):
        for tok in re.findall(r'[%s][%s]+' % (MAY, MIN), f[1:] if f else ''):
            propios.add(tok)
    anios = re.findall(r'\b(?:19|20)\d{2}\b', txt)
    meses = re.findall(MESES, txt, re.I)
    cifras = re.findall(r'\d[\d.,]*\s*%|\b\d[\d.,]*\b', txt)
    citas = re.findall(r'«[^»]{6,}»|"[^"]{6,}"|“[^”]{6,}”', txt)
    return {'propios': sorted(propios), 'anios': anios, 'meses': meses, 'cifras': cifras,
            'citas': citas,
            'total': len(propios) + len(anios) + len(meses) + len(cifras) + len(citas)}


def densidad(txt):
    pal = max(len(txt.split()), 1)
    return 100.0 * anclajes(txt)['total'] / pal


def marcos(txt):
    hits = []
    for f in frases(txt):
        for rx in MARCOS_RE:
            if rx.search(f[:90]):
                hits.append(f[:110])
                break
    return hits


def cmd_perfil(path):
    t = io.open(path, encoding='utf-8').read()
    ps = parrafos(t)
    print('=' * 78)
    print('PERFIL DE %s  (%d palabras, %d parrafos)' % (path, len(t.split()), len(ps)))
    print('=' * 78)

    print('\n-- Cadencia --')
    print(fmt_cadencia(cadencia(t), 'texto'))
    print('  No hay objetivo hasta que midas. El perfil humano NO es universal: en un ensayo')
    print('  periodistico los tramos humanos tenian mas varianza y mas frases cortas que los')
    print('  marcados; en un capitulo de tesis, menos de ambas. Saca el objetivo de los')
    print('  fragmentos humanos del propio documento con el subcomando `segmentos`.')

    med = st.median([densidad(p) for p in ps if len(p.split()) >= 25] or [0])
    print('\n-- Anclajes por parrafo (nombres propios, anios, cifras, citas) --')
    print('  mediana del documento: %.1f por 100 palabras' % med)
    flojos = []
    for i, p in enumerate(ps):
        pal = len(p.split())
        if pal < 25:
            continue
        a, d = anclajes(p), densidad(p)
        bajo = d < med * 0.5
        if bajo:
            flojos.append(i)
        print('%s%-3d %4d pal | dens %5.1f | propios %-2d anios %-2d cifras %-2d citas %-2d | %s' % (
            '>> ' if bajo else '   ', i, pal, d, len(a['propios']), len(a['anios']),
            len(a['cifras']), len(a['citas']), p[:44].replace('\n', ' ')))
    if flojos:
        print('\n  %d parrafos con menos de la mitad de la densidad mediana (>>). En un texto' % len(flojos))
        print('  academico, donde todo parrafo cita por convencion, mira ademas COMO llega la')
        print('  cita: entregada casi literal cuenta, parafraseada dentro de una subordinada')
        print('  de sintesis no.')
        rachas, actual = [], []
        idx = set(flojos)
        for i in range(len(ps)):
            if i in idx:
                actual.append(i)
            elif actual:
                rachas.append(actual); actual = []
        if actual:
            rachas.append(actual)
        peor = max(rachas, key=lambda r: sum(len(ps[i].split()) for i in r)) if rachas else None
        if peor and len(peor) > 1:
            print('  Racha mas larga: parrafos %s (%d palabras seguidas). Un tramo abstracto' % (
                '-'.join(str(i) for i in peor), sum(len(ps[i].split()) for i in peor)))
            print('  contiguo se marca por serlo, y cuanto mas largo, peor.')

    ms = marcos(t)
    print('\n-- Marcos de parrafo (frases que anuncian o interpretan en vez de dar) --')
    if ms:
        for m in ms:
            print('  - %s' % m)
        print('\n  %d encontrados. Borrarlos y abrir por el hecho es la palanca mas grande.' % len(ms))
        print('  Hay falsos positivos: una frase asi dentro de un fragmento que el detector')
        print('  marca como humano no se toca. Manda la medicion, no el patron.')
    else:
        print('  Ninguno con los patrones conocidos, lo que NO significa que no los haya: la')
        print('  lista no cubre las variantes reordenadas ni el vocabulario de cada disciplina.')
        print('  Lee los tramos marcados buscando frases que preparan al lector para el')
        print('  contenido, o que lo resumen despues, en lugar de darlo.')


def cmd_segmentos(path):
    d = json.load(io.open(path, encoding='utf-8'))
    t = d['text']
    f = d.get('fractions', {})
    print('=' * 78)
    print('VEREDICTO : %s  (%.1f%% de probabilidad global)' % (d['verdict'], 100 * d['ai_likelihood']))
    print('REPARTO   : IA %.1f%% | IA-asistida %.1f%% | Humano %.1f%%   (%d fragmentos, %d palabras)' % (
        100 * f.get('ai', 0), 100 * f.get('ai_assisted', 0), 100 * f.get('human', 0),
        d.get('segment_counts', {}).get('total', len(d['segments'])), d.get('word_count', 0)))
    print('=' * 78)

    marcadas = 0
    hum_flag = False
    print('\n%-3s %-14s %-7s %7s %6s  %s' % ('#', 'etiqueta', 'conf', 'IA%', 'pal', 'inicio'))
    for i, s in enumerate(d['segments']):
        hz = ''
        if s.get('is_humanized'):
            hz = '  [HUMANIZADO score=%s]' % s.get('humanizer_score')
            hum_flag = True
        if s['label'] != 'Human':
            marcadas += s.get('word_count', 0)
        print('%-3d %-14s %-7s %6.1f%% %6d  %s%s' % (
            i, s['label'], s['confidence'], 100 * s['ai_likelihood'], s.get('word_count', 0),
            t[s['start']:s['start'] + 56].replace('\n', ' '), hz))
    print('\nPalabras marcadas como no humanas: %d  <- el mejor indicador de progreso entre' % marcadas)
    print('iteraciones. El porcentaje global se mueve poco mientras el bloque marcado se encoge.')
    print('Marca de humanizador automatico: %s' % ('SI, revisar' if hum_flag else 'ninguna'))

    hum = ' '.join(t[s['start']:s['end']] for s in d['segments'] if s['label'] == 'Human')
    ia = ' '.join(t[s['start']:s['end']] for s in d['segments'] if s['label'] != 'Human')
    if not hum.strip() or not ia.strip():
        print('\n(Texto homogeneo: no hay los dos tipos de fragmento, no se puede sacar el perfil')
        print(' objetivo. Pide al usuario otro texto suyo del mismo registro que pase por humano.)')
        return

    ch, ci = cadencia(hum), cadencia(ia)
    print('\n-- Perfil comparado: ESTE es tu objetivo, no ningun numero de otro texto --')
    print(fmt_cadencia(ch, 'HUMANO'))
    print(fmt_cadencia(ci, 'IA'))
    if ch and ci:
        n = min(ch['n'], ci['n'])
        if n < 12:
            print('  (Ojo: solo %d frases en el lado menor. Perfil orientativo, no lo persigas' % n)
            print('   al decimal.)')
        dif = ch['desv'] - ci['desv']
        if abs(dif) >= 2:
            print('  Direccion: los tramos humanos tienen %s varianza que los marcados (%+.1f).' % (
                'MAS' if dif > 0 else 'MENOS', dif))
    ah, ai_ = anclajes(hum), anclajes(ia)
    ph, pi = max(len(hum.split()), 1), max(len(ia.split()), 1)
    print('\n  anclajes por 100 palabras   HUMANO %.1f   IA %.1f' % (
        100.0 * ah['total'] / ph, 100.0 * ai_['total'] / pi))
    print('    nombres propios            HUMANO %.1f   IA %.1f' % (
        100.0 * len(ah['propios']) / ph, 100.0 * len(ai_['propios']) / pi))
    print('    citas literales            HUMANO %.1f   IA %.1f' % (
        100.0 * len(ah['citas']) / ph, 100.0 * len(ai_['citas']) / pi))

    mi = marcos(ia)
    if mi:
        print('\n-- Marcos DENTRO de los tramos marcados (borrar estos primero) --')
        for m in mi:
            print('  - %s' % m)


def _firma(t, s):
    return re.sub(r'\s+', ' ', t[s['start']:s['start'] + 70]).strip()


def _buscar(t, firma):
    """Localiza la firma en el texto crudo tolerando cualquier espaciado.

    La firma viene con los espacios normalizados; el texto destino conserva sus saltos de
    linea. Buscarla tal cual falla en cuanto el fragmento cruza un salto (un titulo, por
    ejemplo) y reporta como REESCRITO un tramo intacto, que es justo la direccion en la que
    esta herramienta no se puede equivocar.
    """
    partes = [re.escape(w) for w in firma.split()]
    if not partes:
        return -1
    m = re.search(r'\s+'.join(partes), t)
    return m.start() if m else -1


def cmd_comparar(pa, pb):
    """Que etiquetas cambiaron entre dos mediciones, y cuales lejos de lo editado.

    Editar una frase puede reclasificar un parrafo distante que no se toco: el clasificador
    resegmenta el documento entero. Sin este diff, esas regresiones se descubren tarde.
    """
    a = json.load(io.open(pa, encoding='utf-8'))
    b = json.load(io.open(pb, encoding='utf-8'))
    ta, tb = a['text'], b['text']
    print('=' * 78)
    print('%s  ->  %s' % (pa, pb))
    print('  %-22s %5.1f%% IA global | fraccion IA %.3f | %d palabras marcadas' % (
        a['verdict'], 100 * a['ai_likelihood'], a.get('fractions', {}).get('ai', 0),
        sum(s.get('word_count', 0) for s in a['segments'] if s['label'] != 'Human')))
    print('  %-22s %5.1f%% IA global | fraccion IA %.3f | %d palabras marcadas' % (
        b['verdict'], 100 * b['ai_likelihood'], b.get('fractions', {}).get('ai', 0),
        sum(s.get('word_count', 0) for s in b['segments'] if s['label'] != 'Human')))
    print('=' * 78)

    print('\n-- Que paso con cada fragmento del ANTES --')
    for i, s in enumerate(a['segments']):
        firma = _firma(ta, s)
        pos = _buscar(tb, firma)
        if pos < 0:
            m = difflib.SequenceMatcher(None, tb, firma).find_longest_match(0, len(tb), 0, len(firma))
            pos = m.a if m.size > len(firma) * 0.6 else -1
        if pos < 0:
            print('  %-3d %-14s -> REESCRITO   %s' % (i, s['label'], firma[:44]))
            continue
        dest = next((x for x in b['segments'] if x['start'] <= pos < x['end']), None)
        if dest is None:
            print('  %-3d %-14s -> ?            %s' % (i, s['label'], firma[:44]))
            continue
        if dest['label'] == s['label']:
            print('  %-3d %-14s =  igual       %s' % (i, s['label'], firma[:44]))
        else:
            flecha = 'MEJORA ' if dest['label'] == 'Human' else 'EMPEORA'
            print('  %-3d %-14s -> %-12s %s  [%s]' % (
                i, s['label'], dest['label'], firma[:44], flecha))
    print('\n  Un fragmento que empeora sin que lo tocaras es propagacion del clasificador, no')
    print('  culpa del texto que hay ahi. Si aparece, la edicion que la causo esta en otro')
    print('  sitio: vuelve a la mejor version y haz el cambio de otra manera.')


def main(argv):
    if len(argv) >= 3 and argv[1] == 'perfil':
        cmd_perfil(argv[2])
    elif len(argv) >= 3 and argv[1] == 'segmentos':
        cmd_segmentos(argv[2])
    elif len(argv) >= 4 and argv[1] == 'comparar':
        cmd_comparar(argv[2], argv[3])
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
