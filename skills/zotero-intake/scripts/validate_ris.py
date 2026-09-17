#!/usr/bin/env python3
"""Valida un fichero .ris contra el importador RIS real de Zotero 7.

El importador de Zotero falla en silencio: una linea mal formada se descarta y una
etiqueta que no corresponde al tipo de item acaba en una nota, sin aviso. Este script
hace visible eso antes de importar.

Uso:
    python validate_ris.py fichero.ris
    python validate_ris.py fichero.ris --strict   # los avisos tambien fallan

Codigos de salida: 0 sin errores, 1 con errores, 2 problema al leer el fichero.
Solo biblioteca estandar.
"""

import argparse
import re
import unicodedata
import sys

# Expresion exacta de RIS.js (Zotero 7): dos caracteres de etiqueta, 1-2 espacios, guion.
RIS_LINE = re.compile(r"^([A-Z][A-Z0-9]) {1,2}-(?: (.*))?$")

# TY -> tipo de item de Zotero, segun los mapas de RIS.js.
TYPE_MAP = {
    "JOUR": "journalArticle", "CHAP": "bookSection", "BOOK": "book", "RPRT": "report",
    "DATA": "dataset", "THES": "thesis", "CONF": "conferencePaper", "MGZN": "magazineArticle",
    "NEWS": "newspaperArticle", "BLOG": "blogPost", "ELEC": "webpage", "COMP": "computerProgram",
    "MANSCPT": "manuscript", "SLIDE": "presentation", "MAP": "map", "SOUND": "audioRecording",
    "VIDEO": "videoRecording", "MPCT": "film", "ART": "artwork", "PAT": "patent",
    "CASE": "case", "STAT": "statute", "BILL": "bill", "HEAR": "hearing", "PCOMM": "letter",
    "DICT": "dictionaryEntry", "ENCYC": "encyclopediaArticle", "ICOMM": "instantMessage",
    # aceptados al importar aunque Zotero no los exporte asi
    "GOVDOC": "report", "STAND": "report", "DBASE": "dataset", "EJOUR": "journalArticle",
    "JFULL": "journalArticle", "ABST": "journalArticle", "GEN": "journalArticle",
    "ECHAP": "bookSection", "EBOOK": "book", "EDBOOK": "book", "CLSWK": "book", "SER": "book",
    "CPAPER": "conferencePaper", "WEB": "webpage", "INPR": "manuscript", "UNPD": "manuscript",
    "PAMP": "manuscript", "UNBILL": "manuscript", "ADVS": "film", "CHART": "artwork",
    "FIGURE": "artwork", "MUSIC": "audioRecording", "MULTI": "videoRecording",
    "CTLG": "magazineArticle", "LEGAL": "case", "AGGR": "document", "ANCIENT": "document",
    "EQUA": "document", "GRNT": "document",
}

# Etiquetas validas para cualquier tipo.
UNIVERSAL = {
    "TY": "tipo", "TI": "titulo", "T1": "titulo", "AU": "autor", "A1": "autor",
    "A4": "traductor", "AB": "resumen", "KW": "etiqueta", "N1": "nota",
    "L1": "adjunto PDF", "L2": "adjunto HTML", "L4": "otro adjunto",
    "PY": "fecha (año)", "DA": "fecha", "Y1": "fecha", "ER": "fin de registro",
    "DO": "DOI", "LA": "idioma", "UR": "URL", "Y2": "fecha de consulta",
    "ST": "titulo corto", "DP": "catalogo", "DB": "archivo",
    "AN": "loc. en archivo", "CN": "signatura", "J2": "abreviatura de revista",
}

# Las universales que sí van a un campo concreto: hay que comprobar que ese campo
# exista en el tipo, o Zotero lo descartara igual que a las dependientes del tipo.
UNIVERSAL_FIELD = {
    "AB": "abstractNote", "LA": "language", "UR": "url", "Y2": "accessDate",
    "ST": "shortTitle", "DP": "libraryCatalog", "DB": "archive",
    "AN": "archiveLocation", "CN": "callNumber", "J2": "journalAbbreviation",
}

