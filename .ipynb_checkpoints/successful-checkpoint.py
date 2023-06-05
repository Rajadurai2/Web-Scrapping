#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd


# In[2]:


from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import requests
import time
from selenium.webdriver.chrome.service import Service
from collections import defaultdict
from selenium.webdriver.common.by import By


# In[3]:


##Options for chromedriver, when using selenium, does not matter when using Collab since it acts more like a remote machine
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')


# In[4]:


#driver = webdriver.Chrome('chromedriver',options=chrome_options,executable_path='/path/to/chromedriver')
#driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
service = Service('/path/to/chromedriver')

driver = webdriver.Chrome(service=service, options=chrome_options)


# In[5]:


cricbuzz_highlights_url='https://www.cricbuzz.com/cricket-full-commentary/66169/gt-vs-csk-1st-match-indian-premier-league-2023'


# In[6]:


#https://www.cricbuzz.com/cricket-series/5945/indian-premier-league-2023


# In[7]:


driver.get(cricbuzz_highlights_url)


# In[8]:


cricbuzz_soup= BeautifulSoup(driver.page_source, 'html.parser')


# In[9]:


div_tag=cricbuzz_soup.find_all('div',{'class':"cb-col cb-col-100 ng-scope"})
#cb-com-ln ng-binding ng-scope cb-col cb-col-90


# In[10]:


#class="cb-col cb-col-100 ng-scope"
#class="cb-col cb-col-100 ng-scope"
#class="cb-col cb-col-100 ng-scope"
#class="cb-com-ln ng-binding ng-scope cb-col cb-col-90"
#class="cb-col cb-col-20" match box
#class=cb-nav-subhdr cb-font-12  header 
#class="cb-billing-plans-text cb-team-lft-item" team names


# In[11]:


#cricbuzz_soup.find_all('p',{'class':'cb-com-ln ng-binding ng-scope cb-col cb-col-90'})


# In[12]:


match_name=cricbuzz_highlights_url.split('/')[-1]
match_name


# In[13]:


match_metadata_values=[c.next_element.next_element.next_element.text.replace('\xa0','') for c in cricbuzz_soup.find_all('span',{'class':'text-bold'})]

match_metadata_values


# In[14]:


year=match_metadata_values[0].split()[-1]
series="IPL"
venue=match_metadata_values[1]
date=match_metadata_values[2]+year


# In[15]:


def match_no():
    team_names=cricbuzz_soup.find('div',{'class':"cb-billing-plans-text cb-team-lft-item"})
    teams=team_names.text.split(',')[1]
    return teams.strip()[0:3]


# In[16]:


def short_name(team):
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
    return short_name[team]


# In[17]:


#cb-com-ln ng-binding ng-scope cb-col cb-col-90
def find_toss():
    toss=cricbuzz_soup.find_all('p',{'class':"cb-com-ln ng-binding ng-scope cb-col cb-col-90"})
    for i in toss:
        if "won the toss" in i.get_text().lower():
            return i.get_text()


# In[18]:


def team_names():
    team_names=cricbuzz_soup.find('div',{'class':"cb-billing-plans-text cb-team-lft-item"})
    teams=team_names.text.split(',')[0]
    teams=teams.split('vs')
    teams=[team.strip() for team in teams]
    return teams


# In[19]:


def match_info():
    match_details=cricbuzz_soup.find('div',{'class':"cb-col cb-col-20"})
    match_info=""
    for i in match_details:
        match_info+=i.get_text()
    return match_info    


# In[20]:


def find_team_subs(team):
    preview_obj=cricbuzz_soup.find_all('p',{'class':'cb-com-ln ng-binding ng-scope cb-col cb-col-90'})
    for i in preview_obj:
        if 'subs' in i.text.lower() and (team in i.text or short_name(team) in i.text):
            return i.get_text()


# In[21]:


def find_team_playing11(team):
    preview_obj=cricbuzz_soup.find_all('p',{'class':'cb-com-ln ng-binding ng-scope cb-col cb-col-90'})
    for i in preview_obj:
        if '(Playing XI)'.casefold() in i.text.casefold() and (team in i.text or short_name(team) in i.text):
            return i.get_text()


# In[22]:


link_text=[]
div_tag=cricbuzz_soup.find_all('div',{"class":"cb-hig-pil ng-scope"})
for a_tag in div_tag:
    link_text.append(a_tag.a.string)
link_text=link_text[1:]
link_text


# In[23]:


cricbuzz_page_soup=[]
##Iterate through the link textss
for l in link_text:
        ##Click the innings text
        
        try:
            loadMoreButton=driver.find_element(By.LINK_TEXT,l)
            loadMoreButton.click()
            time.sleep(5)  #must
            ##Collect the soup of the existing view that has been clicked by the driver element
            cricbuzz_soup_inner=BeautifulSoup(driver.page_source, 'html.parser')
            ##Append each of the page contents to a list
            cricbuzz_page_soup.append(cricbuzz_soup_inner)
            print(l,' Analysed')
        except:
            print('success')

##Scraping has been completed
print ("Full scraping of key events complete...")
##Stop the driver element
driver.quit()


# In[24]:


match_commentary_df=pd.DataFrame()
for inn_num,cricbuzz_highlights_soup in enumerate(cricbuzz_page_soup):
    cricbuzz_innings_soup=cricbuzz_highlights_soup.find_all('div',{'class':'cb-col cb-col-8 text-bold ng-scope'})
    ball_overs=[]
    ball_commentary=[]
    for cinn_soup in cricbuzz_innings_soup:
        ball_overs.append(cinn_soup.text)
        ball_commentary.append(str(cinn_soup.find_next('p').text))
        #ball_commentry.append()
    innings_commentary_df=pd.DataFrame({'ball':ball_overs,'Commentary Text':ball_commentary})
    innings_commentary_df['ball']=innings_commentary_df['ball']
    innings_commentary_df['innings']=link_text[inn_num]
    match_commentary_df=pd.concat([match_commentary_df,innings_commentary_df])


# In[25]:


match_commentary_df.reset_index(inplace=True,drop=True)
match_commentary_df


# In[26]:


team_a,team_b=team_names()
match_commentary_df['match_no']=match_no()
match_commentary_df['team_a']=team_a
match_commentary_df['team_b']=team_b
match_commentary_df['team_a_11']=find_team_playing11(team_a)
match_commentary_df['team_b_11']=find_team_playing11(team_b)
match_commentary_df['team_a_subs']=find_team_subs(team_a)
match_commentary_df['team_b_subs']=find_team_subs(team_b)
match_commentary_df['series']=series
match_commentary_df['season']=year
match_commentary_df['venue']=venue
match_commentary_df['date']=date
match_commentary_df['toss']=find_toss()


# In[27]:


match_commentary_df


# In[32]:


csv=match_commentary_df.to_csv(f'{match_name}.csv',index= False)


# In[41]:


df=pd.read_csv(f'{match_name}.csv')


# In[42]:


df


# In[ ]:




