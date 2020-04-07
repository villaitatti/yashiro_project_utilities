import json
import os
import re
from bs4 import BeautifulSoup as bs

# Yashiro (in Paris) to Mary Berenson
# Yashiro to Bernard Berenson
# Elizabeth Berenson (in Settignano) to Yashiro (in Palo Alto, California)

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

def _write(filename, content, directory):

    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, filename)

    with open(filename, 'w') as f:
        f.write(str(content))
        f.close()

def execute(filename, directory):

    extension = '.html'
    folder = 'files'

    with open(filename, 'r') as f:
        data = json.load(f)

        for letter in data:
            date = letter['created']

            title = letter['title']
            filename = f'{_manipulate_title(title)}{date}{extension}'

            body = letter['body_value']
            file_body = _clean_body(body)

            _write(filename, content=file_body, directory=directory)

        f.close()