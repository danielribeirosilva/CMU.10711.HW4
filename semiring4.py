#!/usr/bin/env python
import sys
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
      valDiff = value2[0] - value1[0]
      return 1 if valDiff < 0 else -1      

# Derivation Forest

#The idea here is to make a boolean-like semiring that keeps the rules
#The first element o the tuple works like the boolean semiring and the second
#argument keeps the rules
semiZero = (False,set())
semiOne = (True,set())
def semiPlus(a, b): return (a[0] or b[0], a[1].union(b[1]))
def semiTimes(a, b): return (a[0] and b[0], a[1].union(b[1]))
#def A(word, startPos, endPos, sOne): return sOne
#each rule is stored as a 2-tuple: left and right hand side
def R(ruleLhs, ruleRhs, ruleWeight): 
    if ruleWeight > 0:
        ruleStr = ruleLhs + " ->";
        for rule in ruleRhs:
            ruleStr += " "+rule
        return (True, set([ruleStr]))
    else:
        return (False, set())
            

# You can omit declaring prune() except in Section 5
def prune(item):
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
    goalSet = goalValue[1];    
    for item in goalSet:
        print "SENT {0} GOAL SCORE: {1}".format(i, item)
        
