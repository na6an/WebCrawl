import re, json, requests
import os
from urllib.parse import urlparse
from urllib.parse import urljoin
from selenium import webdriver
from time import sleep
from datetime import date
from bs4 import BeautifulSoup

url = "https://www.att.jobs/search-jobs/"
company = "att"

class Jobcrawl(object):
    def __init__(self):
    	driver = webdriver.Firefox(executable_path="C:\\WebDriver\\geckodriver.exe")
		driver.get(url)

    def save_jobd(self, job_id, jobd_html):
        jobd_path = os.path.join(company, job_id + ".html")
        jobd_file = open(jobd_file_path, "w")
        jobd_file.write(jobd_html)
        jobd_file.close()

    def save_joblist(self, jobs):
        joblist_file_path = os.path.join(company, "gm_jobs.html")
        with open('gm_jobs.json', 'w') as jsonfile:
            json.dump(jobs, jsonfile)

    def save_html(self, html_content):
        html_file_path = os.path.join(company, "job_list.html")
        html_file = open(html_file_path, "w")
        html_file.write(html_content)
        html_file.close()

    def crawl(self):
        jobs = self.crawl_links()

        if len(jobs) > 0:
            if not os.path.exists(company):
                os.makedirs(company)

        for idx, job in enumerate(jobs):
            self.driver.get(job['url'])
            sleep(0.2)
            jobdetail = self.driver.find_element_by_css_selector('section.job-description')
            jobd = BeautifulSoup(jobdetail.get_attribute('outerHTML'), "lxml")
            if jobd is None:
                print('#' + str(idx) + ":", job['id'], job['title'], " no job description")
                continue

            jobd_html = jobd.prettify()
            job['jobd'] = jobd_html
            self.save_job_firestore(job)
            print('#' + str(idx) + ":", job['id'], job['title'])

            # backup and performance
            self.save_jobd(job['id'], jobd_html)

        self.save_joblist(jobs)
        self.driver.quit()

    def crawl_links(self):
        self.driver.get(link)
        sleep(1)

        self.save_html(self.driver.page_source)

        jobs = []
        pageno = 1

        # print(self.driver.page_source)
        while True:
            print('Current Page #' + str(pageno))

            s = BeautifulSoup(self.driver.page_source, "lxml")

            # get search result county
            if pageno == 1:
                elem = self.driver.find_element_by_xpath("//section[@id='search-results']/h2")
                job_count = int(re.match(r'(\d+)\s.+', elem.text).group(1))
                print("Total search result count is " + str(job_count))

            r = re.compile(r'/job/\S+/\S+/\S+/\d{7}')

            for a in s.findAll('a', href=r):

                job = {}
                job['id'] = a['data-job-id']
                job['title'] = a.find('h2').text
                job['url'] = urljoin(link, a['href'])
                job['location'] = a.find_all('span', attrs={'class':'job-location-search'}, limit=1)[0].text
                job['posting_date'] = date.today().strftime('%m/%d/%Y')
                #print(job)

                jobs.append(job)

            print("# of jobs: " + str(len(jobs)))

            if len(jobs) >= job_count:
                break

            try:
                next_page_elem = self.driver.find_element_by_css_selector('a.next')
                job_page = next_page_elem.get_attribute("href")
                self.driver.get(job_page)
                pageno += 1
                sleep(0.2)
            except:
                traceback.print_exc()
                break

        return jobs

if __name__ == '__main__':
    crawlr = Jobcrawl()
    crawlr.crawl()
