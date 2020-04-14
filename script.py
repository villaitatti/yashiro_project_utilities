from utilities import utils as ut
import os

DB = 'letters.json'

DIR_data = os.path.join(os.path.abspath('.'),'data')
DIR_metadata = os.path.join(os.path.abspath('.'),'metadata')

FILENAME = os.path.join(os.path.abspath('.'),'dbs',DB)

# Extract data and write
data = ut.extract(FILENAME, directory=DIR_data)

metadata = ut.tag(data, directory=DIR_metadata)

#upload to RS
# curl 'http://127.0.0.1:10214/sparql' -u admin:admin -H 'Content-Type: application/sparql-update; charset=UTF-8' -H 'Accept: text/boolean' -d @insert.sq