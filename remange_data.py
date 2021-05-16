#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import csv
import pandas as pd
h_r_t_name = [":Entity", "role", ":Entity_1"]
h_r_t = pd.read_table("../data/row_data.txt", sep=',', names=h_r_t_name)  # 读取三元组
print(h_r_t.info())
print(h_r_t.head())

entity = set(h_r_t[':Entity'].tolist() + h_r_t[':Entity_1'].tolist())
w_entity = csv.writer(open("../data/entity.csv", "w", newline='', encoding='utf-8'))
w_entity.writerow(("entity:ID", "name", ":LABEL"))
entity = list(entity)
entity_dict = {}
for i in range(len(entity)):
    w_entity.writerow(("e" + str(i), entity[i], "_entity"))
    entity_dict[entity[i]] = "e" + str(i)
h_r_t[':Entity'] = h_r_t[':Entity'].map(entity_dict)
h_r_t[':Entity_1'] = h_r_t[':Entity_1'].map(entity_dict)
h_r_t[":TYPE"] = h_r_t['role']
h_r_t.pop('role')
h_r_t.to_csv("../data/roles.csv", index=False)