# Etiqueta -> significado por tipo. Generado cruzando el fieldMap de RIS.js
# con el esquema de tipos de Zotero. None = el valor se pierde; '__nota__' = acaba
# en una nota adjunta, no en un campo. No editar a mano.
BY_TYPE = {
    'A2': {'audioRecording': 'performer', 'bill': 'sponsor', 'book': 'editor de la serie', 'bookSection': 'editor', 'case': 'reporter', 'conferencePaper': 'editor', 'dictionaryEntry': 'editor', 'document': 'editor', 'email': 'recipient', 'encyclopediaArticle': 'editor', 'instantMessage': 'recipient', 'interview': 'interviewer', 'journalArticle': 'editor', 'letter': 'recipient', 'patent': 'issuingAuthority', 'presentation': 'presenter', 'report': 'editor de la serie', "_default": None},
    'A3': {'bill': 'cosponsor', 'book': 'editor', 'bookSection': 'editor de la serie', 'conferencePaper': 'editor de la serie', 'dictionaryEntry': 'editor de la serie', 'encyclopediaArticle': 'editor de la serie', 'film': 'producer', 'map': 'editor de la serie', 'radioBroadcast': 'producer', 'thesis': 'colaborador', 'tvBroadcast': 'producer', 'videoRecording': 'producer', "_default": None},
    'AD': {"_default": '__nota__'},
    'AV': {'annotation': None, 'attachment': None, 'bill': None, 'blogPost': None, 'case': None, 'email': None, 'forumPost': None, 'hearing': None, 'instantMessage': None, 'note': None, 'nsfReviewer': None, 'patent': None, 'podcast': None, 'presentation': None, 'statute': None, 'webpage': None, "_default": 'archiveLocation'},
    'BT': {'book': 'title', 'bookSection': 'titulo del libro', 'manuscript': 'title', "_default": '__nota__'},
    'C1': {'conferencePaper': 'lugar', 'map': 'scale', 'patent': 'filingDate', "_default": None},
    'C2': {'blogPost': 'comentarista', 'bookSection': 'autor del libro', 'patent': 'issueDate', "_default": None},
    'C3': {'artwork': 'tamaño', 'conferencePaper': 'titulo de las actas', 'patent': 'country', "_default": None},
    'CA': {"_default": '__nota__'},
    'CR': {'annotation': None, 'attachment': None, 'note': None, 'nsfReviewer': None, "_default": 'rights'},
    'CT': {'annotation': None, 'note': None, "_default": 'title'},
    'CY': {'audioRecording': 'lugar', 'book': 'lugar', 'bookSection': 'lugar', 'computerProgram': 'lugar', 'conferencePaper': 'lugar', 'dataset': 'ubicacion del repositorio', 'dictionaryEntry': 'lugar', 'encyclopediaArticle': 'lugar', 'hearing': 'lugar', 'manuscript': 'lugar', 'map': 'lugar', 'newspaperArticle': 'lugar', 'patent': 'lugar', 'preprint': 'lugar', 'presentation': 'lugar', 'radioBroadcast': 'lugar', 'report': 'lugar', 'standard': 'lugar', 'thesis': 'lugar', 'tvBroadcast': 'lugar', 'videoRecording': 'lugar', "_default": None},
    'ED': {"_default": 'editor'},
    'EP': {'bill': 'paginas', 'bookSection': 'paginas', 'case': 'paginas', 'conferencePaper': 'paginas', 'dictionaryEntry': 'paginas', 'encyclopediaArticle': 'paginas', 'hearing': 'paginas', 'journalArticle': 'paginas', 'magazineArticle': 'paginas', 'newspaperArticle': 'paginas', 'patent': 'paginas', 'report': 'paginas', 'statute': 'paginas', "_default": None},
    'ET': {'bill': 'sesion', 'book': 'edicion', 'bookSection': 'edicion', 'computerProgram': 'version', 'dataset': 'version', 'dictionaryEntry': 'edicion', 'encyclopediaArticle': 'edicion', 'hearing': 'sesion', 'map': 'edicion', 'newspaperArticle': 'edicion', 'statute': 'sesion', "_default": None},
    'H1': {"_default": '__nota__'},
    'H2': {"_default": '__nota__'},
    'ID': {"_default": '__nota__'},
    'IS': {'bookSection': 'numero de volumenes', 'dataset': 'version', 'journalArticle': 'numero', 'magazineArticle': 'numero', "_default": None},
    'JA': {'journalArticle': 'journalAbbreviation', "_default": None},
    'JF': {'blogPost': 'publicacion', 'bookSection': 'publicacion', 'conferencePaper': 'publicacion', 'dictionaryEntry': 'publicacion', 'encyclopediaArticle': 'publicacion', 'forumPost': 'publicacion', 'journalArticle': 'publicacion', 'magazineArticle': 'publicacion', 'newspaperArticle': 'publicacion', 'radioBroadcast': 'publicacion', 'tvBroadcast': 'publicacion', 'webpage': 'publicacion', "_default": None},
    'JO': {'conferencePaper': 'nombre del congreso', 'journalArticle': 'journalAbbreviation', "_default": None},
    'LB': {"_default": '__nota__'},
    'M1': {'annotation': None, 'attachment': None, 'bill': 'billNumber', 'book': 'numero de serie', 'bookSection': 'numero de volumenes', 'computerProgram': 'system', 'hearing': 'documentNumber', 'journalArticle': 'numero', 'note': None, 'nsfReviewer': None, 'patent': 'applicationNumber', 'podcast': 'episodeNumber', 'radioBroadcast': 'episodeNumber', 'statute': 'publicLawNumber', 'tvBroadcast': 'episodeNumber', 'webpage': 'accessDate', "_default": 'extra'},
    'M2': {'annotation': None, 'attachment': None, 'note': None, 'nsfReviewer': None, "_default": 'extra'},
    'M3': {'artwork': 'medio', 'blogPost': 'tipo de sitio', 'conferencePaper': 'DOI', 'dataset': 'DOI', 'forumPost': 'postType', 'interview': 'interviewMedium', 'journalArticle': 'DOI', 'letter': 'letterType', 'manuscript': 'tipo de manuscrito', 'map': 'tipo de mapa', 'podcast': 'audioFileType', 'preprint': 'DOI', 'presentation': 'tipo de presentacion', 'report': 'tipo de informe', 'standard': 'DOI', 'thesis': 'tipo de tesis', 'webpage': 'tipo de sitio', "_default": None},
    'N2': {'annotation': None, 'attachment': None, 'note': None, 'nsfReviewer': None, "_default": 'abstractNote'},
    'NV': {'audioRecording': 'numero de volumenes', 'book': 'numero de volumenes', 'bookSection': 'numero de volumenes', 'dataset': 'identificador', 'dictionaryEntry': 'numero de volumenes', 'encyclopediaArticle': 'numero de volumenes', 'hearing': 'numero de volumenes', 'videoRecording': 'numero de volumenes', "_default": None},
    'OP': {"_default": '__nota__'},
    'PB': {'audioRecording': 'sello', 'book': 'editorial', 'bookSection': 'editorial', 'case': 'court', 'computerProgram': 'empresa', 'conferencePaper': 'editorial', 'dataset': 'repositorio', 'dictionaryEntry': 'editorial', 'document': 'editorial', 'encyclopediaArticle': 'editorial', 'film': 'distribuidora', 'hearing': 'editorial', 'map': 'editorial', 'patent': 'assignee', 'preprint': 'editorial', 'radioBroadcast': 'network', 'report': 'institucion', 'standard': 'editorial', 'thesis': 'universidad', 'tvBroadcast': 'network', 'videoRecording': 'studio', "_default": None},
    'RI': {"_default": '__nota__'},
    'RN': {"_default": '__nota__'},
    'SE': {'case': '__nota__', "_default": None},
    'SN': {'audioRecording': 'ISBN', 'book': 'ISBN', 'bookSection': 'ISBN', 'computerProgram': 'ISBN', 'conferencePaper': 'ISBN', 'dictionaryEntry': 'ISBN', 'encyclopediaArticle': 'ISBN', 'journalArticle': 'ISSN', 'magazineArticle': 'ISSN', 'map': 'ISBN', 'newspaperArticle': 'ISSN', 'patent': 'numero de patente', 'report': 'numero de informe', 'videoRecording': 'ISBN', "_default": None},
    'SP': {'bill': 'codePages', 'book': 'numero de paginas', 'bookSection': 'paginas', 'case': 'firstPage', 'conferencePaper': 'paginas', 'dictionaryEntry': 'paginas', 'encyclopediaArticle': 'paginas', 'film': 'runningTime', 'hearing': 'paginas', 'journalArticle': 'paginas', 'magazineArticle': 'paginas', 'manuscript': 'numero de paginas', 'newspaperArticle': 'paginas', 'patent': 'paginas', 'report': 'paginas', 'statute': 'paginas', 'thesis': 'numero de paginas', "_default": None},
    'SV': {'bookSection': 'numero de serie', 'case': 'docketNumber', "_default": None},
    'T2': {'bill': 'code', 'blogPost': 'titulo del blog', 'book': 'serie', 'bookSection': 'titulo del libro', 'computerProgram': 'titulo de la serie', 'conferencePaper': 'nombre del congreso', 'dictionaryEntry': 'dictionaryTitle', 'encyclopediaArticle': 'encyclopediaTitle', 'forumPost': 'forumTitle', 'hearing': 'committee', 'journalArticle': 'publicacion', 'magazineArticle': 'publicacion', 'map': 'titulo de la serie', 'newspaperArticle': 'publicacion', 'presentation': 'nombre de la reunion', 'radioBroadcast': 'programTitle', 'report': 'titulo de la serie', 'statute': 'code', 'tvBroadcast': 'programTitle', 'webpage': 'titulo del sitio', "_default": '__nota__'},
    'T3': {'audioRecording': 'titulo de la serie', 'bill': 'legislativeBody', 'book': 'serie', 'bookSection': 'serie', 'conferencePaper': 'serie', 'hearing': 'legislativeBody', 'journalArticle': 'serie', "_default": None},
    'TA': {"_default": '__nota__'},
    'TT': {"_default": '__nota__'},
    'VL': {'audioRecording': 'volumen', 'bill': 'codeVolume', 'book': 'volumen', 'bookSection': 'volumen', 'case': 'reporterVolume', 'conferencePaper': 'volumen', 'dictionaryEntry': 'volumen', 'encyclopediaArticle': 'volumen', 'journalArticle': 'volumen', 'magazineArticle': 'volumen', 'patent': '__nota__', 'statute': 'codeNumber', 'videoRecording': 'volumen', 'webpage': 'accessDate', "_default": None},
}

