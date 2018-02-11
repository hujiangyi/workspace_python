from random import *
class BaseMath:
    def __init__(self):
        self.firstNum = 0
        self.operator = '+'
        self.secondNum = 0
        self.result = 0
    def makeMath(self):
        self.doMake()
        return self.firstNum,self.operator,self.secondNum,self.result
    def doMake(self):
        print 'doMake'
class Addition(BaseMath):
    def doMake(self):
        self.operator = '+'
        self.firstNum = randint(1,9)
        range = 10 - self.firstNum
        self.secondNum = randint(1,range)
        self.result = self.firstNum + self.secondNum
class Subtraction(BaseMath):
    def doMake(self):
        self.operator = '-'
        self.firstNum = randint(3,10)
        self.secondNum = randint(1,self.firstNum)
        self.result = self.firstNum - self.secondNum
class AddWithCarry(BaseMath):
    def doMake(self):
        self.operator = '+'
        self.firstNum = randint(1,10)
        rangeLow = 10 - self.firstNum
        rangeHigh = 20 - self.firstNum
        self.secondNum = randint(rangeLow,rangeHigh)
        self.result = self.firstNum + self.secondNum
class AbdicationSubtraction(BaseMath):
    def doMake(self):
        self.operator = '-'
        self.firstNum = randint(11,19)
        range = self.firstNum - 10
        self.secondNum = randint(range,9)
        self.result = self.firstNum - self.secondNum

types = {
    1:Addition,
    2:Subtraction,
    3:AddWithCarry,
    4:AbdicationSubtraction,
    5:AddWithCarry,
    6:AbdicationSubtraction,
    7:AddWithCarry,
    8:AbdicationSubtraction,
    9:AddWithCarry,
    10:AbdicationSubtraction
}

def dispath():
    baseMath = types[randint(1, 10)]()
    return baseMath.makeMath()
