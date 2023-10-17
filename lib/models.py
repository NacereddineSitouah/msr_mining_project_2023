from typing import Dict, DefaultDict, NamedTuple, List
from enum import Enum

class StrEnum(str, Enum):
    pass

class ReviewStatus(StrEnum):
  ON_TIME = 'on_time'
  #LATE = 'late'
  LATE24 = '24_hours_late'
  LATE72 = '72_hours_late'
  LATE1M = '1Month_late'
  TOOLATE = 'More_than_one_month_late'
  CoMTOOLATE = 'More_than_a_Month_late_with_merge_or_PRR_closed'  
  CoMLATELess1M = 'Less_than_a_Month_late_with_merge_or_PRR_closed' 
  CoMLATELess72h = 'Less_than_72h_late_with_merge_or_PRR_closed' 
  CoMLATELess24h = 'Less_than_24h_late_with_merge_or_PRR_closed' 
  CoMNoRev = 'CoM_without_Review_OnTime' 
  RTOOLATE = 'More_than_a_Month_late_PR_Removed' 
  RLATELess1M = 'Less_than_a_Month_late_with__PR_Removed' 
  RLATELess72h = 'Less_Than_72h_late_with__PR_Removed' 
  RLATELess24h = 'Less_than_24h_late_with__PR_Removed' 
  REMOVED = 'Removed_with_Review_onTime'

class Review(NamedTuple):
  reviewer: str
  status: ReviewStatus
  time_due: str

class Reviews:
  def __init__(self):
    self.on_time = 0
    self.late24 = 0
    self.late72=0
    self.late1m=0
    self.toolate=0
    
    self.no_response = 0 
    
    self.comnorev = 0
    self.comlateless24h = 0
    self.comlateless72h = 0 
    self.comlateless1m = 0 
    self.comtoolate = 0
    
    self.removed = 0
    self.rlateless24h = 0
    self.rlateless72h = 0 
    self.rlateless1m = 0 
    self.rtoolate = 0


  @property
  def total(self):
    return self.on_time + self.late24 + self.late72 +    self.late1m + self.toolate


  @property
  def total_R(self): 
    return  self.removed +self.rlateless24h+  self.rlateless72h +self.rlateless1m + self.rtoolate 
  
  
  @property
  def total_CoM(self): 
    return  self.comnorev + self.comlateless24h + self.comlateless72h + self.comlateless1m +  self.comtoolate

  @property
  def Total(self): 
    return  self.total + self.total_R + self.total_CoM
 

  @property
  def on_time_ratio(self):
    if not self.on_time and not self.late24 and not self.late72:
      return 0
    return self.on_time / (self.on_time + self.late24+self.late72)

  @property
  def late_ratio(self):
    if not self.on_time and not self.late24:
      return 0
    return self.late24+self.late72 / (self.on_time + self.late24 + self.late72)

  @property
  def no_response_ratio(self):
    if not self.total:
      return 0
    return self.no_response / self.total

 
  @property
  def totals(self):
    return "total: {:>6}; total Closed or merg: {:>6}; total removed: {:6>} ------> Total is : {:>6}".format(
      self.total, self.total_CoM, self.total_R, self.Total )



  def __str__(self):
    return "total: {:>6}; on_time: {:>4} ({:5.2%}); late24: {:>4} ({:7.2%}); late72: {:>4} ({:7.2%}); no_response: {:>4} ({:7.2%})".format(
      self.total, self.on_time, self.on_time_ratio, self.late24, self.late72, self.late_ratio, self.no_response, self.no_response_ratio,
    )
