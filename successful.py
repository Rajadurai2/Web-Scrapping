
import pandas as pd
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
import os. path
import IPython

def start(url):

    ##Options for chromedriver, when using selenium, does not matter when using Collab since it acts more like a remote machine
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    #driver = webdriver.Chrome('chromedriver',options=chrome_options,executable_path='/path/to/chromedriver')
    #driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
    service = Service('/path/to/chromedriver')

    driver = webdriver.Chrome(service=service, options=chrome_options)


    cricbuzz_highlights_url=url

    driver.get(cricbuzz_highlights_url)

    cricbuzz_soup= BeautifulSoup(driver.page_source, 'html.parser')

    div_tag=cricbuzz_soup.find_all('div',{'class':"cb-col cb-col-100 ng-scope"})
    

    match_name=cricbuzz_highlights_url.split('/')[-1]
    match_name

    match_metadata_values=[c.next_element.next_element.next_element.text.replace('\xa0','') for c in cricbuzz_soup.find_all('span',{'class':'text-bold'})]

    match_metadata_values

    year=match_metadata_values[0].split()[-1]
    series="IPL"
    venue=match_metadata_values[1]
    date=match_metadata_values[2]+year

    def match_no():
        team_names=cricbuzz_soup.find('div',{'class':"cb-billing-plans-text cb-team-lft-item"})
        teams=team_names.text.split(',')[1]
        return teams.strip()[0:3]

    def short_name(team):
        short_name={'Chennai Super Kings':'CSK',
    'Mumbai Indians':'MI',
    'Gujarat Titans':'GT',
    'Kolkata Knight Riders':'KKR',
    'Punjab Kings':'PBKS',
    'Sunrisers Hyderabad':'SRH',
    'Rajasthan Royals':'RR',
    'Lucknow Super Giants':'LSG',
    'Delhi Capitals':'DC',
    'Royal Challengers Bangalore':'RCB'
    }
        return short_name[team]

    #cb-com-ln ng-binding ng-scope cb-col cb-col-90
    def find_toss():
        toss=cricbuzz_soup.find_all('p',{'class':"cb-com-ln ng-binding ng-scope cb-col cb-col-90"})
        for i in toss:
            if "won the toss" in i.get_text().lower():
                return i.get_text()
            
    def team_names():
        team_names=cricbuzz_soup.find('div',{'class':"cb-billing-plans-text cb-team-lft-item"})
        teams=team_names.text.split(',')[0]
        teams=teams.split('vs')
        teams=[team.strip() for team in teams]
        return teams

    def match_info():
        match_details=cricbuzz_soup.find('div',{'class':"cb-col cb-col-20"})
        match_info=""
        for i in match_details:
            match_info+=i.get_text()
        return match_info    

    def find_team_subs(team):
        preview_obj=cricbuzz_soup.find_all('p',{'class':'cb-com-ln ng-binding ng-scope cb-col cb-col-90'})
        for i in preview_obj:
            if 'subs' in i.text.lower() and (team in i.text or short_name(team) in i.text):
                return i.get_text()

    def find_team_playing11(team):
        preview_obj=cricbuzz_soup.find_all('p',{'class':'cb-com-ln ng-binding ng-scope cb-col cb-col-90'})
        for i in preview_obj:
            if '(Playing XI)'.casefold() in i.text.casefold() and (team in i.text or short_name(team) in i.text):
                return i.get_text()


    link_text=[]
    div_tag=cricbuzz_soup.find_all('div',{"class":"cb-hig-pil ng-scope"})
    for a_tag in div_tag:
        link_text.append(a_tag.a.string)
    link_text=link_text[1:]
    link_text

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
                #driver.quit()

    ##Scraping has been completed
    print ("Full scraping of key events complete...")
    ##Stop the driver element
    driver.close()

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

    match_commentary_df.reset_index(inplace=True,drop=True)
    match_commentary_df


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
    match_commentary_df

    #csv=match_commentary_df.to_csv(f'{match_name}.csv',index= False)
    match_commentary_df.to_csv(os.path.join('files/2022',f'{match_name}.csv'),index=False)
    #df=pd.read_csv(f'{match_name}.csv')

