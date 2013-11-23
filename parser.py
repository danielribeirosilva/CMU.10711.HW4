#!/usr/bin/env python
import sys
import logging
from collections import defaultdict

BOLD = '\033[1m'
GREEN = BOLD + '\033[92m'
RED = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'

log = logging.getLogger('parser')
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

def LTR_INC_COMP(item1, item2):
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
      # This is where things get intereting. If the semiring value is not a float,
      # then assume the value is iterable, and use the first float we find
      # Otherwise, just use zero
      def findFloat(val):
        try:
          return float(val)
        except TypeError:
          try:
            it = iter(val)
          except TypeError:
            return 0 # Not iterable
          for x in it:
            try:
              return float(x)
            except:
              pass
          return 0
            
      float1 = findFloat(value1)
      float2 = findFloat(value2)
      valDiff = float2 - float1
      return 1 if valDiff > 0 else -1      

# TODO: Latex Chart

def readRules(rules, logconf):
  # ruleMap: rhsSym -> [(rhsIdx, lhs, rhs, weight)]
  # * rhsIdx lets us know what position the rhs occurs in for this rule
  ruleMap = defaultdict(lambda: [])
  nRule = 0
  for rule in rules:
    try:
      (lhs, remain) = rule.split('->')
      lhs = lhs.strip()
      (strRhs, strWeight) = remain.split('/')
      rhs = tuple(strRhs.strip().split(' '))
      if len(rhs) > 2:
        print >>sys.stderr, "Grammar is not in CNF"
        sys.exit(1)
      weight = float(strWeight.strip())
      for (i, antecedent) in enumerate(rhs):
        ruleMap[antecedent].append( (i, lhs, rhs, weight) )
      #log.debug('Got rule: %s -> %s / %f'%(lhs, str(rhs), weight))
    except:
      log.error('ERROR: Skipping malformed rule %d: %s'%(nRule, rule))
    nRule += 1
  return ruleMap

def init(sent, ruleMap, agenda, sOne, A, prune, stats, logconf):
  # Seed lexical items to agenda (with no backpointers)
  log.info('Seeding agenda with input sentence...')
  for (i, word) in enumerate(sent):
    axiomValue = A(word, i, i+1, sOne)
    newItem = (i, i+1, word, axiomValue)
    if prune(newItem):
      log.debug('Pruned axiom item: start=%d end=%d word=%s derivationValue=%s'%(i, i+1, word, str(axiomValue)))
    else:
      agenda.append(newItem)
      stats['agendaAdds'] += 1
      log.debug('Seeding item to agenda: start=%d end=%d word=%s derivationValue=%s'%(i, i+1, word, str(axiomValue)))

def dumpChart(chart, goal):
  goalValue = None
  for (startPos, endPos, lhs, value) in sorted([ (startPos, endPos, lhs, value)
                                                 for lhs in chart.iterkeys()
                                                 for ((startPos, endPos), value) in chart[lhs].iteritems() ]):
    if (startPos, endPos, lhs) == goal:
      log.info('%s%d %d %s = %s%s'%(GREEN, startPos, endPos, lhs, str(value), ENDC))
      goalValue = value
    else:
      log.info('%d %d %s = %s'%(startPos, endPos, lhs, str(value)))
  return goalValue

