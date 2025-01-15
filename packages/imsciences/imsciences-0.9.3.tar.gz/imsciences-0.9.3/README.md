# IMS Package Documentation

The **Independent Marketing Sciences** package is a Python library designed to process incoming data into a format tailored for projects, particularly those utilising weekly time series data. This package offers a suite of functions for efficient data collection, manipulation, visualisation and analysis.

---

## Key Features
- Seamless data processing for time series workflows.
- Aggregation, filtering, and transformation of time series data.
- Visualising Data
- Integration with external data sources like FRED, Bank of England, ONS and OECD.

---

Table of Contents
=================

1. [Data Processing for Time Series](#data-processing-for-time-series)
2. [Data Processing for Incrementality Testing](#data-processing-for-incrementality-testing)
3. [Data Visualisations](#data-visualisations)
4. [Data Pulling](#data-pulling)
5. [Installation](#installation)
6. [Usage](#usage)
7. [License](#license)

---

## Data Processing for Time Series

## 1. `get_wd_levels`
- **Description**: Get the working directory with the option of moving up parents.
- **Usage**: `get_wd_levels(levels)`
- **Example**: `get_wd_levels(0)`

## 2. `aggregate_daily_to_wc_long`
- **Description**: Aggregates daily data into weekly data, grouping and summing specified columns, starting on a specified day of the week.
- **Usage**: `aggregate_daily_to_wc_long(df, date_column, group_columns, sum_columns, wc, aggregation='sum')`
- **Example**: `aggregate_daily_to_wc_long(df, 'date', ['platform'], ['cost', 'impressions', 'clicks'], 'mon', 'average')`

## 3. `convert_monthly_to_daily`
- **Description**: Converts monthly data in a DataFrame to daily data by expanding and dividing the numeric values.
- **Usage**: `convert_monthly_to_daily(df, date_column, divide=True)`
- **Example**: `convert_monthly_to_daily(df, 'date')`

## 4. `week_of_year_mapping`
- **Description**: Converts a week column in 'yyyy-Www' or 'yyyy-ww' format to week commencing date.
- **Usage**: `week_of_year_mapping(df, week_col, start_day_str)`
- **Example**: `week_of_year_mapping(df, 'week', 'mon')`

## 5. `rename_cols`
- **Description**: Renames columns in a pandas DataFrame with a specified prefix or format.
- **Usage**: `rename_cols(df, name='ame_')`
- **Example**: `rename_cols(df, 'ame_facebook')`

## 6. `merge_new_and_old`
- **Description**: Creates a new DataFrame by merging old and new dataframes based on a cutoff date.
- **Usage**: `merge_new_and_old(old_df, old_col, new_df, new_col, cutoff_date, date_col_name='OBS')`
- **Example**: `merge_new_and_old(df1, 'old_col', df2, 'new_col', '2023-01-15')`

## 7. `merge_dataframes_on_column`
- **Description**: Merge a list of DataFrames on a common column.
- **Usage**: `merge_dataframes_on_column(dataframes, common_column='OBS', merge_how='outer')`
- **Example**: `merge_dataframes_on_column([df1, df2, df3], common_column='OBS', merge_how='outer')`

## 8. `merge_and_update_dfs`
- **Description**: Merges two dataframes, updating columns from the second dataframe where values are available.
- **Usage**: `merge_and_update_dfs(df1, df2, key_column)`
- **Example**: `merge_and_update_dfs(processed_facebook, finalised_meta, 'OBS')`

## 9. `convert_us_to_uk_dates`
- **Description**: Convert a DataFrame column with mixed US and UK date formats to datetime.
- **Usage**: `convert_us_to_uk_dates(df, date_col)`
- **Example**: `convert_us_to_uk_dates(df, 'date')`

## 10. `combine_sheets`
- **Description**: Combines multiple DataFrames from a dictionary into a single DataFrame.
- **Usage**: `combine_sheets(all_sheets)`
- **Example**: `combine_sheets({'Sheet1': df1, 'Sheet2': df2})`

## 11. `pivot_table`
- **Description**: Dynamically pivots a DataFrame based on specified columns.
- **Usage**: `pivot_table(df, index_col, columns, values_col, filters_dict=None, fill_value=0, aggfunc='sum', margins=False, margins_name='Total', datetime_trans_needed=True, reverse_header_order=False, fill_missing_weekly_dates=False, week_commencing='W-MON')`
- **Example**: `pivot_table(df, 'OBS', 'Channel Short Names', 'Value', filters_dict={'Master Include': ' == 1'}, fill_value=0)`

## 12. `apply_lookup_table_for_columns`
- **Description**: Maps substrings in columns to new values based on a dictionary.
- **Usage**: `apply_lookup_table_for_columns(df, col_names, to_find_dict, if_not_in_dict='Other', new_column_name='Mapping')`
- **Example**: `apply_lookup_table_for_columns(df, col_names, {'spend': 'spd'}, if_not_in_dict='Other', new_column_name='Metrics Short')`

## 13. `aggregate_daily_to_wc_wide`
- **Description**: Aggregates daily data into weekly data and pivots it to wide format.
- **Usage**: `aggregate_daily_to_wc_wide(df, date_column, group_columns, sum_columns, wc='sun', aggregation='sum', include_totals=False)`
- **Example**: `aggregate_daily_to_wc_wide(df, 'date', ['platform'], ['cost', 'impressions'], 'mon', 'average', True)`

## 14. `merge_cols_with_seperator`
- **Description**: Merges multiple columns in a DataFrame into one column with a specified separator.
- **Usage**: `merge_cols_with_seperator(df, col_names, separator='_', output_column_name='Merged')`
- **Example**: `merge_cols_with_seperator(df, ['Campaign', 'Product'], separator='|', output_column_name='Merged Columns')`

## 15. `check_sum_of_df_cols_are_equal`
- **Description**: Checks if the sum of two columns in two DataFrames are equal and provides the difference.
- **Usage**: `check_sum_of_df_cols_are_equal(df_1, df_2, cols_1, cols_2)`
- **Example**: `check_sum_of_df_cols_are_equal(df_1, df_2, 'Media Cost', 'Spend')`

## 16. `convert_2_df_cols_to_dict`
- **Description**: Creates a dictionary from two DataFrame columns.
- **Usage**: `convert_2_df_cols_to_dict(df, key_col, value_col)`
- **Example**: `convert_2_df_cols_to_dict(df, 'Campaign', 'Channel')`

## 17. `create_FY_and_H_columns`
- **Description**: Adds financial year and half-year columns to a DataFrame based on a start date.
- **Usage**: `create_FY_and_H_columns(df, index_col, start_date, starting_FY, short_format='No', half_years='No', combined_FY_and_H='No')`
- **Example**: `create_FY_and_H_columns(df, 'Week', '2022-10-03', 'FY2023', short_format='Yes')`

## 18. `keyword_lookup_replacement`
- **Description**: Updates values in a column based on a lookup dictionary with conditional logic.
- **Usage**: `keyword_lookup_replacement(df, col, replacement_rows, cols_to_merge, replacement_lookup_dict, output_column_name='Updated Column')`
- **Example**: `keyword_lookup_replacement(df, 'channel', 'Paid Search Generic', ['channel', 'segment'], lookup_dict, output_column_name='Channel New')`

## 19. `create_new_version_of_col_using_LUT`
- **Description**: Creates a new column based on a lookup table applied to an existing column.
- **Usage**: `create_new_version_of_col_using_LUT(df, keys_col, value_col, dict_for_specific_changes, new_col_name='New Version of Old Col')`
- **Example**: `create_new_version_of_col_using_LUT(df, 'Campaign Name', 'Campaign Type', lookup_dict)`

## 20. `convert_df_wide_2_long`
- **Description**: Converts a wide-format DataFrame into a long-format DataFrame.
- **Usage**: `convert_df_wide_2_long(df, value_cols, variable_col_name='Stacked', value_col_name='Value')`
- **Example**: `convert_df_wide_2_long(df, ['col1', 'col2'], variable_col_name='Var', value_col_name='Val')`

## 21. `manually_edit_data`
- **Description**: Manually updates specified cells in a DataFrame based on filters.
- **Usage**: `manually_edit_data(df, filters_dict, col_to_change, new_value, change_in_existing_df_col='No', new_col_to_change_name='New', manual_edit_col_name=None, add_notes='No', existing_note_col_name=None, note=None)`
- **Example**: `manually_edit_data(df, {'col1': '== 1'}, 'col2', 'new_val', add_notes='Yes', note='Manual Update')`

## 22. `format_numbers_with_commas`
- **Description**: Formats numerical columns with commas and a specified number of decimal places.
- **Usage**: `format_numbers_with_commas(df, decimal_length_chosen=2)`
- **Example**: `format_numbers_with_commas(df, decimal_length_chosen=1)`

## 23. `filter_df_on_multiple_conditions`
- **Description**: Filters a DataFrame based on multiple column conditions.
- **Usage**: `filter_df_on_multiple_conditions(df, filters_dict)`
- **Example**: `filter_df_on_multiple_conditions(df, {'col1': '>= 5', 'col2': '== 'val''})`

## 24. `read_and_concatenate_files`
- **Description**: Reads and concatenates files from a specified folder into a single DataFrame.
- **Usage**: `read_and_concatenate_files(folder_path, file_type='csv')`
- **Example**: `read_and_concatenate_files('/path/to/files', file_type='xlsx')`

## 25. `upgrade_outdated_packages`
- **Description**: Upgrades all outdated Python packages except specified ones.
- **Usage**: `upgrade_outdated_packages(exclude_packages=['twine'])`
- **Example**: `upgrade_outdated_packages(exclude_packages=['pip', 'setuptools'])`

## 26. `convert_mixed_formats_dates`
- **Description**: Converts mixed-format date columns into standardized datetime format.
- **Usage**: `convert_mixed_formats_dates(df, column_name)`
- **Example**: `convert_mixed_formats_dates(df, 'date_col')`

## 27. `fill_weekly_date_range`
- **Description**: Fills in missing weekly dates in a DataFrame with a specified frequency.
- **Usage**: `fill_weekly_date_range(df, date_column, freq='W-MON')`
- **Example**: `fill_weekly_date_range(df, 'date_col')`

## 28. `add_prefix_and_suffix`
- **Description**: Adds prefixes and/or suffixes to column names, with an option to exclude a date column.
- **Usage**: `add_prefix_and_suffix(df, prefix='', suffix='', date_col=None)`
- **Example**: `add_prefix_and_suffix(df, prefix='pre_', suffix='_suf', date_col='date_col')`

## 29. `create_dummies`
- **Description**: Creates dummy variables for columns, with an option to add a total dummy column.
- **Usage**: `create_dummies(df, date_col=None, dummy_threshold=0, add_total_dummy_col='No', total_col_name='total')`
- **Example**: `create_dummies(df, date_col='date_col', dummy_threshold=1)`

## 30. `replace_substrings`
- **Description**: Replaces substrings in a column based on a dictionary, with options for case conversion and new column creation.
- **Usage**: `replace_substrings(df, column, replacements, to_lower=False, new_column=None)`
- **Example**: `replace_substrings(df, 'text_col', {'old': 'new'}, to_lower=True, new_column='updated_text')`

## 31. `add_total_column`
- **Description**: Adds a total column to a DataFrame by summing values across columns, optionally excluding one.
- **Usage**: `add_total_column(df, exclude_col=None, total_col_name='Total')`
- **Example**: `add_total_column(df, exclude_col='date_col')`

## 32. `apply_lookup_table_based_on_substring`
- **Description**: Categorizes text in a column using a lookup table based on substrings.
- **Usage**: `apply_lookup_table_based_on_substring(df, column_name, category_dict, new_col_name='Category', other_label='Other')`
- **Example**: `apply_lookup_table_based_on_substring(df, 'text_col', {'sub1': 'cat1', 'sub2': 'cat2'})`

## 33. `compare_overlap`
- **Description**: Compares overlapping periods between two DataFrames and summarizes differences.
- **Usage**: `compare_overlap(df1, df2, date_col)`
- **Example**: `compare_overlap(df1, df2, 'date_col')`

## 34. `week_commencing_2_week_commencing_conversion_isoweekday`
- **Description**: Maps dates to the start of the current ISO week based on a specified weekday.
- **Usage**: `week_commencing_2_week_commencing_conversion_isoweekday(df, date_col, week_commencing='mon')`
- **Example**: `week_commencing_2_week_commencing_conversion_isoweekday(df, 'date_col', week_commencing='fri')`

---

## Data Processing for Incrementality Testing

## 1. `pull_ga`
- **Description**: Pull in GA4 data for geo experiments.
- **Usage**: `pull_ga(credentials_file, property_id, start_date, country, metrics)`
- **Example**: `pull_ga('GeoExperiment-31c5f5db2c39.json', '111111111', '2023-10-15', 'United Kingdom', ['totalUsers', 'newUsers'])`

## 2. `process_itv_analysis`
- **Description**: Pull in GA4 data for geo experiments.
- **Usage**: `process_itv_analysis(self, raw_df, itv_path, cities_path, media_spend_path, output_path, group1, group2)`
- **Example**: `process_itv_analysis(df, 'itv regional mapping.csv', 'Geo_Mappings_with_Coordinates.xlsx', 'IMS.xlsx', 'itv_for_test_analysis_itvx.csv', ['West', 'Westcountry', 'Tyne Tees'], ['Central Scotland', 'North Scotland'])`

---

## Data Visualisations

## 1. `plot_one`
- **Description**: Plots a specified column from a DataFrame with white background and black axes.
- **Usage**: `plot_one(df1, col1, date_column)`
- **Example**: `plot_one(df, 'sales', 'date')`

## 2. `plot_two`
- **Description**: Plots specified columns from two DataFrames, optionally on the same or separate y-axes.
- **Usage**: `plot_two(df1, col1, df2, col2, date_column, same_axis=True)`
- **Example**: `plot_two(df1, 'sales', df2, 'revenue', 'date', same_axis=False)`

## 3. `plot_chart`
- **Description**: Plots various chart types using Plotly, including line, bar, scatter, area, pie, etc.
- **Usage**: `plot_chart(df, date_col, value_cols, chart_type='line', title='Chart', x_title='Date', y_title='Values')`
- **Example**: `plot_chart(df, 'date', ['sales', 'revenue'], chart_type='line', title='Sales and Revenue')`

---

## Data Pulling

## 1. `pull_fred_data`
- **Description**: Fetch data from FRED using series ID tokens.
- **Usage**: `pull_fred_data(week_commencing, series_id_list)`
- **Example**: `pull_fred_data('mon', ['GPDIC1', 'Y057RX1Q020SBEA', 'GCEC1', 'ND000333Q', 'Y006RX1Q020SBEA'])`

## 2. `pull_boe_data`
- **Description**: Fetch and process Bank of England interest rate data.
- **Usage**: `pull_boe_data(week_commencing)`
- **Example**: `pull_boe_data('mon')`

## 3. `pull_oecd`
- **Description**: Fetch macroeconomic data from OECD for a specified country.
- **Usage**: `pull_oecd(country='GBR', week_commencing='mon', start_date='2020-01-01')`
- **Example**: `pull_oecd('GBR', 'mon', '2000-01-01')`

## 4. `get_google_mobility_data`
- **Description**: Fetch Google Mobility data for the specified country.
- **Usage**: `get_google_mobility_data(country, wc)`
- **Example**: `get_google_mobility_data('United Kingdom', 'mon')`

## 5. `pull_seasonality`
- **Description**: Generate combined dummy variables for seasonality, trends, and COVID lockdowns.
- **Usage**: `pull_seasonality(week_commencing, start_date, countries)`
- **Example**: `pull_seasonality('mon', '2020-01-01', ['US', 'GB'])`

## 6. `pull_weather`
- **Description**: Fetch and process historical weather data for the specified country.
- **Usage**: `pull_weather(week_commencing, country)`
- **Example**: `pull_weather('mon', 'GBR')`

## 7. `pull_macro_ons_uk`
- **Description**: Fetch and process time series data from the Beta ONS API.
- **Usage**: `pull_macro_ons_uk(additional_list, week_commencing, sector)`
- **Example**: `pull_macro_ons_uk(['HBOI'], 'mon', 'fast_food')`

## 8. `pull_yfinance`
- **Description**: Fetch and process time series data from Yahoo Finance.
- **Usage**: `pull_yfinance(tickers, week_start_day)`
- **Example**: `pull_yfinance(['^FTMC', '^IXIC'], 'mon')`

---

## Installation

Install the IMS package via pip:

```bash
pip install imsciences
```

---

## Usage 

```bash
from imsciences import * 
ims_proc = dataprocessing()
ims_geo = geoprocessing()
ims_pull = datapull()
ims_vis = datavis()
```

---

## License

This project is licensed under the MIT License. ![License](https://img.shields.io/badge/license-MIT-blue.svg)

---