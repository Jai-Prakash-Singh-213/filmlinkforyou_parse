import req_proxy
from bs4 import BeautifulSoup
from lxml import html
from Queue import Queue
import threading 
import time
import logging
import re
from lxml import html
import profile 
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

num_fetch_threads = 5 
enclosure_queue = Queue()



class filmlink_for_u(object):

    def __init__(self):
        self.link = "http://www.filmlinks4u.net/"
        self.movie_page_link = []
	self.page_link_to_mov_link = open("page_link_movie_link.csv", "a+")
        self.pl_ml_tp_wl = open("pl_ml_tp_wl.csv", "a+")



    #def __del__(self):
    #    del self.link
    #    del self.all_cat_a
    #    obj.pl_ml_tp_wl.close() 


  
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



    def movie_link_to_data(self, line):
        line_list = line.strip().split(",")

        page = req_proxy.main(line_list[-1])
	soup = BeautifulSoup(page, "html.parser")

        image_box =  soup.find("div", attrs={"class":"entry"})
	movie_image = image_box.find("img").get("src")
      
        tag_hotserver  = soup.find_all("span", text=re.compile("Host Server"))

        f = self.pl_ml_tp_wl

	for l in tag_hotserver:
	    video_type =  l.next_sibling
	    next_a = l.find_next("a")

            if str(next_a.get_text()).strip() == "Watch Online Full Movie":
	        f.write(",".join(map(self.my_strip, [line_list[0], line_list[-1], 
                                                     video_type, next_a.get_text(), movie_image])) +  "\n")

                logging.debug([line_list[0], line_list[-1],video_type, next_a.get_text(), movie_image])



    def my_strip(self, x):
        return str(x.encode("ascii", "ignore")).replace("\n", " ").replace("\t", " ").replace("," , " ").replace("\r", " ").strip()



def main_process2(i, q):
    for line, obj in iter(q.get, None):
        try:
            obj.movie_link_to_data(line.strip())

        except:
            f = open("error_in_line.csv", "a+")
            f.write(str(line) + "\n")
            f.close()

        time.sleep(2)
        q.task_done()

    q.task_done()




    
def supermain():
    obj = filmlink_for_u()
    #obj.page1_cat_link_collect()

    #for link in obj.all_cat_a:
    #    obj.movie_link_tu_page(link)

    #obj.page1_to_2_link_to_movlink()
    #obj.page_link_to_mov_link.close()

    f2 = open("page_link_movie_link.csv")

    procs = []

    for i in range(num_fetch_threads):
        procs.append(threading.Thread(target=main_process2, args=(i, enclosure_queue,)))
        procs[-1].start()

    for line in f2:
        enclosure_queue.put((line, obj))

    enclosure_queue.join()

    for p in procs:
        enclosure_queue.put(None)

    enclosure_queue.join()

    for p in procs:
        p.join()
    
    f2.close()


if __name__=="__main__":

    dt = datetime.now()
    supermain()
    print datetime.now() - dt


    

