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

# Direct Viterbi Derivation

#The idea here is to make a semiring that keeps a pair (weight, tree)
semiZero = (0,"")
semiOne = (1,"")

def semiPlus(a, b):     
    log.debug('SEMIPLUS: {0} + {1}'.format(a, b))
    return  a if a[0] >= b[0] else b
    
def semiTimes(a, b): 
    log.debug('SEMITIMES: {0} + {1}'.format(a, b))
    resultScore = a[0]*b[0]
    
    ruleA = a[1:]
    ruleB = b[1:] 
    ruleA_RHS = ruleA[1:];
    ruleB_RHS = ruleB[1:];
    
    
    
    log.debug('a: {0}'.format(a))    
    log.debug('b: {0}'.format(b)) 
    log.debug('ruleA: {0}'.format(ruleA))    
    log.debug('ruleB: {0}'.format(ruleB)) 
    log.debug('ruleA_RHS: {0}'.format(ruleA_RHS))    
    log.debug('ruleB_RHS: {0}'.format(ruleB_RHS))    
    
    if len(ruleB_RHS) == 0:
        log.debug('RETURN: {0}'.format( (resultScore,)+a[1:]  ))    
        return (resultScore,)+a[1:]
    
    resultTree = (ruleA[0],)
    
    # we want to find the non-terminal LHS_B on the rhs of a:
    # a is assumed to be in the form X -> Y Z   (Z can be empty)
    # LHS_B will be either Y or Z
    derivationIsDone = False
    for elementA in ruleA_RHS:
        
        #not element to be replaced. don't do anything
        if(elementA != ruleB[0] or derivationIsDone):
            replacingElement = elementA
        #is variable to be replaced. Replace with derivation
        else:
            if len(ruleB_RHS)==2:
                replacingElement = ruleB[0] + " (" + ruleB_RHS[0] + " " + ruleB_RHS[1] + ")"
            else:
                replacingElement = ruleB[0] + " " + ruleB_RHS[0]
            derivationIsDone = True
        #do replacement
        log.debug('REPLACING_ELEMENT: {0}'.format(replacingElement))
        resultTree = resultTree + (replacingElement,)
        log.debug('RESULT_TREE: {0}'.format(resultTree))
            
    return (resultScore, ) + resultTree
    

#def A(word, startPos, endPos, sOne): return sOne

def R(ruleLhs, ruleRhs, ruleWeight): 
    log.debug('R_RETURN LHS: {0}'.format( ruleLhs  ))
    log.debug('R_RETURN RHS: {0}'.format( ruleRhs  ))
    log.debug('R_RETURN WEIGHT: {0}'.format( ruleWeight  ))
    log.debug('R_RETURN: {0}'.format( (ruleWeight,ruleLhs)+ruleRhs ))
    return (ruleWeight,ruleLhs)+ruleRhs
    #log.debug('R_RETURN: {0}'.format( (ruleWeight,ruleLhs,ruleRhs)  ))
    #return (ruleWeight,ruleLhs,ruleRhs)
            
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
    print "SENT {0} GOAL SCORE: {1}".format(i, goalValue[0])
    if len(goalValue[2:]) == 2:
        print "SENT {0} GOAL DERIVATION: ({1} ({2}) ({3}))".format(i, goalValue[1], goalValue[2], goalValue[3])
    else:
        print "SENT {0} GOAL DERIVATION: ({1} ({2}))".format(i, goalValue[1], goalValue[2])
        
