from extractor import extractor as ex
import os

FILENAME = os.path.join(os.path.abspath('.'),'dbs','letters.json')
DIR = os.path.join(os.path.abspath('.'),'data')

# Extract data and write
ex.execute(FILENAME, directory=DIR)
