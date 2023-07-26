class CustomQueue(object):
    # 初始化队列
    def __init__(self):
        self.items = []

    # 入队
    def enqueue(self, item):
        self.items.append(item)

    # 出队
    def dequeue(self):
        if self.is_Empty():
            print("当前队列为空！！")
        else:
            return self.items.pop(0)

    # 判断是否为空
    def is_Empty(self):
        return self.items == []

    # 队列长度
    def size(self):
        return len(self.items)

    # 返回队头元素，如果队列为空的话，返回None
    def front(self):
        if self.is_Empty():
            print("当前队列为空！！")
        else:
            return self.items[len(self.items) - 1]