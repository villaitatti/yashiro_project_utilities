import json
import os
import re
import random
import string

from datetime import datetime
from rdflib import Graph, URIRef, namespace, Namespace, Literal
from bs4 import BeautifulSoup as bs

# Yashiro (in Paris) to Mary Berenson
# Yashiro to Bernard Berenson
# Elizabeth Berenson (in Settignano) to Yashiro (in Palo Alto, California)

key_date = 'created'
key_title = 'title'
key_body = 'body_value'

key_production_place = 'production_place'
key_receiving_place = 'receiving_place'

key_sender = 'sender'
key_receiver = 'receiver'
key_sending_date = 'sending_date'

key_filename = 'filename'

date_format = '%Y/%m/%d'

extension_html = 'html'
extension_ttl = 'ttl'

key_actors = 'actor'
key_places = 'places'

URI = {
    key_actors: {},
    key_places: {}
}

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
            content_output.append(para)

    return content_output

def _write_letter_html(filename, content, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, filename)

    with open(filename, 'w') as f:
        f.write(str(content))
        f.close()

def _parse_title(title):

    print(title)

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
    return datetime.fromtimestamp(date).strftime(date_format)

def _create_RDF(metadata):

    g = Graph()

    RDF = namespace.RDF
    XSD = namespace.XSD
    RDFS = namespace.RDFS

    CRM = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
    CRM_NAME = 'crm'

    DPUB_ANNOTATION = Namespace('http://dpub.cordh.net/annotation-schema/')
    CRMDIG = Namespace('http://www.ics.forth.gr/isl/CRMdig/')
    LDP = Namespace('http://www.w3.org/ns/ldp#')

    PROV = Namespace('http://www.w3.org/ns/prov#')
    PROV_NAME = 'prov'

    BASE = Namespace('http://www.researchspace.org/resource/')

    PLATFORM = Namespace('http://www.metaphacts.com/ontologies/platform#')
    PLATFORM_NAME = 'Platform'

    USER = Namespace('http://www.metaphacts.com/resource/user/')

    base_uri = 'http://yashiro.itatti.harvard.edu/'


    g.namespace_manager.bind(PLATFORM_NAME, PLATFORM, override = True, replace=True)
    g.namespace_manager.bind(PROV_NAME, PROV, override = True, replace=True)
    g.namespace_manager.bind(CRM_NAME, CRM, override = True, replace=True)

    # Main node
    base_node_uri = f'{base_uri}document/{metadata[key_filename]}'
    BASE_NODE = URIRef(base_node_uri)

    g.add( (BASE_NODE, RDF.type, CRM.E33_Linguistic_Object) )
    g.add( (BASE_NODE, RDF.type, DPUB_ANNOTATION.TextDocument) )
    g.add( (BASE_NODE, RDF.type, CRMDIG.D1_Digital_Object) )
    g.add( (BASE_NODE, RDF.type, PLATFORM.File) )
    g.add( (BASE_NODE, RDF.type, LDP.Resource) )
    g.add( (BASE_NODE, RDF.type, PROV.Entity) )
    g.add( (BASE_NODE, PLATFORM.fileContext, BASE.TextDocuments) )
    g.add( (BASE_NODE, PLATFORM.fileName, Literal(metadata[key_filename])) )
    g.add( (BASE_NODE, PLATFORM.mediaType, Literal('form-data')) )
    g.add( (BASE_NODE, PROV.generatedAtTime, Literal('DATE_HERE', datatype=XSD.dateTime)) )
    g.add( (BASE_NODE, PROV.wasAttributedTo, USER.admin) )

    g.add( (PLATFORM.fileContainer , URIRef('http://www.w3.org/ns/ldp#contains'), BASE_NODE) )
    
    base_uri = f'{base_uri}resource/'
    
    # Letter
    letter_id = _id_generator()
    letter_uri = f'{base_uri}letter/{letter_id}'
    LETTER = URIRef(letter_uri)

    g.add( (LETTER, RDF.type, CRM['E22_Man-made_Object']) )
    g.add( (BASE_NODE, CRM.P1_is_identified_by, LETTER) )

    # Activity exchange
    activity_exchange_id = _id_generator()
    activity_exchange_uri = f'{letter_uri}/exchange/{activity_exchange_id}'
    ACTIVITY_EXCHANGE = URIRef(activity_exchange_uri)

    g.add( (ACTIVITY_EXCHANGE, RDF.type, CRM.E7_Activity) )
    g.add( (ACTIVITY_EXCHANGE, CRM.P16_used_specific_object, LETTER) )

    # Actor as sender (?)
    actor_as_sender_uri = f'{activity_exchange_uri}/actor_as_sender'
    ACTOR_AS_SENDER = URIRef(actor_as_sender_uri)

    # Actor as receiver (?)
    actor_as_receiver_uri = f'{activity_exchange_uri}/actor_as_receiver'
    ACTOR_AS_RECEIVER = URIRef(actor_as_receiver_uri) 

    # Sender role
    sender_role_uri = f'{base_uri}role/sender'
    SENDER_ROLE = URIRef(sender_role_uri)

    g.add( (SENDER_ROLE, RDF.type, CRM.E55_Type) )
    g.add( (SENDER_ROLE, RDFS.label, Literal('Sender',datatype=XSD.string)) )

    g.add( (ACTOR_AS_SENDER, CRM['P14.1_in_the_role_of'], SENDER_ROLE) )

    # Receiver role
    receiver_role_uri = f'{base_uri}role/receiver'
    RECEIVER_ROLE = URIRef(receiver_role_uri)

    g.add( (RECEIVER_ROLE, RDF.type, CRM.E55_Type) )
    g.add( (RECEIVER_ROLE, RDFS.label, Literal('Receiver',datatype=XSD.string)) )

    g.add( (ACTOR_AS_RECEIVER, CRM['P14.1_in_the_role_of'], RECEIVER_ROLE) ) 

    # Sender person

    # Create new ID for the person and keep track
    try:
        sender_id = URI[key_actors][key_sender] 
    except:
        sender_id = _id_generator()
        URI[key_actors][metadata[key_sender]] = sender_id

    sender_uri = f'{base_uri}person/{sender_id}'
    SENDER = URIRef(sender_uri)

    g.add( (SENDER, RDF.type, CRM.E21_Person) )
    g.add( (SENDER, RDFS.label, Literal(metadata[key_sender], datatype=XSD.string)) )

    g.add( (ACTOR_AS_SENDER, CRM.P02_has_range, SENDER) )

    # Receiver person
    try:
        receiver_id = URI[key_actors][key_sender] 
    except:
        receiver_id = _id_generator()
        URI[key_actors][metadata[key_sender]] = sender_id

    receiver_uri = f'{base_uri}person/{receiver_id}'
    RECEIVER = URIRef(receiver_uri)

    g.add( (RECEIVER, RDF.type, CRM.E21_Person) )
    g.add( (RECEIVER, RDFS.label, Literal(metadata[key_receiver], datatype=XSD.string)) )

    g.add( (ACTOR_AS_RECEIVER, CRM.P02_has_range, RECEIVER) )

    # Production
    production_id = _id_generator()
    production_uri = f'{activity_exchange_uri}/compilation/{production_id}'
    PRODUCTION = URIRef(production_uri)

    g.add( (PRODUCTION, RDF.type, CRM.E12_Production) )
    g.add( (PRODUCTION, RDFS.label, Literal('Compilation',datatype=XSD.string)) )
    g.add( (PRODUCTION, CRM.P9i_forms_part_of, ACTIVITY_EXCHANGE) )
    g.add( (PRODUCTION, CRM.P01_has_domain, ACTOR_AS_SENDER) )
    g.add( (PRODUCTION, CRM.P108_has_produced, LETTER) )

    # Production place
    try:
        production_place_id = URI[key_places][key_production_place] 
    except:
        production_place_id = _id_generator()
        URI[key_places][metadata[key_production_place]] = production_place_id

    production_place_uri = f'{base_uri}place/{production_place_id}'
    PRODUCTION_PLACE = URIRef(production_place_uri)

    g.add( (PRODUCTION_PLACE, RDF.type, CRM.E53_Place) )
    g.add( (PRODUCTION_PLACE, RDFS.label, Literal(metadata[key_production_place], datatype=XSD.string)))

    g.add( (PRODUCTION, CRM.P7_took_place_at, PRODUCTION_PLACE))

    # Sending 
    sending_id = _id_generator()
    sending_uri = f'{activity_exchange_uri}/sending/{sending_id}'
    SENDING = URIRef(sending_uri)

    g.add( (SENDING, RDF.type, CRM.E7_Activity) )
    g.add( (SENDING, RDFS.label, Literal('Sending',datatype=XSD.string)) )
    g.add( (SENDING, CRM.P16_used_specific_object, LETTER) )
    g.add( (SENDING, CRM.P9i_forms_part_of, ACTIVITY_EXCHANGE) )

    # Timespan
    sending_timespan_id = _id_generator()
    sending_timespam_uri = f'{sending_uri}/timespan/{sending_timespan_id}'
    SENDING_TIMESPAN = URIRef(sending_timespam_uri)
    
    g.add( (SENDING_TIMESPAN, RDF.type, CRM['E54_Time-span']) )

    g.add( (PRODUCTION, CRM.P4_has_time_span, SENDING_TIMESPAN))
    g.add( (SENDING, CRM.P4_has_time_span, SENDING_TIMESPAN))

    g.add( (SENDING_TIMESPAN, CRM.P81a_end_of_the_begin, Literal(metadata[key_date], datatype=XSD.dateTime)) )
    g.add( (SENDING_TIMESPAN, CRM.P81b_begin_of_the_end, Literal(metadata[key_date], datatype=XSD.dateTime)) )

    """
    # Timespan start
    sending_timespam_end_of_the_begin_uri = f'{sending_timespam_uri}/end_of_the_begin'
    SENDING_TIMESPAN_END_OF_THE_BEGIN = URIRef(sending_timespam_end_of_the_begin_uri)

    g.add( (SENDING_TIMESPAN_END_OF_THE_BEGIN, RDF.type, XSD.dateTime) )
    g.add( (SENDING_TIMESPAN_END_OF_THE_BEGIN, RDFS.label, Literal(metadata[key_date],datatype=XSD.dateTime)) )


    # Timespan end
    sending_timespam_begin_of_the_end_uri = f'{sending_timespam_uri}/begin_of_the_end'
    SENDING_TIMESPAN_BEGIN_OF_THE_END = URIRef(sending_timespam_begin_of_the_end_uri)

    g.add( (SENDING_TIMESPAN_BEGIN_OF_THE_END, RDF.type, XSD.dateTime) )
    g.add( (SENDING_TIMESPAN_BEGIN_OF_THE_END, RDFS.label, Literal(metadata[key_date],datatype=XSD.dateTime)) )
    """

    return g

def _write_RDF(filename, metadata, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    metadata.serialize(destination=f'{directory}/{filename}', format='turtle')

def extract(filename, directory):

    extracted_data = []

    with open(filename, 'r') as f:
        data = json.load(f)

        for letter in data:
            date = letter[key_date]
            title = letter[key_title]
            body = letter[key_body]

            filename = f'{_manipulate_title(title)}_{date}.{extension_html}'
            file_body = _clean_body(body)

            _write_letter_html(filename, content=file_body, directory=directory)

            extracted_data.append({
                key_filename: filename,
                key_title: title,
                key_date: date
            })

        f.close()

    return extracted_data

def tag(input_metadata, directory):

    extracted_metadata = []

    for letter in input_metadata:

        for key, metadatum in _parse_title(letter[key_title]).items():
            letter[key] = metadatum

        letter[key_sending_date] = _parse_date(letter[key_date])

        data = _create_RDF(letter)

        _write_RDF(f'{letter[key_filename]}.{extension_ttl}', data, directory)

        return data