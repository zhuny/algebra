import heapq


class HeapQueueSet:
    def __init__(self):
        self.queue = []
        self.queue_set = set()

    def size(self):
        return len(self.queue)

    def push(self, i):
        if i not in self.queue_set:
            heapq.heappush(self.queue, i)
            self.queue_set.add(i)

    def pop(self):
        i = heapq.heappop(self.queue)
        self.queue_set.remove(i)
        return i
