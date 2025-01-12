'''
Filter significance in the CSV file
First, evaluate the significance for each entry:

If the left p-value is less than 0.05 and the statistical indicator value is less than 1, 
the relationship is considered significantly repulsive.
If the right p-value is less than 0.05 and the statistical indicator value is greater than 1, 
the relationship is considered significantly attractive.
'''

import re
import csv
import argparse

def process_value(A, p1, p2, a):
    if A == "None":
        return ""  
    
    A = float(A)
    p1 = float(p1)
    p2 = float(p2)

    if (p1 < a and A < 1) or (p2 < a and A > 1):
        return str(A)
    elif (p1 < a and A > 1) or (p2 < a and A < 1):
        return "error"
    else:
        return ""

pattern = re.compile(r"([-\d.eENone]+), \(([-\d.eENone]+), ([-\d.eENone]+)\)")

def sig_csv(input_file_path, a, output_file_path):
    with open(input_file_path, mode='r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        processed_data = [header]
        
        for row in reader:
            new_row = row[:]
            for i, value in enumerate(row):
                if i in [2, 3]:  
                    continue  
                match = pattern.search(value)
                if match:
                    A, p1, p2 = match.groups()
                    new_row[i] = process_value(A, p1, p2,a)
                else:
                    new_row[i] = value  
            processed_data.append(new_row)

    with open(output_file_path, mode='w', newline='', encoding='utf-8-sig') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(processed_data)

    print("The csv is save to:", output_file_path)

def help():
    print("Determine significance level and save to CSV.")
    print("Arguments:")
    print("sta_sig(INPUT_FILE, A, OUTPUT_FILE)")
    print("  <INPUT_FILE>  Path to the LI csv file.")
    print("  <A>  significance level")
    print("  <OUTPUT_FILE>  Path to the output csv file.")
    print("  help  Show this help message and exit.")

def main():

    parser = argparse.ArgumentParser(description='Filter for significance in CSV files')
    parser.add_argument('--input_file', type=str, help='Input CSV file path')
    parser.add_argument('--a', type=float, help='significance level')
    parser.add_argument('--output_file', type=str, help='Output CSV file path')

    args = parser.parse_args()

    with open(args.input_file, mode='r', newline='', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        processed_data = [header]
        
        for row in reader:
            new_row = row[:]
            for i, value in enumerate(row):
                if i in [2, 3]:  
                    continue  
                match = pattern.search(value)
                if match:
                    A, p1, p2 = match.groups()
                    new_row[i] = process_value(A, p1, p2,args.a)
                else:
                    new_row[i] = value  
            processed_data.append(new_row)

    with open(args.output_file, mode='w', newline='', encoding='utf-8-sig') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(processed_data)

    print(f"The local indicators with significant values at {args.a} have been filtered. The output file has been saved to:{args.output_file}")

if __name__ == "__main__":
    main()
