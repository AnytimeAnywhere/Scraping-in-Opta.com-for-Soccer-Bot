

from playwright.sync_api import Playwright, sync_playwright
import re
import time
import sqlite3
import datetime
import os

# URL of the page
url = 'https://optaplayerstats.statsperform.com/en_GB/soccer'

# Set up Playwright options
options = {
    'headless': False,  # Run in headless mode to avoid opening a new window
}

# Get current date
current_date = datetime.datetime.now().strftime('%Y-%m-%d')

# Define a function to create the database
def create_database(database_name):
    # Check if SQLite DB with given name exists
    if os.path.exists(f"{database_name}.db"):
        print(f"SQLite DB with name {database_name}.db already exists.")
    else:
        # Remove any existing SQLite DB in the same directory
        for file in os.listdir():
            if file.endswith(".db"):
                os.remove(file)

        # Create new SQLite DB with given name
        conn = sqlite3.connect(f"{database_name}.db")
        print(f"Created new SQLite DB with name {database_name}.db.")
        conn.close()

def create_table(database_name, table_name,  game_name, game_url):
    # Open the SQLite DB with the given name
    conn = sqlite3.connect(f"{database_name}.db")

    # Check if table exists
    c = conn.cursor()
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if c.fetchone() is None:
        # Create table if it does not exist
        c.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, 'game_name' TEXT, 'game_url' TEXT, 'game_event_id' INTEGER, 'game_team' TEXT, 'game_event_title' TEXT, 'game_event_time' TEXT, 'game_event_member1' TEXT, 'game_event_member2' TEXT)")
        insert_row_table(database_name, table_name, game_name, game_url, 0, "", "", "", "", "")
    else:
        print(f"Table '{table_name}' already exists.")

    # Close the connection
    conn.close()


def delete_table(database_name, table_name):
    # Open the SQLite DB with the given name
    conn = sqlite3.connect(f"{database_name}.db")

    # Create a cursor object
    c = conn.cursor()

    # Execute SQL command to drop table
    c.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"Table '{table_name}' has been deleted from '{database_name}'.")

def get_all_table_names(database_name):
    """
    Returns a list of all table names in the specified SQLite database.
    """
    conn = conn = sqlite3.connect(f"{database_name}.db")
    c = conn.cursor()

    # Get the names of all tables in the database
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [row[0] for row in c.fetchall()]

    conn.close()

    return table_names

def smart_tables(current_date, LiveGames):
    """
    Deletes tables that do not have a corresponding 'gameName' value in the LiveGames array.
    
    Args:
    current_date (datetime): Current date
    LiveGames (list): List of live games
    
    Returns:
    None
    """
    tableNames = get_all_table_names(current_date)

    for tableName in tableNames:
        found = False
        for LiveGame in LiveGames:
            new_table_name = LiveGame['tableName']
            if tableName == new_table_name:
                found = True
                print(f'"{tableName}" is present in the array.')
                break
        if not found:
            delete_table(current_date, tableName)
            print("No value of 'tableName' is present in the array.")

