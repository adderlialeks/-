#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
from pathlib import Path

def load_gene_cards_csv(csv_path):
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def filter_protein_coding(data):
    return [row for row in data if row.get('Category') == 'Protein Coding']

def add_extra_splicing_genes(extra_symbols, top_list, existing_symbols):
    for sym in extra_symbols:
        if sym not in existing_symbols:
            new_row = {
                'Gene Symbol': sym,
                'Description': 'Added manually (splicing factor)',
                'Category': 'Protein Coding',
                'Uniprot ID': '',
                'Gifts': '',
                'GC Id': '',
                'Relevance score': '0',
                'GeneCards Link': ''
            }
            top_list.append(new_row)
            existing_symbols.add(sym)
    return top_list

def main():
    input_file = "GeneCards-SearchResults.csv"
    output_file = "filtered_genes.txt"
    top_n = 200
    splicing_factors = [
        "SRSF1", "SRSF2", "SRSF3", "SRSF6", "SRSF7", "SRSF9",
        "PTBP1", "HNRNPA1", "HNRNPH1", "HNRNPK", "LSM2", "SF3B1",
        "RBM10", "RBM5", "RBM6", "TRA2A", "TRA2B", "SRSF5"
    ]

    raw_data = load_gene_cards_csv(input_file)
    print(f"Прочитано строк: {len(raw_data)}")

    protein_coding = filter_protein_coding(raw_data)
    print(f"После фильтра по Category (Protein Coding): {len(protein_coding)}")

    if not protein_coding:
        print("Нет белок-кодирующих генов. Проверьте название колонки 'Category'.")
        sys.exit(1)

    unique_genes = {}
    for row in protein_coding:
        sym = row['Gene Symbol']
        try:
            score = float(row['Relevance score']) if row['Relevance score'] else 0.0
        except ValueError:
            score = 0.0
        if sym not in unique_genes or score > unique_genes[sym]['Relevance score']:
            unique_genes[sym] = row
            unique_genes[sym]['Relevance score'] = score

    print(f"Уникальных генов после удаления дубликатов: {len(unique_genes)}")

    sorted_genes = sorted(unique_genes.values(), key=lambda x: x['Relevance score'], reverse=True)
    top_genes = sorted_genes[:top_n]
    existing_symbols = {row['Gene Symbol'] for row in top_genes}
    print(f"Топ-{top_n} генов (до добавления сплайсинговых факторов): {len(top_genes)}")

    top_genes = add_extra_splicing_genes(splicing_factors, top_genes, existing_symbols)
    print(f"После добавления сплайсинговых факторов: {len(top_genes)}")

    with open(output_file, 'w', encoding='utf-8') as f:
        for row in top_genes:
            f.write(row['Gene Symbol'] + '\n')

    print(f"Список сохранён в {output_file}")

    full_output = "top_genes_full.csv"
    with open(full_output, 'w', encoding='utf-8', newline='') as f:
        if top_genes:
            fieldnames = top_genes[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(top_genes)
    print(f"Полная таблица топ-генов сохранена в {full_output}")

if __name__ == '__main__':
    main()
