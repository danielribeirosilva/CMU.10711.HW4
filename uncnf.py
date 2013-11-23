#!/usr/bin/env python

import logging
import fileinput


log = logging.getLogger('parser')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

def removeNonTerminalsFromCNF (sentence):
    #iterate through chars to find first CNF variable
    for pos in range(0,len(sentence)):
        #found a CNF variable (represented by X<number>, e.g. X2 or X532 )
        if sentence[pos] == "(" and sentence[pos+1] == "[" and sentence[pos+2] == "X" and sentence[pos+3].isdigit():
            lastDigitPos = positionOfLastCharOfThisCnfVariable (pos+2, sentence)
            #cut '([X#]'
            newSentenceBegin = sentence[0:pos]
            #remove closing parenthsis
            newSentenceEnd = removeClosingParenthesis(sentence[lastDigitPos+1:])    
            #remove remaining CNF variables
            newSentenceEnd = removeNonTerminalsFromCNF (newSentenceEnd)
            #return edited sentence
            return newSentenceBegin+newSentenceEnd
    #if no CNF variable is found
    return sentence
            
#takes part of text that comes after a parenthesis and closes the corresponding closing parenthesis
def removeClosingParenthesis (sentence):
    openParenthesis = 1
    for pos in range(0,len(sentence)):
        if sentence[pos]=="(":
            openParenthesis += 1
        if sentence[pos]==")":
            openParenthesis -= 1
        if openParenthesis==0:
            return sentence[0:pos]+sentence[pos+1:]
    return sentence
    
# currentPos is the position of the first digit number of the CNF variable
# the number of digits is unknow, it has tipically 1 or 2 digits (X3 or X35), 
# but it can also have multiple digits if the FCG is huge (X9826934)
def positionOfLastCharOfThisCnfVariable (firstDigitPos, sentence):
    for CNFvarPos in range(firstDigitPos+1, len(sentence)):
        if sentence[CNFvarPos]=="]":
            if sentence[CNFvarPos+1]==" ":
                return CNFvarPos+1
            return CNFvarPos
    log.error('ERROR: closing ] not found')
    return len(sentence)-1
    

#print "{0}".format(removeNonTerminalsFromCNF("([S] ([NP-SBJ] ([NNP] Ms.) ([NNP] Haag)) ([X49] ([VP] ([VBZ] plays) ([NP] ([NNP] Elianti))) ([.] .)))") )

for line in fileinput.input():
    print removeNonTerminalsFromCNF(line)