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

timestring = "%Y/%D/%mT%H:%M:%S.%Z"

def _create_rdf(base_uri, _manifest, _image, _resource, _filename):

    #https://iiif.itatti.harvard.edu/iiif/2/yashiro!to_berenson!1923!Letter-001_1.jpg/full/full/0/default.jpg
    def _get_index(_filename):
        print(_filename.lower())
        return _filename.split('_')[-1]

    g = Graph()

    RDF = namespace.RDF
    RDFS = namespace.RDFS
    XSD = namespace.XSD
    
    g.namespace_manager.bind('ldp', Namespace('http://www.w3.org/ns/ldp#'), override = True, replace=True)
    g.namespace_manager.bind('prov', Namespace('http://www.w3.org/ns/prov#'), override = True, replace=True)
    g.namespace_manager.bind('crm', Namespace('http://www.cidoc-crm.org/cidoc-crm/'), override = True, replace=True)
    g.namespace_manager.bind('rso', Namespace('http://www.researchspace.org/ontology/'), override=True, replace=True)


    "<http://www.example.org/image/abcd1234> a crm:E38_Image"
    # Image ID node
    _image_node = URIRef(_image)

    g.add( (_image_node, RDF.type, URIRef('http://www.cidoc-crm.org/cidoc-crm/E38_Image')) )
    g.add( (_image_node, RDF.type, URIRef("http://www.researchspace.org/ontology/EX_Digital_Image")) )
    g.add( (_image_node, URIRef("http://www.researchspace.org/ontology/image_index"), Literal(_get_index(_filename), datatype=XSD.integer)) )
    g.add( (_image_node, URIRef('http://www.cidoc-crm.org/cidoc-crm/P165i_is_incorporated_in'), URIRef(_resource)) )

    return g

def _write_rdf(filename, metadata, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    metadata.serialize(destination=f'{directory}/{filename}', format='turtle')

def tag1(filename, uri, directory):
    with open(filename, 'r') as f:
        images = json.load(f)

        for image in images:

            _manifest = image['IIIF_manifest']
            _image = image['IIIF_image']
            _resource = image['resource']
            _filename = image['filename']

            _rdf = _create_rdf(uri, _manifest, _image, _resource, _filename)

            _write_rdf(f'{_filename}.ttl', _rdf, directory)

def tag2(filename, uri, directory):
    with open(filename, 'r') as f:
        images = json.load(f)

        for image in images:

            _manifest = image['IIIF_manifest']
            _image = image['IIIF_image']
            _resource = image['resource']
            _filename = f'{image["Letter corrected"].replace("_","-")}_{image["sequence_num"]}'

            _rdf = _create_rdf(uri, _manifest, _image, _resource, _filename)
            _write_rdf(f'{_filename}.ttl', _rdf, directory) 
