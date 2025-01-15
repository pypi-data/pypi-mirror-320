# noaa_weather_hourly

`noaa_weather_hourly` cleans historical LCD weather files from the National Oceanic and Atmospheric Administration (NOAA).  It uses a simple command line interface to generate observed hourly (and other frequency) .CSV files.  

## Output Columns
* Date
* AltimeterSetting
* DewPointTemperature
* DryBulbTemperature
* Precipitation
* PressureChange
* RelativeHumidity
* StationPressure
* Sunrise
* Sunset
* Visibility
* WetBulbTemperature
* WindDirection
* WindGustSpeed
* WindSpeed
* No source data

<img alt="Clean LCD output file" width="800px" src="images\Clean LCD output file.PNG" />
<img alt="Command Line Output" width="800px" src="images\command line output.PNG" />

- [LCD Weather File Documentation](noaa_weather_hourly/data/LCD_documentation.pdf)

## Installation
This is a Python script that requires a local Python installation.  The following method uses pipx for installation which makes the 'noaa_weather_hourly' command available to run from any directory on the computer.  

Does this seem like too much work?  [Download a NOAA CSV file](#download-noaa-lcd-csv-file) and try to use it.  As described in [Process Details](#process-details), there can be numerous issues that complicate the use of a raw source file in spreadsheet analysis.

1. __Obtain Code__ through git OR download<BR>
    a. `git clone https://github.com/emskiphoto/noaa_weather_hourly.git` at a terminal prompt (requires git installation [git installation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git))
    a. Simple download….<BR>
    
2. [__Install Python__ (version 3.8 or newer)](https://www.python.org/downloads/#:~:text=Looking%20for%20a%20specific%20release%3F)
3. __Install pipx__ <BR>
    Windows:  
    `py -m pip install --user pipx`<BR>
    `py -m pipx ensurepath`<BR>
    Unix/macOS:<BR>
    `python3 -m pip install --user pipx`<BR>
    `python3 -m pipx ensurepath`<BR>
4. __Install noaa_weather_hourly__ 
    `pipx install noaa_weather_hourly`
<img alt="pipx install successful" width="800px" src="images\pipx install.PNG" />

## Usage
Open a terminal prompt ('Powershell' in Windows).  Navigate to specific folders using the `cd folder_name` command to go up the directory tree and `cd..` to go back down the directory tree.
    
### Usage for specific file 
Process the version 1 LCD file ".\data\3876540.csv" that is included in installation.<BR>
$ `noaa_weather_hourly -filename ".\data\3876540.csv"`

### Usage for most recent file(s)
Automatically select the newest files in the current directory based on last date modified and group all files with the same weather station ID in to a single output.<BR>
$ `noaa_weather_hourly`

### Usage for Frequencies other than Hourly
The default output contains Hourly frequency data.  Any of the following data frequencies can be output using the `-frequency` argument:<BR>
$ `noaa_weather_hourly [-frequency FREQUENCY] filename`

For example, a 15-minute frequency output:<BR>
$ `noaa_weather_hourly -frequency '15T' '<path_to_LCD_CSV_file>'`

Or a daily frequency output using the most recent file(s):<BR>
$ `noaa_weather_hourly -frequency 'D'`

'H':    'Hourly',
'T':    'Minutely'
'D':    'Daily',
'W':    'Weekly',
'M':    'Monthly',
'Q':    'Quarterly',
'Y':    'Yearly',

The core frequency argument can be modified for other frequencies.  For example, a 15-minute frequency dataset can be generated with '15T' and '3H' will generate a '3-Hourly' frequency file.


## Download NOAA LCD .CSV file
`noaa_weather_hourly` takes a raw NOAA Local Climatological Data .csv-format file as input.   Download file(s) for a specific location and date range from NOAA as described below.  NOAA changed the download process & interface in 2024 to use AWS buckets for storage.  As of December 2024 the new and old methods both work.  No account or API key is required, just an email address to receive a download link.

* [NOAA Data Tools: Local Climatological Data](https://www.ncdc.noaa.gov/cdo-web/datatools/lcd)
* [LCD Weather File Documentation](noaa_weather_hourly/data/LCD_documentation.pdf)
* [LCD Documentation Source](https://www.ncei.noaa.gov/data/local-climatological-data/doc/LCD_documentation.pdf)

It is recommended to store downloaded files in separate folders by location.   

### Before Spring 2024 (_multiple years in a single, large file_):
<img alt="NOAA LCD Website" width="800px" src="images\NOAA_LCD_data_tools_website.PNG" />
    
1. Go to [NOAA Data Tools: Local Climatological Data](https://www.ncdc.noaa.gov/cdo-web/datatools/lcd)
2. Find the desired Weather Station and select 'Add to Cart'
3. Click on 'cart (Free items)'
4. Select the Output Format 'LCD CSV'
5. Select the Date Range.  Consider adding an additional week before and after the needed date range to support interpolation of missing values.
6. "Enter Email Address" where a link to the LCD CSV download should be delivered.
7. "Submit Order"
8. Check email inbox for a "Climate Data Online request 1234567 complete" message and Download the LCD CSV file to a local folder using the "Download" link.  Do not change the name(s) of the LCD file(s).

### After Spring 2024 (_one or more files per calendar year, or single multi-year bundle_):
<img alt="NOAA LCD2 Website" width="600px" src="images\NOAA_LCD2_data_tools_website.PNG" />
    
1. Go to [Local Climatological Data (LCD), Version 2 (LCDv2)](https://www.ncei.noaa.gov/access/search/data-search/local-climatological-data-v2)
2. __What ?__: Select columns to be included in the file by clicking on 'Show List'.    
    - Beware that selecting columns that are not available for a given location will result in that location being excluded entirely from the search results.  
    - It's recommended to select only the columns listed in  [Output Columns](#output-columns)  
3. __Where ?__:  Input weather station location.  A list of all available annual weather files for all matching locations will be displayed.  Use the 'When' inputs to filter this list.
4. __When ?__:  (optional) For a single calendar year, select any date in that year.  For multiple calendar years click 'Select Date Range' and input start and end dates of the range.
5. (Recommended) Review list of matching files and click "Download" for each file.
    - (Alternatively) Merge multiple years of data as a single large file by "+ Select" multiple files.  Then select "Output Format" csv, click on "Configure and Add" and "Add Order to Cart".  "Proceed to Cart", provide and Email address and click "Submit".  Check email inbox for a "Climate Data Online request 1234567 complete" message and download the LCD CSV file to any local folder using the "Download" link.  Do not change the name(s) of the LCD file(s).  

## Process Details
The `noaa_weather_hourly` makes the source LCD file ready-to-use by resolving the following data formatting and quality issues.  
<img alt="Raw LCD file data issues" width="600px" src='images\Raw LCD file data issues.PNG' />
    
NOAA LCD files can contain more than 100 types of meteorological observations, but `noaa_weather_hourly` processes only [these output columns](#output-columns).  This is a standalone process that does not access any external (internet) resources and operates only in the directory it is intiated in unless a `-filename` in another directory is provided.

1. Locates the most recent LCD v1 or v2 file in the current directory (or uses optional file specified in `-filename`) and creates a copy of the source file(s), leaving the source file(s) unmodified
2. Extracts ID data and gathers additional station details
3. Determines if input files are LCD v1 or v2 and 
3. Merges multiple source files having the same station ID and resolves overlapping date ranges
4. Formats 'Sunrise' and 'Sunset' times
5. Removes recurring daily timestamps that contain more null values than allowed by 'pct_null_timestamp_max' parameter
6. Displays the percent of null values in source data to screen
7. Resamples and/or interpolates values per the input '-frequency' value
    - most columns are expected to have numeric values for every timestamp.  The maximum number of contiguous missing values to be interpolated is 24.  The 'max_records_to_interpolate' default can be overriden in the command line, for example `noaa_weather_hourly -max_records_to_interpolate 12` would limit interpolations to no more than 12 missing values in a row 
    - some columns are expected to have null values at some times and the null values are preserved in the output (ie., 'Precipitation', 'WindGustSpeed') 
8. Saves a single .CSV file to the same location as the source LCD file(s) (will overwrite existing files if an identical file already exists).
9. Output file is named "{STATION_NAME} {start_MM-DD-YYYY} to {end_MM-DD-YYYY} {frequency}.csv", (ie.,
    "CHICAGO O'HARE INTERNATIONAL 2020-01-01 to 2023-12-31 H.csv")

### Weather Station Directory
`noaa_weather_hourly` includes a processed 'isd-history.csv' file containing the details of ~11,600 active stations and ID cross-references (ICAO, FAA, WMO, WBAN) provided by [Historical Observing Metadata Repository (HOMR)](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt).  This data is only used to weather station location details as they are not provided in the LCD CSV file.  The data source is updated regularly, but the version in this script is not.  If updates are needed, consider running the 'ISD History Station Table.py' to update 'data/isd-history.csv'.

### Limitations:
* NOAA LCD source is for atmospheric data primarily for locations in the United States of America.
* NOAA LCD data is not certified for use in litigation
* `noaa_weather_hourly` is not an API
* `noaa_weather_hourly` Python module does not (currently) integrate with other Python tools
* Does not validate
* Does not visualize
* Processes only 'Hourly...' columns and 'Sunrise', 'Sunset' & 'DATE'
* Does not modify values from source
    - Does not filter or smooth apparently noisy source data
* Does not process or convert categorical data like 'HourlySkyConditions'
* Intended for data frequencies between yearly and 15-minutely.  Will accept frequencies
  as low as minutely ('T') but the output file size may be excessively large.   
* Does not compare to other references
* Uses only units of measure used by LCD (no unit conversion)
* No Forecast

    
## Acknowledgements
* [diyepw](https://github.com/IMMM-SFA/diyepw/tree/main) -  Amanda D. Smith, Benjamin Stürmer, Travis Thurber, & Chris R. Vernon. (2021). diyepw: A Python package for [EnergyPlus Weather (EPW) files](https://bigladdersoftware.com/epx/docs/8-3/auxiliary-programs/energyplus-weather-file-epw-data-dictionary.html) generation. Zenodo. https://doi.org/10.5281/zenodo.5258122<BR>
* [pycli](https://github.com/trstringer/pycli/tree/master) - Python command-line interface reference
* [Degree Days.net](https://www.degreedays.net/) - Excellent reference for weather-related energy engineering analysis    

## Example Alternative Observed Weather Data Sources
* http://weather.whiteboxtechnologies.com/hist<BR>
* https://openweathermap.org/history<BR>
* https://docs.synopticdata.com/services/weather-data-api<BR>
* https://mesowest.utah.edu/<BR>
* https://registry.opendata.aws/noaa-isd/<BR>
* https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database<BR>
* https://registry.opendata.aws/noaa-isd/<BR>

## Related Weather & Energy Model Code
* https://github.com/celikfatih/noaa-weather<BR>
* https://github.com/cagledw/climate_analyzer<BR>
* https://pypi.org/project/diyepw/<BR>
* https://github.com/GClunies/noaa_coops<BR>
* https://github.com/DevinRShaw/simple_noaa<BR>
* https://github.com/awslabs/amazon-asdi/tree/main/examples/noaa-isd<BR>
* https://pypi.org/project/climate-analyzer<BR>



## TL;DR - Background
### Different Weather Causes Different Performance
Weather-dependent models like building energy models generally use typical weather values to estimate a given metric for a system.  For example, typical weather values would be used to estimate the annual energy consumption of a building cooling system.  Inevitably, the actual weather the system experiences in the real world is _different_ than the weather used to create the model.  If the model is sensitive to weather the distinct typical & actual weather values will cause cumulative metrics to be different.  If the amplitude of these differences is larger than the cumulative impact of individual system elements (ex. the cooling system), it may not be possible to compare modeled and actual performance.  

### Analysis by Spreadsheet
The use cases below often require reporting & analysis that is easy to access, distribute, understand and review.  Therefore, energy engineers often must use spreadsheet software like MS Excel, Google Sheets, etc.  `noaa_weather_hourly` was developed to support spreadsheet analysis where a single missing value can break the calculation.  

### Financial Context of Energy Models
Many building design choices must be made before a physical building exists, and once equipment is installed, changing design choices become costly.  The installed performance will likely persist as-is for a decade or more until equipment needs to be replaced.   The building owners and the environment will feel the impact of early-stage design choices every year until equipment is changed.  Because the life-cycle cost of _operating_ the equipment may be several times larger than the _initial purchase price_, it is cost-effective to develop energy models that optimize operational cost and inform system design choices.

### Measurement & Verification of Modeled Expectations
Incentives and financing of high-efficiency solutions are ubiquitous.  When large financial incentives are in play, many providers must measure and verify (M&V) the true impact of specific system elements (energy conservation measures) to ensure that incentives are returning the intended results.   

Energy Service Companies (ESCO) and other efficiency solutions providers often guarantee specific performance improvements in contracts (ie., 10% reduction in annual electricity cost due to cooling system replacement).  If the solution does not achieve the estimated savings, the ESCO is liable for the financial difference in operating cost and possibly more.  Observed performance improvements are determined by comparing a baseline model to observed performance.  

In both cases, __the estimation of performance improvements is only valid if the impact of weather variance between the baseline model and observed reality is accounted for__. 

### Solution:  Weather-normalization
The solution to aligning the results of a model made with one set of weather values and actual results resulting from a different set of values is to weather-normalize the results.  This normalization process is only possible if both the typical and actual weather values are available.  Once the modeled and actual results are aligned (ie. the influence of weather variance is removed) the difference in expected and actual performance can be evaluated in detail.

### Availability of Free Weather Data
Otaining good, _usable_ data that is already available in the public domain is not necessarily easy or free of cost.  `noaa_weather_hourly` was created to facilitate convenient, free usage of limited volumes of hourly observed weather published by NOAA as a convenient .CSV file.  

There are numerous subscription or purchase-based [sources of historical weather](#example-alternative-observed-weather-data-sources), and many offer API access.  These sources may be preferable when many locations are needed and/or the data need to be updated frequently.