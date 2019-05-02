import aLEXis as alexis
import math
from Tokens import *

OrderOfOperations = {
	'^' : 1,
	'*' : 2,
	'/' : 2,
	'+' : 3,
	'-' : 3
}

SolverRegistry = alexis.TokenRegistry([NumberToken, GroupingToken, OperatorToken, ComparisonToken, SeperatorToken, KeywordToken])

# Knu Structures

class TokenList(list): # Using a class because it'll let me edit it from other functions
	pass

class Grouping:
	def __init__(self, state, parent=None):
		self.tokens = TokenList()
		self.state = state
		self.parent = parent

	def AddToken(self, knu):
		knu.parent = self
		self.tokens.append(knu)

	def __repr__(self):
		return "Group[State="+str(self.state)+" | "+ (" ".join(str(t) for t in self.tokens))+" ]"

	def __len__(self):
		return len(self.tokens)

	def __getitem__(self, index):
		return self.tokens[index]

	def __setitem__(self, index, knu):
		self.tokens[index] = knu

	def __delitem__(self, item):
		del self.tokens[item]

	def index(self, target):
		return self.tokens.index(target)

	def recast(self):
		myIndex = self.parent.index(self)
		if len(self.tokens) == 1:
			if myIndex == 0 or not isinstance(self.parent[myIndex-1], KeywordToken):
				self.parent[myIndex] = self.tokens[0]
				self.parent = None

	def packageNumbers(self):
		return [float(token.data) for token in self.tokens if isinstance(token, NumberToken)]
				

# Functions

def RefactorTokens(tokens):
	Knu = TokenList()
	GroupingStates = []
	for n in range(len(tokens)):
		current = tokens[n]
		if isinstance(current, GroupingToken):
			if current.data == "(":
				parent = Knu if len(GroupingStates) == 0 else GroupingStates[-1]
				knuGroup = Grouping(len(GroupingStates)+1, parent)
				GroupingStates.append(knuGroup)
				#knuGroup.AddToken(current)
			else: # It's closing
				kGroup = GroupingStates.pop()
				#kGroup.AddToken(current)
				if len(GroupingStates) == 0:
					Knu.append(kGroup)
				else:
					GroupingStates[-1].AddToken(kGroup)
		else: # regular token
			if len(GroupingStates) > 0:
				lastGroup = GroupingStates[-1]
				lastGroup.AddToken(current)
			else:
				current.parent = Knu
				Knu.append(current)
	return Knu

def firstByOrder(tokenList, priorities: dict):
	if len(tokenList) == 0: return None
	important = None
	for t in tokenList:
		if not isinstance(t, Grouping) and t.data in priorities and ( not important or priorities[t.data] < priorities[important.data]):
			important = t
	return important

def SimplifyGroup(group: Grouping):
	internalGroups = [g for g in group.tokens if isinstance(g, Grouping)]
	for g in internalGroups:
		SimplifyGroup(g)
	Operation = firstByOrder(group.tokens, OrderOfOperations)
	while Operation:
		Operation.Solve()
		Operation = firstByOrder(group.tokens, OrderOfOperations)
	if group.parent:
		group.recast()

def SimplifyEquation(tokens):
	Groupings = [g for g in tokens if isinstance(g, Grouping)]
	for g in Groupings:
		SimplifyGroup(g)
	Functions = [f for f in tokens if isinstance(f, KeywordToken)]
	for f in Functions:
		f.Solve()
	Operation = firstByOrder(tokens, OrderOfOperations)
	while Operation:
		Operation.Solve()
		Operation = firstByOrder(tokens, OrderOfOperations)
	return tokens

Equation = input("Input a normal expression: ")

Alexios = alexis.Lexer(Equation, SolverRegistry, BurnSticks=True) # Totally not an AC Odyssey reference O_O
Alexios.FullParse()
ParsedTokens = RefactorTokens(TokenList(RefactorTokens(Alexios.tokens)))
print(SimplifyEquation(ParsedTokens))