import req_proxy
import phan_proxy
from bs4 import BeautifulSoup
from lxml import html
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

class wl_to_eml(object):
    
    def __init__(self):
        self.f = open("wl_ml.csv", "a+")


    
    def __del__(self):
        self.f.close()



    def wl_to_el(self, line):
        #page = req_proxy.main(link)
    
        driver = phan_proxy.main(line[-2])
        page = driver.page_source
        driver.quit()

        tree = html.fromstring(page)

        if len(tree.xpath("/html/body/center/table/tbody/tr[2]/td/iframe/@src")) != 0:
            embedlink = tree.xpath("/html/body/center/table/tbody/tr[2]/td/iframe/@src")

        elif len(tree.xpath("/html/body/div[2]/center/div/div/div[2]/object/embed/@src")) != 0:
            embedlink = tree.xpath("/html/body/div[2]/center/div/div/div[2]/object/embed/@src")

        elif len(tree.xpath("/html/body/object/embed/@src")) != 0:
            embedlink = tree.xpath("/html/body/object/embed/@src")

        elif len(tree.xpath("/html/body/div[2]/center/div/div/div[2]/iframe/@src")) != 0:
            embedlink = tree.xpath("/html/body/div[2]/center/div/div/div[2]/iframe/@src") 

        else:
            embedlink = []

        data =  [filter(None, line[0].split("/"))[3], line[0], line[1].split("/")[-1][:-5], 
                 line[1], line[2], line[3], embedlink[0], line[-1], line[-2]]

        self.f.write(",".join(data) + "\n")
        logging.debug("inserted......")


    
def supermain():
    line = "http://www.filmlinks4u.net/category/adult/page/6,http://www.filmlinks4u.net/2010/02/item-girl-2007-hot-hindi-movie-watch-online.html,- Youtube,Watch Online Full Movie,http://www.filmshowonline.net/videos/76538/,http://www.filmlinks4u.net/wp-content/uploads/2010/02/Item-Girl-2007-Hot-Hindi-Movie-Watch-Online.jpg"

    #link = "http://videolinkz.us/yt.php?url=t-R9V1b67MY"
    #wl_to_el(link)

    obj = wl_to_eml()
    obj.wl_to_el(line.strip().split(","))


if __name__=="__main__":
    supermain()
