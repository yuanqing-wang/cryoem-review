import pandas as pd

df = pd.DataFrame()

f_handle = open('emdb_summary.csv', 'r')


idx = 0
to_append = []
for line in f_handle:
    to_append.append(line.split('\t')[1])
    if idx == 10:
        to_append = [to_append]
        df = df.append(to_append)
        to_append = []
        idx = 0

df.to_csv('emdb_summary_.csv', sep='\t')
