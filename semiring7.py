#!/usr/bin/env python
import sys
from parser import *

# SEMIRING 7: DIRECT VITERBI DERIVATION WITH BACKPOINTERS
# obtains best Viterbi derivation of sentence (the one with highest score) 
# and the corresponding score, storing the backpointers

# data format
# vector: (weight, i, j, LHS, (RHS), (backpointers))
# backpointer: (LHS,i,j)

rules = [ line.strip() for line in open(sys.argv[1]) ]


#trace the ponters back and builds the derivation tree

def backtrace(chart, lhs, startPos, endPos):
    chartElement = chart[lhs][(startPos,endPos)]
    furtherBackpointers = chartElement[5] 
    
    if len(furtherBackpointers) == 0:
        return chartElement[3]
    
    resultString = '('+lhs
    
    for backpointer in furtherBackpointers:
        resultString += ' ' + backtrace(chart, backpointer[0], backpointer[1], backpointer[2])
        
    resultString += ')'
    
    return resultString

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

MAX_VALUE = sys.maxint
MIN_VALUE = -1

semiZero = (0,MAX_VALUE,MIN_VALUE,"",(),())
semiOne = (1,MAX_VALUE,MIN_VALUE,"",(),())

def semiPlus(a, b): 
    return  a if a[0] >= b[0] else b
    
def semiTimes(a, b): 
    #print "--------------------------TIMES--------------------------"
    #print "a: {0}".format(a)
    #print "b: {0}".format(b)    
    
    if a == semiZero or b == semiZero:  
        return semiZero
    
    if a == semiOne:
        return b
        
    if b == semiOne:
        return a    
    
    A_weight = a[0]
    A_i = a[1]
    A_j = a[2]
    A_LHS = a[3]
    A_RHS = a[4]
    A_backpointers = a[5]
    
    B_weight = b[0]
    B_i = b[1]
    B_j = b[2]
    B_LHS = b[3]
    #B_RHS = b[4]
    
    Result_weight = A_weight
    Result_i = A_i
    Result_j = A_j
    Result_LHS = A_LHS
    Result_RHS = ()
    Result_backpointers = A_backpointers
    
    
    # we want to find the non-terminal LHS_B on the rhs of a:
    # a is assumed to be in the form X -> Y Z   (Z can be empty)
    # we want B_LHS to be either Y or Z in order for a derivation to take place
    derivationIsDone = False
    for elementA in A_RHS:
        
        #not element to be replaced. don't do anything
        if(elementA != B_LHS or derivationIsDone):
            Result_RHS = Result_RHS + (elementA,)
        #is variable to be replaced. Replace with derivation
        else:
            #update weight
            Result_weight = A_weight * B_weight
            #update indexes
            Result_i = min(A_i, B_i)
            Result_j = max(A_j, B_j)
            #add backpointer
            Result_backpointers = Result_backpointers + ( (B_LHS,B_i,B_j), )
            derivationIsDone = True
            
    return (Result_weight, Result_i, Result_j, Result_LHS, Result_RHS, Result_backpointers)
    

def A(word, startPos, endPos, sOne):     
    #log.debug('A_RETURN: {0}'.format( (1,startPos,endPos,word,(),())   ))        
    return (1,startPos,endPos,word,(),() ) 

def R(ruleLhs, ruleRhs, ruleWeight): 
    #log.debug('R_RETURN: {0}'.format( (ruleWeight,MAX_VALUE,MIN_VALUE,ruleLhs,()+ruleRhs,() )  ))    
    return ( ruleWeight,MAX_VALUE,MIN_VALUE,ruleLhs,()+ruleRhs,() ) 

            
# You can omit declaring prune() except in Section 5
def prune(item):
  return False

for (i, sent) in enumerate(sys.stdin):
    sent = sent.strip().split()
    # You should omit unused keyword arguments
    # (e.g. leave out agendaCmp except in Section 1)
    # (e.g. always omit the logging options such as dump in your solutions)
    (goalValue, chart, stats) = parse(sent, rules,
                                      sZero=semiZero, sOne=semiOne, sPlus=semiPlus, sTimes=semiTimes, R=R, A=A,
                                      pruner=prune,
                                      dumpAgenda=False, dumpChart=False, logConsidering=False)
    print "SENT {0} AGENDA ADDS: {1}".format(i, stats['agendaAdds'])
    
    print "SENT {0} GOAL SCORE: {1}".format(i, goalValue[0])
    
    S_Backpointers = list()
    for backpointer in goalValue[5]:
        S_Backpointers.append(backpointer)
    print "SENT {0} GOAL BACKPOINTERS: {1}".format(i, S_Backpointers)

    char_max_index =  len(sent)  
    print "SENT {0} GOAL DERIVATION: {1}".format(i, backtrace(chart, '[S]', 0, char_max_index))
        
