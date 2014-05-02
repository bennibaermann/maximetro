class Semaphore(object):
    '''Blocks a station or (part of) a track for use with other cars'''
    
    def __init__(self):
        self.used = False
        self.queue = []

        
    def block(self,car):
            
        self.queue.append(car)
        self.used = True
        
        
    def free(self):
            
        l = len(self.queue)
        if l:
            self.queue.pop()
        if not self.queue:
            self.used = False