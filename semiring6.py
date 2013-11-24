#!/usr/bin/env python
import sys
from parser import *

# SEMIRING 6: VITERBI K-BEST DERIVATIONS
# obtains the top K best Viterbi derivations of a sentence (the ones with highest scores) 
# and the corresponding scores

K = 10

rules = [ line.strip() for line in open(sys.argv[1]) ]

# adds element to a top-K list
# if list has less than K elements, add it
# if list has >=K elements, add only if element's score is bigger 
# than the smallest on in the list
def addToTopKList (topKList, K, candidateElement):
    if len(topKList) < K:
        topKList.append(candidateElement)
    else:
        lowestElement = min(topKList)
        if lowestElement[0] < candidateElement[0]:
            topKList.remove(lowestElement)
            topKList.append(candidateElement)

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

#The idea here is to make a semiring that keeps a pair (weight, tree)
semiZero = list()
semiOne = list( [(1,"")] )

def semiPlus(a, b):
    print "--------------------------PLUS--------------------------"
    print "a: {0}".format(a)
    print "b: {0}".format(b)
    sumList = list()
    for elementA in a:
        addToTopKList (sumList, K, elementA)
    for elementB in b:
        addToTopKList (sumList, K, elementB)
    
    sumList = list(set(sumList))
    print "result: {0}".format(sumList)
    return sumList
    
def semiTimes(a, b): 
    
    print "--------------------------TIMES--------------------------"
    print "a: {0}".format(a)
    print "b: {0}".format(b)
    
    resultingList = list()
    for currentA in a:
        for currentB in b:
            resultScore = currentA[0]*currentB[0]
            
            ruleA = currentA[1:]
            ruleB = currentB[1:] 
            ruleA_RHS = ruleA[1:];
            ruleB_RHS = ruleB[1:];
            
            if currentA==semiOne[0]:
                print "appended element: {0}".format( currentB )
                resultingList.append(currentB)
                resultingList = list(set(resultingList))
                continue
            
            if currentB==semiOne[0]:
                print "appended element: {0}".format( currentA )
                resultingList.append(currentA)
                resultingList = list(set(resultingList))
                continue
            
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
                        replacingElement = "(" + ruleB[0] + " " + ruleB_RHS[0] + " " + ruleB_RHS[1] + ")"
                        print "replacingElement: {0}".format(replacingElement)
                    else:
                        replacingElement = "(" + ruleB[0] + " " + ruleB_RHS[0] + ")"
                        print "replacingElement: {0}".format(replacingElement)
                    derivationIsDone = True
                #do replacement
                resultTree = resultTree + (replacingElement,)
            #end of for
            #only add if derivation took place
            if derivationIsDone and resultScore>0:
                resultingList.append( (resultScore, ) + resultTree )
                resultingList = list(set(resultingList))
                print "appended element: {0}".format( (resultScore, ) + resultTree )
    
        #end of for B
    #end of for A
    print "result: {0}".format(list(set(resultingList)))    
    resultingList = sorted(list(set(resultingList)))
    
    return resultingList
    

#def A(word, startPos, endPos, sOne): return sOne

def R(ruleLhs, ruleRhs, ruleWeight):  
    return list( [(ruleWeight,ruleLhs)+ruleRhs] )
    

            
# You can omit declaring prune() except in Section 5
def prune(item):
  return False

for (i, sent) in enumerate(sys.stdin):
    sent = sent.strip().split()
    # You should omit unused keyword arguments
    # (e.g. leave out agendaCmp except in Section 1)
    # (e.g. always omit the logging options such as dump in your solutions)
    (goalValue, chart, stats) = parse(sent, rules,
                                      sZero=semiZero, sOne=semiOne, sPlus=semiPlus, sTimes=semiTimes, R=R,
                                      pruner=prune,
                                      dumpAgenda=False, dumpChart=False, logConsidering=False)
    print "SENT {0} AGENDA ADDS: {1}".format(i, stats['agendaAdds'])

    K_idx = 0
    for currentGoalValue in goalValue:
        print "SENT {0} GOAL SCORE K={1}: {2}".format(i, K_idx, currentGoalValue[0])
        if len(currentGoalValue[2:]) == 2:
            print "SENT {0} GOAL DERIVATION K={1}: ({2} {3} {4})".format(i, K_idx, currentGoalValue[1], currentGoalValue[2], currentGoalValue[3])
        else:
            print "SENT {0} GOAL DERIVATION K={1}: ({2} {3})".format(i, K_idx, currentGoalValue[1], currentGoalValue[2])
        K_idx += 1
