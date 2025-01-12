'''
Calculate the K value for each row of elements based on the distance threshold. The idea here is similar to K-nearest neighbors; 
however, in the KSR calculation, the K elements in each row are equal, while in DLI, the K value is different for each row.

Read the first K elements from each line of the txt file, find the corresponding row in the csv file, and count the event types in these rows. 
Then, compute the relevant indicators and output them to the csv file.

If a row does not contain K elements, the corresponding local indicator value for that row is considered statistically insignificant.
'''
import scipy.stats as stats
import pandas as pd
import csv
from collections import Counter
import time
import argparse

def get_events(csv_file):
    events = []
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            events.append([row['OBJECTID'], row['Type'], row['m_lng'], row['m_lat']])
    return events

def get_types(csv_file):
    type_dict = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            traffic_type = row['Type']
            type_dict[traffic_type] = type_dict.get(traffic_type, 0) + 1
    return type_dict

def get_klist(txt_file, threshold):
    k_list = []
    with open(txt_file, 'r', encoding='utf-8-sig') as f:
        for line in f:
            elements = line.strip().split(';')
            count = sum(1 for element in elements[1:] if float(element.split(',')[1]) < threshold)
            k_list.append(count)
    return k_list

def read_txt(txt_file, csv_file, d):
    results = []
    events = get_events(csv_file)
    k_list = get_klist(txt_file, d)
    with open(txt_file, 'r', encoding='utf-8-sig') as txt:
        for i, line in enumerate(txt):
            elements = line.strip().split(';')
            k = k_list[i]
            code_counter = Counter()
            if len(elements) > k + 1:
                for element in elements[1:k + 1]:
                    index = int(element.split(',')[0])
                    if index < len(events):
                        code = events[index][1]
                        code_counter[code] += 1
            results.append([i, code_counter])
    return results

def cal_p(N, K, n, k):
    p_plus_value = stats.hypergeom.sf(k - 1, N, K, n)
    p_minus_value = stats.hypergeom.cdf(k, N, K, n)
    return p_minus_value, p_plus_value

def cal_dli(txt_file, csv_file, d, event_value_dict):
    results = read_txt(txt_file, csv_file, d)
    events = get_events(csv_file)
    k_list = get_klist(txt_file, d)
    dli_list = []
    total = sum(event_value_dict.values()) - 1
    for i, j in enumerate(results):
        k = k_list[i]
        code_counter = j[1]
        temp = []
        save_list = events[i]
        for event, value in event_value_dict.items():
            obv = code_counter.get(event, 0)
            K1 = event_value_dict[event]
            if save_list[1] == event:
                value -= 1
                K1 -= 1
            p1, p2 = cal_p(total, K1, k, obv)
            exp = k * (value / total) if obv != 0 else 0
            dli = obv / exp if exp != 0 else 0
            temp.append((dli, (p1, p2)))
        save_list.extend(temp)
        dli_list.append(save_list)
    return dli_list

def save_csv(results, output_file, event_value_dict):
    headers = ['OBJECTID', 'Type', 'm_lng', 'm_lat'] + list(event_value_dict.keys())
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(results)

def dli_csv(txt_file, csv_file, d, output_file):
    start_time = time.time()
    type_dict = get_types(csv_file)
    dli_list = cal_dli(txt_file, csv_file, d, type_dict)
    save_csv(dli_list, output_file, type_dict)
    end_time = time.time()
    print(f"The processing time:{end_time - start_time:.2f}s")

def help():
    print("Calculate DLI and p-value, save to CSV.")
    print("Arguments:")
    print("dli_csv(txt_file, csv_file, d, output_file)")
    print("  <txt_file>  Path to the input txt file.")
    print("  <csv_file>  Path to the input csv file.")
    print("  <output_file>  Path to the output csv file.")
    print("  <d>  Threshold distance.")
    print("  help  Show this help message and exit.")

def main():
    # Configure command-line argument parsing.
    parser = argparse.ArgumentParser(description='Calculate DLI and save to CSV.')
 
    # Add command-line parameters.
    parser.add_argument('--txt_file', type=str, required=True, help='Path to the input txt file.')
    parser.add_argument('--csv_file', type=str, required=True, help='Path to the input csv file.')
    parser.add_argument('--d', type=float, required=True, help='Threshold distance.')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output csv file.')

    args = parser.parse_args()

    start_time = time.time()
    type_dict = get_types(args.csv_file)
    # Calculate DLI
    dli_list = cal_dli(args.txt_file, args.csv_file, args.d, type_dict)
    
    # save to CSV
    save_csv(dli_list, args.output_file, type_dict)
    
    end_time = time.time()
    print(f"The processing time:{end_time - start_time:.2f}s")
    print(f"The DLI is save to:{args.output_file}")

if __name__ == '__main__':
    main()
