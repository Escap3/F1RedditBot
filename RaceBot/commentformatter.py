import json

def convert_race_to_post(data):

    """
    Parses the JSON into a list of list containing the result from a race.
    Then passes on the created lists to a commentformatter that creates the
    finished comment as a string.
    @return The finished comment as a string
    """

    finaltable = [['Pos', 'No.', 'Driver', 'Constructor', 'Lap', 'Time/Retired', 'Grid', 'Points']]
    depth = 0
    try:
        parsed = json.loads(data)
        result = parsed['MRData']['RaceTable']['Races'].pop(0)
        link = result["url"]
        title = result['season'] + ' ' + result['raceName']        
        for res in result['Results']:
            if(depth > 25):
                break
            depth += 1
            driver = []
            driver.append(res['position'])
            driver.append(res['number'])
            driver.append(res['Driver']['givenName'] + ' ' + res['Driver']['familyName'])
            driver.append(res['Constructor']['name'])
            driver.append(res['laps'])
            if ('Time' in res.keys()):
                driver.append(res['Time']['time'])
            else:
                driver.append(res['status'])
            driver.append(res['grid'])
            driver.append(res['points'])
            finaltable.append(driver)
    except (ValueError, TypeError) as err:
        print("Error parsing JSON " + err.args[0])
        return None
    return format_comment(finaltable, title, link, 8)


def convert_season_to_post(data):

    """
    Parses the JSON into a list of list containing the result from a season.
    Then passes on the created lists to a commentformatter that creates the
    finished comment as a string.
    @return The finished comment as a string
    """

    finaltable = [['Pos', 'Driver', 'Constructor', 'Points']]
    depth = 0
    try:
        parsed = json.loads(data)
        result = parsed['MRData']['StandingsTable']['StandingsLists'].pop(0)
        season = result['season']
        for res in result['DriverStandings']:
            if(depth > 25):
                break
            depth += 1
            driver = []
            driver.append(res['position'])
            driver.append(res['Driver']['givenName'] + ' ' + res['Driver']['familyName'])
            driver.append(res['Constructors'].pop(0)['name'])
            driver.append(res['points'])
            finaltable.append(driver)
    except (ValueError, TypeError) as err:
        print("Error parsing JSON " + err.args[0])
        return None
    return format_comment(finaltable, season, 'https://en.wikipedia.org/wiki/' + season + '_Formula_One_season', 4)


def format_comment(table, title, link, columncount):

    """
    Takes the parsed JSON and turns it into a comment
    @return The finished comment 
    """

    str = "**[{0} Results]({1})**\n\n\n".format(title, link)
    for list in table:
        counter = 0
        for i in list:
            counter += 1
            if counter is columncount: 
                str += "{0}".format(i)
            else:
                str += "{0} | ".format(i)
        if table.index(list) is 0: 
            str += '\n'
            str += ":--|:--|:--|:--|:--|:--|:--|:--\n"
        else:
            str += '\n'
    return str

