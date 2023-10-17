import argparse
import json
import sys
from collections import defaultdict, namedtuple
from datetime import datetime
from typing import Dict, DefaultDict, NamedTuple, List

import chartify
import pandas as pd

from lib.models import *

actif_totals=0
C_or_M_totals=0
R_totals=0
parser = argparse.ArgumentParser(description='Analyzes the output of parse_data.py and generates visualizations')
parser.add_argument('output_filename', help='filename for the generated chart')
parser.add_argument('-f', '--input-file', help='file to analyze; if omitted uses stdin')
parser.add_argument('-g', '--group-file', help='json file specifying a mapping from group to list of users')
parser.add_argument(
    '--goal', type=int, default=75, help='integer, from 0 to 100, representing the desired percent of on-time reviews'
)
parser.add_argument(
    '--min-reviews',
    type=int,
    default=150,
    help='integer, representing the min number of reviews a user must have to show up in the chart'
)
args = parser.parse_args()
 
print('********************************')
if args.input_file:
    with open(args.input_file, 'r') as f:
        data = json.load(f)
else:
    data = json.load(sys.stdin)

if args.group_file:
    with open(args.group_file, 'r') as f:
        group_to_users = json.load(f)


# Create a `Reviews` object for each user

reviews_by_user: DefaultDict[str, Reviews] = defaultdict(lambda: Reviews())
#print(type(reviews_by_user))
#print(reviews_by_user)
for row in data:
    #print(row)
    reviews = reviews_by_user[row['reviewer']]
    if row['status'] == ReviewStatus.ON_TIME: 
        reviews.on_time += 1
    if row['status'] == ReviewStatus.LATE24:
        reviews.late24 += 1
    if row['status'] == ReviewStatus.LATE72:
        reviews.late72 += 1
    if row['status'] == ReviewStatus.LATE1M:
        reviews.late1m += 1
    if row['status'] == ReviewStatus.TOOLATE:
        reviews.toolate += 1

    if row['status'] == ReviewStatus.CoMNoRev: 
        reviews.comnorev += 1
    if row['status'] == ReviewStatus.CoMLATELess24h:
        reviews.comlateless24h += 1
    if row['status'] == ReviewStatus.CoMLATELess72h:
        reviews.comlateless72h += 1
    if row['status'] == ReviewStatus.CoMLATELess1M:
        reviews.comlateless1m += 1
    if row['status'] == ReviewStatus.CoMTOOLATE:
        reviews.comtoolate += 1
                     
    if row['status'] == ReviewStatus.REMOVED: 
        reviews.removed += 1
    if row['status'] == ReviewStatus.RLATELess24h:
        reviews.rlateless24h += 1
    if row['status'] == ReviewStatus.RLATELess72h:
        reviews.rlateless72h += 1
    if row['status'] == ReviewStatus.RLATELess1M:
        reviews.rlateless1m += 1
    if row['status'] == ReviewStatus.RTOOLATE:
        reviews.rtoolate += 1

# create a data frame with a user, team, and on_time_ratio column
users, on_time_ratios = zip(
    *((k, v.on_time_ratio) for (k, v) in reviews_by_user.items() if v.Total >= args.min_reviews)
)

users, on_time, late24,late72, late1m,toolate = zip(
    *((k, v.on_time*100/v.total,v.late24*100/v.total,v.late72*100/v.total,v.late1m*100/v.total,v.toolate*100/v.total) for (k, v) in reviews_by_user.items() if v.Total >= args.min_reviews)
)
#elf.on_time + self.late24 + self.late72 +    self.late1m + self.toolate
#print (users,on_time_ratios)
#print the totals for each reviewr: 
print(users, on_time, late24,late72, late1m,toolate )


print('------------------------------------')
users, on_time, late24,late72, late1m,toolate = zip(
    *((k, v.comnorev*100/v.total_CoM,v.comlateless24h*100/v.total_CoM,v.comlateless72h*100/v.total_CoM,v.comlateless1m*100/v.total_CoM,v.comtoolate*100/v.total_CoM) for (k, v) in reviews_by_user.items() if v.Total >= args.min_reviews)
)
print(users, on_time, late24,late72, late1m,toolate )
#self.comnorev + self.comlateless24h + self.comlateless72h + self.comlateless1m +  self.comtoolate

 #total_R(self): 
   # return  self.removed +self.rlateless24h+  self.rlateless72h +self.rlateless1m + self.rtoolate 

print('------------------------------------')
users, on_time, late24,late72, late1m,toolate = zip(
    *((k, v.removed*100/v.total_R,v.rlateless24h*100/v.total_R,v.rlateless72h*100/v.total_R,v.rlateless1m*100/v.total_R,v.rtoolate*100/v.total_R) for (k, v) in reviews_by_user.items() if v.Total >= args.min_reviews)
)
print(users, on_time, late24,late72, late1m,toolate )





#print(len(users)*100/len(reviews_by_user.items()))
for (k,v) in reviews_by_user.items():
    actif_totals+=v.total
    C_or_M_totals+=v.total_CoM
    R_totals+=v.total_R
    #print(k,v.Total)
tt=  actif_totals+  C_or_M_totals+R_totals

#print(users)
#print(on_time_ratios)
#print(sum(on_time_ratios)*100/len(data))

#sums of reviews by time with ratios: 
#print("total sum of reviews in normal state:", actif_totals, "(", (actif_totals*100/tt) ,"%)")
#print("total sum of reviews after PR closed or merged:", C_or_M_totals, "(", (C_or_M_totals*100/tt) ,"%)")   
#print("total sum of reviews after PR removed:", R_totals, "(", (R_totals*100/tt) ,"%)")   
user_to_group = {}
if args.group_file:
    for k, v in group_to_users.items():
        for x in v:
            user_to_group[x] = k
            
groups = [user_to_group.get(user, 'Other') for user in users]
#print(groups)
#print(users)
#print(on_time_ratios)
data_frame = pd.DataFrame({
    'user': users,
    'on_time_ratio': on_time_ratios,
    'group': groups,
})


# create the chart of our results
ch = chartify.Chart(blank_labels=True, x_axis_type='categorical')
ch.set_title('On-time review rate')

ch.plot.bar(
    data_frame=data_frame,
    categorical_columns=(['group', 'user'] if args.group_file else ['user']),
    numeric_column='on_time_ratio',
    **({'color_column': 'group'} if args.group_file else {}),
).callout.line(
    args.goal / 100,
    line_dash='dashed',
)

ch.axes.set_yaxis_range(0, 1)
ch.axes.set_yaxis_tick_format('0%')
ch.axes.set_xaxis_tick_orientation(['diagonal', 'horizontal'])
ch.save(args.output_filename)






# create the chart of our results22222222222222222
ch2 = chartify.Chart(blank_labels=True, x_axis_type='categorical')
ch2.set_title('On-time review rate2')

ch2.plot.bar(
    data_frame=data_frame,
    categorical_columns=(['group', 'user'] if args.group_file else ['user']),
    numeric_column='on_time_ratio',
    **({'color_column': 'group'} if args.group_file else {}),
).callout.line(
    args.goal / 100,
    line_dash='dashed',
)

ch2.axes.set_yaxis_range(0, 1)
ch2.axes.set_yaxis_tick_format('0%')
ch2.axes.set_xaxis_tick_orientation(['diagonal', 'horizontal'])
#ch2.save(args.output_filename)

print('...')
#print(ch)
#ch.show('png')

