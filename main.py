# URL of the page
url = 'https://optaplayerstats.statsperform.com/en_GB/soccer/league-one-2022-2023/45jmw2vsxaigdle6d987w7lsk/match/accrington-stanley-vs-plymouth-argyle/819jdl9ktqv66nzi74n4224no/match-summary'

from playwright.sync_api import Playwright, sync_playwright
import re

# Set up Playwright options
options = {
    'headless': False,  # Run in headless mode to avoid opening a new window
}


length1 = 0
# Launch a new browser instance
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(**options)
    page = browser.new_page()

    # Navigate to the website
    page.goto(url)

    # Wait for the div with class "Opta-Cf Opta-Timeline-Bar" to become visible
    # page.wait_for_selector('.Opta-Cf .Opta-Timeline-Bar ')
    # page.wait_for_load_state('load')
    # Wait for the div with class "Opta-Cf Opta-Timeline-Bar" to become visible
    page.wait_for_selector('.Opta-Cf .Opta-Timeline-Bar ')

    # Get the content of all li in ul with class = "Opta, Events Opta-Home"
    div_element = page.query_selector('.Opta-Cf.Opta-Timeline-Bar')

    ul_elements = div_element.query_selector_all('ul')

    gameData = []

    for i, ul_element in enumerate(ul_elements):
        print(f"--->Contents of ul {i}")
        gameData_eachteam = []
        li_elements = ul_element.query_selector_all('li')
        for j, li_element in enumerate(li_elements):
            eachData_dict = {}
            # print(f"------->Contents of li {j}: {li_element.inner_html()}")
            print(f"------->Contents of li {j}")
            span_element_title = li_element.query_selector('.Opta-Event-Title').inner_text()
            print(f"---------------->Title: {span_element_title}")
            
            span_element_min = li_element.query_selector('.Opta-Event-Min').inner_text()
            print(f"---------------->Min: {span_element_min}")

            span_element_hidden = li_element.query_selector('.Opta-Hidden')
            div_elements = span_element_hidden.query_selector_all('div')
            # Filter out any p elements and locate the second child div element
            members = []
            for i, div_element in enumerate(div_elements):
                div_content = div_element.inner_html()
                # print(f"----------------------->Contents of div {i}: {div_content}")

                members.append(div_element.query_selector('p').inner_text())
                print(f"\n----------------------->Contents of p : {members[i]}")
            
            num_str = re.sub(r'[^\d]+', '', span_element_min)


            if num_str.startswith("45") or num_str.startswith("90"):
                prefix = num_str[:2]   # Extract the first two characters of the string
                suffix = num_str[2:]   # Extract the rest of the string
                if num_str[2:] != "":
                    num_str = prefix + "+" + suffix
            try:
                eachData_dict = {
                    "title": span_element_title,
                    "time": num_str,
                    "member1": members[0],
                    "member2": members[1]
                }
            except IndexError as e:
                print(f"IndexError occurred: {e}")
                eachData_dict = {
                    "title": span_element_title,
                    "time": num_str,
                    "member1": members[0],
                    "member2": ""
                }
            print(f"--------------------------------------------------->\n{eachData_dict}")
            gameData_eachteam.append(eachData_dict)
        print(f"--------------------------------------------------------------------->\n{gameData_eachteam}")
        gameData.append(gameData_eachteam)
    print(f"=======================>\n{gameData}")
    if length1 < len(gameData[0]):
        diff_length1 = len(gameData[0]) - length1
        print(f"***************************>{diff_length1}")
        length1 = len(gameData[0])
        for k in range(diff_length1-1, -1, -1):
            print(f"*********************************************>{gameData[0][len(gameData[0]) - 1 - k]}")
        


        
    # Close the browser
    browser.close()
