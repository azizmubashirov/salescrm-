import random
import string
from contextlib import closing
from django.db import connection
import barcode
from barcode.writer import ImageWriter


SHORTCODE_MIN = 8

def code_generator(size=SHORTCODE_MIN, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def create_tabnumber(instance, size=SHORTCODE_MIN):
    country_code = str(random.choice([str(x) for x in range(450, 461)] + [str(x) for x in range(490, 501)]))
    new_code = country_code + code_generator(size=4)
    ean = barcode.get_barcode_class('ean8')
    book_barcode = ean(new_code, writer=ImageWriter())
    extra_sql = """select(EXISTS(SELECT 1 FROM client WHERE tab_number=%s)) as has"""
    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, [book_barcode.get_fullcode()])
        exists = cursor.fetchone()
    if exists[0]:
        return create_tabnumber(instance, size=size)
    
    outputFileFolder = 'media/clinet_barcode/'
    outputFile = outputFileFolder + f'{book_barcode.get_fullcode()}_barcode'
    book_barcode.save(outputFile)
    return book_barcode.get_fullcode(), outputFile+".png"



        
        