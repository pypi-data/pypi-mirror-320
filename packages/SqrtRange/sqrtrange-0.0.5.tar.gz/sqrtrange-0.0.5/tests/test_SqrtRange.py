import SqrtRange

testfirstnumber = -10
testsecondnumber = 10
logFile = "log.log"
clearLog = True

def test():
    SqrtRange.Calculate(testfirstnumber, testsecondnumber, logFile, clearLog)
    SqrtRange.CalculateWOLogging(testfirstnumber, testsecondnumber)