# Campos que existen en cada tipo, segun el esquema de Zotero 7. Generado.
SCHEMA = {
    'annotation': {},
    'artwork': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'artworkMedium', 'artworkSize', 'callNumber', 'date', 'extra', 'language', 'libraryCatalog', 'medium', 'rights', 'shortTitle', 'title', 'url'},
    'attachment': {'accessDate', 'title', 'url'},
    'audioRecording': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'audioRecordingFormat', 'callNumber', 'date', 'extra', 'label', 'language', 'libraryCatalog', 'medium', 'numberOfVolumes', 'place', 'publisher', 'rights', 'runningTime', 'seriesTitle', 'shortTitle', 'title', 'url', 'volume'},
    'bill': {'abstractNote', 'accessDate', 'authority', 'billNumber', 'code', 'codePages', 'codeVolume', 'date', 'extra', 'history', 'language', 'legislativeBody', 'number', 'pages', 'rights', 'section', 'session', 'shortTitle', 'title', 'url', 'volume'},
    'blogPost': {'abstractNote', 'accessDate', 'blogTitle', 'date', 'extra', 'language', 'publicationTitle', 'rights', 'shortTitle', 'title', 'type', 'url', 'websiteType'},
    'book': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'edition', 'extra', 'language', 'libraryCatalog', 'numPages', 'numberOfVolumes', 'place', 'publisher', 'rights', 'series', 'seriesNumber', 'shortTitle', 'title', 'url', 'volume'},
    'bookSection': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'bookTitle', 'callNumber', 'date', 'edition', 'extra', 'language', 'libraryCatalog', 'numberOfVolumes', 'pages', 'place', 'publicationTitle', 'publisher', 'rights', 'series', 'seriesNumber', 'shortTitle', 'title', 'url', 'volume'},
    'case': {'abstractNote', 'accessDate', 'authority', 'caseName', 'court', 'date', 'dateDecided', 'docketNumber', 'extra', 'firstPage', 'history', 'language', 'number', 'pages', 'reporter', 'reporterVolume', 'rights', 'shortTitle', 'title', 'url', 'volume'},
    'computerProgram': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'company', 'date', 'extra', 'libraryCatalog', 'place', 'programmingLanguage', 'publisher', 'rights', 'seriesTitle', 'shortTitle', 'system', 'title', 'url', 'versionNumber'},
    'conferencePaper': {'DOI', 'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'conferenceName', 'date', 'extra', 'language', 'libraryCatalog', 'pages', 'place', 'proceedingsTitle', 'publicationTitle', 'publisher', 'rights', 'series', 'shortTitle', 'title', 'url', 'volume'},
    'dataset': {'DOI', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'citationKey', 'date', 'extra', 'format', 'identifier', 'language', 'libraryCatalog', 'medium', 'number', 'place', 'publisher', 'repository', 'repositoryLocation', 'rights', 'shortTitle', 'title', 'type', 'url', 'versionNumber'},
    'dictionaryEntry': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'dictionaryTitle', 'edition', 'extra', 'language', 'libraryCatalog', 'numberOfVolumes', 'pages', 'place', 'publicationTitle', 'publisher', 'rights', 'series', 'seriesNumber', 'shortTitle', 'title', 'url', 'volume'},
    'document': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'language', 'libraryCatalog', 'publisher', 'rights', 'shortTitle', 'title', 'url'},
    'email': {'abstractNote', 'accessDate', 'date', 'extra', 'language', 'rights', 'shortTitle', 'subject', 'title', 'url'},
    'encyclopediaArticle': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'edition', 'encyclopediaTitle', 'extra', 'language', 'libraryCatalog', 'numberOfVolumes', 'pages', 'place', 'publicationTitle', 'publisher', 'rights', 'series', 'seriesNumber', 'shortTitle', 'title', 'url', 'volume'},
    'film': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'distributor', 'extra', 'genre', 'language', 'libraryCatalog', 'medium', 'publisher', 'rights', 'runningTime', 'shortTitle', 'title', 'type', 'url', 'videoRecordingFormat'},
    'forumPost': {'abstractNote', 'accessDate', 'date', 'extra', 'forumTitle', 'language', 'postType', 'publicationTitle', 'rights', 'shortTitle', 'title', 'type', 'url'},
    'hearing': {'abstractNote', 'accessDate', 'authority', 'committee', 'date', 'documentNumber', 'extra', 'history', 'language', 'legislativeBody', 'number', 'numberOfVolumes', 'pages', 'place', 'publisher', 'rights', 'session', 'shortTitle', 'title', 'url'},
    'instantMessage': {'abstractNote', 'accessDate', 'date', 'extra', 'language', 'rights', 'shortTitle', 'title', 'url'},
    'interview': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'interviewMedium', 'language', 'libraryCatalog', 'medium', 'rights', 'shortTitle', 'title', 'url'},
    'journalArticle': {'DOI', 'ISSN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'issue', 'journalAbbreviation', 'language', 'libraryCatalog', 'pages', 'publicationTitle', 'rights', 'series', 'seriesText', 'seriesTitle', 'shortTitle', 'title', 'url', 'volume'},
    'letter': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'language', 'letterType', 'libraryCatalog', 'rights', 'shortTitle', 'title', 'type', 'url'},
    'magazineArticle': {'ISSN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'issue', 'language', 'libraryCatalog', 'pages', 'publicationTitle', 'rights', 'shortTitle', 'title', 'url', 'volume'},
    'manuscript': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'language', 'libraryCatalog', 'manuscriptType', 'numPages', 'place', 'rights', 'shortTitle', 'title', 'type', 'url'},
    'map': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'edition', 'extra', 'language', 'libraryCatalog', 'mapType', 'place', 'publisher', 'rights', 'scale', 'seriesTitle', 'shortTitle', 'title', 'type', 'url'},
    'newspaperArticle': {'ISSN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'edition', 'extra', 'language', 'libraryCatalog', 'pages', 'place', 'publicationTitle', 'rights', 'section', 'shortTitle', 'title', 'url'},
    'note': {},
    'nsfReviewer': {'accepted', 'address', 'date', 'dateDue', 'dateSent', 'discipline', 'email', 'homepage', 'institution', 'name', 'nsfID', 'programDirector', 'telephone', 'title', 'url'},
    'patent': {'abstractNote', 'accessDate', 'applicationNumber', 'assignee', 'authority', 'country', 'date', 'extra', 'filingDate', 'issueDate', 'issuingAuthority', 'language', 'legalStatus', 'number', 'pages', 'patentNumber', 'place', 'priorityNumbers', 'references', 'rights', 'shortTitle', 'status', 'title', 'url'},
    'podcast': {'abstractNote', 'accessDate', 'audioFileType', 'episodeNumber', 'extra', 'language', 'medium', 'number', 'rights', 'runningTime', 'seriesTitle', 'shortTitle', 'title', 'url'},
    'preprint': {'DOI', 'abstractNote', 'accessDate', 'archive', 'archiveID', 'archiveLocation', 'callNumber', 'citationKey', 'date', 'extra', 'genre', 'language', 'libraryCatalog', 'number', 'place', 'publisher', 'repository', 'rights', 'series', 'seriesNumber', 'shortTitle', 'title', 'type', 'url'},
    'presentation': {'abstractNote', 'accessDate', 'date', 'extra', 'language', 'meetingName', 'place', 'presentationType', 'rights', 'shortTitle', 'title', 'type', 'url'},
    'radioBroadcast': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'audioRecordingFormat', 'callNumber', 'date', 'episodeNumber', 'extra', 'language', 'libraryCatalog', 'medium', 'network', 'number', 'place', 'programTitle', 'publicationTitle', 'publisher', 'rights', 'runningTime', 'shortTitle', 'title', 'url'},
    'report': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'institution', 'language', 'libraryCatalog', 'number', 'pages', 'place', 'publisher', 'reportNumber', 'reportType', 'rights', 'seriesTitle', 'shortTitle', 'title', 'type', 'url'},
    'standard': {'DOI', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'authority', 'callNumber', 'citationKey', 'committee', 'date', 'extra', 'language', 'libraryCatalog', 'numPages', 'number', 'organization', 'place', 'publisher', 'rights', 'shortTitle', 'status', 'title', 'type', 'url', 'versionNumber'},
    'statute': {'abstractNote', 'accessDate', 'code', 'codeNumber', 'date', 'dateEnacted', 'extra', 'history', 'language', 'nameOfAct', 'number', 'pages', 'publicLawNumber', 'rights', 'section', 'session', 'shortTitle', 'title', 'url'},
    'thesis': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'language', 'libraryCatalog', 'numPages', 'place', 'publisher', 'rights', 'shortTitle', 'thesisType', 'title', 'type', 'university', 'url'},
    'tvBroadcast': {'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'episodeNumber', 'extra', 'language', 'libraryCatalog', 'medium', 'network', 'number', 'place', 'programTitle', 'publicationTitle', 'publisher', 'rights', 'runningTime', 'shortTitle', 'title', 'url', 'videoRecordingFormat'},
    'videoRecording': {'ISBN', 'abstractNote', 'accessDate', 'archive', 'archiveLocation', 'callNumber', 'date', 'extra', 'language', 'libraryCatalog', 'medium', 'numberOfVolumes', 'place', 'publisher', 'rights', 'runningTime', 'seriesTitle', 'shortTitle', 'studio', 'title', 'url', 'videoRecordingFormat', 'volume'},
    'webpage': {'abstractNote', 'accessDate', 'date', 'extra', 'language', 'publicationTitle', 'rights', 'shortTitle', 'title', 'type', 'url', 'websiteTitle', 'websiteType'},
}

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
DATE_RE = re.compile(r"^\d{4}(/\d{0,2}(/\d{0,2}(/.*)?)?)?$")
ISO639 = re.compile(r"^[a-z]{2,3}([-_].+)?$")


