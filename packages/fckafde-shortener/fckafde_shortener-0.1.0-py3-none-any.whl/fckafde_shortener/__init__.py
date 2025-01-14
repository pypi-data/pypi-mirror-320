from requests import get, Session
from bs4 import BeautifulSoup
from logging import error

SHORT_URL_BASE = "https://fckaf.de/"

def shorten_url(long_url, delay: int = 5):
    try:
        session = Session()
        get_resp = session.get(SHORT_URL_BASE)

        soup = BeautifulSoup(get_resp.text, "html.parser")
        csrf_input = soup.find("input", attrs={"name": "csrf_token"})
        if not csrf_input or not csrf_input.get("value"):
            raise Exception("CSRF token not found on page; site structure may have changed")
        csrf_token = csrf_input["value"]

        form_data = {
            "csrf_token": csrf_token,
            "target": long_url,
            "delay": "15",
            "submit": "Speichern"
        }

        post_resp = session.post(SHORT_URL_BASE, data=form_data)
        post_resp.raise_for_status()

        result_soup = BeautifulSoup(post_resp.text, "html.parser")
        link_input = result_soup.find("input", id="link")
        if not link_input or not link_input.get("value"):
            return None
        short_url = link_input["value"]

    except Exception as e:
        error(e)
        return None

    return short_url

def de_shorten_url(fckafde_shorturl):
    """
    De-shorten the given FCKAF.DE short URL and return the original URL
    """
    try:
        response = get(fckafde_shorturl)
        soup = BeautifulSoup(response.text, "html.parser")
        link = soup.find("meta", attrs={"http-equiv": "refresh"})
        if link == None:
            return None
        
        link = link["content"]
        link = link.split("; ")
        link = link[1]
        link = link.replace("url=", "")

    except Exception as e:
        error(e)
        return None
    
    return link

def generate_forward_url(fckafde_shorturl, info):
    """
    Generate a forward URL from the given FCKAF.DE short URL
    """
    real_url = de_shorten_url(fckafde_shorturl)
    if real_url is None:
        return None
    
    real_url = real_url + f"?info={info}"

    return real_url