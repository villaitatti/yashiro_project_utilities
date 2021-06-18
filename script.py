from letters import utils as letter_ut
from people import utils as people_ut
from images import utils as images_ut
import argparse
import urllib
import os

auth = {
    "user": "",
    "pasw": ""    
}

def post(endpoint, uri, function, directory, auth):

    def _del(filename, url, auth):

        # curl -v -u admin:admin -X DELETE -H 'Content-Type: text/turtle' http://127.0.0.1:10214/rdf-graph-store?graph=http%3A%2F%2Fdpub.cordh.net%2Fdocument%2FBernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html%2Fcontext

        command = f'curl -u {auth["user"]}:{auth["pasw"]} -X DELETE -H \'Content-Type: text/turtle\' {url}'

        return f'DEL\t{os.system(command)}'

    def _post(filename, url, directory, auth):

        #curl -v -u admin:admin -X POST -H 'Content-Type: text/turtle' --data-binary '@metadata/Bernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html.ttl' http://127.0.0.1:10214/rdf-graph-store?graph=http%3A%2F%2Fdpub.cordh.net%2Fdocument%2FBernard_Berenson_in_Consuma_to_Yashiro_-1149037200.html%2Fcontext

        filename = os.path.join(directory, filename)
        command = f'curl -u {auth["user"]}:{auth["pasw"]} -X POST -H \'Content-Type: text/turtle\' --data-binary \'@{filename}.ttl\' {url}'

        return f'POST\t{os.system(command)}'

    for metadata_file in os.listdir(directory):

        filename = metadata_file.split('.')[0]
        graph_name = urllib.parse.quote(f'{uri}{function}/{filename}/context', safe='')
        
        r_url = f'{endpoint}?graph={graph_name}'

        print(f'\n{filename}')

        #DEL
        print(_del(filename, r_url, auth))

        #PUT
        print(_post(filename, r_url, directory, auth))


"""

USAGE: python script.py -f [letters] [people] [images] 

"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--function', dest='functions', type=str, nargs='+')
    args = parser.parse_args()

    DIR_CURR = os.path.abspath(os.path.curdir)
    BASE_IRI = 'https://yashiro.itatti.harvard.edu/resource/'

    ENDPOINT_URL = 'https://y.itatti.harvard.edu/rdf-graph-store'

    for function in args.functions:

        DIR_DATA = os.path.join(DIR_CURR, function, 'data')
        DIR_METADATA = os.path.join(DIR_CURR, function, 'metadata')
        FILENAME = os.path.join(DIR_CURR, 'dbs', f'{function}.json')

        if function == "letters":
            data = letter_ut.extract(FILENAME, directory=DIR_DATA)

            letter_ut.tag(BASE_IRI, data, directory=DIR_METADATA)
            post(ENDPOINT_URL, BASE_IRI, function, directory=DIR_METADATA, auth=auth)

        if function == "people":
            people_ut.tag(FILENAME, BASE_IRI, directory=DIR_METADATA)
            post(ENDPOINT_URL, BASE_IRI, function, directory=DIR_METADATA, auth=auth)

        if function == "images":
            images_ut.tag(FILENAME, BASE_IRI, directory=DIR_METADATA)
            post(ENDPOINT_URL, BASE_IRI, function, directory=DIR_METADATA, auth=auth)




