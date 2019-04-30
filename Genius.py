import aLEXis as alexis
import math

class NumberToken(alexis.Token):

	identifiers = "1234567890.,"

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

class OperatorToken(alexis.Token):

	identifiers = "+-/*^"

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

	def Solve(self):
		selfPosition = self.parent.index(self)
		if selfPosition == len(self.parent)-1 or selfPosition <= 0:
			return False
		else:
			left = self.parent[selfPosition-1]
			right = self.parent[selfPosition+1]
			# print(">",left, right,"<")
			if self.data == '+':
				Simplified = NumberToken(self.line, self.column, self.truePosition, float(left.data)+float(right.data))
			elif self.data == "/":
				Simplified = NumberToken(self.line, self.column, self.truePosition, float(left.data)/float(right.data))
			elif self.data == "*":
				Simplified = NumberToken(self.line, self.column, self.truePosition, float(left.data)*float(right.data))
			elif self.data == "-":
				Simplified = NumberToken(self.line, self.column, self.truePosition, float(left.data)-float(right.data))
			elif self.data == "^":
				Simplified = NumberToken(self.line, self.column, self.truePosition, float(left.data)**float(right.data))
				
			self.parent[selfPosition-1] = Simplified
			del self.parent[selfPosition+1]
			del self.parent[selfPosition]
			if not isinstance(self.parent, list):
				self.parent.recast()

class SeperatorToken(alexis.Token):
	
	identifiers = ","

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

class KeywordToken(alexis.Token):

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

	def Solve(self):
		selfPosition = self.parent.index(self)
		if selfPosition == len(self.parent)-1:
			return False
		else:
			right = self.parent[selfPosition+1]
			if hasattr(math, self.data.lower()):
				Simplified = NumberToken(self.line, self.column, self.truePosition, getattr(math, self.data.lower())(float(right.data)))
			self.parent[selfPosition] = Simplified
			del self.parent[selfPosition+1]
			if not isinstance(self.parent, list):
				self.parent.recast()

	@classmethod
	def isValidCharacter(cls, char):
		return char not in "()" # This makes it so this *has* to be the last token in the registry

class ComparisonToken(alexis.Token):
	
	identifiers = "=><"

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

class GroupingToken(alexis.Token):
	
	identifiers = "()"
	OnlyOne = True

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

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
		if len(self.tokens) == 1:
			myIndex = self.parent.index(self)
			self.parent[myIndex] = self.tokens[0]

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

def getTokenByClass(tokenList, classType):
	return [group for group in tokenList if isinstance(group, Grouping)]

def firstByOrder(tokenList, priorities: dict):
	if len(tokenList) == 0: return None
	important = None
	for t in tokenList:
		if not isinstance(t, Grouping) and t.data in priorities and ( not important or priorities[t.data] < priorities[important.data]):
			important = t
	return important

OrderOfOperations = {
	'^' : 1,
	'*' : 2,
	'/' : 2,
	'+' : 3,
	'-' : 3
}

def SimplifyGroup(group: Grouping):
	internalGroups = getTokenByClass(group.tokens, Grouping)
	for g in internalGroups:
		SimplifyGroup(g)
	Operation = firstByOrder(group.tokens, OrderOfOperations)
	if Operation:
		Operation.Solve()
	group.recast()

def SimplifyEquation(tokens):
	Groupings = [g for g in tokens if isinstance(g, Grouping)]
	for g in Groupings:
		SimplifyGroup(g)
	Operation = firstByOrder(tokens, OrderOfOperations)
	while Operation:
		Operation.Solve()
		Operation = firstByOrder(tokens, OrderOfOperations)
	return tokens
# print("Starting solve")
Equation = input("Input a normal expression: ")
Debug = False

if Equation == "DEBUG":
	Debug = True
	Equation = "sqrt(2)"

Alexios = alexis.Lexer(Equation, SolverRegistry, BurnSticks=True) # Totally not an AC Odyssey reference O_O
Alexios.FullParse()
ParsedTokens = RefactorTokens(TokenList(RefactorTokens(Alexios.tokens)))
if Debug:
	print(ParsedTokens)
print(SimplifyEquation(ParsedTokens))