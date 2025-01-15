import pandas as pd
# first code
def calculate_filtered_sum(file_path, column_name, filter_value):
    try:
        # Load the dataset
        data = pd.read_csv(file_path)
        
        # Filter the data
        filtered_data = data[data[column_name] > filter_value]
        
        # Calculate the sum
        total_sum = filtered_data[column_name].sum()
        
        # Print the result
        print(f"Sum: {total_sum}")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except KeyError:
        print(f"Error: The column {column_name} does not exist in the dataset.")

# second code
def calculate_mean_median(file_path, column_name):
    try:
        # Load the dataset
        df = pd.read_csv(file_path)
        
        # Calculate mean and median of a column
        mean_value = df[column_name].mean()
        median_value = df[column_name].median()
        
        # Print the results
        print(f"Mean: {mean_value}, Median: {median_value}")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except KeyError:
        print(f"Error: The column {column_name} does not exist in the dataset.")        