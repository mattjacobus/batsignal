from __future__ import print_function
import requests
from StringIO import StringIO
import base64
from PIL import Image

def get_image(url, content_type, format='ppm'):
    r = requests.get(url)
    i = Image.open(StringIO(r.content))
    output = StringIO()
    i.save(output, format=format)
    return base64.b64encode(output.getvalue())
    

