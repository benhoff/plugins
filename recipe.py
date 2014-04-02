import random

from util import hook, http, web

METADATA_URL = "http://omnidator.appspot.com/microdata/json/?url={}"

BASE_URL = "http://www.cookstr.com"
SEARCH_URL = BASE_URL + "/searches"
RANDOM_URL = SEARCH_URL + "/surprise"

# set this to true to censor this plugin!
censor = True
phrases = [
    u"EAT SOME FUCKING \x02{}\x02",
    u"YOU WON'T NOT MAKE SOME FUCKING \x02{}\x02",
    u"HOW ABOUT SOME FUCKING \x02{}\x02",
    u"WHY DON'T YOU EAT SOME FUCKING \x02{}\x02",
    u"MAKE SOME FUCKING \x02{}\x02",
    u"INDUCE FOOD COMA WITH SOME FUCKING \x02{}\x02"
]

clean_key = lambda i: i.split("#")[1]


class ParseError(Exception):
    pass


def get_data(url):
    """ Uses the omnidator API to parse the metadata from the provided URL """
    try:
        omni = http.get_json(METADATA_URL.format(url))
    except (http.HTTPError, http.URLError) as e:
        raise ParseError(e)
    schemas = omni["@"]
    for d in schemas:
        if d["a"] == "<http://schema.org/Recipe>":
            data = {clean_key(key): value for (key, value) in d.iteritems()
                    if key.startswith("http://schema.org/Recipe")}
            return data
    raise ParseError("No recipe data found")


@hook.command(autohelp=False)
def recipe(inp):
    """recipe [term] - Gets a recipe for [term], or ets a random recipe if [term] is not provided"""
    if inp:
        # get the recipe URL by searching
        try:
            search = http.get_soup(SEARCH_URL, query=inp.strip())
        except (http.HTTPError, http.URLError) as e:
            return "Could not get recipe: {}".format(e)

        # find the list of results
        results = search.find('div', {'class': 'found_results'})

        if results:
            result = results.find('div', {'class': 'recipe_result'})
        else:
            return "No results"

        # extract the URL from the result
        url = BASE_URL + result.find('div', {'class': 'image-wrapper'}).find('a')['href']

    else:
        # get a random recipe URL
        try:
            page = http.open(RANDOM_URL)
        except (http.HTTPError, http.URLError) as e:
            return "Could not get recipe: {}".format(e)
        url = page.geturl()

    # use get_data() to get the recipe info from the URL
    try:
        data = get_data(url)
    except ParseError as e:
        return "Could not parse recipe: {}".format(e)

    name = data["name"].strip()
    return u"Try eating \x02{}!\x02 - {}".format(name, web.try_isgd(url))


@hook.command(autohelp=False)
def wtfisfordinner(inp):
    """wtfisfordinner - WTF IS FOR DINNER"""
    try:
        page = http.open(RANDOM_URL)
    except (http.HTTPError, http.URLError) as e:
        return "Could not get recipe: {}".format(e)
    url = page.geturl()

    try:
        data = get_data(url)
    except ParseError as e:
        return "Could not parse recipe: {}".format(e)

    name = data["name"].strip().upper()
    text = random.choice(phrases).format(name)

    if censor:
        text = text.replace("FUCK", "F**K")

    return u"{} - {}".format(text, web.try_isgd(url))