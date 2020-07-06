#!/usr/bin/env python

class FifoArray():
    '''First In First Out Array'''
    def __init__(self, max, contents, order=None):
        self.fifo = []
        self.order = order if order else []
        self.max = max
        for i in contents:
            self.order.append(len(self.fifo))
            self.fifo.append(i)
        self.update()

    def append(self, value):
        self.order.append(len(self.fifo))
        ret = self.fifo.append(value)
        self.update()
        return(ret)

    def clear(self):
        self.order.clear()
        ret = self.fifo.clear()
        self.update()
        return(ret)

    def copy(self):
        ret = FifoArray(self.max, self.fifo, order=self.order)
        return(ret)

    def count(self, search):
        ret = self.fifo.count(search)
        return(ret)

    def extend(self, values):
        for i in values:
            self.order.append(len(self.fifo))
            self.fifo.append(i)
        self.update()
        return(self.fifo)

    def index(self, value):
        ret = self.fifo.index(value)
        return(ret)

    def insert(self, index, value):
        for i in range(len(self.order)):
            if self.order[i] >= index:
                self.order[i] += 1
        self.order.append(index)
        self.fifo.insert(index, value)
        self.update()
        return(self.fifo)

    def pop(self, index):
        for i in range(len(self.order)):
            if self.order[i] >= index:
                self.order[i] -= 1
        self.order.pop(index)
        ret = self.fifo.pop(index)
        self.update()
        return(ret)

    def remove(self, value):
        for i in range(len(self.fifo)):
            if self.fifo[i] == value:
                cur = self.order[i]
                del self.fifo[i]
                del self.order[i]
                for j in range(len(self.order)):
                    if self.order[j] >= cur:
                        self.order[j] -= 1
                break
        self.update()
        try:
            return(i)
        except UnboundLocalError:
            raise ValueError('x not in list')

    def reverse(self):
        self.order.reverse()
        self.fifo.reverse()
        self.update()
        return(self.fifo)

    def setmax(self, max):
        self.max = max
        self.update()
        return(self.max)

    def update(self):
        while len(self.fifo) > self.max:
            cur = self.order[0]
            del self.fifo[self.order[0]]
            del self.order[0]
            for i in range(len(self.order)):
                if self.order[i] >= cur:
                    self.order[i] -= 1
        print(self.fifo)
        print(self.order)

    def __add__(self, value):
        return(self.extend(value))
    def __contains__(self, value):
        return(value in self.fifo)
    def __delitem__(self, index):
        return(self.pop(index))
    def __eq__(self, value):
        return(value == self.fifo)
    def __format__(self, placeholder):
        return(str(self.fifo))
    def __getitem__(self, index):
        return(self.fifo[index])
    def __iter__(self):
        return(list(self.fifo))
    def __len__(self):
        return(len(self.fifo))
    def __ne__(self):
        return(value != self.fifo)
    def __repr__(self):
        return(str(self.fifo))
    def __str__(self):
        return(str(self.fifo))
    def __setitem__(self, index, value):
        self.fifo[index] = value
        return(self.fifo[index])



class LifoArray():
    '''Last In First Out Array'''
    def __init__(self, max, contents, order=None):
        self.lifo = []
        self.order = order if order else []
        self.max = max
        for i in contents:
            self.order.append(len(self.lifo))
            self.lifo.append(i)
        self.update()

    def append(self, value):
        self.order.append(len(self.lifo))
        ret = self.lifo.append(value)
        self.update()
        return(ret)

    def clear(self):
        self.order.clear()
        ret = self.lifo.clear()
        self.update()
        return(ret)

    def copy(self):
        ret = lifoArray(self.max, self.lifo, order=self.order)
        return(ret)

    def count(self, search):
        ret = self.lifo.count(search)
        return(ret)

    def extend(self, values):
        for i in values:
            self.order.append(len(self.lifo))
            self.lifo.append(i)
        self.update()
        return(self.lifo)

    def index(self, value):
        ret = self.lifo.index(value)
        return(ret)

    def insert(self, index, value):
        for i in range(len(self.order)):
            if self.order[i] >= index:
                self.order[i] += 1
        self.order.append(index)
        self.lifo.insert(index, value)
        self.update()
        return(self.lifo)

    def pop(self, index):
        for i in range(len(self.order)):
            if self.order[i] >= index:
                self.order[i] -= 1
        self.order.pop(index)
        ret = self.lifo.pop(index)
        self.update()
        return(ret)

    def remove(self, value):
        for i in range(len(self.lifo)):
            if self.lifo[i] == value:
                cur = self.order[i]
                del self.lifo[i]
                del self.order[i]
                for j in range(len(self.order)):
                    if self.order[j] >= cur:
                        self.order[j] -= 1
                break
        self.update()
        try:
            return(i)
        except UnboundLocalError:
            raise ValueError('x not in list')

    def reverse(self):
        self.order.reverse()
        self.lifo.reverse()
        self.update()
        return(self.lifo)

    def setmax(self, max):
        self.max = max
        self.update()
        return(self.max)

    def update(self):
        while len(self.lifo) > self.max:
            cur = self.order[-1]
            del self.lifo[self.order[-1]]
            del self.order[-1]
            for i in range(len(self.order)):
                if self.order[i] >= cur:
                    self.order[i] -= 1
        print(self.lifo)
        print(self.order)

    def __add__(self, value):
        return(self.extend(value))
    def __contains__(self, value):
        return(value in self.lifo)
    def __delitem__(self, index):
        return(self.pop(index))
    def __eq__(self, value):
        return(value == self.lifo)
    def __format__(self, placeholder):
        return(str(self.lifo))
    def __getitem__(self, index):
        return(self.lifo[index])
    def __iter__(self):
        return(list(self.lifo))
    def __len__(self):
        return(len(self.lifo))
    def __ne__(self):
        return(value != self.lifo)
    def __repr__(self):
        return(str(self.lifo))
    def __str__(self):
        return(str(self.lifo))
    def __setitem__(self, index, value):
        self.lifo[index] = value
        return(self.lifo[index])