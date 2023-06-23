
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os. path


def start(url):

    ##Options for chromedriver, when using selenium, does not matter when using Collab since it acts more like a remote machine

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    #driver = webdriver.Chrome('chromedriver',options=chrome_options,executable_path='/path/to/chromedriver')
    #driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
    # setting up a Selenium WebDriver instance using Chrome as the browser

    service = Service('/path/to/chromedriver')

    driver = webdriver.Chrome(service=service, options=chrome_options)


    cricbuzz_highlights_url=url
    #Navigate the WebDriver instance (driver) to a specific URL
    driver.get(cricbuzz_highlights_url)
    # load the driver contents to beatifulSoup to extract data
    cricbuzz_soup= BeautifulSoup(driver.page_source, 'html.parser')

    div_tag=cricbuzz_soup.find_all('div',{'class':"cb-col cb-col-100 ng-scope"})
    
    # get the match name from url given

    match_name=cricbuzz_highlights_url.split('/')[-1]
    match_name

    # get the Series,Year,Statdium,Date of the match

    match_metadata_values=[c.next_element.next_element.next_element.text.replace('\xa0','') for c in cricbuzz_soup.find_all('span',{'class':'text-bold'})]

    # split the meta values 

    year=match_metadata_values[0].split()[-1]
    series="IPL"
    venue=match_metadata_values[1]
    date=match_metadata_values[2]+year

    # find the match no 

    def match_no():
        team_names=cricbuzz_soup.find('div',{'class':"cb-billing-plans-text cb-team-lft-item"})
        teams=team_names.text.split(',')[1]
        return teams.strip()[0:3]
    
    # convert the full name of the teams to short name 

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
    'Delhi Daredevils':'DD',
    'Royal Challengers Bangalore':'RCB',
    'Kings XI Punjab':'PBKS',
    'Rising Pune Supergiant':'RPS',
    'Gujarat Lions':'GL'
    }
        return short_name[team]

    # find who won the toss as string

    def find_toss():
        toss=cricbuzz_soup.find_all('p',{'class':"cb-com-ln ng-binding ng-scope cb-col cb-col-90"})
        for i in toss:
            if "won the toss" in i.get_text().lower():
                return i.get_text()
            
    # find the both team names

    def team_names():
        team_names=cricbuzz_soup.find('div',{'class':"cb-billing-plans-text cb-team-lft-item"})
        teams=team_names.text.split(',')[0]
        teams=teams.split('vs')
        teams=[team.strip() for team in teams]
        return teams
    
    # get the match details

    def match_info():
        match_details=cricbuzz_soup.find('div',{'class':"cb-col cb-col-20"})
        match_info=""
        for i in match_details:
            match_info+=i.get_text()
        return match_info
        
        # find the substitutes players of the teams


    def find_team_subs(team):
        preview_obj=cricbuzz_soup.find_all('p',{'class':'cb-com-ln ng-binding ng-scope cb-col cb-col-90'})
        for i in preview_obj:
            if 'subs' in i.text.lower() and (team in i.text or short_name(team) in i.text):
                return i.get_text()

    #find the playing 11 of each teams

    def find_team_playing11(team):
        preview_obj=cricbuzz_soup.find_all('p',{'class':'cb-com-ln ng-binding ng-scope cb-col cb-col-90'})
        for i in preview_obj:
            if '(Playing XI)'.casefold() in i.text.casefold() and (team in i.text or short_name(team) in i.text):
                return i.get_text()
    
    # get the player of the match

    def get_moth(url):
        cricbuzz_highlights_url=url
        cricbuzz_highlights_url=cricbuzz_highlights_url.replace('cricket-full-commentary','cricket-scores')
        cricbuzz_highlights_url
        page=requests.get(cricbuzz_highlights_url)
        soup=BeautifulSoup(page.content,'html.parser')
        try: 
            win=soup.find('div',{'class':'cb-col cb-col-100 cb-min-stts cb-text-complete'}).text
            #cb-col cb-col-100 cb-mini-col cb-min-comp ng-scope
            #cb-link-undrln ng-binding
            a=soup.find('span',{'class':'cb-text-gray cb-font-12'})
            try:
                man_of_the_match=a.next_sibling.next_sibling.next_sibling.text
            except:
                man_of_the_match=None
        except:
            win = None
            man_of_the_match=None
        return win,man_of_the_match

    winner,playe_of_the_match=get_moth(url=url)


    # get the Inns played in that match

    link_text=[]
    div_tag=cricbuzz_soup.find_all('div',{"class":"cb-hig-pil ng-scope"})
    for a_tag in div_tag:
        link_text.append(a_tag.a.string)
    link_text=link_text[1:]
    link_text

    # scrap the bal by ball commentry

    cricbuzz_page_soup=[]
    ##Iterate through the Inns
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
                
            except Exception as e:
                print(e)
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

    toss_string=find_toss()
    
    team_a,team_b=team_names()
    
    print('team_a=',team_a)
    print('teamb=',team_b)
    match_commentary_df['match_no']=match_no()
    match_commentary_df['team_a']=team_a
    match_commentary_df['team_b']=team_b
    match_commentary_df['team_a_11']=find_team_playing11(team_a)
    match_commentary_df['team_b_11']=find_team_playing11(team_b)
    # team subs given only for 2023
    match_commentary_df['team_a_subs']=find_team_subs(team_a)
    match_commentary_df['team_b_subs']=find_team_subs(team_b)
    match_commentary_df['series']=series
    match_commentary_df['season']=year
    match_commentary_df['venue']=venue
    match_commentary_df['date']=date
    match_commentary_df['toss']=find_toss()
    match_commentary_df['winner']=winner
    match_commentary_df['player_of_the_match']=playe_of_the_match
    match_commentary_df['toss_winner']= short_name(toss_string[:toss_string.find('have')].strip())
    match_commentary_df['toss_choosen']= toss_string.split(' ')[-1]
    print(match_commentary_df)

    # store the dataframe to your files csv or xlsx using to_csv or to_excel 

    #match_commentary_df.to_csv(os.path.join('files/2022',f'{match_name}.csv'),index=False)
    


# give the match link to extract the data

start('https://www.cricbuzz.com/cricket-full-commentary/46051/dc-vs-rr-34th-match-indian-premier-league-2022')





    


