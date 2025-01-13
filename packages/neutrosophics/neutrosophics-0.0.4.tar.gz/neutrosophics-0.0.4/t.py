from neutrosophics.types import NetrosophicSet
from neutrosophics.logic import NetrosophicLogic
from neutrosophics.analysis import NetrosophicAnalyzer

ns1 = NetrosophicSet(0.5, 0.3, 0.2)
ns2 = NetrosophicSet(0.4, 0.2, 0.1)

print("Addition:", ns1 + ns2)
print("Subtraction:", ns1 - ns2)
print("Multiplication:", ns1 * ns2)
print("Division:", ns1 / 0.5)
logic = NetrosophicLogic()
analyzer = NetrosophicAnalyzer()

print("Conjunction:", logic.conjunction(ns1, ns2))
print("Disjunction:", logic.disjunction(ns1, ns2))
print("Negation:", logic.negation(ns1))
print("Analysis:\n", analyzer.analyze(ns1))
print("From tuple:", NetrosophicSet.from_tuple((0.6, 0.5, 0.4)))
print("To tuple:", ns1.to_tuple())