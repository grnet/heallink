from collections import defaultdict, Counter
from itertools import combinations, permutations

import unittest

from sys import stdout

class SchulzeCalculator:

    def __init__(self, ballots):
        self.d = defaultdict(Counter)
        self.p = defaultdict(lambda: defaultdict(int))
        self.positions = {}
        self.candidates = set()
        self.results = []
        self.path_strengths = {}
        # create matrix d
        print "Creating matrix d"
        for ballot in ballots:
            for combination in combinations(ballot, 2):
                self.candidates.add(combination[0])
                self.candidates.add(combination[1])
                self.d[combination[0]][combination[1]] += 1
        # create matrix p
        print "First go at matrix p, candidates=", len(self.candidates)
        count = 1
        for i, j in permutations(self.candidates, 2):
            if count % 10000 == 0:
                stdout.write("\r{}".format(format(count, ',')))
                stdout.flush()
            count += 1
            if self.d[i][j] > self.d[j][i]:
                self.p[i][j] = self.d[i][j]
            else:
                self.p[i][j] = 0
        print(format(format(count, ',')))
        print "Second go at matrix p"
        count = 1 
        for i, j, k in permutations(self.candidates, 3):
            if count % 10000 == 0:
                stdout.write("\r{}".format(format(count, ',')))
                stdout.flush()
            count += 1
            self.p[j][k] = max(self.p[j][k], min(self.p[j][i], self.p[i][k]))
        self.positions = dict.fromkeys(self.candidates, 0)
        print(format(format(count, ',')))
        count = 1
        print "Calculating strongest paths"        
        for i, j in permutations(self.candidates, 2):
            if count % 10000 == 0:
                stdout.write("\r{}".format(format(count, ',')))
                stdout.flush()
            count += 1            
            p_ij = self.p[i][j]
            p_ji = self.p[j][i]
            if p_ij > p_ji:
                self.positions[i] += 1
                self.path_strengths[(i, j)] = p_ij
        print(format(format(count, ',')))        
        sorted_positions = sorted(self.positions, key=self.positions.get,
                                  reverse=True)
        for position in sorted_positions:
            self.results.append((position, self.positions[position]))
            

class TestSchulzeCalculator(unittest.TestCase):

    def test_wikipedia_results(self):
        ballots = ["ACBED" for x in range(5)]
        ballots.extend(["ADECB" for x in range(5)])
        ballots.extend(["BEDAC" for x in range(8)])
        ballots.extend(["CABED" for x in range(3)])
        ballots.extend(["CAEBD" for x in range(7)])
        ballots.extend(["CBADE" for x in range(2)])
        ballots.extend(["DCEBA" for x in range(7)])
        ballots.extend(["EBADC" for x in range(8)])        

        sc = SchulzeCalculator(ballots)
        results = [('E', 4), ('A', 3), ('C', 2), ('B', 1), ('D', 0)]
        self.assertEqual(sc.results, results)

    def test_wikipedia_path_strengths(self):
        ballots = ["ACBED" for x in range(5)]
        ballots.extend(["ADECB" for x in range(5)])
        ballots.extend(["BEDAC" for x in range(8)])
        ballots.extend(["CABED" for x in range(3)])
        ballots.extend(["CAEBD" for x in range(7)])
        ballots.extend(["CBADE" for x in range(2)])
        ballots.extend(["DCEBA" for x in range(7)])
        ballots.extend(["EBADC" for x in range(8)])        

        sc = SchulzeCalculator(ballots)
        path_strengths = {
            ('A', 'B'): 28,
            ('A', 'C'): 28,
            ('A', 'D'): 30,
            ('B', 'D'): 33,
            ('C', 'B'): 29,
            ('C', 'D'): 29,
            ('E', 'A'): 25,
            ('E', 'B'): 28,
            ('E', 'C'): 28,
            ('E', 'D'): 31
        }
        self.assertEqual(sc.path_strengths, path_strengths)

    def test_schulze_ex1(self):
        ballots = ["ACDB" for x in range(8)]
        ballots.extend(["BADC" for x in range(2)])
        ballots.extend(["CDBA" for x in range(4)])
        ballots.extend(["DBAC" for x in range(4)])
        ballots.extend(["DCBA" for x in range(3)])

        sc = SchulzeCalculator(ballots)
        path_strengths = {
            ('A', 'B'): 14,
            ('A', 'C'): 14,
            ('C', 'B'): 15,
            ('D', 'A'): 13,
            ('D', 'B'): 19,
            ('D', 'C'): 13,            
        }
        self.assertEqual(sc.path_strengths, path_strengths)

    
if __name__=="__main__":
    unittest.main()
    
