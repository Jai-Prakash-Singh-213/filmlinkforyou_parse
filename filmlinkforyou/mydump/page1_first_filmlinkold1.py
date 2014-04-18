import req_proxy
from bs4 import BeautifulSoup
from lxml import html
from Queue import Queue
import threading 
import time
import logging
import re

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

num_fetch_threads = 10
enclosure_queue = Queue()



class filmlink_for_u(object):

    def __init__(self):
        self.link = "http://www.filmlinks4u.net/"
        self.movie_page_link = []
	self.page_link_to_mov_link = open("page_link_movie_link.csv", "a+")


    def __del__(self):
        del self.link
        del self.all_cat_a
	self.page_link_to_mov_link.close()

  
    def page1_cat_link_collect(self):
        page = req_proxy.main(self.link)

        tree = html.fromstring(page)
        cat_box = tree.xpath("/html/body/div/div/div[5]/div[2]/div[2]/div/ul/li[2]/ul/li")

        all_cat_a = []
        for cat_link in cat_box:
            all_cat_a.append(cat_link.xpath("a/@href")[0])
    
        self.all_cat_a = all_cat_a


    def page1_to_2_link_to_movlink(self):
        procs = []

        for i in range(num_fetch_threads):
            procs.append(threading.Thread(target=self.movie_link, args=(i, enclosure_queue,)))
            procs[-1].start()

        for link in self.movie_page_link:
            enclosure_queue.put(link)

        enclosure_queue.join()

        for p in procs:
            enclosure_queue.put(None)

        enclosure_queue.join()

        for p in procs:
            p.join()


    def movie_link(self, i, q):
        for link in iter(q.get, None):
            try:
                self.page_link_to_movie_link(link)
                logging.debug(link)

            except:
                pass

            time.sleep(2)
            q.task_done()

        q.task_done()



    def movie_link_tu_page(self, link):
        page = req_proxy.main(link)      
        soup = BeautifulSoup(page)

        try:
	    page_links_div = soup.find("div", attrs={"id":"wp_page_numbers"})
            page_links_li = page_links_div.find_all("a")

	    for a  in page_links_li[:-1]:
	        self.movie_page_link.append(a.get("href"))

        except:
            self.movie_page_link.append(link)


    def page_link_to_movie_link(self, link):
        f = self.page_link_to_mov_link

        page = req_proxy.main(link)
	soup = BeautifulSoup(page)

	movi_link_box = soup.find("div", attrs={"id":"content"})
        movi_link_list = movi_link_box.find_all("a", title=re.compile("Permanent Link"))

	for mov_link in movi_link_list:
	    f.write(",".join([link, str(mov_link.get("href"))]) + "\n")
	    logging.debug([link, str(mov_link.get("href"))])


def supermain():
    obj = filmlink_for_u()
    obj.page1_cat_link_collect()

    for link in obj.all_cat_a:
        obj.movie_link_tu_page(link)

    obj.page1_to_2_link_to_movlink()
    


if __name__=="__main__":
    supermain()


    

