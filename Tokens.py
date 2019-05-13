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
			
			Simplified.parent = self.parent
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
				Knu = getattr(math, self.data.lower())( *right.packageNumbers() )
				Simplified = NumberToken(self.line, self.column, self.truePosition, Knu)
			Simplified.parent = self.parent
			self.parent[selfPosition] = Simplified
			del self.parent[selfPosition+1]
			if not isinstance(self.parent, list):
				self.parent.recast()

	@classmethod
	def isValidCharacter(cls, char):
		return char.lower()	in "abcdefghijklmnpqrstuvwxyz" # This makes it so this *has* to be the last token in the registry

class ComparisonToken(alexis.Token):
	
	identifiers = "=><"

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)

class GroupingToken(alexis.Token):
	
	identifiers = "()"
	OnlyOne = True

	def __init__(self, lineNum, columnNum, truePosition, data):
		super().__init__(lineNum, columnNum, truePosition, data)
