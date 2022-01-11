import json
import os
import re
import random
import string
import requests
import urllib

from operator import itemgetter
from datetime import datetime
from rdflib import Graph, URIRef, namespace, Namespace, Literal
from bs4 import BeautifulSoup as bs

tmp1 = 'admin'
tmp2 = 'admin'

key_date = 'created'
key_title = 'title'
key_body = 'body_value'
key_body_text = 'body_text'
key_id = 'id'

key_production_place = 'production_place'
key_receiving_place = 'receiving_place'

key_sender = 'sender'
key_receiver = 'receiver'
key_sending_date = 'sending_date'

key_filename = 'filename'

extension_html = 'html'
extension_txt = 'txt'
extension_ttl = 'ttl'
extension_rdf = 'rdf'

key_actors = 'actor'
key_places = 'places'

URI = {
    key_actors: {},
    key_places: {}
}

timestring = "%Y-%m-%dT%H:%M:%S"

people = {}
places = {}


people = {}

def _id_generator(stringLength=8):

    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('I','')
    chars = chars.replace('O','')
    chars = chars.replace('1','')
    chars = chars.replace('0','')

    return ''.join(random.choice(chars) for i in range(stringLength))

def _manipulate_title(title):

    divider = '_'

    title = title.strip()
    title = re.sub(r'\s+', divider, title)
    title = re.sub(r'[\(\)\,]*', '', title)

    return title

def _clean_body(body):

    engine = 'lxml'

    content_input = bs(body, engine)
    content_output = bs('', engine)

    for para in content_input.findAll('p'):

        if len(para.text) > 0:

            new_para = bs.new_tag(content_input,'p')
            new_para.string = para.text

            content_output.append(new_para)

    return content_output


def _write_letter_txt(filename, content, directory):
  content = re.sub(r"<[^<>]+>", '\n', str(content))
  _write_letter_html(filename, content, directory)

def _write_letter_html(filename, content, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, filename)

    with open(filename, 'w') as f:
        f.write(str(content))
        f.close()

def _parse_title(title):

    rex_places = r'\s\(+[^\(]+\)[\s]*'
    rex_parenthesis = r'[\(\)]'
    metadata = dict()

    places = re.findall(rex_places, title)
    actors = re.split(rex_places, title)

    metadata[key_sender] = actors[0].strip()
    metadata[key_receiver] = actors[1].replace('to ','').strip()

    metadata[key_production_place] = re.sub(rex_parenthesis, '', places[0]).strip()
    metadata[key_production_place] = metadata[key_production_place].replace('in ','')
    
    if len(places) > 1:
        metadata[key_receiving_place] = re.sub(rex_parenthesis, '', places[1]).strip()

    return metadata

def _parse_date(date):
    
    # todo: timezone
    return datetime.fromtimestamp(date).strftime(timestring)

def _create_person_id(name):

    if name in people:
        return people[name]

    pid = name.lower()
    pid = pid.replace(' ','_')

    # Custom transformation
    if pid == 'yashiro':
        pid = 'yukio_yashiro'

    people[name] = pid

    return pid

def _create_place_id(name):

    if name in places:
        return places[name]

    pid = _id_generator()
    places[name] = pid

    return pid

