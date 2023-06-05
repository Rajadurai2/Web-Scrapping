#!/usr/bin/env python
# coding: utf-8

# In[6]:


from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import os
import requests
import time
from collections import defaultdict
from selenium.webdriver.common.by import By


# In[2]:


cricbuzz_url='https://www.cricbuzz.com/cricket-series/5945/indian-premier-league-2023/matches'


# In[3]:


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


# In[4]:


driver = webdriver.Chrome('chromedriver',options=chrome_options)


# In[30]:


driver.get(cricbuzz_url)


# In[31]:


cricbuzz_soup= BeautifulSoup(driver.page_source, 'html.parser')


# In[32]:


a=requests.get(cricbuzz_url)


# In[11]:


c=BeautifulSoup(a.content,'html.parser')
match_links=[]
div_tag=c.find_all('div',{'class':'cb-col-60 cb-col cb-srs-mtchs-tm'})
for a_tag in div_tag:
    match_links.append(a_tag.a['href'])


# In[ ]:





# In[24]:


#cb-col-60 cb-col cb-srs-mtchs-tm


# In[25]:


match_links=[]
div_tag=cricbuzz_soup.find_all('div',{'class':'cb-col-60 cb-col cb-srs-mtchs-tm'})
for a_tag in div_tag:
    match_links.append(a_tag.a['href'])
    


# In[26]:


#https://www.cricbuzz.com/cricket-full-commentary/66169/gt-vs-csk-1st-match-indian-premier-league-2023
#/cricket-scores/72622/csk-vs-gt-final-reserve-day-indian-premier-league-2023


# In[27]:


def create_link(link):
    a=link.split('/')[2:]
    a='/'.join(a)
    http='https://www.cricbuzz.com/cricket-full-commentary/'
    result=http+a
    return result


# In[28]:


working_links=list(map(create_link,match_links))


# In[29]:


working_links


# In[9]:


short_name={'Chennai Super Kings':'CSK',
  'Mumbai Indians':'MI',
   'Gujarat Titans':'GT',
   'Kolkata Knight Riders':'KKR',
   'Punjab Kings':'PBKS',
   'SunRisers Hyderabad':'SRH',
   'Rajasthan Royals':'RR',
   'Lucknow Super Giants':'LSG',
   'Delhi Capitals':'DC',
   'Royal Challengers Bangalore':'RCB'
  }


# In[8]:


d['Chennai Super Kings']


# In[ ]:


cricbuzz_page_soup=[]
##Iterate through the link textss
for l in link_text:
        ##Click the innings text
        print(l,' Analysed')
        loadMoreButton=driver.find_element(By.LINK_TEXT,l)
        loadMoreButton.click()
        ##Click the 'dropped catches' text box, or the option chosen above. 
        #l2=driver.find_element(By.LINK_TEXT,option)
        #l2.click()
        time.sleep(5)
        ##Collect the soup of the existing view that has been clicked by the driver element
        cricbuzz_soup_inner=BeautifulSoup(driver.page_source, 'html.parser')

        ##Append each of the page contents to a list
        cricbuzz_page_soup.append(cricbuzz_soup_inner)

##Scraping has been completed
print ("Full scraping of key events complete...")
##Stop the driver element
driver.quit()