ORG_WORDS = {
    "banco", "bank", "ministerio", "ministry", "instituto", "institute", "institut",
    "universidad", "university", "universite", "universitat", "servicio", "service",
    "departamento", "department", "comision", "comisión", "commission", "consejo",
    "council", "organizacion", "organización", "organisation", "organization",
    "fondo", "fund", "oficina", "office", "agencia", "agency", "centro", "centre",
    "center", "observatorio", "observatory", "fundacion", "fundación", "foundation",
    "secretaria", "secretaría", "secretariat", "direccion", "dirección", "school",
    "faculty", "facultad", "association", "asociacion", "asociación", "society",
    "group", "grupo", "programme", "program", "programa", "network", "red",
    "committee", "comite", "comité", "board", "authority", "autoridad", "unit",
    "unidad", "division", "division", "bureau", "administracion", "administración",
}


def looks_institutional(value):
    """Un autor con coma que en realidad es un organismo.

    Zotero parte por la primera coma, asi que 'Banco de Espana, Servicio de Estudios'
    entraria como apellido 'Banco de Espana' y nombre 'Servicio de Estudios'. Un nombre
    de pila real rara vez tiene tres palabras ni contiene palabras de organismo.
    """
    surname, _, given = value.partition(",")
    given = given.strip()
    if not given:
        return False
    words = [w for w in re.split(r"\s+", given) if w]
    tokens = {unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode().lower().strip(".")
              for w in re.split(r"\s+", value)}
    if tokens & ORG_WORDS:
        return True
    return len(words) >= 3


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def error(self, line_no, msg):
        self.errors.append((line_no, msg))

    def warn(self, line_no, msg):
        self.warnings.append((line_no, msg))

    def note(self, msg):
        self.notes.append(msg)


