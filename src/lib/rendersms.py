from __future__ import print_function
from PIL import Image, ImageDraw, ImageFont
import requests
from StringIO import StringIO
import base64
from render import render_text_to_image

def get_image(url, content_type, format='ppm', width=128):
    # get image from twillio
    r = requests.get(url)
    i = Image.open(StringIO(r.content))

    # resize
    i_resize = i.resize((width, i.size[1]*width/i.size[0]))

    # base64 encode
    output = StringIO()
    i_resize.save(output, format=format)
    return base64.b64encode(output.getvalue())

def render_images(event):
    num_media = int(event['NumMedia'])
    return [get_image(event['MediaUrl%d'%i], event['MediaContentType%d'%i])
              for i in range(0, num_media)]

# returns list of images
def render_sms(to_name, from_name, message, images):
    if message:
        images.insert(0, render_text_to_image(message,
                                              from_name=from_name, 
                                              to_name=to_name))
    return images
    

