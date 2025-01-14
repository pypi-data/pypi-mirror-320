from bs4 import BeautifulSoup
import re
from urllib.parse import unquote




#############################################################################################
def html_get_newsurl(url, html=None) :
    """ Extract valid News URLS from HTML page
    
    """
    soup       = BeautifulSoup(html, "html.parser")
    a_nodes    = soup.find_all('a', href=True)
    valid_urls = []

    # Get the base url. Relative paths have to be created with base url. which is http tag and domain name
    root_url = url_valid_base_url(url)

    # Parse all a nodes
    for a_node in a_nodes :
        href = a_node["href"]
        text = a_node.text

        # Urls can be found in decoded format in html. We need to normalize them in order to apply length based rules.
        href = unquote(url_valid_complete_lnk(href, root_url))

        if url_valid_ad_url(href, text): continue 
        if not url_valid_newsurl(href, text)   : continue
        
        valid_urls.append(href)

    return valid_urls







#############################################################################################
##### Functions to identify if given url is Ads related #####
def url_valid_ad_words(url, text) :

    # Find urls having Ad keywords and "utm" ( "utm" is used to track landing page e.g. utm_source=google)
    ad_words_in_url = [".ads.", ".ad.", "/ads/", "/ad/", "sponsored", "promotions", "clickbait", "utm_", "click?"]
    ad_words_in_text = ["Search Ad", "AdAd"]
    ad_words_match_text = ["Ad", "Ads", "Advertisement"]
    
    for ad_word in ad_words_in_url :
        if ad_word in url.lower() :
            return True

    # Inner text of 'a' element is specific, like "Ad". This is a very common case, and should be covered. (keeping it case sensitive, for precise match)
    for ad_word in ad_words_in_text :
        if ad_word in text :
            return True

    for ad_word in ad_words_match_text :
        if ad_word == text :
            return True
        
    return False

def url_valid_ad_pattern(url, text) :
    # Url with ads have no text (cases where ad is image) and have additional parameters
    if len(text) == 0 and "?" in url and "&" in url:
        return True

    # Urls with ad pattern have multiple parameters with ids to track its source
    if "?" in url and len(url.rsplit("?", 1)[-1]) > 30 :
        return True 

    return False

def url_valid_ad_url(href, text) :
    ad_word    = url_valid_ad_words(href, text)
    ad_pattern = url_valid_ad_pattern(href, text)

    # If one of the rule identifies url as invalid, skip it
    if ad_word or ad_pattern :
        return True

    return False


###################################################################################
##### Base url related functions #####
def url_valid_base_url(url):
    if url == None or url == "" :
        return ""

    # Regular expression pattern to match HTTP/HTTPS and domain part
    pattern = r'^(https?://[^/]+)'
    
    # Use re.findall to find all matches
    matches = re.findall(pattern, url)
    
    # If a match is found then first one is the base url, if not found then return ""
    return matches[0] if matches else ""

def url_valid_complete_lnk(url, root_url) :
    # Check if url is already complete i.e. url has some base url in it with "http" and domain
    if url_valid_base_url(url) != "" :
        return url

    # Complete the relative url by adding base url 
    else :
        url = root_url + url

    return url



def url_valid_newsurl(href, text) :
    """ 
       ##### Functions to extract only the valid, useful content Urls #####
       # Inner text length and words length based filters
    
    """
    words = text.strip().split(" ")
    if(len(text) > 20 and len(words) >= 4 and len(text.strip().split("  ")) < 2) :
        #print(text," : ", len(text.strip().split(" ")))
        return True
    return False





def html_get_element(soup, container, attr, article_url) :
    if article_url != "" :
        return article_url
    
    if container :
        return container[attr]

    return ""
        
def html_get_article_url(soup, article_url) :
    # Since we get only the html string as input to the function, we need to find out base url, in order to complete the relative urls. There are several paths in every standard html, where url of the article is provided.
    article_url = html_get_element(soup, soup.find("link", {"rel": "canonical"}), "href", article_url)
    article_url = html_get_element(soup, soup.find("meta", {"property" : "og:url"}), "content", article_url)
    article_url = html_get_element(soup, soup.find("base"), "href", article_url)
    return article_url






###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




