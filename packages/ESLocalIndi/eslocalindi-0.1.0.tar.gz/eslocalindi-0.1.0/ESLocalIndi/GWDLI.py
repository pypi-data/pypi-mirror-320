'''
Weighting based on DLI
'''
import scipy.stats as stats
import pandas as pd
import csv
from collections import Counter
import numpy as np
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
            count = 0
            d_list = []
            if len(elements) > 1:
                for element in elements[1:]:
                    dis = float(element.split(',')[1])
                    if dis < threshold:
                        count += 1
                        d_list.append(dis)
            k_list.append([count, d_list])
    return k_list

def cal_weight(d_list, d):
    return [np.exp(-0.5 * (i**2 / d**2)) for i in d_list]

def read_txt(txt_file, csv_file, d):
    results = []
    events = get_events(csv_file)
    k_list = get_klist(txt_file, d)
    with open(txt_file, 'r', encoding='utf-8-sig') as txt:
        for i, line in enumerate(txt):
            elements = line.strip().split(';')
            k = k_list[i][0]
            code_counter = Counter()
            weight = Counter()
            if len(elements) > k + 1:
                w_list = cal_weight(k_list[i][1], d)
                for j, element in enumerate(elements[1:k + 1]):
                    index = int(element.split(',')[0])
                    if index < len(events):
                        code = events[index][1]
                        code_counter[code] += 1
                        weight[code] += w_list[j]
            results.append([i, code_counter, weight])
    return results

def cal_p(N, K, n, k):
    p_plus_value = stats.hypergeom.sf(k - 1, N, K, n)
    p_minus_value = stats.hypergeom.cdf(k, N, K, n)
    return p_minus_value, p_plus_value

def cal_gwdli(txt_file, csv_file, d, event_value_dict):
    results = read_txt(txt_file, csv_file, d)
    events = get_events(csv_file)
    k_list = get_klist(txt_file, d)
    DLI_list = []
    total = sum(event_value_dict.values()) - 1
    for i, j in enumerate(results):
        k = k_list[i][0]
        code_counter = j[1]
        weight = j[2]
        w_k = sum(weight.values())
        temp = []
        save_list = events[i]
        for event, value in event_value_dict.items():
            obv = code_counter.get(event, 0)
            w = weight.get(event, 0)
            K1 = event_value_dict[event]
            if save_list[1] == event:
                value -= 1
                K1 -= 1
            p1, p2 = cal_p(total, K1, k, obv)
            exp = w_k * (value / total) if w != 0 else 0
            gwdli = w / exp if exp != 0 else 0
            temp.append((gwdli, (p1, p2)))
        save_list.extend(temp)
        DLI_list.append(save_list)
    return DLI_list

def save_csv(results, output_file, event_value_dict):

    headers = ['OBJECTID', 'Type', 'm_lng', 'm_lat'] + list(event_value_dict.keys())
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(results)

def gwdli_csv(txt_file, csv_file, d, output_file):
    start_time = time.time()
    type_dict = get_types(csv_file)
    #print(type_dict)
    gwdli_list = cal_gwdli(txt_file, csv_file, d, type_dict)
    save_csv(gwdli_list, output_file, type_dict)
    end_time = time.time()
    print(f"The processing time:{end_time - start_time:.2f}s")

def help():
    print("Calculate GWDLI and p-value, save to CSV.")
    print("Arguments:")
    print("gwdli_csv(txt_file, csv_file, d, output_file)")
    print("  <txt_file>  Path to the input txt file.")
    print("  <csv_file>  Path to the input csv file.")
    print("  <output_file>  Path to the output csv file.")
    print("  <d>  Threshold distance.")
    print("  help  Show this help message and exit.")


def main():
    # Configure command-line argument parsing.
    parser = argparse.ArgumentParser(description='Calculate GWDLI and save to CSV.')
    
    # Add command-line parameters.
    parser.add_argument('--txt_file', type=str, required=True, help='Path to the input txt file.')
    parser.add_argument('--csv_file', type=str, required=True, help='Path to the input csv file.')
    parser.add_argument('--d', type=float, required=True, help='Threshold distance.')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output csv file.')

    args = parser.parse_args()

    start_time = time.time()

    type_dict = get_types(args.csv_file)
    gwdli_list = cal_gwdli(args.txt_file, args.csv_file, args.d, type_dict)

    # save to CSV
    save_csv(gwdli_list, args.output_file, type_dict)
 
    end_time = time.time()
    print(f"The processing time:{end_time - start_time:.2f}s")
    print(f"The GWDLI is save to:{args.output_file}")

if __name__ == '__main__':
    main()