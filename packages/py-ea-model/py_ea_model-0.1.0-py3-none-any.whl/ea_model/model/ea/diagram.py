from ...model.ea.collection import EACollection
from ...model.ea.exception import EAMethodCallError
from ...model.ea.type_def import EAObjectType

class Connector:
    def __init__(self):
        pass

class Diagram:
    def __init__(self):
        self.Author = ""
        self.createdData = ""
        self.cx = 0
        self.cy = 0
        self.DiagramGUID = ""
        self.DiagramID = 0
        self.DiagramLinks = None                        # type: EACollection
        self.DiagramObjects = None                      # type: EACollection
        self.ExtendedStyle = ""
        self.FilterElements = ""
        self.HighlightImports = False
        self.IsLocked = False
        self.MetaType = ""
        self.ModifiedDate = ""
        self.Name = ""
        self.Notes = ""
        self.ObjectType = None                          # type: EAObjectType
        self.Orientation = ""
        self.PackageID = 0
        self.PageHeight = 0
        self.PageWidth = 0
        self.ParentID = 0
        self.Scale = 0
        self.SelectedConnector = None                   # type: Connector
        self.SelectedObjects = None                     # type: EACollection
        self.ShowDetails = 0
        self.ShowPackageContents = False
        self.ShowPrivate = False
        self.ShowProtected = False
        self.ShowPublic = False
        self.Stereotype = ""
        self.StyleEx = ""
        self.Swimlanes = ""
        self.SwimlaneDef = None                         # type: SwimlaneDef
        self.Type = ""
        self.Version = ""

    def FindElementInDiagram(self, element_id: int) -> bool:
        raise EAMethodCallError()

    def Update(self):
        raise EAMethodCallError()