# add new items to the agenda
# triggeringChartItem is a tuple (start, end, consequentSymbol, semiValue)
def addItems(chart, agenda, lhs, triggeringAgendaItem, triggeringChartItem,
             agendaCmp, ruleMap, sTimes, R, prune, stats, logconf):
    def unpack(rhs, fixedRhsIdx, fixedItem, i=0, antecedents=[]):
      if i == len(rhs):
        yield antecedents
      else:
        if i == fixedRhsIdx: # our fix item must fill this position by constraint
          antecedents.append(fixedItem)
          for x in unpack(rhs, fixedRhsIdx, fixedItem, i+1, antecedents):
            yield x
          antecedents.pop()
        else: # otherwise, draw from the chart for previously completed items
          for ((antStart, antEnd), antValue) in chart[rhs[i]].iteritems():
            antecedents.append( (antStart, antEnd, rhs[i], antValue) )
            for x in unpack(rhs, fixedRhsIdx, fixedItem, i+1, antecedents):
              yield x
            antecedents.pop()

    potentialRules = ruleMap[lhs]
    log.debug('Checking if this item can complete any new items for %d potential rules'%(len(potentialRules)))
    itemsAdded = False
    for (ruleRhsIdx, ruleLhs, ruleRhs, ruleWeight) in potentialRules:
      if logconf['logConsidering']:
        log.debug("Considering completing rule: %s -> %s / %f"%(ruleLhs, str(ruleRhs), ruleWeight))
      # Use triggeringAgendaItem instead of triggeringChartItem
      # (i.e. use u instead of chart[x] according to Noah's slides)
      for antecedents in unpack(ruleRhs, ruleRhsIdx, triggeringAgendaItem):
        # antecedents is a list [(antStart, antEnd, rhsTrigger, antValue)]
        
        #log.debug("Considering antecedents: %s"%(str(antecedents)))

        # check that antecedents meet the contiguous constraint
        # (we could have done this incrementally in unpack)
        isContiguous = True
        for i in range(1, len(antecedents)):
          (antStart1, antEnd1, antLhs1, antValue1) = antecedents[i-1]
          (antStart2, antEnd2, antLhs2, antValue2) = antecedents[i]
          isContiguous &= (antEnd1 == antStart2)
        if isContiguous:
          newStartPos = antecedents[0][0]
          newEndPos = antecedents[-1][1]
          ruleValue = R(ruleLhs, ruleRhs, ruleWeight)
          log.debug('Adding new item to agenda from rule (filled RHS position %d): %s -> %s / %f (RValue: %s)'%(ruleRhsIdx, ruleLhs, str(ruleRhs), ruleWeight, str(ruleValue)))
          aggValue = ruleValue
          for (antStart, antEnd, antLhs, antValue) in antecedents:
            aggValue = sTimes(aggValue, antValue)

          newItem = (newStartPos, newEndPos, ruleLhs, aggValue)
          if prune(newItem):
            log.debug('Pruned item: %d %d %s = %s'%(newStartPos, newEndPos, ruleLhs, str(aggValue)))
          else:
            agenda.append(newItem)
            stats['agendaAdds'] += 1
            #stats['agendaAddsDueTo{}-{}'.format(triggeringChartItem[0], triggeringChartItem[1])] += 1
            #stats['agendaAddsInto{}-{}'.format(newStartPos, newEndPos)] += 1
            itemsAdded = True
            log.debug('Added agenda item: %d %d %s = %s'%(newStartPos, newEndPos, ruleLhs, str(aggValue)))    

    if itemsAdded: # worse than insertion sort, but oh well
      log.debug('Agenda changed this iteration, resorting')
      agenda.sort(cmp=agendaCmp)
    else:
      log.debug('Agenda did not change. Skipping sort.')

