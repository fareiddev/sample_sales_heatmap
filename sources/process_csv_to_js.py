import pandas as pd
import json
import os

# debug
print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))


def process_sales_data(csv_file_path):
    """
    Processes a sales CSV to generate data for the heatmap visualization.

    This script reads a CSV file containing transaction data, aggregates it by
    day of the week and hour, performs a basic sales analysis, and outputs
    a JavaScript file containing the data in the required format.

    Args:
        csv_file_path (str): The path to the input CSV file. The CSV must
                             contain columns for date, time, and amount.

    Returns:
        str: A string containing the complete content for the 'sales-data.js' file.
    """
    try:
        # Read the CSV file into a pandas DataFrame.
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file '{csv_file_path}' was not found.")
        return None

    # --- 1. Data Cleaning and Preparation ---

    # **FIX:** Standardize column names to be lowercase and stripped of leading/trailing whitespace.
    # This makes the script more robust to variations in the CSV file's header.
    df.columns = [col.strip().lower() for col in df.columns]

    # **FIX:** Dynamically find column names for datetime and amount based on Malay keywords.
    # The script now searches for 'tarikh & masa' for datetime and 'jumlah' for amount.
    try:
        # The user's CSV has a single column for both date and time. We'll look for 'tarikh & masa'.
        datetime_col = next(col for col in df.columns if 'tarikh & masa' in col)
        # The amount column is 'jumlah keseluruhan (rm)'. We'll search for 'jumlah'.
        amount_col = next(col for col in df.columns if 'jumlah' in col)
    except StopIteration:
        print("\n--- ERROR ---")
        print("Could not automatically find columns for datetime ('tarikh & masa') or amount ('jumlah').")
        print(f"The columns found in your CSV are: {list(df.columns)}")
        print("Please ensure your CSV file has columns with these keywords.")
        print("---------------\n")
        return None

    # Convert the found datetime column to datetime objects for time-based analysis.
    df['DateTime'] = pd.to_datetime(df[datetime_col], errors='coerce')

    # Remove any rows where the date could not be parsed.
    df.dropna(subset=['DateTime'], inplace=True)

    # Rename the found amount column to 'Amount' so the rest of the script works as expected.
    df.rename(columns={amount_col: 'Amount'}, inplace=True)

    # If the 'Amount' column is a string (e.g., "$1,234.56"),
    # clean it by removing currency symbols and commas, then convert to a numeric type.
    # This will also handle the '(rm)' in the user's column name.
    if df['Amount'].dtype == 'object':
        df['Amount'] = df['Amount'].replace({r'[^\d.]': ''}, regex=True).astype(float)

    # Extract the day of the week (Monday=0, Sunday=6) and the hour (0-23).
    df['day'] = df['DateTime'].dt.dayofweek
    df['hour'] = df['DateTime'].dt.hour

    # --- 2. Heatmap Data Aggregation ---

    # Group data by day and hour, then sum the sales amount for each group.
    heatmap_data_df = df.groupby(['day', 'hour'])['Amount'].sum().reset_index()
    heatmap_data_df.rename(columns={'Amount': 'sales'}, inplace=True)

    # Convert the aggregated DataFrame to a list of dictionaries for JSON.
    heatmap_data_list = heatmap_data_df.to_dict(orient='records')

    # Round the sales figures to two decimal places.
    for item in heatmap_data_list:
        item['sales'] = round(item['sales'], 2)

    # --- 3. Critical Sales Analysis ---

    total_sales = df['Amount'].sum()
    total_transactions = len(df)
    avg_transaction_value = total_sales / total_transactions if total_transactions > 0 else 0

    # Determine the best and worst day by total sales.
    daily_sales = df.groupby('day')['Amount'].sum()
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    best_day_name = days_of_week[daily_sales.idxmax()] if not daily_sales.empty else "N/A"
    worst_day_name = days_of_week[daily_sales.idxmin()] if not daily_sales.empty else "N/A"

    # Determine the peak hour by total sales across all days.
    hourly_sales = df.groupby('hour')['Amount'].sum()
    peak_hour_index = hourly_sales.idxmax() if not hourly_sales.empty else -1
    
    # **FIX:** Use a cross-platform compatible way to format the peak hour.
    # The `%-I` directive is not supported on all systems (e.g., Windows).
    # We now use `%I` and then remove the leading zero if it exists.
    if peak_hour_index != -1:
        peak_hour_time = pd.to_datetime(f'{peak_hour_index}:00:00').strftime('%I:%M %p')
        if peak_hour_time.startswith('0'):
            peak_hour_time = peak_hour_time[1:]
    else:
        peak_hour_time = "N/A"


    # --- 4. Construct Final Data Structure ---

    final_data_structure = {
        "heatmap_data": heatmap_data_list,
        "analysis": {
            "total_sales": round(total_sales, 2),
            "total_transactions": total_transactions,
            "avg_transaction_value": round(avg_transaction_value, 2),
            "best_day": best_day_name,
            "worst_day": worst_day_name,
            "peak_hour": peak_hour_time
        }
    }

    # --- 5. Generate JavaScript File Content ---

    # Convert the Python dictionary into a nicely formatted JSON string.
    json_data = json.dumps(final_data_structure, indent=4)

    # Wrap the JSON in the JavaScript export statement.
    js_content = f"""// sales-data.js

// By placing the data in its own file, you can easily update it
// without changing the main application logic.
// The 'export' keyword makes this data available to other JavaScript files.

export const salesData = {json_data};
"""
    return js_content


# --- Main execution block ---
if __name__ == "__main__":
    # Define the name of your input CSV file.
    # This should be in the same directory as your script, or provide a full path.
    input_csv_file = "RK sales-report_20250622.csv"
    output_js_file = "sales-data.js"

    # Run the processing function.
    javascript_code = process_sales_data(input_csv_file)

    # Save the generated JavaScript code to the output file.
    if javascript_code:
        try:
            with open(output_js_file, "w") as f:
                f.write(javascript_code)
            print(f"Successfully created '{output_js_file}'.")
        except IOError as e:
            print(f"An error occurred while writing the file: {e}")
