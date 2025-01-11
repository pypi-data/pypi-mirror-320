from ea_model.model.ea.exception import EAMethodCallError
from ea_model.model.ea.type_def import EAObjectType


class EACollection:
    def __init__(self):
        self.Count = 0                                  # type: int
        self.ObjectType = None                          # type: EAObjectType

    def AddNew(self, name: str, type: str):
        raise EAMethodCallError()

    def Delete(self, index: int):
        raise EAMethodCallError()

    def GetAt(self, index: int):
        raise EAMethodCallError()

    def DeleteAt(self, index: int, refresh: bool):
        raise EAMethodCallError()

    def Refresh(self):
        raise EAMethodCallError()

    def Update(self):
        raise EAMethodCallError()