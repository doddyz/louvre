# Deploy & Share with Fo
# Convert MET App accordingly
# Adapt code to deployed version, see subfolder code logic
# urls = pd.read_clipboard(header=None)[0].values.tolist() use this to grab list of urls from browser

import numpy as np
import pandas as pd
import re
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
from pathlib import Path

BASE_SEARCH_URL = 'https://collections.louvre.fr/en/recherche?collection%5B0%5D=3&sort=date'

BASE_OBJECT_URL = 'https://collections.louvre.fr/en/ark:/53355/'

IMAGE_MAIN_URL_REGEX = re.compile(r'\/media\/cache\/large\/[0-9]{10}\/[0-9]{10}\/[0-9]{10}_[A-Z]+\.JPG')

IMAGE_THUMB_URL_REGEX = re.compile(r'\/media\/cache\/small\/[0-9]{10}\/[0-9]{10}\/[0-9]{10}_[A-Z]+\.JPG')

IMAGE_FILE_REGEX = re.compile(r'([0-9]{10}_[A-Z]+\.JPG)')

OBJECT_DATE_CAPTION_REGEX = re.compile(r'\(.+\)')

BASE_URL_LOUVRE = 'https://collections.louvre.fr'

SAMPLE_OBJECT_URL = 'https://collections.louvre.fr/en/ark:/53355/cl010020253'

SAMPLE_OBJECT_URLS = [
    'https://collections.louvre.fr/en/ark:/53355/cl010020253',
    'https://collections.louvre.fr/en/ark:/53355/cl010011049',
    'https://collections.louvre.fr/en/ark:/53355/cl010010843',
    'https://collections.louvre.fr/en/ark:/53355/cl010012746',
    'https://collections.louvre.fr/en/ark:/53355/cl010022808'
    ]

SAMPLE_IMAGE_URL = 'https://collections.louvre.fr/media/cache/large/0000000021/0000020253/0000403023_OG.JPG'

# HTML ELTS REGEXES to scrap particular pieces of text on webpage
H1_REGEX = re.compile(r'<h1 class="notice__title h_1">(.+\n*.+\n*)</h1>')
TITLE_REGEX = re.compile(r'<title>(.+\n*.+\n*)</title>')
OBJECT_DATE_REGEX = re.compile(r'Date de création\/fabrication : ([^()0-9-]+)(.+)(-\d+ - -\d+)')


# Search Funs
def louvre_search_url(search_query):
    return BASE_SEARCH_URL + '&q=' + search_query


def louvre_search_results_csv(search_query):
    return louvre_search_url(search_query).replace('recherche', 'search/export')


def add_image_url_cols_to_df(df):
    image_thumb_urls = []
    # Get Image Thumb for each Object in the df
    for i in range(df.shape[0]):
        r = requests.get(df.loc[df.index[i], 'Object Url'])
        image_thumb_url_path_list = re.findall(IMAGE_THUMB_URL_REGEX, r.text)
        # Skip results without images
        if len(image_thumb_url_path_list) > 0:
            image_thumb_url_path = image_thumb_url_path_list[0] 
            image_thumb_url = BASE_URL_LOUVRE + image_thumb_url_path
            # Add empty url value which will be skipped in main function
        else:
            image_thumb_url = ''

        image_thumb_urls.append(image_thumb_url)
        
    df['Image Thumb Url'] = image_thumb_urls
    df['Image Url'] = df['Image Thumb Url'].str.replace('small', 'large')
    

@st.cache
def louvre_results_df(search_query, number_results_limit):
    image_thumb_urls = []
    df = pd.read_csv(louvre_search_results_csv(search_query), delimiter=';')
    df['Object Url'] = BASE_OBJECT_URL + df['ARK']

    number_results_total = df.shape[0]

    # Restrict df size to user chosen number of results
    df = df[:number_results_limit]

    add_image_url_cols_to_df(df)

    return df, number_results_total


def write_results_images(df, number_results, width):
    captions = df['Object name/Title'] + '\n' + df['Date'].str.replace(OBJECT_DATE_CAPTION_REGEX, '') + '\n' + df['Object Url']
    # return st.image(df['Image Thumb Url'].to_list(), df['Object name/Title'].to_list(), width)
    return st.image(df['Image Thumb Url'].to_list(), captions.to_list(), width)


