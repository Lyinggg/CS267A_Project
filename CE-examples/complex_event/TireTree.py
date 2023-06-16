import copy
from typing import List, Tuple


Event = Tuple[str,List[int]]
EventList = List[Event]
InputActivity = Tuple[int, float]
ActivityPair = List[InputActivity]
ActivityList = List[ActivityPair]


class Node:
    def __init__(self) -> None:
        self.isEvent = False
        self.eventName = ""
        self.next = None
        self.val = -1
    
    
class TireTree:
    '''Create an empty tree. activitiesNum is the total number that all events can have'''
    
    def __init__(self, activitiesNum: int) -> None:
        self.activitiesNum = activitiesNum
        self.root = Node()
        self.queue = [[self.root.next, 1]]
    
    
    def buildTree(self, eventList: EventList) -> None:
        '''
        Build a tree by an event list as following format
        [["event Name1", [activity1, activity2, activity3,...]], ["event Name2", [activity1, activity2, activity3,...]], ...]
        where event Name is a string type, and activity is corresponding int number of label
        '''
        for event in eventList:
            eventName = event[0]
            actList = event[1]
            p = self.root
            
            for act in actList:
                if p.next is None:
                    p.next = [Node() for i in range(self.activitiesNum)]
                p = p.next[act]
            
            p.isEvent = True
            p.eventName = eventName
            
        self.queue = [[self.root.next, 1]]
            
    
    def findEventByActList(self, inputActList: ActivityList) -> List:
        '''
        find a corresponding event based on the input
        The input should be an ActitityList which contains a pair list of top n possible activities
        Take top3 activities as an example:
        ActivityList = [[[0, 0.8], [2, 0.78], [7, 0.67]], [[2, 0.93], [8, 0.87], [0, 0.5]], ...]
        '''
        possibleQueue = [[self.root.next, 1]]
        # this is the seaching queue, all possbile start point will store in to this
        # first element is the current node, and second element is the current probability of reaching there
        
        result = []
        
        inputLen = len(inputActList)
        for i in range(inputLen):
            curQueue = possibleQueue
            possibleQueue = []
            while len(curQueue) > 0:
                actPair = inputActList[i]
                elm = curQueue.pop(0)
                startPoint = elm[0]
                prob = elm[1]
                
                for act in actPair:
                    activity = act[0]
                    actProb = act[1]
                    if startPoint is not None:
                        if startPoint[activity].isEvent and i == inputLen -1:
                            event = [startPoint[activity].eventName, prob*actProb]
                            result.append(event)
                            
                        elif startPoint[activity].next is not None:
                                possibleQueue.append([startPoint[activity].next, prob*actProb])
        
        return result
    
    
    def clearFEBSAqueue(self) -> None:
        '''This function used to clear the queue cache for function findEventBySingleAct'''
        self.queue = [[self.root.next, 1]]
    
    
    def findEventBySingleAct(self, actPair: ActivityPair) -> List:
        '''
        find event by single activity, it will accumulate all possible outcomes in self.queue
        return value is a list of all possible event at this point
        Thus it only support track one input stream, and must manually clear the queue cache by call clearFEBSAqueue
        before start a new track
        
        input should be a pair of top n possible activities at one time, take top3 as example:
        the input should looks like following:
        [[0, 0.8], [2, 0.78], [7, 0.67]]
        '''
        result = []
        curQueue = self.queue
        self.queue = []
        while len(curQueue) > 0:
            elm = curQueue.pop(0)
            startPoint = elm[0]
            prob = elm[1]
            
            for act in actPair:
                activity = act[0]
                actProb = act[1]
                if startPoint is not None:
                    if startPoint[activity].isEvent:
                        event = [startPoint[activity].eventName, prob*actProb]
                        result.append(event)
                    if startPoint[activity].next is not None:
                        self.queue.append([startPoint[activity].next, prob*actProb])
        
        return result
    
    def findFuturePossibleEvent(self) -> List:
        '''
        This function will return all possbile future event
        based on current queue cache build by findEventBySingleAct
        '''
        
        result = []
        
        tempQueue = copy.deepcopy(self.queue)
        
        while len(tempQueue) > 0:
            startPoint, _ = tempQueue.pop(0)
            if startPoint is not None:
                for e in startPoint:
                    if e.isEvent:
                        result.append(e.eventName)
                    if e.next is not None:
                        tempQueue.append([e.next, 1])
                        
        return result
    
    def calcProb(self, inputData):
        result = []
        actTemp = []
        temp = []
        for i in range(0,4):
            
            prob = 1
            for j in range(0,4): 
                prob *= inputData[j][i]
            temp.append([i, prob])
        result.append(temp)
        
        temp = []
        for i in range(0,4):
            prob = 1
            for j in range(4,7):
                prob *= inputData[j][i]
            temp.append([i, prob])
        result.append(temp)
        
        temp = []
        for i in range(0,4): 
            prob = 1
            for j in range(7,10):
                prob *= inputData[j][i]
            temp.append([i, prob])
        result.append(temp)
        
        return result
    
    def oneHotPredict(self, actListBatch):
        '''
        Input: a batch of predicted activity list. For example:
        [
            [1,1,1,1,2,2,2,0,0,0],
            [1,1,1,1,1,2,0,2,0,0],
            ...
        ]
        Output: will be a batch of int value of event prediction
        '''
        eventPredictBatch = []
        
        actListBatch = actListBatch
        for actList in actListBatch:
            actProb =  self.calcProb(actList)
            #print(actProb)
            result = self.findEventByActList(actProb)
            sortedResult = sorted(result, reverse=True, key=lambda x: x[1])
            eventPredictBatch.append(int(sortedResult[0][0]))
        
        return eventPredictBatch
        