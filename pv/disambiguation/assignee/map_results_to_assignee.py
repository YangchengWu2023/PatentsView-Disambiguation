import pickle
import pandas as pd
from collections import defaultdict
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="aeolus"
)
mycursor = mydb.cursor()
mycursor.execute("USE granted")
mycursor.execute("SELECT * FROM granted.rawassignee LIMIT 100000;")
mid2org = {}
for i in mycursor:
    patent_id, organization, sequence = i[1], i[7], i[8]
    mention_id = '{}-{}'.format(patent_id, sequence)
    mid2org[mention_id] = organization if organization is not None else ''
mycursor.close()
mydb.close()
# with open('data/assignee/assignee_mentions.assignee_mentions.pkl', 'rb') as f:
with open('/home/ubuntu/workspace/PatentsView-Disambiguation/exp_out/assignee/1m/assignee.records.pkl', 'rb') as f:
    ams = pickle.load(f)
# import pdb
# pdb.set_trace()
results = pd.read_csv('/home/ubuntu/workspace/PatentsView-Disambiguation/output/assignee/mini/disambiguation.tsv', sep='\t', encoding='utf-8')
results.columns = ['mention_id', 'cluster_uuid']
cluster2mid = defaultdict(list)
for index, row in results.iterrows():
    cluster2mid[row[1]].append(row[0])
# results.
with open('/home/ubuntu/workspace/PatentsView-Disambiguation/output/assignee/results.csv', 'w') as f:
    for mention_cluster in cluster2mid.values():
        tmp = set()
        for mention_id in mention_cluster:
            tmp.add(mid2org.get(mention_id, '#').strip())
        s = str(tmp)
        if len(s.strip()) == 0:
            continue
        else:
            f.write(s + '\n')

# results['organization'] = results.apply(lambda x: ams[x['uuid']].organization, axis=1)


def get_master_name(group):
    """
    a group contains the same uuid
    pick the first name in the group as the mastername
    """
    master_name = group['organization'].values.tolist()[0]
    group['standard_name'] = master_name
    return group

# results = results.groupby('uuid').apply(get_master_name)

# results.to_csv('/home/ubuntu/workspace/PatentsView-Disambiguation/output/assignee/results.csv', index=False)