# Valid kwargs are:
# * For agenda ordering: agendaCmp
# * For a semiring: sZero, sOne, sPlus, sTimes, R
# * For agenda pruning: pruner
#
# Returns a tuple (goalValue, stats)
# stats is a dictionary with keys { 'agendaAdds' }
# 
# Logging options are keyword arguments (e.g. add logAgenda=True)
# dumpAgenda: Dump agenda every iteration?
# dumpChart: Dump chart every iteration?
# logConsidering: Log every time we consider completing a rule?
def parse(sent, rules, **kwargs):

  logconf = {'dumpAgenda': False, 'dumpChart': False, 'logConsidering': False}

  # Validate options to fail fast
  semiringArgs = set(['sZero', 'sOne', 'sPlus', 'sTimes', 'R'])
  for key in kwargs:
    if key not in set(['agendaCmp', 'pruner', 'A']) | semiringArgs | set(logconf):
      log.error('ERROR: Unrecognized keyword argument {0}'.format(key))
      sys.exit(1)
  if any(arg in kwargs for arg in semiringArgs):
    if not all(arg in kwargs for arg in semiringArgs):
      log.error('ERROR: You passed some semiring keyword args, but not all of them'.format(key))
      missing = [arg for arg in semiringArgs if arg not in kwargs]
      log.error('Missing: {0}'.format(missing))
      sys.exit(1)

  for (key, val) in kwargs.iteritems():
    if key in logconf:
      logconf[key] = val

  agendaCmp = kwargs.get('agendaCmp', LTR_INC_COMP)
  pruner = kwargs.get('pruner', lambda item: False)

  # Use the Viterbi semiring by default iff no 
  def vPlus(a, b): return max(a,b)
  def vTimes(a, b): return a * b
  def defaultSeedAxiom(word, startPos, endPos, sOne): return sOne
  def defaultGetWeight(ruleLhs, ruleRhs, ruleWeight): return ruleWeight
  def defaultNewChartCell(lhs, i, j, sZero): return sZero

  sZero = kwargs.get('sZero', 0)
  sOne = kwargs.get('sOne', 1)
  sPlus = kwargs.get('sPlus', vPlus)
  sTimes = kwargs.get('sTimes', vTimes)
  A = kwargs.get('A', defaultSeedAxiom)
  R = kwargs.get('R', defaultGetWeight)

  log.info('Reading rules...')
  ruleMap = readRules(rules, logconf)

  goal = (0, len(sent), "[S]")

  # chart has lhs -> (startPos, endPos) -> value
  # * if we don't have en entry yet, assume semiring zero as the value
  chart = defaultdict(lambda: defaultdict(lambda: sZero))

  # * agenda items are "proven" items that are waiting to trigger their
  #   consequents and then find their resting place in the chart
  # * handling a proven item on the agenda consists of:
  #   - finding all rules that contain its lhs anywhere on their rhs
  #   - try using this new proven item for each applicable positions
  #     within the matching RHS; unfilled RHS positions are populated
  #     using entries from the chart; if all RHS slots are filled, we
  #     generate a new agenda entry
  # agenda has (startPos, endPos, lhs, itemValue)
  # * itemValue is the result of appling sTimes to the antecedents
  #   and the inference rule; it is waiting to be aggregated using sPlus
  agenda = []

  #stats = {'agendaAdds': 0}
  stats = defaultdict(lambda: 0)

  # Seed lexical items to agenda
  init(sent, ruleMap, agenda, sOne, A, pruner, stats, logconf)
  agenda.sort(cmp=agendaCmp)

  prevChartUpdate = None # For logging
  iteration = 0
  while len(agenda) > 0:
    iteration += 1
    log.info('--------------------------------------------------------------------------------')
    log.info('Begin iteration %d'%iteration)
    if logconf['dumpChart']:
      log.info('Current chart:')
      dumpChart(chart, goal)

    log.info('Processing agenda (size is %d):'%len(agenda))
    if logconf['dumpAgenda']:
      for x in agenda:
        log.debug(x)

    item = agenda.pop()
    (startPos, endPos, lhs, itemValue) = item
    log.info('Got agenda item: ' + str(item))

    # 1) Put this agenda item into the chart by aggregating
    #    using sPlus
    prevAggValue = chart[lhs][(startPos,endPos)]
    newAggValue = sPlus(prevAggValue, itemValue)
    log.debug('Aggregating completed item into chart using sPlus: {0} + {1} = {2}'.format(prevAggValue, itemValue, newAggValue))
    if prevAggValue == newAggValue:
      # TODO: Count times chart value changed due to initialization
      # versus due to new update
      # TODO: Is it possible to track if it affected a span outside of the "current scope"
      log.debug('Chart value unchanged. No need to propagate updates.')
    else:
      if (startPos, endPos) != prevChartUpdate:
        prevChartUpdate = (startPos, endPos)
        if prevAggValue == sZero:
          log.debug('Initialized new chart cell: {0} {1}'.format(startPos, endPos))
        else:
          log.debug('Change to different chart cell: {0} {1}'.format(startPos, endPos))
      else:
        log.debug('Change to same chart cell: {0} {1}'.format(startPos, endPos))

      chart[lhs][(startPos,endPos)] = newAggValue

      # 2) Check all rules that have this consequent (LHS)
      #    anywhere as an antecedent (in their RHS)
      # * If so, add those proven items to the agenda
      #   so that we can later deal with their consequence
      log.debug('Chart value changed. Considering new items to add to agenda...')
      triggeringChartItem = (startPos, endPos, lhs, newAggValue)
      addItems(chart, agenda, lhs, item, triggeringChartItem,
               agendaCmp, ruleMap, sTimes, R, pruner, stats, logconf)
      
  log.info('Final chart:')
  goalValue = dumpChart(chart, goal)

  return (goalValue, chart, stats)
