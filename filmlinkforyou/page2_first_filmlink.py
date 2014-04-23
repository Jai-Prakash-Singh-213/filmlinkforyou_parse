#!/usr/bin/python
from Queue import Queue
import threading
import time
import req_proxy
import phan_proxy
from bs4 import BeautifulSoup
from lxml import html
import logging

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

num_fetch_threads = 20
enclosure_queue = Queue()

class wl_to_eml(object):
    
    def __init__(self):
        self.f = open("wl_ml.csv", "a+")


    
    def __del__(self):
        self.f.close()



    def wl_to_el(self, line):
        driver = phan_proxy.main(line[-2])
        page = driver.page_source
        driver.quit()

        tree = html.fromstring(page)

        if len(tree.xpath("/html/body/center/table/tbody/tr[2]/td/iframe/@src")) != 0:
            embedlink = tree.xpath("/html/body/center/table/tbody/tr[2]/td/iframe/@src")[0]

        elif len(tree.xpath("/html/body/center/table/tbody/tr[2]/td/embed/@src")) != 0:
            embedlink = tree.xpath("/html/body/center/table/tbody/tr[2]/td/embed/@src")[0]

        elif len(tree.xpath("/html/body/div[2]/center/div/div/div[2]/object/embed/@src")) != 0:
            embedlink = tree.xpath("/html/body/div[2]/center/div/div/div[2]/object/embed/@src")[0]

        elif len(tree.xpath("/html/body/object/embed/@src")) != 0:
            embedlink = tree.xpath("/html/body/object/embed/@src")[0]

        elif len(tree.xpath("/html/body/div[2]/center/div/div/div[2]/iframe/@src")) != 0:
            embedlink = tree.xpath("/html/body/div[2]/center/div/div/div[2]/iframe/@src")[0]

        elif len(tree.xpath("/html/body/div/div[2]/div[3]/div[3]/div/input/@value")) !=0:
            embedlink = tree.xpath("/html/body/div/div[2]/div[3]/div[3]/div/input/@value")
            start = embedlink[0].find("src=")
            end = embedlink[0].find('"', start+5)
            embedlink = embedlink[0][start+5 :end].strip()
            

        else:
            embedlink =  ''
  
        try:
            data =  [filter(None, line[0].split("/"))[3], line[0], line[1].split("/")[-1][:-5], 
                                  line[1], line[2], line[3], embedlink, line[-1], line[-2]]

            self.f.write(",".join(data) + "\n")
            logging.debug(("inserted....", embedlink))

        except:
            pass 



def main_process2(i, q):
    for line, obj in iter(q.get, None):
        try:
            obj.wl_to_el(line.strip().split(","))

        except:
            f = open("error_in_line_page2.csv", "a+")
            f.write(line.strip() + "\n")
            f.close()

        time.sleep(2)
        q.task_done()

    q.task_done()



def page_link_movie_link():
    obj = wl_to_eml()

    f2 = open("pl_ml_tp_wl.csv")

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



def supermain():
    page_link_movie_link()



if __name__=="__main__":
    supermain()
