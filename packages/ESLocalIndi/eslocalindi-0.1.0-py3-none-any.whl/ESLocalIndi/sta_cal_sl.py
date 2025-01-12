import pandas as pd
import argparse
import csv
import argparse

def load_data(file_path):
    return pd.read_csv(file_path)

def calculate_statistics(df,i):
    for col in df.columns[i:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    categories = df['Type'].unique()
    
    result_dict = {category: {} for category in categories}
    
    for category in categories:
        filtered_df = df[df['Type'] == category]
        total_count = len(filtered_df)
        for col in df.columns[4:]:  
            count_ge_1 = (filtered_df[col] >= 1).sum()
            #print(total_count)
            result_dict[category][col] = count_ge_1 / total_count if total_count > 0 else 0
    result_matrix = pd.DataFrame.from_dict(result_dict, orient='index')
    return result_matrix

def save_results(matrix, output_file):
    matrix.to_csv(output_file)

def sl_csv(input_file, i, output_file):
    df = load_data(input_file)
    result_matrix = calculate_statistics(df,i)
    save_results(result_matrix, output_file)
    print(f'The result is save to: {output_file}')

def help():
    print("Calculate statistics from CSV file.")
    print("Arguments:")
    print("cal_sl_csv(input_file, i, output_file)")
    print("  <input_file>  Path to the input CSV file.")
    print("  <output_file>  Path to save the output CSV file.")
    print("  <i>  Start from the i-th column in the CSV.")
    print("  help  Show this help message and exit.")

def main():
    parser = argparse.ArgumentParser(description='Calculate statistics from CSV file.')
    parser.add_argument('--input_file', type=str, help='Path to the input_file.')
    parser.add_argument('--i', type=int, help='The local indicator start from the i-th column in the CSV.')
    parser.add_argument('--output_file', type=str, help='Path to the output csv file.')
    
    args = parser.parse_args()

    df = load_data(args.input_file)
    result_matrix = calculate_statistics(df,args.i)
    save_results(result_matrix, args.output_file)
    print(f'The SL is save to: {args.output_file}')

if __name__ == '__main__':
    main()