from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO
from os import path
import random
import base64

colors=['red','green','blue','white']

def get_font(filename, size):
    fontPath = path.join(path.dirname(path.abspath(__file__)), filename)
    # assumes font file is peer of PIL
    getMessagePath = path.join(path.dirname(path.abspath(__file__)), 
                               'PIL/OleFileIO-README.md')
    return ImageFont.truetype(fontPath, size)

# returns single image
def render_text_to_image(text, from_name=None, to_name=None,
                         format='ppm', font=get_font('Calibri.ttf', 16)):
    img = Image.new('RGB', (128, 16), (0, 0, 0))

    # get a drawing context
    d = ImageDraw.Draw(img)
    w,h = d.textsize(text, font=font)
    img = img.resize((w+30,h))
    d = ImageDraw.Draw(img)

    color = colors[random.randint(0, len(colors)-1)]

    d.text((5,0), text, font=font, fill=color)
    output = StringIO()
    img.save(output, format=format)
    return base64.b64encode(output.getvalue())    
    
