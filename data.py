from bs4 import BeautifulSoup
import urllib.request

url = "http://web.mta.info/developers/turnstile.html"
u = urllib.request.urlopen(url)
html = u.read()

soup = BeautifulSoup(html, "html.parser")
links = soup.find_all('a')

for a_tag in links:
    page = a_tag.get("href")
    
    if (page is not None) and ("1706" in page):
        
        # this prefix is common to all file URLs
        link_prefix = "http://web.mta.info/developers/"
        
        # this suffix depends on the date for we want to retrieve data
        link_suffix = str(page)
        
        # filename from URL without extension
        filename = str(page).split("/")[-1][10:-4]
        
        # formatting of datetime as mentioned above
        day, month, year = filename[-2:], filename[-4:-2], filename[:2]
        
        # order it to create the specified file name
        filename = "turnstile_" + day + month + year + ".txt"
        print(filename)
        
        # download URL
        link_do_arquivo = link_prefix + link_suffix
        
        print(link_do_arquivo)
        urllib.request.urlretrieve(link_do_arquivo, filename)
