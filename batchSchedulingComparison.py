import sys
import os

'''
Author: Antonio Lang
Date: March 30, 2022

This program simulates the process execution by the following scheduling algorithms: Shortest First, First-Come-First-Serve, and Priority.
The program than outputs the average turnaround and wait time for the processes based on the given scheduling algorithm.
'''

'''
Shortest first, first come first serve, and priority scheduling algoirthms are similar since they all examine a process's characteristics and schedule process execution.
Shortest first and priority are similar since they change which process is executed based on a process's characteristic even during execution of another process.
For example, if shortest first is executing a process with a burst time of 50 and one arrives with a burst time of 30, it will switch to executing the second one.
Similarly if priority is executing a process with a priority of 3, and another arrives with priority 1, it will switch to executing the new process.
In contrast, first come first serve only looks at arrival time and compares PIDs in the event there are processes with the same arrival time.
The scheduling algorithms differ on the characteristic they examine. Shortest first checks burst time, priority checks priority, and first come first serve checks arrival time.
Shortest first and priority also examine arrival time but are primarily concerned with each's respective characteristic.

'''


class Job:
    def __init__ (self, PID, arrTime, burstTime, priority):
        self.PID = PID
        self.arrTime = arrTime
        self.burstTime = burstTime
        self.priority = priority

    def __repr__(self):
        return "[" + str(self.PID) + ", " + str(self.arrTime) + ", " + str(self.burstTime) + ", " + str(self.priority) + "]"

    def getPID(self):
        return self.PID
    def getArrTime(self):
        return self.arrTime
    def getBurstTime(self):
        return self.burstTime
    def getPriority(self):
        return self.priority

def main():

    # requests user for proper arguments until provided
    if (len(sys.argv) != 3):
        tempLine = []
        sys.argv = ['']
        while (len(tempLine) != 2):
            print ("Incorrect input")
            print ("Please enter arguments as: 'BatchfileName.txt' 'SchedulingAlgorithm'")
            line = input()
            tempLine = line.split(' ')
        sys.argv.append(tempLine[0])
        sys.argv.append(tempLine[1])

    # gets information from appropriate CLA index
    fileName = sys.argv[1]
    algorithm = sys.argv[2]
    batchFileJobs = readBatchFile(fileName)
    burstTimes = []
    arrivalTimes = []

    # checks if providied algorithm is valid
    validAlgo = algorithm == 'FCFS' or algorithm == 'ShortestFirst' or algorithm == 'Priority'

    if (validAlgo == False):
        print ("Valid process scheduling algorithms are 'FCFS', 'ShortestFirst', and 'Priority'.")

    # continue program if file has data and proper scheduling algorithm provided
    if (len(batchFileJobs) > 0 and validAlgo == True):

        # calls propor algorithm
        if algorithm == 'FCFS':
            completionTime, PIDs = FirstComeFirstServedSort(batchFileJobs)
        elif algorithm == 'ShortestFirst':
            completionTime, PIDs = ShortestJobFirstSort(batchFileJobs)
        elif algorithm == 'Priority':
            completionTime, PIDs = PrioritySort(batchFileJobs)


        print ("PID ORDER OF EXECUTION")
        for x in PIDs:
            print (x)

        for job in batchFileJobs:
            burstTimes.append(job.getBurstTime())
            arrivalTimes.append(job.getArrTime())

        avgTurnaround, turnaroundTimes = AverageTurnaround(completionTime, arrivalTimes)
        print ("Average Process Turnaround Time: %.2f" % avgTurnaround)
        print ("Average Process Wait Time: %.2f" % AverageWait(turnaroundTimes, burstTimes))


def FirstComeFirstServedSort(batchFileData):
    sortedPIDs = []
    completionTime = []
    time = 0

    # sorts by arrival time, then PID
    batchFileData.sort(key = lambda x: (x.arrTime, x.PID))

    for job in batchFileData:
        sortedPIDs.append(job.getPID())

        # if job arrives later and 'CPU' has 'downtime'
        if job.getArrTime() > time:
            time = job.getArrTime()
        time += job.getBurstTime()
        completionTime.append(time)

    return completionTime, sortedPIDs