def _create_RDF(base_uri, metadata):

    g = Graph()

    RDF = namespace.RDF
    XSD = namespace.XSD
    RDFS = namespace.RDFS

    CRM_NAME = 'crm'
    LDP_NAME = 'ldp'
    PROV_NAME = 'prov'
    PLATFORM_NAME = 'Platform'

    LDP = Namespace('http://www.w3.org/ns/ldp#')
    PROV = Namespace('http://www.w3.org/ns/prov#')
    CRM = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
    CRMDIG = Namespace('http://www.ics.forth.gr/isl/CRMdig/')
    BASE = Namespace('http://www.researchspace.org/resource/')
    DPUB_ANNOTATION = Namespace(base_uri+"annotation-schema/")
    USER = Namespace('http://www.researchspace.org/resource/user/')
    PLATFORM = Namespace('http://www.researchspace.org/resource/system/')
    

    filename = metadata[key_filename]

    # URIs
    base_node_uri = f'{base_uri}document/{filename}'
    letter_uri = f'{base_uri}letter/{filename}'
    letter_content_uri = f'{letter_uri}/content'
    letter_title_uri = f'{letter_uri}/title'
    activity_exchange_uri = f'{letter_uri}/exchange'

    actor_as_sender_uri = f'{activity_exchange_uri}/actor_as_sender'
    actor_as_receiver_uri = f'{activity_exchange_uri}/actor_as_receiver'

    sender_role_uri = f'{base_uri}sender'
    receiver_role_uri = f'{base_uri}receiver'

    sender_uri = f'{base_uri}person/{_create_person_id(metadata[key_sender])}'

    production_uri = f'{activity_exchange_uri}/compilation'
    production_place_uri = f'{base_uri}place/{_create_place_id(metadata[key_production_place])}'

    sending_uri = f'{activity_exchange_uri}/sending'
    sending_timespam_uri = f'{sending_uri}/timespan/{_id_generator()}'


    # Nodes
    BASE_NODE = URIRef(base_node_uri)

    LETTER = URIRef(letter_uri)
    LETTER_CONTENT = URIRef(letter_content_uri)
    LETTER_TITLE = URIRef(letter_title_uri)

    ACTIVITY_EXCHANGE = URIRef(activity_exchange_uri)

    ACTOR_AS_SENDER = URIRef(actor_as_sender_uri)
    ACTOR_AS_RECEIVER = URIRef(actor_as_receiver_uri) 

    SENDER_ROLE = URIRef(sender_role_uri)
    RECEIVER_ROLE = URIRef(receiver_role_uri)
    SENDER = URIRef(sender_uri)

    PRODUCTION = URIRef(production_uri)
    PRODUCTION_PLACE = URIRef(production_place_uri)

    SENDING = URIRef(sending_uri)
    SENDING_TIMESPAN = URIRef(sending_timespam_uri)

    # Text Document
    g.add( (PLATFORM.fileContainer , URIRef('http://www.w3.org/ns/ldp#contains'), BASE_NODE) )

    g.add( (BASE_NODE, RDF.type, CRM.E33_Linguistic_Object) )
    g.add( (BASE_NODE, RDF.type, DPUB_ANNOTATION.TextDocument) )
    g.add( (BASE_NODE, RDF.type, CRMDIG.D1_Digital_Object) )
    g.add( (BASE_NODE, RDF.type, PLATFORM.File) )
    g.add( (BASE_NODE, RDF.type, LDP.Resource) )
    g.add( (BASE_NODE, RDF.type, PROV.Entity) )
    g.add( (BASE_NODE, PLATFORM.fileContext, BASE.TextDocuments) )
    g.add( (BASE_NODE, PLATFORM.fileName, Literal(f'{filename}.{extension_html}')) )
    g.add( (BASE_NODE, PLATFORM.mediaType, Literal('form-data')) )
    g.add( (BASE_NODE, PROV.generatedAtTime, Literal(datetime.now().strftime(timestring), datatype=XSD.dateTime)) )
    g.add( (BASE_NODE, PROV.wasAttributedTo, USER.admin) )
    g.add( (BASE_NODE, RDFS.label, Literal(filename, datatype=XSD.string)) )
    g.add( (BASE_NODE, CRM.P1_is_identified_by, LETTER) )

    # Letter
    g.add( (LETTER, RDF.type, CRM['E22_Man-made_Object']) )
    g.add( (LETTER, RDFS.label, Literal(filename, datatype=XSD.string)) )
    g.add( (LETTER, CRM.P128_carries, LETTER_CONTENT) )
    g.add( (LETTER, CRM.P48_has_preferred_identifier, LETTER_TITLE) )

    #Letter Content
    #TODO: choose appropriate property in the place of RDFS.label
    g.add( (LETTER_CONTENT, RDF.type, CRM['E90_Symbolic_Object']) )
    g.add( (LETTER_CONTENT, RDF.value, (Literal(metadata[key_body_text], datatype=XSD.string))) )

    # Title
    g.add( (LETTER_TITLE, RDF.type, CRM.E42_Identifier) )
    g.add( (LETTER_TITLE, RDFS.label, Literal(metadata[key_title], datatype=XSD.string)) )

    # Activity exchange
    g.add( (ACTIVITY_EXCHANGE, RDF.type, CRM.E7_Activity) )
    g.add( (ACTIVITY_EXCHANGE, CRM.P16_used_specific_object, LETTER) )
    g.add( (ACTIVITY_EXCHANGE, CRM.P01_has_domain, ACTOR_AS_SENDER))
     

    # Actor as sender (?)
    g.add( (ACTOR_AS_SENDER, CRM['P14.1_in_the_role_of'], SENDER_ROLE) )
    g.add( (ACTOR_AS_SENDER, CRM.P02_has_range, SENDER) )

    # Sender role
    g.add( (SENDER_ROLE, RDF.type, CRM.E55_Type) )
    g.add( (SENDER_ROLE, RDFS.label, Literal('Sender',datatype=XSD.string)) )

    # Sender person
    g.add( (SENDER, RDF.type, CRM.E21_Person) )
    g.add( (SENDER, RDFS.label, Literal(metadata[key_sender], datatype=XSD.string)) )

    # Production
    g.add( (PRODUCTION, RDF.type, CRM.E12_Production) )
    g.add( (PRODUCTION, RDFS.label, Literal('Compilation',datatype=XSD.string)) )
    g.add( (PRODUCTION, CRM.P9i_forms_part_of, ACTIVITY_EXCHANGE) )
    g.add( (PRODUCTION, CRM.P01_has_domain, ACTOR_AS_SENDER) )
    g.add( (PRODUCTION, CRM.P108_has_produced, LETTER) )
    g.add( (PRODUCTION, CRM.P7_took_place_at, PRODUCTION_PLACE))
    g.add( (PRODUCTION, CRM.P4_has_time_span, SENDING_TIMESPAN))

    # Production place
    g.add( (PRODUCTION_PLACE, RDF.type, CRM.E53_Place) )
    g.add( (PRODUCTION_PLACE, RDFS.label, Literal(metadata[key_production_place], datatype=XSD.string)))

    # Sending 
    g.add( (SENDING, RDF.type, CRM.E7_Activity) )
    g.add( (SENDING, RDFS.label, Literal('Sending',datatype=XSD.string)) )
    g.add( (SENDING, CRM.P16_used_specific_object, LETTER) )
    g.add( (SENDING, CRM.P9i_forms_part_of, ACTIVITY_EXCHANGE) )
    g.add( (SENDING, CRM.P4_has_time_span, SENDING_TIMESPAN))

    # Sending timespan    
    d = datetime.fromtimestamp(metadata[key_date]).strftime(timestring)

    g.add( (SENDING_TIMESPAN, RDF.type, CRM['E54_Time-span']) )
    g.add( (SENDING_TIMESPAN, CRM.P81a_end_of_the_begin, Literal(d, datatype=XSD.date)) )
    g.add( (SENDING_TIMESPAN, CRM.P81b_begin_of_the_end, Literal(d, datatype=XSD.date)) )

    # Get number of receivers
    if "Bernard and Mary Berenson" in metadata[key_receiver]:
      receivers = metadata[key_receiver]
      for receiver in receivers.split(' and '):

        if receiver == "Bernard":
          receiver = "Bernard Berenson"

        receiver_uri = f'{base_uri}person/{_create_person_id(receiver)}'
        RECEIVER = URIRef(receiver_uri)

        # Actor as receiver (?)
        g.add( (ACTIVITY_EXCHANGE, CRM.P01_has_domain, ACTOR_AS_RECEIVER))
        g.add( (ACTOR_AS_RECEIVER, CRM['P14.1_in_the_role_of'], RECEIVER_ROLE) ) 
        g.add( (ACTOR_AS_RECEIVER, CRM.P02_has_range, RECEIVER) )
        
        # Receiver role
        g.add( (RECEIVER_ROLE, RDF.type, CRM.E55_Type) )
        g.add( (RECEIVER_ROLE, RDFS.label, Literal('Receiver',datatype=XSD.string)) )

        # Receiver person
        g.add( (RECEIVER, RDF.type, CRM.E21_Person) )
        g.add( (RECEIVER, RDFS.label, Literal(receiver, datatype=XSD.string)) )
    else:
      receiver_uri = f'{base_uri}person/{_create_person_id(metadata[key_receiver])}'
      RECEIVER = URIRef(receiver_uri)

      # Actor as receiver (?)
      g.add( (ACTIVITY_EXCHANGE, CRM.P01_has_domain, ACTOR_AS_RECEIVER))
      g.add( (ACTOR_AS_RECEIVER, CRM['P14.1_in_the_role_of'], RECEIVER_ROLE) ) 
      g.add( (ACTOR_AS_RECEIVER, CRM.P02_has_range, RECEIVER) )
      
      # Receiver role
      g.add( (RECEIVER_ROLE, RDF.type, CRM.E55_Type) )
      g.add( (RECEIVER_ROLE, RDFS.label, Literal('Receiver',datatype=XSD.string)) )

      # Receiver person
      g.add( (RECEIVER, RDF.type, CRM.E21_Person) )
      g.add( (RECEIVER, RDFS.label, Literal(metadata[key_receiver], datatype=XSD.string)) )

    g.namespace_manager.bind(PLATFORM_NAME, PLATFORM, override = True, replace=True)
    g.namespace_manager.bind(PROV_NAME, PROV, override = True, replace=True)
    g.namespace_manager.bind(CRM_NAME, CRM, override = True, replace=True)
    g.namespace_manager.bind(LDP_NAME, LDP, override=True, replace=True)

    return g

