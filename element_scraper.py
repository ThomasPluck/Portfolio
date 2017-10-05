# Import selenium objects
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Sleep to help us wait
from time import sleep

# NLTK words corpus and the random choice function
try:
    from nltk.corpus import words
except ModuleNotFoundError:
    pass
    
from random import choice

# PIL's Image object
from PIL import Image
import os

"""
We're going to set up a selenium chrome webdriver and
then google search random words using the nltk words
corpus.

We will select a random result and then crop images
of all the visible hyperlink and input elements

Both the screenshot and cropped images will be save
"""

def exitscript(i,j,raw_dir,crop_dir):
    """
    Quick script that prints images found and memory used on exit

    :i: int of raw images created
    
    :j: int of cropped images created
    
    :raw_dir: string representing screenshot saving directory
    
    :crop_dir: string representing cropped screenshot saving directory
    """
    screen_mem = sum(os.path.getsize(raw_dir) for f in os.listdir('.')\
                         if os.path.isfile(raw_dir))
    crop_mem = sum(os.path.getsize(crop_dir) for f in os.listdir('.')\
                     if os.path.isfile(crop_dir))
    
    print('\nScraper Closed!\n\nFinal Output:\n\n\tSites Scraped:\t',i,
          '\n\tImages Found:\t',j,'\n\n\tScreenshot Memory:\t',screen_mem//(1024**2),'MiB',
          '\n\n\tCropped Memory:\t',crop_mem//(1024**2),'MiB')

#Run until keyboard interrupt

def scrape_images(driver = webdriver.Chrome(),
                  crop_size = (100,100),
                  tag_list = ['a','input'],
                  word_list = words.words(),
                  raw_dir = 'scraped/raw',
                  crop_dir = 'scraped/cropped',
                  save_raw = True):
    """
    Function that scrapes screenshots from web pages from google searches
    and then crops out images of elements with tag names in tag_list in a
    loop over each string in the word_list

    :driver: A browser Selenium object (default:webdriver.Chrome())

    :crop_size: a tuple of ints representing pixel width and height of crops (default: (100,100))

    :tag_list: list of strings representing tags of elements to find on web pages (default: ['a','input'])

    :word_list: list of strings to represent search terms (default: nltk words corpus in list form)

    :raw_dir: string of directory to save screen shots (default: 'scraped/raw')

    :crop_dir: string of directory to save crops (default: 'scraped/cropped')

    :save_raw: boolean representing whether or not to save screenshots (default: True)
    """
    
    print('Starting Image Scraper!\n\n'+\
          'DO NOT MINIMIZE OR ALTER SIZE OF WINDOW OF BROWSER\n\n'+\
          'Press Ctrl+C to Interrupt Program Safely!\n')

    driver.maximize_window()

    driver.get('http://google.com')

    #Variables
    i = 0
    j = 0
    window_size = driver.get_window_size()
    
    while len(word_list) != 0:
            
        try:
            #Search a random word from the corpus
            search = driver.find_element_by_name('q')
            rand_word = choice(word_list)
            word_list.remove(rand_word)
            search.send_keys(rand_word)
            search.send_keys(Keys.RETURN)
            sleep(3)

            #Find and click a random search result
            results = driver.find_elements_by_tag_name('h3')
            choice(results).click()
            sleep(3)

            #Find all hyperlinks and inputs
            elements = []
            for tag in tag_list:
                elements.append([(elem,tag) for elem in driver.find_elements_by_tag_name(tag)])

            #Flatten our list and return attributes
            elements = [(elem.location,name) for sublist in elements\
                        for elem,name in sublist]

            #Select only elements visible in screenshot
            bounds = {'x':(crop_size[0]//2,window_size['width'] - crop_size[0]//2),
                      'y':(crop_size[1]//2,window_size['height'] - crop_size[1]//2)}
            
            elements = [(element,name) for element,name in elements \
                        if ((element['x'] > bounds['x'][0])|\
                            (element['x'] < bounds['x'][1])) &\
                        ((element ['y'] > bounds['y'][0])|\
                         (element ['y'] < bounds['y'][1]))]

            #Save screenshot of browser
            driver.save_screenshot(raw_dir+'/scraped_'+str(i).zfill(6)+'.png')
            print('Screenshot From:\t'+driver.current_url+'\n\tSaved At:\t'+raw_dir+'/scraped_'\
                  +str(i).zfill(6)+'.png\n')
            
            #Iterate over our element locations and crop images 
            for element,name in elements:
                img = Image.open('scraped/raw/scraped_'+str(i).zfill(6)+'.png')
                
                crop = img.crop((element['x']-crop_size[0]//2,
                                 element['y']-crop_size[1]//2,
                                 element['x']+crop_size[0]//2,
                                 element['y']+crop_size[1]//2))
                
                crop.save(crop_dir+'/crop_'+name+'_'+str(j).zfill(8)+'.png')

                #Print directory of every 100th cropped image
                if j%100 == 0:
                    print('\tCropped Image of Type:\t'+name+'\n\tSaved At:\t'+crop_dir+'/crop_'\
                          +name+'_'+str(j).zfill(8)+'.png\n')
                j += 1
                
            i += 1
            driver.back()
            search = driver.find_element_by_name('q')
            search.send_keys(len(rand_word)*'\b')
                      
        except KeyboardInterrupt:
            #Some final output about images saved and their space in memory
            exitscript(i,j,raw_dir,crop_dir)
            driver.close()
    else:
        exitscript(i,j,raw_dir,crop_dir)
        driver.close()

scrape_images()
