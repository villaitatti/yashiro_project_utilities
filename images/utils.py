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

def _create_rdf(base_uri, _manifest, _image, _letter):

    def _get_index(_image_uri):
        print(_image_uri.lower())
        _image_name = re.findall('(?<=letter-)(.*)(?=.jpg\/)', _image_uri.lower())[0]
        return _image_name.split('_')[-1]


    g = Graph()

    RDF = namespace.RDF
    RDFS = namespace.RDFS
    XSD = namespace.XSD

    CRM = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
    CRM_NAME = 'crm'
    g.namespace_manager.bind(CRM_NAME, CRM, override = True, replace=True)

    letter_uri = f'{base_uri}letter/{_letter}'

    # types
    image_node = URIRef(_image)
    image_service_node = URIRef(_manifest)
    letter_node = URIRef(letter_uri)

    _index = _get_index(_image)

    g.add( (image_node, RDF.type, CRM.E38_Image) )
    g.add( (image_node, RDFS.label, Literal(letter_uri, datatype=RDFS.Resource)) )
    g.add( (image_node, CRM.P165i_is_incorporated_in, letter_node) )
    g.add( (image_node, URIRef("https://yashiro.itatti.harvard.edu/resource/image_index"), Literal(_index, datatype=XSD.integer)) )

    g.add( (image_service_node, RDF.type, CRM.E73_Information_Object) )
    g.add( (image_service_node, CRM.P129_is_about, image_node) )
    g.add( (image_service_node, CRM.P2_has_type, URIRef("http://iiif.io/api/image")) )

    return g

def _write_rdf(filename, metadata, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    metadata.serialize(destination=f'{directory}/{filename}', format='turtle')

def tag(filename, uri, directory):

    with open(filename, 'r') as f:
        images = json.load(f)

        for image in images:

            _manifest = image['IIIF_manifest']
            _image = image['IIIF_image']
            _letter = image['Letter-resource']
            _filename = image['filename']

            _rdf = _create_rdf(uri, _manifest, _image, _letter)

            _write_rdf(f'{_filename}.ttl', _rdf, directory)
