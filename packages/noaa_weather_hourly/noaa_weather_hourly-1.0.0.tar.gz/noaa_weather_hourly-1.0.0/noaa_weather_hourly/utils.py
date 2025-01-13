# utils.py
# noaa_weather_hourly
import pathlib
import re
import unicodedata
import pandas as pd

def say_hello():
    print('Hello from the Utils.py module')
    
def find_latest_file(directory, pattern):
    """Returns pathlib file path object for most recently modified file in 'directory' whose
    path/name matches 'pattern'.  The 'pattern' is the same pattern that would be input in the
    pathlib.glob() function.  
    Example Usage:  path = find_latest_file(pathlib.Path('data'), '*Minnesota.csv')"""
    try:
        return sorted([(f, f.stat().st_mtime) for f in directory.glob('*') 
                       if re.match(pattern, f.name)],
           key=lambda x: x[1], reverse=True)[0][0]
    except:
        return None
    
def find_file_re_pattern(directory, pattern):
    """Returns list of file names (name only, not paths) in the
    input Pathlib 'directory' that match
    the regular expression 'pattern' provided"""
    try:
        return [x for x in directory.glob('*') if
                          re.search(pattern, x.name) != None]
    except:
        return None
    
    
def find_files_re_pattern_sorted_last_modified(directory, pattern, descending=True):
    """Returns list of pathlib file path objects for most recently modified file
    in 'directory' whose path/name matches 'pattern'.  The 'pattern' is the same pattern
    that would be input in the pathlib.glob() function.  
    Example Usage:  paths = find_file_re_pattern_sorted_last_modified(
                    pathlib.Path('data'), '*Minnesota.csv')"""
    try:
        return [x_[0] for x_ in sorted([(f, f.stat().st_mtime) for f in 
                         find_file_re_pattern(directory, pattern)],
                           key=lambda x: x[1], reverse=descending)]
    except:
        return None
    
    
def datetime_from_HHMM(x):
    """Returns series x with HHMM time values converted to complete
    'YYYY-MM-DD hh:mm:ss' format timestamp objects.  Input series x
    must have a datetime index and is expected to hold time data in
    the '%H%M' format.  For example  '0751' or '751.0' is interpreted as
    07:51:00."""
    
    time = pd.to_datetime(pd.to_numeric(x.dropna().ffill()\
                             .bfill()), format = '%H%M')
    YMDHMS = pd.DataFrame({'Year': x.index.year,
                         'Month' : x.index.month,
                        'Day' : x.index.day,
                        'Hour' : time.dt.hour,
                         'Minute' : time.dt.minute,
                          'Second' : time.dt.second})

    return pd.to_datetime(YMDHMS)
    del time
    del YMDHM
    

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii',                                         'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def google_maps_url(lat, lon):
    """Returns google maps URL containing lat, lon value. 
    Example:  https://maps.google.com/?q=+33.630,-084.442"""
    url = """https://maps.google.com/?q={lat},{long}"""
    return url.format(lat = str(lat), long = str(lon))