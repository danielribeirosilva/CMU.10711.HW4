#!/usr/bin/env python
import sys
import math
from parser import *

rules = [ line.strip() for line in open(sys.argv[1]) ]

# You can omit declaring this function except in Section 1
def agendaComparator(item1, item2):
  (startPos1, endPos1, lhs1, value1) = item1
  (startPos2, endPos2, lhs2, value2) = item2
  span1 = endPos1 - startPos1
  span2 = endPos2 - startPos2
  spanDiff = span2 - span1
  if spanDiff != 0: # sort by span length first
    return 1 if spanDiff > 0 else -1
  else:
    posDiff = startPos2 - startPos1
    if posDiff != 0: # then start position
      return 1 if posDiff > 0 else -1
    else: # then the semiring value of the update to the chart
      valDiff = value2 - value1
      return 1 if valDiff < 0 else -1      

# Viterbi
# You can omit declaring the semiring except in Sections 2-3
semiZero = 0
semiOne = 1
def semiPlus(a, b): return max(a,b)
def semiTimes(a, b): return a * b
#def A(word, startPos, endPos, sOne): return sOne
def R(ruleLhs, ruleRhs, ruleWeight): return ruleWeight

# You can omit declaring prune() except in Section 5
def prune(item):
    #item format: item = (i, j, word, axiomValue)
    item_i = item[0]
    item_j = item[1]
    if item[3] < math.pow( 0.01725, 2*(item_j - item_i) - 1 ):
        return True
    return False

for (i, sent) in enumerate(sys.stdin):
    sent = sent.strip().split()
    # You should omit unused keyword arguments
    # (e.g. leave out agendaCmp except in Section 1)
    # (e.g. always omit the logging options such as dump in your solutions)
    (goalValue, chart, stats) = parse(sent, rules,
                                      agendaCmp=agendaComparator,
                                      sZero=semiZero, sOne=semiOne, sPlus=semiPlus, sTimes=semiTimes, R=R,
                                      pruner=prune,
                                      dumpAgenda=False, dumpChart=False, logConsidering=False)
    print "SENT {0} AGENDA ADDS: {1}".format(i, stats['agendaAdds'])
    print "SENT {0} GOAL SCORE: {1}".format(i, goalValue)
