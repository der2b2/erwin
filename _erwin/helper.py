import os
import re
import shutil

def copy_files(from_folder, to_folder):
    os.makedirs(os.path.dirname(to_folder + "/test.txt"), exist_ok=True)
    for file in os.listdir(from_folder):
        shutil.copy(from_folder + "/" + file, to_folder)

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def count_words(input_string):
    res = len(re.findall(r'\w+', clean_html(input_string)))
    return res

#returns average reading length in minutes
#minimum is 1
def reading_time(input_string):
    return max(int(round(count_words(input_string) / 200.0, 0)), 1)

def prepare_string_for_html(input_string):
    url = input_string.lower()
    chars = {'ö':'oe','ä':'ae','ü':'ue','ß':'ss',' ':'-','_':'-','?':'','!':'','&':'-','/':'-'}
    for char in chars:
        url = url.replace(char,chars[char])
    return url