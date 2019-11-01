# ---------------------------------------------------------------------------------------
# Python class "Amazon" for scientific and research purposes
#
# Purpose: Provide simple functionality for researching data about products on Amazon.de.
# Webpages containing lists of products ("overviews") and stored locally are used as sources.
# The class provides some methods for extracting relevant product data from local HTML files.
# It uses BeautifulSoup and stores the data extracted in a CSV file on a local storage, too.
#
# Input: Assumption about data acquisition
# - Each webpage to be analyzed is stored locally in a file referred to as "source file"
# - Each source file contains the HTML/ CSS/ JavaScript/ etc. data "just as they are"
# - Each source file has the following filename structure: InternalID_YYYY-MM-DD_HH-MM-SS
#
# Output: Target data model and data types
# - The output data consists the following data types: String, Integer and Float
# - Columns/ attributes are as follows:
#   - product_name: String - contains the the product's name
#   - list_position: Integer - contains the product's position in product list
#   - list_position_inverse: Integer - contains the inverse position in the list
#   - product_price_eur: String (should be Float...) - contains price or price range 
#   - product_url: String - URL that points to the product's detail page
#   - rating_stars: String - current star rating of the product ("x of y stars")
#   - rating_stars_clean: Float - current star rating of the product (e.g. "4,4")
#   - rating_count: Integer - contains the absolute number of reviews/ ratings
#   - acquisition_date: YYYY-MM-DD - contains the date according to source filename
#   - acquisition_year, acquisition_month & acquisition_day: see above
#   - acquisition_time: HH:MM:SS - contains the time according to source filename
#   - acquisition_hour, acquisition_minutes & acquisition_seconds: see abovee
#   - source_filename: String - contains the source's filename (see structure given above)
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# Import packages
# ---------------------------------------------------------------------------------------
from bs4 import BeautifulSoup   # Let's use BeautifulSoup for extracting data from HTML
import os                       # Will be used for reading filenames from input directory
import csv                      # We'll export all the data we extract into a csv file
import sys                      # Used only for determining the current version of Python
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# Class definition: Variables, constructor and methods
# ---------------------------------------------------------------------------------------
class Amazon:

    # -----------------------------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------------------------
    def __init__(self):
        self.data_raw = None
        self.data_extracted = []
        print("%s%s" %("Python version: ", sys.version[:5]))   # Tested with 3.7.1 64-bit
    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
    # Parse raw data and extract information
    # -----------------------------------------------------------------------------------
    def parse(self,content,filename):
        try:
            # Use BeautifulSoup for reading HTML data and extract relevant contents
            self.data_raw = BeautifulSoup(content,'html5lib')
            all_products = self.data_raw.find_all('div',{'class':'a-section a-spacing-none aok-relative'})
            
            # For each product extracted from HTML/ CSS data, do the following
            for each in all_products:
                try:
                    ld=[]

                    # Extract the product's name
                    # Assumption: There can be two types of HTML/ CSS classes which can contain the name
                    product_name = ""
                    try:
                        product_name = each.find('div', {'class': 'p13n-sc-truncate p13n-sc-line-clamp-3'}).get_text()
                    except AttributeError:
                        try:
                            product_name = each.find('div', {'class': 'p13n-sc-truncate p13n-sc-line-clamp-2'}).get_text()
                        except AttributeError:
                            product_name = str('Error: Product name not found')
                    ld.append(str(product_name.replace('\n','').encode('ascii', 'ignore').strip()))
                   
                    # Extract the product's position and compute its inverse position
                    # Assumption: The number of products per page (noppp) is always 50
                    noppp = 50
                    list_position = ""
                    list_position = str(each.find('span',{'class':'zg-badge-text'}).get_text().replace(u'#',''))
                    ld.append(list_position.strip())
                    list_position_inverse = str(noppp-int (list_position)+1)
                    ld.append(list_position_inverse)
                    
                    # Extract the product's price
                    product_price_eur = ""
                    try:
                        product_price_eur = each.find('span', {'class': 'p13n-sc-price'}).get_text()
                    except AttributeError:
                        product_price_eur = str('Error: Product price not found')
                    ld.append(product_price_eur.replace('\xa0€', '').strip())
                    
                    # Extract the URL that points to the product's detail page
                    url_full = each.find('a', {'class': 'a-link-normal'})['href'].split('/')
                    product_url = ""
                    for i in range(2,len(url_full)-2,1):
                        product_url += "/" + url_full[i]
                    ld.append(str(product_url).strip())

                    # Extract the current star rating of the product
                    rating_stars = ""
                    rating_stars_clean = ""
                    try:
                        rating_stars = each.find('span', {'class': 'a-icon-alt'}).get_text().strip()
                        rating_stars_clean = str(rating_stars.split(' ')[0]).strip()
                    except AttributeError:
                        rating_stars = str('Error: Stars rating not found')
                        rating_stars_clean = rating_stars
                    ld.append(rating_stars)
                    ld.append(rating_stars_clean)

                    # Extract the absolute number of reviews/ ratings
                    rating_count = ""
                    try:
                        rating_count = each.find('a', {'class': 'a-size-small a-link-normal'}).get_text().strip()
                    except AttributeError:
                        rating_count = str('Error: Number of ratings not found')
                    ld.append(rating_count)

                    # Timestamp part #1: Extract the date from the source's filename
                    # Assumption about filename structure: InternalID_YYYY-MM-DD_HH-MM-SS
                    fnc = filename.split('_')
                    nd = fnc[1]
                    ndd = nd.split('-')
                    nd_year = ndd[0]
                    nd_month = ndd[1]
                    nd_day = ndd[2]
                    ld.append(nd)           # Append date in full, i.e. YYYY-MM-DD
                    ld.append(nd_year)      # Append year solely, i.e. YYYY
                    ld.append(nd_month)     # Append month solely, i.e. MM
                    ld.append(nd_day)       # Append day solely, i.e. DD

                    # Timestamp part #2: Time (extracted from source's filename)
                    # Assumption about filename structure: InternalID_YYYY-MM-DD_HH-MM-SS
                    nt = fnc[2].replace('-',':')
                    nt_hour = nt.split(':')[0]
                    nt_minutes = nt.split(':')[1]
                    nt_seconds = nt.split(':')[2]
                    ld.append(nt)           # Append time in full, i.e. HH:MM:SS
                    ld.append(nt_hour)      # Append hour solely, i.e. HH
                    ld.append(nt_minutes)   # Append minutes solely, i.e. MM
                    ld.append(nt_seconds)   # Append seconds solely, i.e. SS

                    # Append the source's filename to product data
                    ld.append(filename)
                    
                    # Append the product's data to the collection
                    self.data_extracted.append(ld)

                except Exception (e):
                    continue

        except Exception (e):
            print ("Parsing error...")
            #print str (e)
    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
    # Write extracted information to CSV file
    # -----------------------------------------------------------------------------------
    def write(self):
        try:
            columns = ['product_name', 'list_position', 'list_position_inverse',
                    'product_price_eur', 'product_url', 'rating_stars',
                    'rating_stars_clean', 'rating_count', 'acquisition_date',
                    'acquisition_year', 'acquisition_month', 'acquisition_day',
                    'acquisition_time', 'acquisition_hour', 'acquisition_minutes',
                    'acquisition_seconds', 'source_filename']
           
            with open('output.csv', 'w') as f:
                f.write(';'.join(columns) + '\n')
                for row in self.data_extracted:
                    # print(row)
                    f.write(';'.join(row) + '\n')

        except Exception (e):
            print ("Error: Writing data into the output file failed")
            #print str(e)
    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
    # Open local files that contain raw data
    # Filenames of local html files can be specified in the array "files"
    # -----------------------------------------------------------------------------------
    def file_handling(self):
        files = os.listdir()    # Read all filenames from working directory (= source files)
        for filename in files:
            with open(filename,'rb') as fl:
                content = fl.read()
                fl.close()
                self.parse(content,filename)
    # -----------------------------------------------------------------------------------
        
    # -----------------------------------------------------------------------------------
    # Run methods
    # -----------------------------------------------------------------------------------     
    def run(self):
        self.file_handling()
        self.write()
    # -----------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# Create new object and execute code
# ---------------------------------------------------------------------------------------
a = Amazon()
a.run()
# ---------------------------------------------------------------------------------------
