import pandas as pd
import numpy as np
import re
from fredapi import Fred
import time
from datetime import datetime, timedelta
from io import StringIO
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import yfinance as yf
import holidays
from dateutil.easter import easter

from imsciences.mmm import dataprocessing

ims_proc = dataprocessing()

class datapull:
    
    def help(self):
        print("This is the help section. The functions in the package are as follows:")

        print("\n1. pull_fred_data")
        print("   - Description: Get data from FRED by using series id tokens.")
        print("   - Usage: pull_fred_data(week_commencing, series_id_list)")
        print("   - Example: pull_fred_data('mon', ['GPDIC1'])")

        print("\n2. pull_boe_data")
        print("   - Description: Fetch and process Bank of England interest rate data.")
        print("   - Usage: pull_boe_data(week_commencing)")
        print("   - Example: pull_boe_data('mon')")

        print("\n3. pull_oecd")
        print("   - Description: Fetch macroeconomic data from OECD for a specified country.")
        print("   - Usage: pull_oecd(country='GBR', week_commencing='mon', start_date: '2020-01-01')")
        print("   - Example: pull_oecd('GBR', 'mon', '2000-01-01')")

        print("\n4. get_google_mobility_data")
        print("   - Description: Fetch Google Mobility data for the specified country.")
        print("   - Usage: get_google_mobility_data(country, wc)")
        print("   - Example: get_google_mobility_data('United Kingdom', 'mon')")

        print("\n5. pull_seasonality")
        print("   - Description: Generate combined dummy variables for seasonality, trends, and COVID lockdowns.")
        print("   - Usage: pull_seasonality(week_commencing, start_date, countries)")
        print("   - Example: pull_seasonality('mon', '2020-01-01', ['US', 'GB'])")

        print("\n6. pull_weather")
        print("   - Description: Fetch and process historical weather data for the specified country.")
        print("   - Usage: pull_weather(week_commencing, country)")
        print("   - Example: pull_weather('mon', 'GBR')")
        
        print("\n7. pull_macro_ons_uk")
        print("   - Description: Fetch and process time series data from the Beta ONS API.")
        print("   - Usage: pull_macro_ons_uk(aditional_list, week_commencing, sector)")
        print("   - Example: pull_macro_ons_uk(['HBOI'], 'mon', 'fast_food')")
        
        print("\n8. pull_yfinance")
        print("   - Description: Fetch and process time series data from the Beta ONS API.")
        print("   - Usage: pull_yfinance(tickers, week_start_day)")
        print("   - Example: pull_yfinance(['^FTMC', '^IXIC'], 'mon')")

    ###############################################################  MACRO ##########################################################################

    def pull_fred_data(self, week_commencing: str = 'mon', series_id_list: list[str] = ["GPDIC1", "Y057RX1Q020SBEA", "GCEC1"]) -> pd.DataFrame:
        '''
        Parameters
        ----------
        week_commencing : str
            specify the day for the week commencing, the default is 'sun' (e.g., 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')

        series_id_list : list[str]
            provide a list with IDs to download data series from FRED (link: https://fred.stlouisfed.org/tags/series?t=id). Default list is 
            ["GPDIC1", "Y057RX1Q020SBEA", "GCEC1"]
        
        Returns
        ----------
        pd.DataFrame
            Return a data frame with FRED data according to the series IDs provided
        '''
        # Fred API
        fred = Fred(api_key='76f5f8156145fdb8fbaf66f1eb944f8a')

        # Fetch the metadata for each series to get the full names
        series_names = {series_id: fred.get_series_info(series_id).title for series_id in series_id_list}

        # Download data from series id list
        fred_series = {series_id: fred.get_series(series_id) for series_id in series_id_list}

        # Data processing
        date_range = {'OBS': pd.date_range("1950-01-01", datetime.today().strftime('%Y-%m-%d'), freq='d')}
        fred_series_df = pd.DataFrame(date_range)

        for series_id, series_data in fred_series.items():
            series_data = series_data.reset_index()
            series_data.columns = ['OBS', series_names[series_id]]  # Use the series name as the column header
            fred_series_df = pd.merge_asof(fred_series_df, series_data, on='OBS', direction='backward')

        # Handle duplicate columns
        for col in fred_series_df.columns:
            if '_x' in col:
                base_col = col.replace('_x', '')
                fred_series_df[base_col] = fred_series_df[col].combine_first(fred_series_df[base_col + '_y'])
                fred_series_df.drop([col, base_col + '_y'], axis=1, inplace=True)

        # Ensure sum_columns are present in the DataFrame
        sum_columns = [series_names[series_id] for series_id in series_id_list if series_names[series_id] in fred_series_df.columns]

        # Aggregate results by week
        fred_df_final = ims_proc.aggregate_daily_to_wc_wide(df=fred_series_df, 
                                                    date_column="OBS", 
                                                    group_columns=[], 
                                                    sum_columns=sum_columns,
                                                    wc=week_commencing,
                                                    aggregation="average")

        # Remove anything after the instance of any ':' in the column names and rename, except for 'OBS'
        fred_df_final.columns = ['OBS' if col == 'OBS' else 'macro_' + col.lower().split(':')[0].replace(' ', '_') for col in fred_df_final.columns]

        return fred_df_final
    
    def pull_boe_data(self, week_commencing="mon", max_retries=5, delay=5):
        """
        Fetch and process Bank of England interest rate data.

        Args:
            week_commencing (str): The starting day of the week for aggregation.
                                Options are "mon", "tue", "wed", "thur", "fri", "sat", "sun".
                                Default is "mon".
            max_retries (int): Maximum number of retries to fetch data in case of failure. Default is 5.
            delay (int): Delay in seconds between retry attempts. Default is 5.

        Returns:
            pd.DataFrame: A DataFrame with weekly aggregated Bank of England interest rates.
                        The 'OBS' column contains the week commencing dates in 'dd/mm/yyyy' format
                        and 'macro_boe_intr_rate' contains the average interest rate for the week.
        """
        # Week commencing dictionary
        day_dict = {"mon": 0, "tue": 1, "wed": 2, "thur": 3, "fri": 4, "sat": 5, "sun": 6}

        # URL of the Bank of England data page
        url = 'https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp'

        # Retry logic for HTTP request
        for attempt in range(max_retries):
            try:
                # Set up headers to mimic a browser request
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/91.0.4472.124 Safari/537.36"
                    )
                }
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for HTTP errors
                break
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    raise

        # Parse the HTML page
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table on the page
        table = soup.find("table")  # Locate the first table
        table_html = str(table)  # Convert table to string
        df = pd.read_html(StringIO(table_html))[0]  # Use StringIO to wrap the table HTML

        # Rename and clean up columns
        df.rename(columns={"Date Changed": "OBS", "Rate": "macro_boe_intr_rate"}, inplace=True)
        df["OBS"] = pd.to_datetime(df["OBS"], format="%d %b %y")
        df.sort_values("OBS", inplace=True)

        # Create a daily date range
        date_range = pd.date_range(df["OBS"].min(), datetime.today(), freq="D")
        df_daily = pd.DataFrame(date_range, columns=["OBS"])

        # Adjust each date to the specified week commencing day
        df_daily["Week_Commencing"] = df_daily["OBS"].apply(
            lambda x: x - timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7)
        )

        # Merge and forward-fill missing rates
        df_daily = df_daily.merge(df, on="OBS", how="left")
        df_daily["macro_boe_intr_rate"] = df_daily["macro_boe_intr_rate"].ffill()

        # Group by week commencing and calculate the average rate
        df_final = df_daily.groupby("Week_Commencing")["macro_boe_intr_rate"].mean().reset_index()
        df_final["Week_Commencing"] = df_final["Week_Commencing"].dt.strftime('%d/%m/%Y')
        df_final.rename(columns={"Week_Commencing": "OBS"}, inplace=True)

        return df_final
    
    def pull_oecd(self, country: str = "GBR", week_commencing: str = "mon", start_date: str = "2020-01-01") -> pd.DataFrame:
        """
        Fetch and process time series data from the OECD API.

        Args:
            country (list): A string containing a 3-letter code the of country of interest (E.g: "GBR", "FRA", "USA", "DEU")
            week_commencing (str): The starting day of the week for aggregation. 
                                Options are "mon", "tue", "wed", "thur", "fri", "sat", "sun".
            start_date (str): Dataset start date in the format "YYYY-MM-DD"

        Returns:
            pd.DataFrame: A DataFrame with weekly aggregated OECD data. The 'OBS' column contains the week 
                        commencing dates, and other columns contain the aggregated time series values.
        """ 

        def parse_quarter(date_str):
            """Parses a string in 'YYYY-Q#' format into a datetime object."""
            year, quarter = date_str.split('-')
            quarter_number = int(quarter[1])
            month = (quarter_number - 1) * 3 + 1
            return pd.Timestamp(f"{year}-{month:02d}-01")

        # Generate a date range from 1950-01-01 to today
        date_range = pd.date_range(start=start_date, end=datetime.today(), freq='D')

        url_details = [
            ["BCICP",    "SDD.STES,DSD_STES@DF_CLI,",                       ".....",              "macro_business_confidence_index"],
            ["CCICP",    "SDD.STES,DSD_STES@DF_CLI,",                       ".....",              "macro_consumer_confidence_index"],
            ["N.CPI",    "SDD.TPS,DSD_PRICES@DF_PRICES_ALL,",               "PA._T.N.GY",         "macro_cpi_total"],        
            ["N.CPI",    "SDD.TPS,DSD_PRICES@DF_PRICES_ALL,",               "PA.CP041T043.N.GY",  "macro_cpi_housing"],
            ["N.CPI",    "SDD.TPS,DSD_PRICES@DF_PRICES_ALL,",               "PA.CP01.N.GY",       "macro_cpi_food"],
            ["N.CPI",    "SDD.TPS,DSD_PRICES@DF_PRICES_ALL,",               "PA.CP045_0722.N.GY", "macro_cpi_energy"],
            ["UNE_LF_M", "SDD.TPS,DSD_LFS@DF_IALFS_UNE_M,",                 "._Z.Y._T.Y_GE15.",   "macro_unemployment_rate"],
            ["EAR",      "SDD.TPS,DSD_EAR@DF_HOU_EAR,",                     ".Y..S1D",            "macro_private_hourly_earnings"],
            ["RHP",      "ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0", "",                   "macro_real_house_prices"],
            ["PRVM",     "SDD.STES,DSD_KEI@DF_KEI,4.0",                     "IX.C..",             "macro_manufacturing_production_volume"],
            ["TOVM",     "SDD.STES,DSD_KEI@DF_KEI,4.0",                     "IX...",              "macro_retail_trade_volume"],
            ["IRSTCI",   "SDD.STES,DSD_KEI@DF_KEI,4.0",                     "PA...",              "macro_interbank_rate"],
            ["IRLT",     "SDD.STES,DSD_KEI@DF_KEI,4.0",                     "PA...",              "macro_long_term_interest_rate"],
            ["B1GQ",     "SDD.NAD,DSD_NAMAIN1@DF_QNA,1.1",                  "._Z....GY.T0102",    "macro_gdp_growth_yoy"]
        ]

        # Create empty final dataframe
        oecd_df_final = pd.DataFrame()

        daily_df = pd.DataFrame({'OBS': date_range})
        value_columns = []

        # Iterate for each variable of interest
        for series_details in url_details:
            series = series_details[0]
            dataset_id = series_details[1]
            filter = series_details[2]
            col_name = series_details[3]

            # check if request was successful and determine the most granular data available
            for freq in ['M', 'Q', 'A']:
                
                if series in ["UNE_LF_M", "EAR"]:
                    data_url = f"https://sdmx.oecd.org/public/rest/data/OECD.{dataset_id}/{country}.{series}.{filter}.{freq}?startPeriod=1950-01"
                elif series in ["B1GQ"]:
                    data_url = f"https://sdmx.oecd.org/public/rest/data/OECD.{dataset_id}/{freq}..{country}...{series}.{filter}?startPeriod=1950-01"
                else:
                    data_url = f"https://sdmx.oecd.org/public/rest/data/OECD.{dataset_id}/{country}.{freq}.{series}.{filter}?startPeriod=1950-01"

                # Make the request to the OECD API for data
                data_response = requests.get(data_url)

                # Check if the request was successful
                if data_response.status_code != 200:
                    print(f"Failed to fetch data for series {series} with frequency '{freq}' for {country}: {data_response.status_code} {data_response.text}")
                    url_test = False
                    continue
                else:
                    url_test = True
                    break
            
            # get data for the next variable if url doesn't exist
            if url_test is False:
                continue

            root = ET.fromstring(data_response.content)

            # Define namespaces if necessary (the namespace is included in the tags)
            namespaces = {'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'}

            # Lists to store the data
            dates = []
            values = []

            # Iterate over all <Obs> elements and extract date and value
            for obs in root.findall('.//generic:Obs', namespaces):        

                # Extracting the time period (date)
                time_period = obs.find('.//generic:ObsDimension', namespaces).get('value')
                
                # Extracting the observation value
                value = obs.find('.//generic:ObsValue', namespaces).get('value')
                
                # Storing the data
                if time_period and value:
                    dates.append(time_period)
                    values.append(float(value))  # Convert value to float

            # Add variable names that were found to a list
            value_columns.append(col_name)

            # Creating a DataFrame
            data = pd.DataFrame({'OBS': dates, col_name: values})

            # Convert date strings into datetime format
            if freq == 'Q':
                data['OBS'] = data['OBS'].apply(parse_quarter)
            else:
                # Display the DataFrame
                data['OBS'] = data['OBS'].apply(lambda x: datetime.strptime(x, '%Y-%m'))

            # Sort data by chronological order
            data.sort_values(by='OBS', inplace=True)

            # Merge the data based on the observation date
            daily_df = pd.merge_asof(daily_df, data[['OBS', col_name]], on='OBS', direction='backward')


        # Ensure columns are numeric
        for col in value_columns:
            if col in daily_df.columns:
                daily_df[col] = pd.to_numeric(daily_df[col], errors='coerce').fillna(0)
            else:
                print(f"Column {col} not found in daily_df")

        # Aggregate results by week
        country_df = ims_proc.aggregate_daily_to_wc_wide(df=daily_df, 
                                                        date_column="OBS", 
                                                        group_columns=[], 
                                                        sum_columns=value_columns,
                                                        wc=week_commencing,
                                                        aggregation="average")
        
        oecd_df_final = pd.concat([oecd_df_final, country_df], axis=0, ignore_index=True)

        return oecd_df_final
    
    def get_google_mobility_data(self, country="United Kingdom", wc="mon") -> pd.DataFrame:
        """
        Fetch Google Mobility data for the specified country.
        
        Parameters:
        - country (str): The name of the country for which to fetch data.

        Returns:
        - pd.DataFrame: A DataFrame containing the Google Mobility data.
        """
        # URL of the Google Mobility Reports CSV file
        url = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"
        
        # Fetch the CSV file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        
        # Load the CSV file into a pandas DataFrame
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data, low_memory=False)
        
        # Filter the DataFrame for the specified country
        country_df = df[df['country_region'] == country]
        
        final_covid = ims_proc.aggregate_daily_to_wc_wide(country_df, "date", [],  ['retail_and_recreation_percent_change_from_baseline', 'grocery_and_pharmacy_percent_change_from_baseline',
                                                                                'parks_percent_change_from_baseline', 'transit_stations_percent_change_from_baseline',
                                                                                'workplaces_percent_change_from_baseline', 'residential_percent_change_from_baseline'], wc, "average")
        
        final_covid1 = ims_proc.rename_cols(final_covid, 'covid_')
        return final_covid1
        
    ###############################################################  Seasonality  ##########################################################################

    def pull_seasonality(self, week_commencing, start_date, countries):
        # ---------------------------------------------------------------------
        # 0. Setup: dictionary for 'week_commencing' to Python weekday() integer
        # ---------------------------------------------------------------------
        day_dict = {"mon": 0, "tue": 1, "wed": 2, "thur": 3, "fri": 4, "sat": 5, "sun": 6}

        # ---------------------------------------------------------------------
        # 1. Create daily date range from start_date to today
        # ---------------------------------------------------------------------
        date_range = pd.date_range(
            start=pd.to_datetime(start_date), 
            end=datetime.today(), 
            freq="D"
        )
        df_daily = pd.DataFrame(date_range, columns=["Date"])

        # ---------------------------------------------------------------------
        # 1.1 Identify "week_start" for each daily row, based on week_commencing
        # ---------------------------------------------------------------------
        df_daily['week_start'] = df_daily["Date"].apply(
            lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7)
        )

        # ---------------------------------------------------------------------
        # 2. Build a weekly index (df_weekly_start) with dummy columns
        # ---------------------------------------------------------------------
        df_weekly_start = df_daily[['week_start']].drop_duplicates().reset_index(drop=True)
        df_weekly_start.rename(columns={'week_start': "Date"}, inplace=True)
        
        # Set index to weekly "start of week"
        df_weekly_start.index = np.arange(1, len(df_weekly_start) + 1)
        df_weekly_start.set_index("Date", inplace=True)

        # Create individual weekly dummies
        dummy_columns = {}
        for i in range(len(df_weekly_start)):
            col_name = f"dum_{df_weekly_start.index[i].strftime('%Y_%m_%d')}"
            dummy_columns[col_name] = [0] * len(df_weekly_start)
            dummy_columns[col_name][i] = 1

        df_dummies = pd.DataFrame(dummy_columns, index=df_weekly_start.index)
        df_weekly_start = pd.concat([df_weekly_start, df_dummies], axis=1)

        # ---------------------------------------------------------------------
        # 3. Public holidays (daily) from 'holidays' package + each holiday name
        # ---------------------------------------------------------------------
        for country in countries:
            country_holidays = holidays.CountryHoliday(
                country, 
                years=range(int(start_date[:4]), datetime.today().year + 1)
            )
            # Daily indicator: 1 if that date is a holiday
            df_daily[f"seas_holiday_{country.lower()}"] = df_daily["Date"].apply(
                lambda x: 1 if x in country_holidays else 0
            )
            # Create columns for specific holiday names
            for date_hol, name in country_holidays.items():
                col_name = f"seas_{name.replace(' ', '_').lower()}_{country.lower()}"
                if col_name not in df_daily.columns:
                    df_daily[col_name] = 0
                df_daily.loc[df_daily["Date"] == pd.Timestamp(date_hol), col_name] = 1

        # ---------------------------------------------------------------------
        # 3.1 Additional Special Days (Father's Day, Mother's Day, etc.)
        #     We'll add daily columns for each. 
        # ---------------------------------------------------------------------
        # Initialize columns
        extra_cols = [
            "seas_valentines_day", 
            "seas_halloween", 
            "seas_fathers_day_us_uk",
            "seas_mothers_day_us",
            "seas_mothers_day_uk",
            "seas_good_friday",
            "seas_easter_monday",
            "seas_black_friday",
            "seas_cyber_monday",
        ]
        for c in extra_cols:
            df_daily[c] = 0  # default zero

        # Helper: nth_weekday_of_month(year, month, weekday, nth=1 => first, 2 => second, etc.)
        # weekday: Monday=0, Tuesday=1, ... Sunday=6
        def nth_weekday_of_month(year, month, weekday, nth):
            """
            Returns date of the nth <weekday> in <month> of <year>.
            E.g. nth_weekday_of_month(2023, 6, 6, 3) => 3rd Sunday of June 2023.
            """
            # 1st day of the month
            d = datetime(year, month, 1)
            # What is the weekday of day #1?
            w = d.weekday()  # Monday=0, Tuesday=1, ... Sunday=6
            # If we want, e.g. Sunday=6, we see how many days to add
            delta = (weekday - w) % 7
            # This is the first <weekday> in that month
            first_weekday = d + timedelta(days=delta)
            # Now add 7*(nth-1) days
            return first_weekday + timedelta(days=7 * (nth-1))

        def get_good_friday(year):
            """Good Friday is 2 days before Easter Sunday."""
            return easter(year) - timedelta(days=2)

        def get_easter_monday(year):
            """Easter Monday is 1 day after Easter Sunday."""
            return easter(year) + timedelta(days=1)

        def get_black_friday(year):
            """
            Black Friday = day after US Thanksgiving, 
            and US Thanksgiving is the 4th Thursday in November.
            """
            # 4th Thursday in November
            fourth_thursday = nth_weekday_of_month(year, 11, 3, 4)  # weekday=3 => Thursday
            return fourth_thursday + timedelta(days=1)

        def get_cyber_monday(year):
            """Cyber Monday = Monday after US Thanksgiving, i.e. 4 days after 4th Thursday in Nov."""
            # 4th Thursday in November
            fourth_thursday = nth_weekday_of_month(year, 11, 3, 4)
            return fourth_thursday + timedelta(days=4)  # Monday after Thanksgiving

        # Loop over each year in range
        start_yr = int(start_date[:4])
        end_yr = datetime.today().year

        for yr in range(start_yr, end_yr + 1):
            # Valentines = Feb 14
            valentines_day = datetime(yr, 2, 14)
            # Halloween = Oct 31
            halloween_day  = datetime(yr, 10, 31)
            # Father's Day (US & UK) = 3rd Sunday in June
            fathers_day    = nth_weekday_of_month(yr, 6, 6, 3)  # Sunday=6
            # Mother's Day US = 2nd Sunday in May
            mothers_day_us = nth_weekday_of_month(yr, 5, 6, 2)
            # Mother's Day UK: 4th Sunday in Lent => "Mothering Sunday"
            #   We can approximate as: Easter Sunday - 21 days 
            #   BUT we also must ensure it's actually Sunday 
            #   (the 4th Sunday in Lent can shift. We'll do the official approach below.)
            #   Another approach: Easter Sunday - 7 * (4 weeks) is the 4th Sunday prior to Easter.
            #   But that might overshoot if Lent started mid-week. 
            # Let's do a quick approach:
            #   Officially: Mothering Sunday = 3 weeks before Easter Sunday (the 4th Sunday is Easter Sunday itself).
            #   So Easter - 21 days should be the Sunday, but let's confirm with weekday check.
            mothering_sunday = easter(yr) - timedelta(days=21)
            # If for some reason that's not a Sunday (rare corner cases), shift to Sunday:
            while mothering_sunday.weekday() != 6:  # Sunday=6
                mothering_sunday -= timedelta(days=1)

            # Good Friday, Easter Monday
            gf = get_good_friday(yr)
            em = get_easter_monday(yr)

            # Black Friday, Cyber Monday
            bf = get_black_friday(yr)
            cm = get_cyber_monday(yr)

            # Mark them in df_daily if in range
            for special_date, col in [
                (valentines_day, "seas_valentines_day"),
                (halloween_day,  "seas_halloween"),
                (fathers_day,    "seas_fathers_day_us_uk"),
                (mothers_day_us, "seas_mothers_day_us"),
                (mothering_sunday, "seas_mothers_day_uk"),
                (gf, "seas_good_friday"),
                (em, "seas_easter_monday"),
                (bf, "seas_black_friday"),
                (cm, "seas_cyber_monday"),
            ]:
                # Convert to pd.Timestamp:
                special_ts = pd.Timestamp(special_date)

                # Only set if it's within your daily range
                if (special_ts >= df_daily["Date"].min()) and (special_ts <= df_daily["Date"].max()):
                    df_daily.loc[df_daily["Date"] == special_ts, col] = 1

        # ---------------------------------------------------------------------
        # 4. Add daily indicators for last day & last Friday of month
        #    Then aggregate them to weekly level using .max()
        # ---------------------------------------------------------------------
        # Last day of month (daily)
        df_daily["seas_last_day_of_month"] = df_daily["Date"].apply(
            lambda d: 1 if d == d.to_period("M").to_timestamp("M") else 0
        )

        # Last Friday of month (daily)
        def is_last_friday(date):
            # last day of the month
            last_day_of_month = date.to_period("M").to_timestamp("M")
            last_day_weekday = last_day_of_month.weekday()  # Monday=0,...Sunday=6
            # Determine how many days we go back from the last day to get Friday (weekday=4)
            if last_day_weekday >= 4:
                days_to_subtract = last_day_weekday - 4
            else:
                days_to_subtract = last_day_weekday + 3
            last_friday = last_day_of_month - pd.Timedelta(days=days_to_subtract)
            return 1 if date == last_friday else 0

        df_daily["seas_last_friday_of_month"] = df_daily["Date"].apply(is_last_friday)

        # ---------------------------------------------------------------------
        # 5. Weekly aggregation for holiday columns & monthly dummies
        # ---------------------------------------------------------------------
        # For monthly dummies, create a daily col "Month", then get_dummies
        df_daily["Month"] = df_daily["Date"].dt.month_name().str.lower()
        df_monthly_dummies = pd.get_dummies(
            df_daily, 
            prefix="seas", 
            columns=["Month"], 
            dtype=int
        )
        # Recalculate 'week_start' (already in df_daily, but just to be sure)
        df_monthly_dummies['week_start'] = df_daily['week_start']

        # Group monthly dummies by .sum() or .mean()—we often spread them across the week
        df_monthly_dummies = (
            df_monthly_dummies
            .groupby('week_start')
            .sum(numeric_only=True)    # sum the daily flags
            .reset_index()
            .rename(columns={'week_start': "Date"})
            .set_index("Date")
        )
        # Spread monthly dummies by 7 to distribute across that week
        monthly_cols = [c for c in df_monthly_dummies.columns if c.startswith("seas_month_")]
        df_monthly_dummies[monthly_cols] = df_monthly_dummies[monthly_cols] / 7

        # Group holiday & special-day columns by .max() => binary at weekly level
        df_holidays = (
            df_daily
            .groupby('week_start')
            .max(numeric_only=True)   # if any day=1 in that week, entire week=1
            .reset_index()
            .rename(columns={'week_start': "Date"})
            .set_index("Date")
        )

        # ---------------------------------------------------------------------
        # 6. Combine weekly start, monthly dummies, holiday flags
        # ---------------------------------------------------------------------
        df_combined = pd.concat([df_weekly_start, df_monthly_dummies], axis=1)
        df_combined = pd.concat([df_combined, df_holidays], axis=1)
        df_combined = df_combined.loc[:, ~df_combined.columns.duplicated()]

        # ---------------------------------------------------------------------
        # 7. Create weekly dummies for Week of Year & yearly dummies
        # ---------------------------------------------------------------------
        df_combined.reset_index(inplace=True)
        df_combined.rename(columns={"index": "old_index"}, inplace=True)  # just in case
        
        df_combined["Week"] = df_combined["Date"].dt.isocalendar().week
        df_combined = pd.get_dummies(df_combined, prefix="seas", columns=["Week"], dtype=int)
        
        df_combined["Year"] = df_combined["Date"].dt.year
        df_combined = pd.get_dummies(df_combined, prefix="seas", columns=["Year"], dtype=int)
        
        # ---------------------------------------------------------------------
        # 8. Add constant & trend
        # ---------------------------------------------------------------------
        df_combined["Constant"] = 1
        df_combined["Trend"] = df_combined.index + 1
        
        # ---------------------------------------------------------------------
        # 9. Rename Date -> OBS and return
        # ---------------------------------------------------------------------
        df_combined.rename(columns={"Date": "OBS"}, inplace=True)
        
        return df_combined

    
    def pull_weather(self, week_commencing, country) -> pd.DataFrame:
        import pandas as pd
        import urllib.request  # noqa: F811
        from datetime import datetime
        import requests
        from geopy.geocoders import Nominatim  # noqa: F811

        # Week commencing dictionary
        day_dict = {"mon": 0, "tue": 1, "wed": 2, "thur": 3, "fri": 4, "sat": 5, "sun": 6}

        # Country dictionary
        country_dict = {"AUS": "AU__ASOS", "GBR": "GB__ASOS", "USA": "USCRN", "DEU": "DE__ASOS", "CAN": "Canada", "ZAF": "ZA__ASOS"}

        # Function to flatten a list of nested lists into a list
        def flatten_list(nested_list):
            return [item for sublist in nested_list for item in sublist]

        # Choose country
        country = country_dict[country]

        # Choose start and end dates
        start_day = 1
        start_month = 1
        start_year = 2014
        formatted_date = datetime(start_year, start_month, start_day).strftime("%Y-%m-%d")
        today = datetime.now()
        end_day = today.day
        end_month = today.month
        end_year = today.year

        if country == "GB__ASOS":
            stations = ["&stations=EGCC", "&stations=EGNM", "&stations=EGBB",
                        "&stations=EGSH", "&stations=EGFF", "&stations=EGHI",
                        "&stations=EGLC", "&stations=EGHQ", "&stations=EGAC",
                        "&stations=EGPF", "&stations=EGGD", "&stations=EGPE",
                        "&stations=EGNT"]
        elif country == "AU__ASOS":
            stations = ["&stations=YPDN", "&stations=YBCS", "&stations=YBBN",
                        "&stations=YSSY", "&stations=YSSY", "&stations=YMEN",
                        "&stations=YPAD", "&stations=YPPH"]
        elif country == "USCRN":
            stations = ["&stations=64756", "&stations=64758", "&stations=03761", "&stations=54797",  # North
                        "&stations=53968", "&stations=53960", "&stations=54932", "&stations=13301",  # Midwest
                        "&stations=64756", "&stations=64756", "&stations=92821", "&stations=63862",  # South
                        "&stations=53152", "&stations=93245", "&stations=04138", "&stations=04237"]  # West
        elif country == "DE__ASOS":
            stations = ["&stations=EDDL", "&stations=EDDH", "&stations=EDDB",
                        "&stations=EDDN", "&stations=EDDF", "&stations=EDDK",
                        "&stations=EDLW", "&stations=EDDM"]
        elif country == "FR__ASOS":
            stations = ["&stations=LFPB"]
        elif country == "Canada":
            institute_vector = ["CA_NB_ASOS", "CA_NF_ASOS", "CA_NT_ASOS", "CA_NS_ASOS",
                                "CA_NU_ASOS"]
            stations_list = [[] for _ in range(5)]
            stations_list[0].append(["&stations=CYQM", "&stations=CERM", "&stations=CZCR",
                                    "&stations=CZBF", "&stations=CYFC", "&stations=CYCX"])

            stations_list[1].append(["&stations=CWZZ", "&stations=CYDP", "&stations=CYMH",
                                    "&stations=CYAY", "&stations=CWDO", "&stations=CXTP",
                                    "&stations=CYJT", "&stations=CYYR", "&stations=CZUM",
                                    "&stations=CYWK", "&stations=CYWK"])

            stations_list[2].append(["&stations=CYHI", "&stations=CZCP", "&stations=CWLI",
                                    "&stations=CWND", "&stations=CXTV", "&stations=CYVL",
                                    "&stations=CYCO", "&stations=CXDE", "&stations=CYWE",
                                    "&stations=CYLK", "&stations=CWID", "&stations=CYRF",
                                    "&stations=CXYH", "&stations=CYWY", "&stations=CWMT"])

            stations_list[3].append(["&stations=CWEF", "&stations=CXIB", "&stations=CYQY",
                                    "&stations=CYPD", "&stations=CXNP", "&stations=CXMY",
                                    "&stations=CYAW", "&stations=CWKG", "&stations=CWVU",
                                    "&stations=CXLB", "&stations=CWSA", "&stations=CWRN"])

            stations_list[4].append(["&stations=CYLT", "&stations=CWEU", "&stations=CWGZ",
                                    "&stations=CYIO", "&stations=CXSE", "&stations=CYCB",
                                    "&stations=CWIL", "&stations=CXWB", "&stations=CYZS",
                                    "&stations=CWJC", "&stations=CYFB", "&stations=CWUW"])

        elif country == "ZA__ASOS":
            cities = ["Johannesburg", "Cape Town", "Durban", "Pretoria"]
            stations = []

            for city in cities:
                geolocator = Nominatim(user_agent="MyApp")
                location = geolocator.geocode(city)
                stations.append(f"&latitude={location.latitude}&longitude={location.longitude}")

        # Temperature
        if country in ["GB__ASOS", "AU__ASOS", "DE__ASOS", "FR__ASOS"]:
            # We start by making a data frame of the following weather stations
            station_query = ''.join(stations)

            raw_weather_list = ''.join(["https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?network=", country,
                                        station_query,
                                        "&year1=", str(start_year), "&month1=", str(start_month), "&day1=", str(start_day),
                                        "&year2=", str(end_year), "&month2=", str(end_month), "&day2=", str(end_day)])
            raw_weather = urllib.request.urlopen(raw_weather_list)
            raw_weather = pd.read_csv(raw_weather)

            # Replace the occurrences of "None" with Missing Value
            raw_weather["max_temp_f"].replace("None", 0, inplace=True)
            raw_weather["min_temp_f"].replace("None", 0, inplace=True)

            # Remove any data that isn't temperature-related
            weather = raw_weather.iloc[:, 0:4]

            weather[["max_temp_f", "min_temp_f"]] = weather[["max_temp_f", "min_temp_f"]].apply(pd.to_numeric)

            # Estimate mean temperature
            weather["mean_temp_f"] = (weather["max_temp_f"] + weather["min_temp_f"]) / 2

            # Convert Fahrenheit to Celsius for max_temp_f
            weather["max_temp_c"] = (weather["max_temp_f"] - 32) * 5 / 9

            # Convert Fahrenheit to Celsius for min_temp_f
            weather["min_temp_c"] = (weather["min_temp_f"] - 32) * 5 / 9

            # Convert Fahrenheit to Celsius for mean_temp_f
            weather["mean_temp_c"] = (weather["mean_temp_f"] - 32) * 5 / 9

            # Aggregate the data to week commencing sunday taking the average of the data
            # Convert the date column to a Date type
            weather["day"] = pd.to_datetime(weather["day"], format="%Y-%m-%d")

            # Determine the starting chosen day for each date
            weather['week_starting'] = weather["day"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = weather.select_dtypes(include='number').columns
            weekly_avg_temp = weather.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_temp.rename(columns={"max_temp_f": "avg_max_temp_f",
                                            "min_temp_f": "avg_min_temp_f",
                                            "mean_temp_f": "avg_mean_temp_f",
                                            "max_temp_c": "avg_max_temp_c",
                                            "min_temp_c": "avg_min_temp_c",
                                            "mean_temp_c": "avg_mean_temp_c"}, inplace=True)
        elif country == "Canada":
            for i in range(len(institute_vector)):
                station_query_temp = ''.join(flatten_list(stations_list[i]))
                institute_temp = institute_vector[i]
                raw_weather_temp = ''.join(["https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?network=", institute_temp,
                                            station_query_temp,
                                            "&year1=", str(start_year), "&month1=", str(start_month), "&day1=", str(start_day),
                                            "&year2=", str(end_year), "&month2=", str(end_month), "&day2=", str(end_day)])
                raw_weather_temp = urllib.request.urlopen(raw_weather_temp)
                raw_weather_temp = pd.read_csv(raw_weather_temp)

                if len(raw_weather_temp.index) == 0:
                    continue
                raw_weather_temp = raw_weather_temp[['station', 'day', 'max_temp_f', 'min_temp_f', 'precip_in']]

                if i == 1:
                    raw_weather = raw_weather_temp
                else:
                    raw_weather = pd.concat([raw_weather, raw_weather_temp])

                # Drop error column if it exists
                if 'ERROR: Invalid network specified' in list(raw_weather.columns):
                    raw_weather.drop('ERROR: Invalid network specified', axis=1, inplace=True)

                # Replace none values
                raw_weather["max_temp_f"].replace("None", 0, inplace=True)
                raw_weather["min_temp_f"].replace("None", 0, inplace=True)
                raw_weather["precip_in"].replace("None", 0, inplace=True)

                weather = raw_weather
                weather[["max_temp_f", "min_temp_f", "precip_in"]] = weather[["max_temp_f", "min_temp_f", "precip_in"]].apply(pd.to_numeric)

                # Estimate mean temperature
                weather["mean_temp_f"] = (weather["max_temp_f"] + weather["min_temp_f"]) / 2

                # Convert Fahrenheit to Celsius for max_temp_f
                weather["max_temp_c"] = (weather["max_temp_f"] - 32) * 5 / 9

                # Convert Fahrenheit to Celsius for min_temp_f
                weather["min_temp_c"] = (weather["min_temp_f"] - 32) * 5 / 9

                # Convert Fahrenheit to Celsius for mean_temp_f
                weather["mean_temp_c"] = (weather["mean_temp_f"] - 32) * 5 / 9

                # Aggregate the data to week commencing sunday taking the average of the data
                # Convert the date column to a Date type
                weather["day"] = pd.to_datetime(weather["day"], format="%Y-%m-%d")

                # Determine the starting chosen day for each date
                weather['week_starting'] = weather["day"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

                # Group by week_starting and summarize
                numeric_columns = weather.select_dtypes(include='number').columns
                weekly_avg_temp = weather.groupby("week_starting")[numeric_columns].mean()
                weekly_avg_temp.rename(columns={"max_temp_f": "avg_max_temp_f",
                                                "min_temp_f": "avg_min_temp_f",
                                                "mean_temp_f": "avg_mean_temp_f",
                                                "max_temp_c": "avg_max_temp_c",
                                                "min_temp_c": "avg_min_temp_c",
                                                "mean_temp_c": "avg_mean_temp_c",
                                                "precip_in": "avg_mean_perc"}, inplace=True)
        elif country == "ZA__ASOS":
            weather_data_list = []

            for city in cities:
                geolocator = Nominatim(user_agent="MyApp")
                location = geolocator.geocode(city)
                url = "https://archive-api.open-meteo.com/v1/archive"

                params = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "start_date": formatted_date,
                    "end_date": today.strftime("%Y-%m-%d"),
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "timezone": "auto"
                }

                response = requests.get(url, params=params)
                response_data = response.json()

                daily_data = response_data["daily"]
                dates = daily_data["time"]

                data = pd.DataFrame({
                    "day": dates,
                    "max_temp_f": daily_data["temperature_2m_max"],
                    "min_temp_f": daily_data["temperature_2m_min"],
                    "precip_in": daily_data["precipitation_sum"]
                })
                data["city"] = city
                weather_data_list.append(data)

            weather = pd.concat(weather_data_list)

            # Convert the date column to a Date type
            weather["day"] = pd.to_datetime(weather["day"])

            # Replace None values
            weather["max_temp_f"].replace("None", 0, inplace=True)
            weather["min_temp_f"].replace("None", 0, inplace=True)
            weather["precip_in"].replace("None", 0, inplace=True)

            weather[["max_temp_f", "min_temp_f", "precip_in"]] = weather[["max_temp_f", "min_temp_f", "precip_in"]].apply(pd.to_numeric)

            # Estimate mean temperature
            weather["mean_temp_f"] = (weather["max_temp_f"] + weather["min_temp_f"]) / 2

            # Convert Fahrenheit to Celsius for max_temp_f
            weather["max_temp_c"] = (weather["max_temp_f"] - 32) * 5 / 9

            # Convert Fahrenheit to Celsius for min_temp_f
            weather["min_temp_c"] = (weather["min_temp_f"] - 32) * 5 / 9

            # Convert Fahrenheit to Celsius for mean_temp_f
            weather["mean_temp_c"] = (weather["mean_temp_f"] - 32) * 5 / 9

            # Determine the starting chosen day for each date
            weather['week_starting'] = weather["day"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = weather.select_dtypes(include='number').columns
            weekly_avg_temp = weather.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_temp.rename(columns={"max_temp_f": "avg_max_temp_f",
                                            "min_temp_f": "avg_min_temp_f",
                                            "mean_temp_f": "avg_mean_temp_f",
                                            "max_temp_c": "avg_max_temp_c",
                                            "min_temp_c": "avg_min_temp_c",
                                            "mean_temp_c": "avg_mean_temp_c",
                                            "precip_in": "avg_mean_perc"}, inplace=True)

        else:
            # We start by making a data frame of the following weather stations
            station_query = ''.join(stations)

            raw_weather_list = ''.join(["https://mesonet.agron.iastate.edu/cgi-bin/request/daily.py?network=", country,
                                        station_query,
                                        "&year1=", str(start_year), "&month1=", str(start_month), "&day1=", str(start_day),
                                        "&year2=", str(end_year), "&month2=", str(end_month), "&day2=", str(end_day)])
            raw_weather = urllib.request.urlopen(raw_weather_list)
            raw_weather = pd.read_csv(raw_weather)

            raw_weather = raw_weather[['day', 'max_temp_f', 'min_temp_f', 'precip_in']]

            # Replace the occurrences of "None" with Missing Value
            raw_weather["max_temp_f"].replace("None", 0, inplace=True)
            raw_weather["min_temp_f"].replace("None", 0, inplace=True)
            raw_weather["precip_in"].replace("None", 0, inplace=True)

            # Remove any data that isn't temperature-related
            weather = raw_weather

            weather[["max_temp_f", "min_temp_f", "precip_in"]] = weather[["max_temp_f", "min_temp_f", "precip_in"]].apply(pd.to_numeric)

            # Estimate mean temperature
            weather["mean_temp_f"] = (weather["max_temp_f"] + weather["min_temp_f"]) / 2

            # Convert Fahrenheit to Celsius for max_temp_f
            weather["max_temp_c"] = (weather["max_temp_f"] - 32) * 5 / 9

            # Convert Fahrenheit to Celsius for min_temp_f
            weather["min_temp_c"] = (weather["min_temp_f"] - 32) * 5 / 9

            # Convert Fahrenheit to Celsius for mean_temp_f
            weather["mean_temp_c"] = (weather["mean_temp_f"] - 32) * 5 / 9

            # Aggregate the data to week commencing sunday taking the average of the data
            # Convert the date column to a Date type
            weather["day"] = pd.to_datetime(weather["day"], format="%Y-%m-%d")

            # Determine the starting chosen day for each date
            weather['week_starting'] = weather["day"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = weather.select_dtypes(include='number').columns
            weekly_avg_temp = weather.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_temp.rename(columns={"max_temp_f": "avg_max_temp_f",
                                            "min_temp_f": "avg_min_temp_f",
                                            "mean_temp_f": "avg_mean_temp_f",
                                            "max_temp_c": "avg_max_temp_c",
                                            "min_temp_c": "avg_min_temp_c",
                                            "mean_temp_c": "avg_mean_temp_c",
                                            "precip_in": "avg_mean_perc"}, inplace=True)

        # Rainfall
        if country == "GB__ASOS":
            # Define cities and date range
            cities = ["Manchester", "Leeds", "Birmingham", "Norwich", "Cardiff", "Southampton", "London", "Newquay", "Belfast", "Glasgow", "Bristol", "Newcastle"]
            
            start_date = formatted_date
            end_date = today.strftime("%Y-%m-%d")

            # Initialize an empty list to store the weather data for each city
            weather_data_list = []

            # Loop through each city and fetch weather data
            for city in cities:
                # Initialize Nominatim API
                geolocator = Nominatim(user_agent="MyApp")
                location = geolocator.geocode(city)
                url = "https://archive-api.open-meteo.com/v1/archive"

                params = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "precipitation_sum",
                    "timezone": "auto"
                }

                response = requests.get(url, params=params)
                response_data = response.json()

                daily_data = response_data["daily"]["precipitation_sum"]
                dates = response_data["daily"]["time"]

                data = pd.DataFrame({"date": dates, "rainfall": daily_data})
                data["city"] = city

                weather_data_list.append(data)

            # Combine all city data into a single data frame
            all_weather_data = pd.concat(weather_data_list)

            # Convert the date column to a Date type
            all_weather_data["date"] = pd.to_datetime(all_weather_data["date"])

            # Set week commencing col up
            all_weather_data['week_starting'] = all_weather_data["date"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = all_weather_data.select_dtypes(include='number').columns
            weekly_avg_rain = all_weather_data.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_rain.rename(columns={"rainfall": "avg_rainfall"}, inplace=True)

            # Change index to datetime
            weekly_avg_rain.index = pd.to_datetime(weekly_avg_rain.index)

        elif country == "AU__ASOS":

            # Define cities and date range
            cities = ["Darwin", "Cairns", "Brisbane", "Sydney", "Melbourne", "Adelaide", "Perth"]

            start_date = formatted_date
            end_date = today.strftime("%Y-%m-%d")

            # Initialize an empty list to store the weather data for each city
            weather_data_list = []

            # Loop through each city and fetch weather data
            for city in cities:
                # Initialize Nominatim API
                geolocator = Nominatim(user_agent="MyApp")
                location = geolocator.geocode(city)
                url = "https://archive-api.open-meteo.com/v1/archive"

                params = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "precipitation_sum",
                    "timezone": "auto"
                }

                response = requests.get(url, params=params)
                response_data = response.json()

                daily_data = response_data["daily"]["precipitation_sum"]
                dates = response_data["daily"]["time"]

                data = pd.DataFrame({"date": dates, "rainfall": daily_data})
                data["city"] = city

                weather_data_list.append(data)

            # Combine all city data into a single data frame
            all_weather_data = pd.concat(weather_data_list)

            # Convert the date column to a Date type
            all_weather_data["date"] = pd.to_datetime(all_weather_data["date"])

            # Set week commencing col up
            all_weather_data['week_starting'] = all_weather_data["date"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = all_weather_data.select_dtypes(include='number').columns
            weekly_avg_rain = all_weather_data.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_rain.rename(columns={"rainfall": "avg_rainfall"}, inplace=True)

            # Change index to datetime
            weekly_avg_rain.index = pd.to_datetime(weekly_avg_rain.index)

        elif country == "DE__ASOS":

            # Define cities and date range
            cities = ["Dortmund", "Düsseldorf", "Frankfurt", "Munich", "Cologne", "Berlin", "Hamburg", "Nuernberg"]

            start_date = formatted_date
            end_date = today.strftime("%Y-%m-%d")

            # Initialize an empty list to store the weather data for each city
            weather_data_list = []

            # Loop through each city and fetch weather data
            for city in cities:
                # Initialize Nominatim API
                geolocator = Nominatim(user_agent="MyApp")
                location = geolocator.geocode(city)
                url = "https://archive-api.open-meteo.com/v1/archive"

                params = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "precipitation_sum",
                    "timezone": "auto"
                }

                response = requests.get(url, params=params)
                response_data = response.json()

                daily_data = response_data["daily"]["precipitation_sum"]
                dates = response_data["daily"]["time"]

                data = pd.DataFrame({"date": dates, "rainfall": daily_data})
                data["city"] = city

                weather_data_list.append(data)

            # Combine all city data into a single data frame
            all_weather_data = pd.concat(weather_data_list)

            # Convert the date column to a Date type
            all_weather_data["date"] = pd.to_datetime(all_weather_data["date"])

            # Set week commencing col up
            all_weather_data['week_starting'] = all_weather_data["date"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = all_weather_data.select_dtypes(include='number').columns
            weekly_avg_rain = all_weather_data.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_rain.rename(columns={"rainfall": "avg_rainfall"}, inplace=True)

            # Change index to datetime
            weekly_avg_rain.index = pd.to_datetime(weekly_avg_rain.index)

        elif country == "FR__ASOS":

            # Define cities and date range
            cities = ["Paris"]

            start_date = formatted_date
            end_date = today.strftime("%Y-%m-%d")

            # Initialize an empty list to store the weather data for each city
            weather_data_list = []

            # Loop through each city and fetch weather data
            for city in cities:
                # Initialize Nominatim API
                geolocator = Nominatim(user_agent="MyApp")
                location = geolocator.geocode(city)
                url = "https://archive-api.open-meteo.com/v1/archive"

                params = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "precipitation_sum",
                    "timezone": "auto"
                }

                response = requests.get(url, params=params)
                response_data = response.json()

                daily_data = response_data["daily"]["precipitation_sum"]
                dates = response_data["daily"]["time"]

                data = pd.DataFrame({"date": dates, "rainfall": daily_data})
                data["city"] = city

                weather_data_list.append(data)

            # Combine all city data into a single data frame
            all_weather_data = pd.concat(weather_data_list)

            # Convert the date column to a Date type
            all_weather_data["date"] = pd.to_datetime(all_weather_data["date"])

            # Set week commencing col up
            all_weather_data['week_starting'] = all_weather_data["date"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = all_weather_data.select_dtypes(include='number').columns
            weekly_avg_rain = all_weather_data.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_rain.rename(columns={"rainfall": "avg_rainfall"}, inplace=True)

            # Change index to datetime
            weekly_avg_rain.index = pd.to_datetime(weekly_avg_rain.index)

        elif country == "ZA__ASOS":
            cities = ["Johannesburg", "Cape Town", "Durban", "Pretoria"]
            start_date = formatted_date
            end_date = today.strftime("%Y-%m-%d")

            weather_data_list = []

            for city in cities:
                geolocator = Nominatim(user_agent="MyApp")
                location = geolocator.geocode(city)
                url = "https://archive-api.open-meteo.com/v1/archive"

                params = {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "precipitation_sum",
                    "timezone": "auto"
                }

                response = requests.get(url, params=params)
                response_data = response.json()

                daily_data = response_data["daily"]["precipitation_sum"]
                dates = response_data["daily"]["time"]

                data = pd.DataFrame({"date": dates, "rainfall": daily_data})
                data["city"] = city

                weather_data_list.append(data)

            # Combine all city data into a single data frame
            all_weather_data = pd.concat(weather_data_list)

            # Convert the date column to a Date type
            all_weather_data["date"] = pd.to_datetime(all_weather_data["date"])

            # Set week commencing col up
            all_weather_data['week_starting'] = all_weather_data["date"].apply(lambda x: x - pd.Timedelta(days=(x.weekday() - day_dict[week_commencing]) % 7))

            # Group by week_starting and summarize
            numeric_columns = all_weather_data.select_dtypes(include='number').columns
            weekly_avg_rain = all_weather_data.groupby("week_starting")[numeric_columns].mean()
            weekly_avg_rain.rename(columns={"rainfall": "avg_rainfall"}, inplace=True)

            # Change index to datetime
            weekly_avg_rain.index = pd.to_datetime(weekly_avg_rain.index)

        # Merge the dataframes
        if country in ["AU__ASOS", "DE__ASOS", "FR__ASOS", "GB__ASOS", "ZA__ASOS"]:
            merged_df = weekly_avg_rain.merge(weekly_avg_temp, on="week_starting")
        else:
            merged_df = weekly_avg_temp

        merged_df.reset_index(drop=False, inplace=True)
        merged_df.rename(columns={'week_starting': 'OBS'}, inplace=True)

        final_weather = ims_proc.rename_cols(merged_df, 'seas_')

        return final_weather
    
    def pull_macro_ons_uk(self, cdid_list=None, week_start_day="mon", sector=None):
        """
        Fetches time series data for multiple CDIDs from the ONS API, converts it to daily frequency, 
        aggregates it to weekly averages, and renames variables based on specified rules.

        Parameters:
            cdid_list (list): A list of additional CDIDs to fetch (e.g., ['JP9Z', 'UKPOP']). Defaults to None.
            week_start_day (str): The day the week starts on (e.g., 'Monday', 'Sunday').
            sector (str): The sector for which the standard CDIDs are fetched (e.g., 'fast_food', 'retail').

        Returns:
            pd.DataFrame: A DataFrame with weekly frequency, containing a 'week_commencing' column 
                        and all series as renamed columns.
        """
        # Define CDIDs for sectors and defaults
        sector_cdids = {
            "fast_food": ["L7TD", "L78Q", "DOAD"],
            "default": ["D7G7", "MGSX", "UKPOP", "IHYQ", "YBEZ", "MS77"],
        }

        default_cdids = sector_cdids["default"]
        sector_specific_cdids = sector_cdids.get(sector, [])
        standard_cdids = list(set(default_cdids + sector_specific_cdids))  # Avoid duplicates

        # Combine standard CDIDs and additional CDIDs
        if cdid_list is None:
            cdid_list = []
        cdid_list = list(set(standard_cdids + cdid_list))  # Avoid duplicates

        base_search_url = "https://api.beta.ons.gov.uk/v1/search?content_type=timeseries&cdids="
        base_data_url = "https://api.beta.ons.gov.uk/v1/data?uri="
        combined_df = pd.DataFrame()

        # Map week start day to pandas weekday convention
        days_map = {"mon": 0, "tue": 1, "wed": 2, "thur": 3, "fri": 4, "sat": 5, "sun": 6}
        if week_start_day not in days_map:
            raise ValueError("Invalid week start day. Choose from: " + ", ".join(days_map.keys()))
        week_start = days_map[week_start_day]

        for cdid in cdid_list:
            try:
                # Search for the series
                search_url = f"{base_search_url}{cdid}"
                search_response = requests.get(search_url)
                search_response.raise_for_status()
                search_data = search_response.json()

                items = search_data.get("items", [])
                if not items:
                    print(f"No data found for CDID: {cdid}")
                    continue

                # Extract series name and latest release URI
                series_name = items[0].get("title", f"Series_{cdid}")
                latest_date = max(
                    datetime.fromisoformat(item["release_date"].replace("Z", "+00:00"))
                    for item in items if "release_date" in item
                )
                latest_uri = next(
                    item["uri"] for item in items
                    if "release_date" in item and datetime.fromisoformat(item["release_date"].replace("Z", "+00:00")) == latest_date
                )

                # Fetch the dataset
                data_url = f"{base_data_url}{latest_uri}"
                data_response = requests.get(data_url)
                data_response.raise_for_status()
                data_json = data_response.json()

                # Detect the frequency and process accordingly
                if "months" in data_json and data_json["months"]:
                    frequency_key = "months"
                elif "quarters" in data_json and data_json["quarters"]:
                    frequency_key = "quarters"
                elif "years" in data_json and data_json["years"]:
                    frequency_key = "years"
                else:
                    print(f"Unsupported frequency or no data for CDID: {cdid}")
                    continue

                # Prepare the DataFrame
                df = pd.DataFrame(data_json[frequency_key])

                # Parse the 'date' field based on frequency
                if frequency_key == "months":
                    df["date"] = pd.to_datetime(df["date"], format="%Y %b", errors="coerce")
                elif frequency_key == "quarters":
                    def parse_quarter(quarter_str):
                        year, qtr = quarter_str.split(" Q")
                        month = {"1": 1, "2": 4, "3": 7, "4": 10}[qtr]
                        return datetime(int(year), month, 1)
                    df["date"] = df["date"].apply(parse_quarter)
                elif frequency_key == "years":
                    df["date"] = pd.to_datetime(df["date"], format="%Y", errors="coerce")

                df["value"] = pd.to_numeric(df["value"], errors="coerce")
                df.rename(columns={"value": series_name}, inplace=True)

                # Combine data
                df = df.loc[:, ["date", series_name]].dropna().reset_index(drop=True)
                if combined_df.empty:
                    combined_df = df
                else:
                    combined_df = pd.merge(combined_df, df, on="date", how="outer")

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for CDID {cdid}: {e}")
            except (KeyError, ValueError) as e:
                print(f"Error processing data for CDID {cdid}: {e}")

        if not combined_df.empty:
            min_date = combined_df["date"].min()
            max_date = datetime.today()
            date_range = pd.date_range(start=min_date, end=max_date, freq='D')
            daily_df = pd.DataFrame(date_range, columns=['date'])
            daily_df = pd.merge(daily_df, combined_df, on="date", how="left")
            daily_df = daily_df.ffill()

            # Aggregate to weekly frequency
            daily_df["week_commencing"] = daily_df["date"] - pd.to_timedelta((daily_df["date"].dt.weekday - week_start) % 7, unit='D')
            weekly_df = daily_df.groupby("week_commencing").mean(numeric_only=True).reset_index()

            def clean_column_name(name):
                name = re.sub(r"\(.*?\)", "", name)
                name = re.split(r":", name)[0]
                name = re.sub(r"\d+", "", name)
                name = re.sub(r"\b(annual|rate)\b", "", name, flags=re.IGNORECASE)
                name = re.sub(r"[^\w\s]", "", name)
                name = name.replace(" ", "_")
                name = re.sub(r"_+", "_", name)
                name = name.rstrip("_")
                return f"macro_{name.lower()}_uk"

            weekly_df.columns = [clean_column_name(col) if col != "week_commencing" else col for col in weekly_df.columns]
            weekly_df.rename(columns={"week_commencing": "OBS"}, inplace=True)

            weekly_df = weekly_df.fillna(0)

            return weekly_df
        else:
            print("No data available to process.")
            return pd.DataFrame()

    def pull_yfinance(self, tickers=None, week_start_day="mon"):
        """
        Fetches stock data for multiple tickers from Yahoo Finance, converts it to daily frequency, 
        aggregates it to weekly averages, and renames variables.

        Parameters:
            tickers (list): A list of additional stock tickers to fetch (e.g., ['AAPL', 'MSFT']). Defaults to None.
            week_start_day (str): The day the week starts on (e.g., 'Monday', 'Sunday').

        Returns:
            pd.DataFrame: A DataFrame with weekly frequency, containing an 'OBS' column 
                        and aggregated stock data for the specified tickers, with NaN values filled with 0.
        """
        # Define default tickers
        default_tickers = ["^FTSE", "GBPUSD=X", "GBPEUR=X", "^GSPC"]

        # Combine default tickers with additional ones
        if tickers is None:
            tickers = []
        tickers = list(set(default_tickers + tickers))  # Ensure no duplicates

        # Automatically set end_date to today
        end_date = datetime.today().strftime("%Y-%m-%d")
        
        # Mapping week start day to pandas weekday convention
        days_map = {"mon": 0, "tue": 1, "wed": 2, "thur": 3, "fri": 4, "sat": 5, "sun": 6}
        if week_start_day not in days_map:
            raise ValueError("Invalid week start day. Choose from: " + ", ".join(days_map.keys()))
        week_start = days_map[week_start_day]

        # Fetch data for all tickers without specifying a start date to get all available data
        data = yf.download(tickers, end=end_date, group_by="ticker", auto_adjust=True)
        
        # Process the data
        combined_df = pd.DataFrame()
        for ticker in tickers:
            try:
                # Extract the ticker's data
                ticker_data = data[ticker] if len(tickers) > 1 else data
                ticker_data = ticker_data.reset_index()

                # Ensure necessary columns are present
                if "Close" not in ticker_data.columns:
                    raise ValueError(f"Ticker {ticker} does not have 'Close' price data.")
                
                # Keep only relevant columns
                ticker_data = ticker_data[["Date", "Close"]]
                ticker_data.rename(columns={"Close": ticker}, inplace=True)

                # Merge data
                if combined_df.empty:
                    combined_df = ticker_data
                else:
                    combined_df = pd.merge(combined_df, ticker_data, on="Date", how="outer")

            except KeyError:
                print(f"Data for ticker {ticker} not available.")
            except Exception as e:
                print(f"Error processing ticker {ticker}: {e}")

        if not combined_df.empty:
            # Convert to daily frequency
            combined_df["Date"] = pd.to_datetime(combined_df["Date"])
            combined_df.set_index("Date", inplace=True)

            # Fill missing dates
            min_date = combined_df.index.min()
            max_date = combined_df.index.max()
            daily_index = pd.date_range(start=min_date, end=max_date, freq='D')
            combined_df = combined_df.reindex(daily_index)
            combined_df.index.name = "Date"
            combined_df = combined_df.ffill()

            # Aggregate to weekly frequency
            combined_df["OBS"] = combined_df.index - pd.to_timedelta((combined_df.index.weekday - week_start) % 7, unit="D")
            weekly_df = combined_df.groupby("OBS").mean(numeric_only=True).reset_index()

            # Fill NaN values with 0
            weekly_df = weekly_df.fillna(0)

            # Clean column names
            def clean_column_name(name):
                name = re.sub(r"[^\w\s]", "", name)
                return f"macro_{name.lower()}"

            weekly_df.columns = [clean_column_name(col) if col != "OBS" else col for col in weekly_df.columns]

            return weekly_df

        else:
            print("No data available to process.")
            return pd.DataFrame()
        
