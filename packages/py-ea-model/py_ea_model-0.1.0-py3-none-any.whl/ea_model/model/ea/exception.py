class EAMethodCallError(Exception):
    def __init__(self):
        self.message = "The method is only for typing hint"

    def __str__(self):
        print(self.message)