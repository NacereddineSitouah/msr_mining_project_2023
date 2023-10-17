import argparse
import json
import sys
from collections import defaultdict, namedtuple
from datetime import datetime
from typing import Dict, DefaultDict, NamedTuple, List

import arrow

from  dateutil import *
from lib.date_utils import *
from lib.models import *

n_nodes=0
N_Rev_no_req=0
#def get_due_time(request_time):
 # if request_time < midday(request_time):
 #   return endofday(request_time)
 # next_business_day = request_time.shift(
 #   days=+days_until_next_business_day(request_time.weekday()),
 # )
 # return midday(next_business_day)
#def is_review_on_time(request_time, review_time):
#  return review_time <= get_due_time(request_time)


tot=0

parser = argparse.ArgumentParser(
    description="Parses the output of download_data.py into a list of reviews and their status, either 'on_time', 'late', or 'no_response'"
)
parser.add_argument("-f", "--input-file", help="file to parse; if omitted uses stdin")
parser.add_argument("-o", "--output-file", help="file to output; if omitted uses stdout")
parser.add_argument("-tz", default="America/Los_Angeles", help="timezone to use for calculating business hours for review status")
args = parser.parse_args()

if args.input_file:
    with open(args.input_file, 'r') as f:
        data = json.load(f)
else:
    data = json.load(sys.stdin)

reviews: List[Review] = []
#reviews=[]
for pr in data:
    # dict from name of login of requested reviewer -> time review should be done
    #requested_reviews: Dict[str, arrow.Arrow] = {}
    j=0
    # raw data transformation step
    for item in pr['timelineItems']['nodes']:
        # transform all datetime strings into localized arrow datetime objects
        if item['__typename'] == "PullRequestReview":
            j=1
            
            
    if (j!=0): 
        tot+=1
        
        
print(tot)
            