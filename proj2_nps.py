#################################
##### Name: Mariele Ventrice
##### Uniqname: marielev
#################################

#### I was not able to figure out how to cache the mapquest request. It kept breaking my program. ####
#### Can we go over caching some more before the final project?? ####

from bs4 import BeautifulSoup
import requests
import json
import secrets

# BASE_URL = "https://www.nps.gov"
CACHE_DICT = {}
CACHE_FILE_NAME = "cache.json"

# MAPQUEST_CACHE_DICT = {}
# MAPQUEST_CACHE_FILENAME = "mapquest_cache.json"

client_key = secrets.API_KEY
client_secret = secrets.API_SECRET

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
    ''' Loads the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary. If the cache file doesn't exist, creates
    a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The loaded cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    contents_to_write = json.dumps(cache)
    cache_file = open(CACHE_FILE_NAME, 'a')
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''Check the cache for a saved result for url. If the result is found,
    return it. Otherwise, send a new request, save it, then return it. 

    Parameters
    ----------
    baseurl: string
        The URL for the get request
    cache: dictionary of json data

    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    if (url in cache.keys()): # the url is unique key
        print("Using cache")
        return cache[url]  
    else:
        print("Fetching")
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []  #empty list to store parameter strings (unique keys)
    connector = "_"
    for key in params.keys(): #for key in key value pair
        param_strings.append(f"{key}_{params[key]}") #adds key, value pair of of each paramater as key_value
    param_strings.sort() #sorts list so keys are in order
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def make_mapquest_api_request_with_cache(baseurl, cache, params):
    # params = {"key": client_key,"origin" : site_object.zipcode, "radius":"10","units":"m", "maxMatches":"10", "ambiguities":"ignore", "outFormat":"json"}
    request_key = construct_unique_key(baseurl, params)
    if request_key in cache.keys():
        print("using cache")
        return cache[request_key]
    else:
        print("fetching")
        cache[request_key] = requests.get(baseurl, params)
        save_cache(cache)
        return cache[request_key]

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
    # CACHE_DICT = load_cache()
    base_url = "https://www.nps.gov"
    response = make_url_request_using_cache("https://www.nps.gov/index.htm", CACHE_DICT)
    # response = requests.get("https://www.nps.gov/index.htm")
    soup = BeautifulSoup(response, "html.parser")
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
    # response = requests.get(site_url)
    # CACHE_DICT = load_cache()
    response = make_url_request_using_cache(site_url, CACHE_DICT)
    soup = BeautifulSoup(response, "html.parser")
    name = soup.find('a', class_="Hero-title").text.strip()
    category = soup.find('span', class_="Hero-designation").text.strip()
    address = soup.find('span', itemprop="addressLocality").text.strip() + ", " + soup.find('span', itemprop="addressRegion").text.strip()
    zipcode = soup.find('span', itemprop="postalCode").text.strip()
    phone = soup.find('span', itemprop="telephone").text.strip()
    park_instance = NationalSite(name=name, category=category, address=address, zipcode=zipcode, phone=phone)
    return park_instance

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
    # CACHE_DICT = load_cache()
    base_url = "https://www.nps.gov"
    response = make_url_request_using_cache(state_url, CACHE_DICT)
    # response = requests.get(state_url)
    soup = BeautifulSoup(response, "html.parser")
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
    base_url = "http://www.mapquestapi.com/search/v2/radius?"
    params = {"key":client_key,"origin":site_object.zipcode, "radius":"10","units":"m", "maxMatches":"10", "ambiguities":"ignore", "outFormat":"json"}
    # unique_key = construct_unique_key(base_url, params)
    # response = make_mapquest_api_request_with_cache(base_url, params, CACHE_DICT)
    response = requests.get(base_url, params=params)
    mapquest_response = response.json()
    return mapquest_response

def format_mapquest_results(mapquest_response):
    '''Prints up to 10 places from mapquest API results
    
    Parameters
        ----------
    mapquest_response
        The results of an API call to MapQuests formatted as json.
    
    Returns
    -------
    none
    '''
    mapquest_list = mapquest_response["searchResults"]
    for i in range(len(mapquest_list)):
        name = mapquest_list[i]["name"]
        category = mapquest_list[i]["fields"]["group_sic_code_name"]
        if category == "":
            category = "no category"
        street_address = mapquest_list[i]["fields"]["address"]
        if street_address == "":
            street_address = "no address"
        city = mapquest_list[i]["fields"]["city"]
        if city == "":
            city = "no city"
        print(f"– {name} ({category}): {street_address}, {city}")


if __name__ == "__main__":
    CACHE_DICT = load_cache()
    state_url_dict = build_state_url_dict()
    while True:
        user_input = input("Enter a state name (e.g. 'Massachusetts') or type 'exit' to quit. ")
        if user_input.lower() == "exit":
            quit()
        elif user_input.lower() not in state_url_dict.keys():
            print("Error. Enter proper state name")
        else:
            print("------------------------------")
            print("List of national sites in" + " " + user_input.capitalize())
            print("------------------------------")
            state_url = state_url_dict[user_input.lower()]
            national_sites = get_sites_for_state(state_url)
        # break
            while True:
                user_input = input("Enter a park number to see nearby places or 'exit' to quit. Enter 'back' to return to state search. ")
                if user_input.lower() == "exit":
                    quit()
                elif user_input.lower() == "back":
                    break
                else:
                    if user_input.isnumeric():
                        if int(user_input) <= len(national_sites):
                            user_input_number = int(user_input) - 1
                            site_object = national_sites[user_input_number]
                            mapquest_data = get_nearby_places(site_object)
                            print("------------------------------")
                            print("Places near" + " " + site_object.name)
                            print("------------------------------")
                            format_mapquest_results(mapquest_data)
                            break
                        else:
                            print("That number is out of range. Please enter a valid number.")
                            break
                    else:
                        print("Error. Please enter a valid number.")
                        break