#start('https://www.cricbuzz.com/cricket-full-commentary/66169/gt-vs-csk-1st-match-indian-premier-league-2023')

match_links=[]
with open(os.path.join('match_links','2022_season_match_links.txt')) as f1:
    for line in f1:
        match_links.append(line.strip())
match_links=match_links[68:]
#match_links=['https://www.cricbuzz.com/cricket-full-commentary/66169/gt-vs-csk-1st-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66173/pbks-vs-kkr-2nd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66176/lsg-vs-dc-3rd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66183/srh-vs-rr-4th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66190/rcb-vs-mi-5th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66197/csk-vs-lsg-6th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66204/dc-vs-gt-7th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66208/rr-vs-pbks-8th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66211/kkr-vs-rcb-9th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66215/lsg-vs-srh-10th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66218/rr-vs-dc-11th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66225/mi-vs-csk-12th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66232/gt-vs-kkr-13th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66236/srh-vs-pbks-14th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66239/rcb-vs-lsg-15th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66243/dc-vs-mi-16th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66250/csk-vs-rr-17th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66253/pbks-vs-gt-18th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66257/kkr-vs-srh-19th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66260/rcb-vs-dc-20th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66264/lsg-vs-pbks-21st-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66271/mi-vs-kkr-22nd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66274/gt-vs-rr-23rd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66278/rcb-vs-csk-24th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66285/srh-vs-mi-25th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66292/rr-vs-lsg-26th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66313/pbks-vs-rcb-27th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66330/dc-vs-kkr-28th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66351/csk-vs-srh-29th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66369/lsg-vs-gt-30th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66404/mi-vs-pbks-31st-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66421/rcb-vs-rr-32nd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66435/kkr-vs-csk-33rd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66449/srh-vs-dc-34th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66470/gt-vs-mi-35th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66484/rcb-vs-kkr-36th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66502/rr-vs-csk-37th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66512/pbks-vs-lsg-38th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66519/kkr-vs-gt-39th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66526/dc-vs-srh-40th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66288/csk-vs-pbks-41st-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66299/mi-vs-rr-42nd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66306/lsg-vs-rcb-43rd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66320/gt-vs-dc-44th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66337/lsg-vs-csk-45th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66327/pbks-vs-mi-46th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66344/srh-vs-kkr-47th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66348/rr-vs-gt-48th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66355/csk-vs-mi-49th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66358/dc-vs-rcb-50th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66365/gt-vs-lsg-51st-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66376/rr-vs-srh-52nd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66379/kkr-vs-pbks-53rd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66386/mi-vs-rcb-54th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66393/csk-vs-dc-55th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66397/kkr-vs-rr-56th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66411/mi-vs-gt-57th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66414/srh-vs-lsg-58th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66428/dc-vs-pbks-59th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66432/rr-vs-rcb-60th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66442/csk-vs-kkr-61st-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66446/gt-vs-srh-62nd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66453/lsg-vs-mi-63rd-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66460/pbks-vs-dc-64th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66467/srh-vs-rcb-65th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66477/pbks-vs-rr-66th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66481/dc-vs-csk-67th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66488/kkr-vs-lsg-68th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66495/mi-vs-srh-69th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/66505/rcb-vs-gt-70th-match-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/69557/gt-vs-csk-qualifier-1-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/69561/lsg-vs-mi-eliminator-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/69568/gt-vs-mi-qualifier-2-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/69575/csk-vs-gt-final-indian-premier-league-2023', 'https://www.cricbuzz.com/cricket-full-commentary/72622/csk-vs-gt-final-reserve-day-indian-premier-league-2023']
for i,link in enumerate(match_links):
    start(link)
    print(i,'completed')


