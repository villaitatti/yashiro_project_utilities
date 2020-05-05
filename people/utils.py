import json
import os
import re
import random
import string
import requests
import urllib

from datetime import datetime
from rdflib import Graph, URIRef, namespace, Namespace, Literal
from bs4 import BeautifulSoup as bs

tmp1 = 'admin'
tmp2 = 'admin'

timestring = "%Y/%D/%mT%H:%M:%S.%Z"

extension_ttl = 'ttl'

people = {}

def _id_generator(stringLength=8):

    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('I','')
    chars = chars.replace('O','')
    chars = chars.replace('1','')
    chars = chars.replace('0','')

    return ''.join(random.choice(chars) for i in range(stringLength))

def _create_person_id(name):

    if name in people:
        return people[name]

    pid = _id_generator()
    people[name] = pid

    return pid

def _create_RDF(base_uri, _id, _name):

    _name = _name.replace('_',' ')

    g = Graph()

    RDF = namespace.RDF
    XSD = namespace.XSD
    RDFS = namespace.RDFS

    CRM = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
    CRM_NAME = 'crm'

    pref_name = 'Preferred Name'

    BASE = Namespace('http://www.researchspace.org/resource/')

    g.namespace_manager.bind(CRM_NAME, CRM, override = True, replace=True)

    actor_uri = f'{base_uri}/person/{_id}'
    actor_name_uri = f'{actor_uri}/identifier/{_id_generator()}'
    actor_name_type_uri = f'{actor_uri}/type/{_id_generator()}'
    
    actor_node = URIRef(actor_uri)
    actor_name_node = URIRef(actor_name_uri)
    actor_name_type_node = URIRef(actor_name_type_uri)

    g.add( (actor_node, RDF.type, CRM.E21_Person) )
    g.add( (actor_node, CRM.P1_is_identified_by, actor_name_node) )

    g.add( (actor_name_node, RDF.type, CRM.E41_Appellation) )
    g.add( (actor_name_node, RDFS.label, Literal(_name, datatype=XSD.string)) )
    g.add( (actor_name_node, CRM.P2_has_type, actor_name_type_node) )

    g.add( (actor_name_type_node, RDF.type, CRM.E55_Type) )
    g.add( (actor_name_type_node, RDFS.label, Literal(pref_name, datatype=XSD.string)) )

    return g

def _write_RDF(filename, metadata, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    metadata.serialize(destination=f'{directory}/{filename}', format='turtle')

def tag(filename, uri, directory):

    uri = f'http://{uri}'

    with open(filename, 'r') as f:
        people = json.load(f)

        for person in people:

            _name = person['title'].strip().replace(' ','_')
            _id = _create_person_id(_name)

            _rdf = _create_RDF(uri, _id, _name)

            _write_RDF(f'{_name}.{extension_ttl}', _rdf, directory)


def _del(filename, url):

    # curl -v -u admin:admin -X DELETE -H 'Content-Type: text/turtle' http://127.0.0.1:10214/rdf-graph-store?graph=http%3A%2F%2Fdpub.cordh.net%2Fdocument%2FBernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html%2Fcontext

    command = f'curl -u {tmp1}:{tmp2} -X DELETE -H \'Content-Type: text/turtle\' {url}'

    return f'DEL\t{os.system(command)}'

def _post(filename, url, directory):

    #curl -v -u admin:admin -X POST -H 'Content-Type: text/turtle' --data-binary '@metadata/Bernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html.ttl' http://127.0.0.1:10214/rdf-graph-store?graph=http%3A%2F%2Fdpub.cordh.net%2Fdocument%2FBernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html%2Fcontext

    filename = os.path.join(directory, filename)
    command = f'curl -u {tmp1}:{tmp2} -X POST -H \'Content-Type: text/turtle\' --data-binary \'@{filename}\' {url}'

    return f'POST\t{os.system(command)}'

def post(uri, directory, n=200):

    i=0

    for metadata_file in os.listdir(directory):

        if i == n:
            break

        filename = metadata_file

        graph_name = urllib.parse.quote(f'http://{uri}/resource/{filename}/context', safe='')
        
        r_url = f'http://127.0.0.1:10214/rdf-graph-store?graph={graph_name}'

        print(f'\n{filename}')

        #DEL
        print(_del(filename, r_url))

        #PUT
        print(_post(filename, r_url, directory))

        i+=1