def _write_RDF(filename, metadata, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    metadata.serialize(destination=f'{directory}/{filename}', format='turtle')

def _update_ids(letters):
    
    _id = 1
    
    ordered_letters = sorted(letters, key=itemgetter(key_date), reverse=False)

    for letter in ordered_letters:
       letter['id'] = f'Letter_{_id:03d}' 
       _id+=1

    with open(os.path.join('dbs', 'letters_ordered.json'), 'w') as f:
        json.dump(ordered_letters, f)

def extract(filename, directory):

    extracted_data = []

    with open(filename, 'r') as f:
        data = json.load(f)

        _update_ids(data)

        for letter in data:

            date = letter[key_date]
            title = letter[key_title]
            body = letter[key_body]
            _id = letter[key_id]

            file_body = _clean_body(body)
            body_text = file_body.get_text(separator="\n")

            _write_letter_html(f'{_id}.{extension_html}', content=file_body, directory=directory)
            _write_letter_txt(f'{_id}.{extension_txt}', content=file_body, directory=directory)

            extracted_data.append({
                key_filename: _id,
                key_title: title,
                key_date: date,
                key_body_text: body_text
            })

        f.close()

    return extracted_data

def tag(uri, input_metadata, directory):

    for letter in input_metadata:

        for key, metadatum in _parse_title(letter[key_title]).items():
            letter[key] = metadatum

        letter[key_sending_date] = _parse_date(letter[key_date])

        data = _create_RDF(uri, letter)

        _write_RDF(f'{letter[key_filename]}.{extension_ttl}', data, directory)

def _del(filename, url):

    # curl -v -u admin:admin -X DELETE -H 'Content-Type: text/turtle' http://127.0.0.1:10214/rdf-graph-store?graph=http%3A%2F%2Fdpub.cordh.net%2Fdocument%2FBernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html%2Fcontext

    command = f'curl -u {tmp1}:{tmp2} -X DELETE -H \'Content-Type: text/turtle\' {url}'

    return f'DEL\t{os.system(command)}'

def _post(filename, url, directory):

    #curl -v -u admin:admin -X POST -H 'Content-Type: text/turtle' --data-binary '@metadata/Bernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html.ttl' http://127.0.0.1:10214/rdf-graph-store?graph=http%3A%2F%2Fdpub.cordh.net%2Fdocument%2FBernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html%2Fcontext

    filename = os.path.join(directory,filename)
    command = f'curl -u {tmp1}:{tmp2} -X POST -H \'Content-Type: text/turtle\' --data-binary \'@{filename}.{extension_ttl}\' {url}'

    return f'POST\t{os.system(command)}'

def post(endpoint, uri, directory):

    for metadata_file in os.listdir(directory):

        filename = metadata_file.split('.')[0]
        graph_name = urllib.parse.quote(f'{uri}/document/{filename}/context', safe='')
        
        r_url = f'{endpoint}?graph={graph_name}'

        print(f'\n{filename}')

        #DEL
        print(_del(filename, r_url))

        #PUT
        #print(_post(filename, r_url, directory))

