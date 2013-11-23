#!/usr/bin/env python

import sys

def main(argv):
    
    if len(argv[1:]) != 1:
        print >> sys.stderr, \
          'Convert a probabilistic context-free grammar to Chomsky normal form'
        print >> sys.stderr, 'usage: {0} input.gra > output.gra'.format(argv[0])
        sys.exit(1)
    
    x_i = 1 # Index for X rules
    
    for line in open(argv[1]):
        try:
            # Parse rule
            (lhs, rest) = [x.strip() for x in line.split('->')]
            (rest, prob) = [x.strip() for x in rest.split('/')]
            rhs = rest.split()
        except:
            print >> sys.stderr, 'Error processing rule line:'
            print >> sys.stderr, line.rstrip('\n')
            sys.exit(1)
        # Replace 'a' with '[Ca]'
        # Add rules [Ca] -> a / 1.0
        c_rules = []
        if len(rhs) > 1:
            for i in range(len(rhs)):
                if not rhs[i].startswith('['):
                    c_nonterm = '[C{0}]'.format(rhs[i])
                    c_rules.append(form_rule(c_nonterm, [rhs[i]], 1.0))
                    rhs[i] = c_nonterm
        # Replace A -> B C ... Y Z / 0.5 with
        # A -> B X1 / 0.5, X1 -> C X2 / 1.0, ... Xn -> Y Z / 1.0
        x_rules = []
        if len(rhs) > 2:
            x_nonterm = '[X{0}]'.format(x_i)
            x_i += 1
            rest_rhs = rhs[1:]
            rhs = [rhs[0], x_nonterm]
            while len(rest_rhs) > 2:
                x_next_nonterm = '[X{0}]'.format(x_i)
                x_i += 1
                x_rules.append(
                    form_rule(x_nonterm, [rest_rhs[0], x_next_nonterm], 1.0)
                )
                x_nonterm = x_next_nonterm
                rest_rhs = rest_rhs[1:]
            x_rules.append(form_rule(x_nonterm, rest_rhs, 1.0))
        # Print rules in a reasonable order
        print form_rule(lhs, rhs, prob) # (possibly modified) base rule
        for rule in x_rules:
            print rule
        for rule in c_rules:
            print rule

def form_rule(lhs, rhs, prob):
    return '{0} -> {1} / {2}'.format(lhs, ' '.join(rhs), prob)

if __name__ == '__main__' : main(sys.argv)
