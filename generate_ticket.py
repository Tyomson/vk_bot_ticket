import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageColor


def generate_ticket(fio, from_, to, date):
    font_template = os.path.join('files', 'ofont.ru_PF Din Text Cond Pro.ttf')
    img_template = os.path.join('files', 'ticket_template.png')
    img = Image.open(img_template)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_template, size=17)

    for field, coordinate in zip([fio, from_, to, date],
                                 [(47, 123), (47, 193), (47, 259), (287, 262)]):
        draw.text(coordinate, field, font=font, fill=ImageColor.colormap['black'])
    # img.show()

    temp_file = BytesIO()
    img.save(temp_file, 'png')
    temp_file.seek(0)
    # save_to = os.path.join('files/test_ticket.png')
    # img.save(save_to)
    return temp_file
