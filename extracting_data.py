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
    
    #print(pr)
    # dict from name of login of requested reviewer -> time review should be done
    requested_reviews: Dict[str, arrow.Arrow] = {}
     
    # raw data transformation step
    for item in pr['timelineItems']['nodes']:
        # transform all datetime strings into localized arrow datetime objects
        if 'createdAt' in item:
            item['createdAt'] = arrow.get(item['createdAt']).to(args.tz)
        if 'submittedAt' in item:
            item['submittedAt'] = arrow.get(item['submittedAt']).to(args.tz)
        n_nodes +=1
    # computation step
    for item in pr['timelineItems']['nodes']:
        typename = item['__typename']
        time_due=None
        if typename == 'ReviewRequestedEvent':
            if item['requestedReviewer'] is not None: 
                if not 'login' in item['requestedReviewer']:
                    continue

                reviewer = item['requestedReviewer']['login']
                #print('************')
                #print(time_due)

                time_due = get_due_time(item['createdAt'])
                #print(item['createdAt'])
                time_due2=  midday(item['createdAt'].shift(days=+days_until_next_business_day(item['createdAt'].weekday())+2,))
                time_due3=  midday(item['createdAt'].shift(days=+days_until_next_business_day(item['createdAt'].weekday())+5,))
                time_due4=  midday(item['createdAt'].shift(days=+days_until_next_business_day(item['createdAt'].weekday())+30,))
                #time_due = get_due_time(item['createdAt'])
               # print(type(time_due))
                requested_reviews[reviewer] = [time_due,time_due2,time_due3,time_due4]

               # exit(1)
    #            print(typename)
        elif typename == 'PullRequestReview':
            if  item['author'] is  None:
                print(item['author'])
            time = item['submittedAt']
            if item['author'] is not None:
                reviewer = item['author']['login']

                if reviewer in requested_reviews:
                    time_due_tab = requested_reviews[reviewer]
                   # print('----')
                    #print(type(time_due_tab[0]))
                    #print(time_due_tab)
                    #print(type(time))
                    #print('--------')
                    v=time_due_tab[0]
                    if (time<=time_due_tab[0]):
                        reviews.append(Review(reviewer, ReviewStatus.ON_TIME, v.isoformat()))
                    else: 
                        if time <= time_due_tab[1]:
                            reviews.append(Review(reviewer, ReviewStatus.LATE24, time_due_tab[1].isoformat()))
                        else: 
                            if time <= time_due_tab[2]:
                                reviews.append(Review(reviewer, ReviewStatus.LATE72, time_due_tab[2].isoformat()))
                            else:
                                if time <= time_due_tab[3]:
                                    reviews.append(Review(reviewer, ReviewStatus.LATE1M, time_due_tab[3].isoformat()))
                                else:
                                    reviews.append(Review(reviewer, ReviewStatus.TOOLATE, time_due_tab[3].isoformat()))

                    requested_reviews.pop(reviewer, None)
                else:
                    # someone submitted a review even though nobody requested it
                    # we don't need to do anything in this case
                    N_Rev_no_req +=1
                    pass

                #exit(1)
        elif typename == 'ReviewRequestRemovedEvent':
            if item['requestedReviewer'] is not None: 
                if not 'login' in item['requestedReviewer']:
                    continue

                reviewer = item['requestedReviewer']['login']
                time = item['createdAt']

                if reviewer in requested_reviews:
                    time_due_tab = requested_reviews[reviewer]

                    # request for review was removed, *but* it is already after when the review should've been completed
                    if time > time_due_tab[3]:
                        reviews.append(Review(reviewer, ReviewStatus.RTOOLATE, time_due_tab[3].isoformat()))
                    else:    
                        if time > time_due_tab[2]:
                            reviews.append(Review(reviewer, ReviewStatus.RLATELess1M, time_due_tab[2].isoformat()))
                        else:
                            if time > time_due_tab[1]:
                                reviews.append(Review(reviewer, ReviewStatus.RLATELess72h, time_due_tab[1].isoformat()))
                    # request for review was removed, before when the review should've been completed
                            else:
                                if time > time_due_tab[0]:
                                    reviews.append(Review(reviewer, ReviewStatus.RLATELess24h, time_due_tab[0].isoformat()))

                                else: 
                                    reviews.append(Review(reviewer, ReviewStatus.REMOVED, time_due_tab[0].isoformat()))

                    requested_reviews.pop(reviewer, None)
                else:
                    # unusual state we don't expect to ever happen:
                    print(f"Review request removed but reviewer #{reviewer} not found", file=sys.stderr)

        elif typename in ['ClosedEvent', 'MergedEvent']:
            time = item['createdAt']

            # for every requested review when the PR is closed, see if it should've been completed yet or not
            for reviewer, time_due in requested_reviews.items():
               # if time > time_due:
                #    reviews.append(Review(reviewer, ReviewStatus.LATE, time_due.isoformat()))
                #else:
                 #   reviews.append(Review(reviewer, ReviewStatus.NO_RESPONSE, time_due.isoformat()))
                    
                    #..
                if time > time_due_tab[3]:
                    reviews.append(Review(reviewer, ReviewStatus.CoMTOOLATE, time_due_tab[3].isoformat()))
                else:    
                    if time > time_due_tab[2]:
                        reviews.append(Review(reviewer, ReviewStatus.CoMLATELess1M, time_due_tab[2].isoformat()))
                    else:
                        if time > time_due_tab[1]:
                            reviews.append(Review(reviewer, ReviewStatus.CoMLATELess72h, time_due_tab[1].isoformat()))
                  
                        else:
                            if time > time_due_tab[0]:
                                reviews.append(Review(reviewer, ReviewStatus.CoMLATELess24h, time_due_tab[0].isoformat()))
                
                            else: 
                                reviews.append(Review(reviewer, ReviewStatus.CoMNoRev, time_due_tab[0].isoformat()))

                #..

        else:
            print(f"Unknown type: {typename}", file=sys.stderr)

# TODO: we should handle review requests that are still open, on an open PR, without a response
# this is slightly trickier because we may need to depend on the system time of the user to tell if the review is late
print(len(data))
#print(n_nodes)
print(N_Rev_no_req)


print(len(reviews))


output_file = open(args.output_file, 'w') if args.output_file else sys.stdout
output_file.write(json.dumps([review._asdict() for review in reviews], indent=2) + "\n")







#print('_---------------_')

#for i in reviews:
    #print(i)