# May reuse in future but would need to fully rewrite from scratch
def write_results_images_grid(df, number_results, width):
    i = 0
    col1, col2, col3, col4 = st.columns(4)
    while (i <= number_results - 1):
        image_col1 = df.loc[df.index[i], 'Image Thumb Url']
        image_col2 = df.loc[df.index[i + 1], 'Image Thumb Url']
        image_col3 = df.loc[df.index[i + 2], 'Image Thumb Url']
        image_col4 = df.loc[df.index[i + 3], 'Image Thumb Url']
        image_title1 = df.loc[df.index[i], 'Object name/Title']
        image_title2 = df.loc[df.index[i + 1], 'Object name/Title']
        image_title3 = df.loc[df.index[i + 2], 'Object name/Title']
        image_title4 = df.loc[df.index[i + 3], 'Object name/Title']
        image_object_url1 = df.loc[df.index[i], 'Object Url']
        image_object_url2 = df.loc[df.index[i + 1], 'Object Url']
        image_object_url3 = df.loc[df.index[i + 2], 'Object Url']
        image_object_url4 = df.loc[df.index[i + 3], 'Object Url']
        image_date1 = df.loc[df.index[i], 'Date']
        image_date2 = df.loc[df.index[i + 1], 'Date']
        image_date3 = df.loc[df.index[i + 2], 'Date']
        image_date4 = df.loc[df.index[i + 3], 'Date']
        image_caption1 = image_title1 + '\n' + OBJECT_DATE_CAPTION_REGEX.sub('', image_date1) + '\n' + image_object_url1
        image_caption2 = image_title2 + '\n' + OBJECT_DATE_CAPTION_REGEX.sub('', image_date2) + '\n' + image_object_url2
        image_caption3 = image_title3 + '\n' + OBJECT_DATE_CAPTION_REGEX.sub('', image_date3) + '\n' + image_object_url3
        image_caption4 = image_title4 + '\n' + OBJECT_DATE_CAPTION_REGEX.sub('', image_date4) + '\n' + image_object_url4


        
        col1.image(image_col1, image_caption1, width)
        col2.image(image_col2, image_caption2, width)
        col3.image(image_col3, image_caption3, width)
        col4.image(image_col4, image_caption4, width)
        
        i += 4
    

# Image Funs
def create_base_object_image_filename(object_url):

    base_title = get_webpage_h1(object_url)[0]
    base_title = base_title.replace(' ; ', '_')
    
    object_date_text1 = get_webpage_text_matching_regex(OBJECT_DATE_REGEX, object_url)[0][0]
    # object_date_text2 = get_webpage_text_matching_regex(OBJECT_DATE_REGEX, object_url)[0][1]
    object_date_text3 = get_webpage_text_matching_regex(OBJECT_DATE_REGEX, object_url)[0][2]

    object_date_text = object_date_text1.strip() + re.sub(r'(-\d+) - (-\d+)', r'_\1_\2', object_date_text3)
    
    return base_title + '_' + object_date_text



def get_all_image_urls_from_object_page(object_url):
    r = requests.get(object_url)
    match_list = re.findall(IMAGE_MAIN_URL_REGEX, r.text)
    # Remove any found duplicates
    match_list_unique = list(set(match_list))
    base_filename = create_base_object_image_filename(object_url)
    
    return {base_filename + '_v' + str(i) + '.jpg': BASE_URL_LOUVRE + match for i, match in enumerate(match_list_unique)}
   

def save_all_images_from_object_pages(object_urls, folder_name):
    cwd = Path.cwd()
    for object_url in object_urls:
        image_urls_dic = get_all_image_urls_from_object_page(object_url)
        for filename in image_urls_dic.keys():     
            fp = cwd / folder_name / filename
            # Fetch image as byte object and save with Image module
            r = requests.get(image_urls_dic[filename])
            i = Image.open(BytesIO(r.content))
            # May need an extra command here to move files to correct folder
            i.save(fp)
def get_webpage_text_matching_regex(regex, webpage_url):
    webpage = requests.get(webpage_url).text    
    return re.findall(regex, webpage)

def get_webpage_title(webpage_url):
    return get_webpage_text_matching_regex(TITLE_REGEX, webpage_url)

def get_webpage_h1(webpage_url):
    return get_webpage_text_matching_regex(H1_REGEX, webpage_url)


# Download Funs
def convert_df(df, to_format='xl'):
    # return df.to_csv().encode('utf-8')
    # excel_filename='Results.xlsx'
    return df.to_excel('Results.xlsx')



# ST Starts here
st.set_page_config(
    page_title="Louvre Egypt Department Search",
    page_icon=":triangular_ruler:",
    layout="wide"
)


'''
# Louvre Egypt Image Search

'''

search_query = st.sidebar.text_input('Search')
number_results_limit = st.sidebar.number_input('Results limit', 20, 100, 20, 20)

# Convert to string otherwise cannot concat for url creation
number_results_limit = int(number_results_limit)
    
st.sidebar.markdown('***')

save_images_section = st.sidebar.expander('Save result images?')
with save_images_section:

    with st.form(key='save_images_form'):
    
        images_subfolder = st.text_input('Image Folder Name (Optional)')
        save_images = st.form_submit_button('Save')


download_results_section = st.sidebar.expander('Download search results')
    
with download_results_section:        
    with st.form(key='download_form'):
            
        save_as_extension = st.radio('Save as' , ('CSV', 'XLSX'))
        file_extension = save_as_extension.lower()
        filename = 'Results' + '.' + file_extension
        download_results = st.form_submit_button('Save')


number_results_total = st.sidebar.empty() 
                                
if search_query:
    try:
        df, number_results_total_int = louvre_results_df(search_query, number_results_limit)
        number_results_total.caption(f'{number_results_total_int} results in total')
        
        write_results_images(df, number_results_limit, 200)

    except:
        st.error('No results matching your query in the Egyptian Antiquities department, try something else')

    if save_images:
        save_all_images_from_object_pages(df['Object Url'][:number_results_limit], images_subfolder)
        st.sidebar.info(f'Saved images in folder {images_subfolder}')

    if download_results:
        data = df.to_csv(filename, index=False) if file_extension == 'csv' else df.to_excel(filename, index=False)
        st.sidebar.info(f'Saved results in {images_subfolder}')

              
    if st.checkbox('Display results table?'):
        df
                
    