def insert_row_table(database_name, table_name, game_name, game_url, game_event_id, game_team, game_event_title, game_event_time, game_event_member1, game_event_member2):
    # Open the SQLite DB with the given name
    conn = sqlite3.connect(f"{database_name}.db")

    # Insert new row into the table
    c = conn.cursor()
    c.execute(f"INSERT INTO {table_name} ('game_name', 'game_url', 'game_event_id', 'game_team', 'game_event_title', 'game_event_time', 'game_event_member1', 'game_event_member2') VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (game_name, game_url, game_event_id, game_team, game_event_title, game_event_time, game_event_member1, game_event_member2))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

import sqlite3

def get_gameUrl(database_name, table_name):
    # Open the SQLite DB with the given name
    conn = sqlite3.connect(f"{database_name}.db")

    # Get the first row in the table
    c = conn.cursor()
    c.execute(f"SELECT game_url FROM {table_name} LIMIT 1")
    row = c.fetchone()

    # Close the connection
    conn.close()

    if row is not None:
        game_url = row[0]
        return game_url
    else:
        print(f"No rows found in table '{table_name}'.")
        return None
def get_gameName(database_name, table_name):
    # Open the SQLite DB with the given name
    conn = sqlite3.connect(f"{database_name}.db")

    # Get the first row in the table
    c = conn.cursor()
    c.execute(f"SELECT game_name FROM {table_name} LIMIT 1")
    row = c.fetchone()

    # Close the connection
    conn.close()

    if row is not None:
        game_name = row[0]
        return game_name
    else:
        print(f"No rows found in table '{table_name}'.")
        return None
def get_max_game_event_id(database_name, table_name):
    # Open the SQLite DB with the given name
    conn = sqlite3.connect(f"{database_name}.db")

    # Execute a SQL query to get the max value of game_event_id
    c = conn.cursor()
    c.execute(f"SELECT MAX(game_event_id) FROM {table_name}")
    row = c.fetchone()

    # Close the connection
    conn.close()

    if row is not None:
        max_game_event_id = row[0]
        return max_game_event_id
    else:
        print(f"No rows found in table '{table_name}'.")
        return 0
def get_event_team(game_name, team_name):
    # Split the input string by underscore
    parts = game_name.split("_")

    if team_name == "team0":
        # Return the first part
        return parts[0]
    elif team_name == "team1":
        # Return the second part
        return parts[1]
    else:
        # Invalid condition
        return None
# Define a function to calculate the time value
def calculate_time(element):
    time_str = element['time']
    if '+' in time_str:
        parts = time_str.split('+')
        return int(parts[0]) + int(parts[1])
    else:
        return int(time_str)
    
# Create the database with the current date as name
create_database(current_date)

# Launch a new browser instance
while True:
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**options)
            page = browser.new_page()

            # Navigate to the website
            page.goto(url)

            link = page.locator('xpath=//a[@class="livescore-container-navigation-dateselection-pre"]')
            # Click the link
            link.click()
            time.sleep(10)
            
            page.wait_for_selector('#LivescoresList')
            div_element = page.query_selector('#LivescoresList')
            href_elements = div_element.query_selector_all('a.livescores-match-container')
            LiveGames = []
            for i, href_element in enumerate(href_elements):
                href_content = href_element.get_attribute("href")
                print(f"https://optaplayerstats.statsperform.com/{href_content}")
                href_html = href_element.inner_html()
                # livescore-container-fixtures-competition-row-team-a
                team_A = href_element.query_selector('.livescore-container-fixtures-competition-row-team-a').inner_text()
                print(f"https://optaplayerstats.statsperform.com/{team_A}")
                team_B = href_element.query_selector('.livescore-container-fixtures-competition-row-team-b').inner_text()
                print(f"https://optaplayerstats.statsperform.com/{team_B}")
                game_name = team_A + "_" + team_B
                new_table_name = game_name.replace(" ", "")
                print(game_name)
                eachLiveGame_new = {
                    "tableName":new_table_name,
                    "gameName": game_name,
                    "gameUrl": "https://optaplayerstats.statsperform.com" + href_content,
                }
                print(eachLiveGame_new['gameUrl'])
                create_table(current_date, new_table_name,  game_name, eachLiveGame_new['gameUrl'])

                LiveGames.append(eachLiveGame_new)

            print(LiveGames)

            # Close the browser
            browser.close()

        smart_tables(current_date, LiveGames)
            # game_name = get_gameName(current_date, tableName)
            # if game_name is not None:
            #     print(f"First gameName: {game_name}")
        tableNames = get_all_table_names(current_date)
        for tableName in tableNames:
            game_url = get_gameUrl(current_date, tableName)
            if game_url is not None:
                print(f"First gameUrl: {game_url}")

                url = game_url
                while True:
                    try:
                        time.sleep(5)
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
                                    for p, div_element in enumerate(div_elements):
                                        div_content = div_element.inner_html()
                                        # print(f"----------------------->Contents of div {i}: {div_content}")

                                        members.append(div_element.query_selector('p').inner_text())
                                        print(f"\n----------------------->Contents of p : {members[p]}")
                                    
                                    num_str = re.sub(r'[^\d]+', '', span_element_min)


                                    if num_str.startswith("45") or num_str.startswith("90"):
                                        prefix = num_str[:2]   # Extract the first two characters of the string
                                        suffix = num_str[2:]   # Extract the rest of the string
                                        if num_str[2:] != "":
                                            num_str = prefix + "+" + suffix
                                    try:
                                        eachData_dict = {
                                            "team" : "team" + str(i),
                                            "title": span_element_title,
                                            "time": num_str,
                                            "member1": members[0],
                                            "member2": members[1]
                                        }
                                    except IndexError as e:
                                        print(f"IndexError occurred: {e}")
                                        eachData_dict = {
                                            "team" : "team" + str(i),
                                            "title": span_element_title,
                                            "time": num_str,
                                            "member1": members[0],
                                            "member2": ""
                                        }
                                    print(f"--------------------------------------------------->\n{eachData_dict}")
                                    gameData.append(eachData_dict)
                            print(f"--------------------------------------------------------------------->\n{gameData}")

                            max_game_event_id = get_max_game_event_id(current_date, tableName)
                            # Sort the array by calculated time value
                            sorted_gameData = sorted(gameData, key=lambda x: calculate_time(x))
                            changeEventNumber = len(sorted_gameData) - max_game_event_id
                            for k in range(changeEventNumber-1, -1, -1):
                                
                                print(f"*********************************************>{sorted_gameData[len(gameData)- 1 - k]}")
                                team_name = sorted_gameData[len(gameData)- 1 - k]['team']
                                game_name = get_gameName(current_date, tableName)
                                game_team = get_event_team(game_name, team_name)
                                game_event_title = sorted_gameData[len(gameData)- 1 - k]['title']
                                game_event_time = sorted_gameData[len(gameData)- 1 - k]['time']
                                game_event_member1 = sorted_gameData[len(gameData)- 1 - k]['member1']
                                game_event_member2 = sorted_gameData[len(gameData)- 1 - k]['member2']
                                insert_row_table(current_date, tableName, game_name, game_url, changeEventNumber-k, game_team, game_event_title, game_event_time, game_event_member1, game_event_member2)


                                
                            # Close the browser
                            browser.close()
                    except:

                        continue
                    else:
                        break
    except:

        continue
    else:
        break









