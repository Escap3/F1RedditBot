import sys, time
from urllib.request import urlopen

def RateLimited(max_requests):

    """ 
    Rate limiter decorator so we don't spam the API. We are allowed    
    two requests per second and 200 per hour. This will limit the
    requests per second but not per hour. Found on:
    http://stackoverflow.com/a/667706 
    """

    min_interval = 1.0 / float(max_requests)
    def decorate(func):
        last_checked = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.time() - last_checked[0]
            left = min_interval - elapsed
            if left > 0:
                time.sleep(left)
            ret = func(*args,**kargs)
            last_checked[0] = time.time()
            return ret
        return rateLimitedFunction
    return decorate


@RateLimited(0.5)
def get_race_result(year, round):

    """ 
    Gets the result for the specified race from the Ergast API in JSON format.       
    The function is limited to one call per two seconds. 
    """

    url = "http://ergast.com/api/f1/" + str(year) + "/" + str(round) + "/results.json"
    try:
        with urlopen(url) as r:
            result = r.read().decode(r.headers.get_content_charset('utf-8'))
    except: 
        e = sys.exc_info()[0]
        print("Error: %s" % e)
        return None
    return result


@RateLimited(0.5)
def get_season_result(year):

    """ 
    Gets the final season standing from the Ergast API in JSON format.
    The function is limited to one call per two seconds. 
    """

    url = "http://ergast.com/api/f1/" + year + "/last/driverStandings.json"
    try:
        with urlopen(url) as r:
            result = r.read().decode(r.headers.get_content_charset('utf-8'))
    except: 
        e = sys.exc_info()[0]
        print("Error: %s" % e)
        return None
    return result