def meaning(tag, item_type):
    """Que significa esta etiqueta para este tipo. None = se descarta."""
    if tag in BY_TYPE:
        table = BY_TYPE[tag]
        return table.get(item_type, table.get("_default"))
    return UNIVERSAL.get(tag, "?")


def validate(text, rep):
    lines = text.split("\n")
    records = 0
    item_type = None
    ty_seen = False
    current_tag = None
    seen_tags = set()

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\r")
        if not line.strip():
            current_tag = None
            continue

        m = RIS_LINE.match(line)
        if not m:
            # Puede ser continuacion legitima de AB/N1/N2/KW, o basura descartada.
            if current_tag in ("AB", "N1", "N2", "RN", "KW", "L1", "L2"):
                continue
            if line != line.rstrip():
                rep.error(i, "linea con espacios finales: Zotero la descarta "
                             "(el patron es ^XX  - valor$)")
            else:
                rep.error(i, "linea que no cumple el formato RIS y se descartara "
                             "en silencio: %r" % line[:60])
            continue

        tag, value = m.group(1), (m.group(2) or "")
        current_tag = tag

        # Formato canonico: dos espacios antes del guion.
        if not line.startswith(tag + "  -"):
            rep.warn(i, "'%s' usa un solo espacio antes del guion; Zotero lo acepta, "
                        "pero el canonico es '%s  - '" % (tag, tag))

        if tag == "TY":
            if ty_seen and item_type is not None:
                rep.error(i, "TY nuevo sin ER que cerrase el registro anterior")
            ty_seen = True
            records += 1
            seen_tags = set()
            if value not in TYPE_MAP:
                rep.error(i, "TY '%s' desconocido: Zotero lo importara como "
                             "journalArticle" % value)
                item_type = "journalArticle"
            else:
                item_type = TYPE_MAP[value]
                rep.note("Registro %d: TY %s -> %s" % (records, value, item_type))
            continue

        if not ty_seen:
            rep.error(i, "etiqueta '%s' antes del primer TY: el registro debe abrir "
                         "con TY" % tag)
            continue

        if tag == "ER":
            item_type = None
            ty_seen = False
            for required in ("TI", "T1"):
                if required in seen_tags:
                    break
            else:
                rep.error(i, "registro %d cerrado sin titulo (TI)" % records)
            continue

        seen_tags.add(tag)

        if tag not in UNIVERSAL and tag not in BY_TYPE:
            rep.warn(i, "etiqueta '%s' no reconocida por Zotero: acabara en una nota, "
                        "no en un campo" % tag)
            continue

        sense = meaning(tag, item_type)
        if sense is None:
            rep.error(i, "'%s' no es valida para %s: Zotero descarta el valor"
                      % (tag, item_type))
            continue
        if sense == "__nota__":
            rep.warn(i, "'%s' no tiene campo propio en %s: el valor acabara en una "
                        "nota adjunta, no en la ficha" % (tag, item_type))
            continue

        # Las universales tambien pueden no existir en el tipo.
        zfield = UNIVERSAL_FIELD.get(tag)
        if zfield and item_type in SCHEMA and zfield not in SCHEMA[item_type]:
            rep.error(i, "'%s' (%s) no existe en %s: Zotero descarta el valor"
                      % (tag, zfield, item_type))
            continue
        if tag == "DO" and item_type in SCHEMA and "DOI" not in SCHEMA[item_type]:
            rep.note("  DO: %s no tiene campo DOI; Zotero lo guardara en Extra como "
                     "'DOI: ...'. Es lo correcto, no lo quites." % item_type)

        if not value.strip():
            rep.warn(i, "'%s' vacia; borra la linea en vez de dejarla" % tag)
            continue

        # Comprobaciones de contenido.
        if tag == "DO":
            if value.startswith("http"):
                rep.error(i, "DOI con URL envolvente; pon solo '10.xxxx/yyyy'")
            elif not DOI_RE.match(value):
                rep.warn(i, "el DOI %r no tiene la forma habitual 10.xxxx/yyyy" % value)
        elif tag in ("PY", "DA", "Y1", "Y2"):
            if not DATE_RE.match(value):
                rep.error(i, "fecha %r invalida; usa AAAA o AAAA/MM/DD "
                             "(parciales: 2024/06//)" % value)
        elif tag == "LA":
            if not ISO639.match(value):
                rep.warn(i, "idioma %r: se espera un codigo ISO 639 como 'spa' o 'eng'"
                         % value)
        elif tag == "L1":
            low = value.lower()
            if not low.startswith(("http://", "https://")) and not re.match(r"^[a-zA-Z]:[\\/]", value):
                rep.warn(i, "L1 deberia ser una URL https o una ruta absoluta local")
            elif low.startswith("http") and ".pdf" not in low:
                rep.warn(i, "L1 no parece apuntar a un PDF directo; si es una landing "
                            "page Zotero no adjuntara nada")
        elif tag in ("AU", "A1", "A2", "A3", "A4", "ED"):
            if value.count(",") > 1:
                rep.warn(i, "'%s' con mas de una coma: Zotero parte por la primera y el "
                            "resto va al nombre (%r)" % (tag, value))
            elif "," not in value:
                rep.note("  %s: '%s' se importara como autor institucional "
                         "(campo unico)" % (tag, value))
            elif looks_institutional(value):
                surname, given = [p.strip() for p in value.split(",", 1)]
                rep.error(i, "'%s' parece un organismo, pero la coma hara que Zotero lo "
                             "parta en apellido %r y nombre %r. Quita la coma para que "
                             "entre como autor institucional"
                          % (tag, surname, given))

    if ty_seen:
        rep.error(len(lines), "el ultimo registro no se cierra con 'ER  - '")
    if records == 0:
        rep.error(1, "no se encontro ningun 'TY  - ': Zotero no reconocera el fichero "
                     "como RIS")
    return records


BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def check_url(url, expect_pdf):
    """Comprueba que la URL existe y sirve lo que decimos que sirve.

    Devuelve (nivel, mensaje) con nivel en {'ok', 'warn', 'error'}. Se usa un
    User-Agent de navegador porque muchos sitios institucionales devuelven 403 a un
    agente de script, y ese 403 no dice nada sobre la URL.
    """
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, headers={
        "User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            head = resp.read(5)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return ("warn", "responde %d (probable filtro anti-bot o muro de pago); "
                            "Zotero puede lograrlo, pero compruebalo a mano" % exc.code)
        return ("error", "responde %d: la URL no existe o cambio" % exc.code)
    except Exception as exc:
        return ("warn", "no se pudo comprobar (%s)" % exc)

    if not expect_pdf:
        return ("ok", "")
    if head.startswith(b"%PDF") or "application/pdf" in ctype:
        return ("ok", "")
    if "html" in ctype:
        return ("error", "devuelve HTML, no un PDF: es una landing page y Zotero no "
                         "adjuntara nada")
    return ("warn", "no parece un PDF (Content-Type: %s)" % (ctype or "desconocido"))


def verify_urls(text, rep, offline):
    """Comprueba en red los L1/L2/UR del fichero."""
    targets = []
    for i, raw in enumerate(text.split("\n"), 1):
        m = RIS_LINE.match(raw.rstrip("\r"))
        if not m:
            continue
        tag, value = m.group(1), (m.group(2) or "").strip()
        if tag in ("L1", "L2", "UR") and value.lower().startswith("http"):
            targets.append((i, tag, value))
    if not targets:
        return
    if offline:
        for i, tag, _ in targets:
            if tag == "L1":
                rep.warn(i, "L1 sin comprobar (--offline): si la URL no existe, Zotero "
                            "no adjunta nada y no avisa")
        return
    for i, tag, url in targets:
        level, msg = check_url(url, expect_pdf=(tag == "L1"))
        if level == "ok":
            rep.note("  %s comprobada: %s" % (tag, url))
        elif level == "warn":
            rep.warn(i, "%s %s" % (tag, msg))
        else:
            rep.error(i, "%s %s -> %s" % (tag, msg, url))


