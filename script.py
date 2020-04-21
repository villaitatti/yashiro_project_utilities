from utilities import utils as ut
import os

DB = 'letters.json'

DIR_data = os.path.join(os.path.abspath('.'),'data')
DIR_metadata = os.path.join(os.path.abspath('.'),'metadata')

FILENAME = os.path.join(os.path.abspath('.'),'dbs',DB)

# Extract data and write
data = ut.extract(FILENAME, directory=DIR_data)

metadata = ut.tag(data, directory=DIR_metadata)

# The server must be on!
request = ut.post(directory=DIR_metadata)