def ShortestJobFirstSort(batchFileData):
    sortedPIDs = []
    completionTime = []
    executionOrder = []
    batchDataCopy = list(batchFileData)
    time = 0
    
    # needs additional logic to account for later arrivals with shorter time
    # sorts data by arrTime then by burstTime
    batchDataCopy.sort(key = lambda x: (x.arrTime, x.burstTime))
    executionOrder.append(batchFileData[0])
    batchDataCopy.pop(0)

    # loops through list and compares searches for any job that will complete faster than the current
    for job in executionOrder:
        for i in range (0, len(batchDataCopy)-1):
            currJobCompletion = time + job.getBurstTime()
            queuedJobCompltion = batchDataCopy[i].getArrTime() + batchDataCopy[i].getBurstTime()
            if currJobCompletion > queuedJobCompltion:
                executionOrder.append(batchDataCopy[i])
                time = batchDataCopy[i].getArrTime()
                tempJob = Job(job.getPID(), time, job.getBurstTime()-(time-job.getArrTime()), job.getPriority())
                job.burstTime = time-job.getArrTime()
                executionOrder.append(tempJob)
                batchDataCopy.pop(i)

    time = 0
    if len(batchDataCopy) > 0:
        batchDataCopy.sort(key = lambda x: x.burstTime)
        for job in batchDataCopy:
            executionOrder.append(job)
    for job in executionOrder:
        sortedPIDs.append(job.getPID())
        time += job.getBurstTime()
        completionTime.append(time)

    # accounts for the completion and burst time of any requeued process
    for i in range (0, len(executionOrder)-1):
        for j in range(i+1, len(executionOrder)-1):
            if executionOrder[i].getPID() == executionOrder[j].getPID():
                completionTime.pop(i)
                executionOrder[i].burstTime += executionOrder[j].getBurstTime()
                executionOrder.pop(j)

    for i in range(0, len(batchFileData)):
        batchFileData.pop()
    for x in executionOrder:
        batchFileData.append(x)
    batchFileData = executionOrder

    return completionTime, sortedPIDs


def PrioritySort(batchFileData):
    sortedPIDs = []
    completionTime = []
    executionOrder = []
    time = 0

    # sorts batchFileData to get first process to run
    batchFileData.sort(key = lambda x: (x.arrTime, x.priority, x.PID))
    executionOrder.append(batchFileData[0])
    batchFileData.pop(0)

    # sorts remaining processes by priority
    # requeues any job that has a greater priority value than a later-arrival process
    for i, job in enumerate(executionOrder):
        for j in range (i+1, len(batchFileData)):
            if batchFileData[j].getPriority() < job.getPriority():
                time = batchFileData[j].getArrTime()
                executionOrder.append(batchFileData[j])
                job.burstTime = job.burstTime - time
                executionOrder.append(job)
                executionOrder.pop(i)
                i -= 1
        if (len(batchFileData) > 0):
            executionOrder.append(batchFileData[0])
            batchFileData.pop(0)

    time = 0
    for job in executionOrder:
        time += job.getBurstTime()
        completionTime.append(time)
        sortedPIDs.append(job.getPID())

    # changes batchFileData to have executionOrder data
    for i in range(0, len(batchFileData)):
        batchFileData.pop()
    for job in executionOrder:
        batchFileData.append(job)

    return completionTime, sortedPIDs


def AverageTurnaround(processCompletionTime, processArrivalTimes):
    totalTurnaround = 0
    processTurnaround = []
    i = 0
    for i, value in enumerate(processCompletionTime):
        turnaround = value - processArrivalTimes[i]
        totalTurnaround += turnaround
        processTurnaround.append(turnaround)
    return totalTurnaround/(i + 1), processTurnaround


def AverageWait(processTurnaroundTimes, processBurstTime):
    totalWait = 0
    i = 0
    for i, value in enumerate(processTurnaroundTimes):
        totalWait += value - processBurstTime[i]
    return totalWait/(i + 1)


def readBatchFile(fileName):
    fileData = []
    jobList = []

    if (os.path.isfile(fileName)):
        with open(fileName, 'r') as file:
            fileData = file.readlines()

        for i, line in enumerate(fileData):
            fileData[i] = fileData[i].replace('\n', '')
            fileData[i] = fileData[i].replace(' ', '')
            x = fileData[i].split(',', 4)

            # creates new job object from the read data and appends to jobList
            jobList.append(Job(int(x[0]), int(x[1]), int(x[2]), int(x[3])))
    else:
        print ("File %s does not exist." % fileName)
    return jobList


if __name__ == "__main__":
    main()