def main():
    ap = argparse.ArgumentParser(description="Valida un .ris contra el importador de Zotero.")
    ap.add_argument("fichero")
    ap.add_argument("--strict", action="store_true",
                    help="tratar los avisos como errores")
    ap.add_argument("--offline", action="store_true",
                    help="no comprobar en red las URLs de L1/L2/UR")
    args = ap.parse_args()

    try:
        with open(args.fichero, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        print("No se pudo leer %s: %s" % (args.fichero, exc))
        return 2

    rep = Report()

    if raw.startswith(b"\xef\xbb\xbf"):
        rep.warn(1, "el fichero empieza con BOM UTF-8; guardalo como UTF-8 sin BOM")
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        print("El fichero no es UTF-8 valido: %s" % exc)
        return 2

    records = validate(text, rep)
    verify_urls(text, rep, args.offline)

    for msg in rep.notes:
        print("  . %s" % msg)
    if rep.notes:
        print()
    for line_no, msg in rep.warnings:
        print("  AVISO  linea %d: %s" % (line_no, msg))
    for line_no, msg in rep.errors:
        print("  ERROR  linea %d: %s" % (line_no, msg))

    print()
    print("%d registro(s), %d error(es), %d aviso(s)."
          % (records, len(rep.errors), len(rep.warnings)))

    if rep.errors:
        return 1
    if args.strict and rep.warnings:
        return 1
    print("Listo para importar en Zotero.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
