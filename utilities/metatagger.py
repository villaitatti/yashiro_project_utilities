# create rdf file with metadata
import re

from datetime import datetime
from rdflib import Graph, URIRef, namespace

# Bernard Berenson (in Settignano) to Yashiro
# Elizabeth Berenson (in Settignano) to Yashiro (in Palo Alto, California)

key_production_place = 'production_place'
key_receiving_place = 'receiving_place'

key_sender = 'sender'
key_receiver = 'receiver'
key_date = 'sending_date'

date_format = '%Y/%m/%d'

def _parse_title(title):

    rex_places = r'\s\(+[^\(]+\)[\s]*'
    rex_parenthesis = r'[\(\)]'
    metadata = dict()

    places = re.findall(rex_places, title)
    actors = re.split(rex_places, title)

    metadata[key_sender] = actors[0].strip()
    metadata[key_receiver] = actors[0].replace('to ','').strip()

    metadata[key_production_place] = re.sub(rex_parenthesis, '', places[0]).strip()
    
    if len(places) > 1:
        metadata[key_receiving_place] = re.sub(rex_parenthesis, '', places[1]).strip()

    return metadata

def _parse_date(date):
    
    # todo: timezone
    return datetime.fromtimestamp(date).strftime(date_format)

def _writeRDF(uri, metadata):

    g = Graph()

    base_uri = 'http://yashiro.itatti.harvard.edu/document/'
    letter_uri = f'{base_uri}{uri}'
    
    CRM = URIRef('http://www.cidoc-crm.org/cidoc-crm/')
    LETTER = URIRef(letter_uri)

    g.add( (LETTER, namespace.RDF.type, CRM.E33_Linguistic_Object) )

    return g

def execute(filename, title, date):

    metadata = _parse_title(title)
    metadata[key_date] = _parse_date(date)

    return metadata