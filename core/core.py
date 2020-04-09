from PySide2.QtCore import QRunnable

class LambdaTask(QRunnable):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        QRunnable.__init__(self)

    def run(self):
        self.func(*self.args, **self.kwargs)