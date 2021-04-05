#################################
##### Name: Mariele Ventrice
##### Uniqname: marielev
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

BASE_URL = "https://www.nps.gov"
CACHE_DICT = {}
CACHE_FILENAME = "nps_scrape.json"

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"


def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): # the url is unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    base_url = "https://www.nps.gov"
    response = requests.get("https://www.nps.gov/index.htm")
    soup = BeautifulSoup(response.text, "html.parser")
    states_ul = soup.find("ul", class_="dropdown-menu SearchBar-keywordSearch")
    list_of_states = states_ul.find_all('a')
    state_dict = {}
    for state in list_of_states:
        state_name = state.text.strip().lower()
        state_dict[state_name] = base_url + state['href']
    return state_dict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    response = requests.get(site_url)
    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find('a', class_="Hero-title").text.strip()
    category = soup.find('span', class_="Hero-designation").text.strip()
    address = soup.find('span', itemprop="addressLocality").text.strip() + ", " + soup.find('span', itemprop="addressRegion").text.strip()
    zipcode = soup.find('span', itemprop="postalCode").text.strip()
    phone = soup.find('span', itemprop="telephone").text.strip()
    park_instance = NationalSite(name=name, category=category, address=address, zipcode=zipcode, phone=phone)
    return park_instance


#Going to pass get_site_instance() into here.#
def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    base_url = "https://www.nps.gov"
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, "html.parser")
    parks_parent = soup.find('ul', id="list_parks")
    parks_list = parks_parent.find_all('li', recursive=False)
    counter = 0
    list_national_park_instances = []
    for park in parks_list:
        park_name = park.find('h3')
        park_url = base_url + park_name.find('a')['href']
        park_instance = get_site_instance(park_url)
        list_national_park_instances.append(park_instance)
        counter += 1
        print(f"[{counter}] {park_instance.info()}")
    return list_national_park_instances
get_sites_for_state("https://www.nps.gov/state/mi/index.htm")


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    pass
    

# if __name__ == "__main__":
# input('Enter a state name (e.g. "Massachusetts") or type "exit" to close program.