from letters import utils as letter_ut
from people import utils as people_ut
import os

def do_letters():
    DB = 'letters'
    URI = 'collection.itatti.harvard.edu/yashiro'

    DIR_data = os.path.join(os.path.abspath('.'),DB ,'data')
    DIR_metadata = os.path.join(os.path.abspath('.'),DB ,'metadata')
    FILENAME = os.path.join(os.path.abspath('.'),'dbs',f'{DB}.json')

    # Extract data and write
    data = letter_ut.extract(FILENAME, directory=DIR_data)

    metadata = letter_ut.tag(URI, data, directory=DIR_metadata)

    # The server must be on!
    request = letter_ut.post(URI, directory=DIR_metadata, n=1)

def do_people():
    DB = 'people'
    URI = 'collection.itatti.harvard.edu'

    DIR_data = os.path.join(os.path.abspath('.'),DB, 'data')
    DIR_metadata = os.path.join(os.path.abspath('.'),DB,'metadata')

    FILENAME = os.path.join(os.path.abspath('.'),'dbs',f'{DB}.json')

    people_ut.tag(FILENAME, URI, directory=DIR_metadata)

    people_ut.post(URI,directory=DIR_metadata, n=1)

#do_letters()
do_people()