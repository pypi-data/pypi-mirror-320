from ...model.ea.collection import EACollection
from ...model.ea.diagram import Diagram
from ...model.ea.exception import EAMethodCallError
from ...model.ea.type_def import EAObjectType
from enum import IntEnum

class EATaggedValue:
    def __init__(self):
        self.ElementID = 0
        self.FQName = ""
        self.Name = ""
        self.Notes = ""
        self.ObjectType = None # type: EAObjectType
        self.PropertyGUID = ""
        self.PropertyID = 0
        self.Value = ""

    def GetAttribute(self, prop_name: str) -> str:
        raise EAMethodCallError()

    def GetLastError(self) ->str:
        raise EAMethodCallError()

    def HasAttributes(self)-> bool:
        raise EAMethodCallError()

    def SetAttribute(self, prop_name: str, prop_value:str):
        raise EAMethodCallError()

    def Update(self):
        raise EAMethodCallError()

class EAPropertyType:
    def __init__(self):
        self.Description = ""
        self.Detail = ""
        self.ObjectType = ""
        self.Tag = ""

class EAEnumRelationSetType(IntEnum):
    rsGeneralizeStart = 0
    rsGeneralizeEnd = 1
    rsRealizeStart = 2
    rsRealizeEnd = 3
    rsDependStart = 4
    rsDependEnd = 5
    rsParents = 6

class EAConnectorEnd:
    def __init__(self):
        self.Aggregation = 0
        self.Alias = ""
        self.AllowDuplicates = False
        self.Cardinality = ""
        self.Constraint =  ""
        self.Containment= ""
        self.Derived = False
        self.DerivedUnion = False
        self.End = ""
        self.IsChangeable = "" # 'frozen', 'addOnly' or none.
        self.IsNavigable = False
        self.Navigable = "" 
        self.ObjectType = None # ObjectType
        self.Role = ""
        self.RoleType = ""

    def GetLastError(self):
        raise EAMethodCallError()

    def Update(self):
        raise EAMethodCallError()
 
class EAConnector:
    def __init__(self):
        self.Alias = ""
        self.AssociationClass = None                        # type: EAElement
        self.ClientEnd = None                               # type: EAConnectorEnd 
        self.ConnectorGUID = ""
        self.ConnectorID = 0
        self.Constraints = None                             # type: EACollection
        self.ConveyedItems = None                           # type: EACollection
        self.CustomProperties = None                        # type: EACollection
        self.DiagramID = 0
        self.Direction = ""
        self.EndPointX = 0
        self.EndPointY = 0
        self.EventFlags = ""
        self.FQStereotype = ""
        self.ForeignKeyInformation = ""
        self.IsLeaf = False
        self.IsRoot = False
        self.IsSpec = False
        self.MessageArguments = ""
        self.MetaType = ""
        self.MiscData = ""
        self.Name = ""
        self.Notes = ""
        self.ObjectType = None # type: EAObjectType
        self.Properties = None # type: Properties
        self.ReturnValueAlias = ""
        self.RouteStyle = 0
        self.SequenceNo = 0
        self.StartPointX = 0
        self.StartPointY = 0
        self.StateFlags = 0
        self.Stereotype = ""
        self.StereotypeEx = ""
        self.StyleEx = ""
        self.Subtype = ""
        self.SupplierEnd = ""
        self.SupplierID = 0
        self.TaggedValues = None

        self.Type  = ""

    def GetLastError(self):
        raise EAMethodCallError()

    def IsConnectorValid(self):
        raise EAMethodCallError()

    def Update(self):
        raise EAMethodCallError()

class EAElement:
    def __init__(self):
        self.Abstract = ""
        self.ActionFlags = ""
        self.Alias = ""
        self.AssociationClassConnectorID = 0
        self.Attributes = None  # type: EACollection
        self.AttributesEx = None  # type: EACollection
        self.Author = ""
        self.BaseClasses = None  # type: EACollection
        self.ClassfierID = 0
        self.ClassifierID = 0
        self.ClassifierName = ""
        self.ClassifierType = ""
        self.Complexity = ""
        self.CompositeDiagram = None                # type: Diagram
        self.Connectors = None                      # type: EACollection
        self.Constraints = None                     # type: EACollection
        self.ConstraintsEx = None                   # type: EACollection
        self.Created = ""                           # type: Date
        self.CustomProperties = None
        self.Diagrams = None                        # type: EACollection
        self.Difficulty = ""
        self.Efforts = None                         # type: EACollection
        self.ElementGUID = ""
        self.ElementID = 0
        self.Elements = None                        # type: EACollection
        self.EmbeddedElements = None                # type: EACollection
        self.EventFlags = ""
        self.Files = None                           # type: EACollection
        self.GenFile = ""
        self.Genlinks = ""
        self.Gentype = ""
        self.IsComposite = False
        self.IsLeaf = False
        self.IsNew = False
        self.IsSpec = False
        self.Issues = None                          # type: EACollection
        self.Locked = False
        self.MetaType = ""
        self.Methods = None                         # type: EACollection
        self.MethodsEx = None                       # type: EACollection
        self.Name = ""
        self.Notes = ""
        self.ObjectType = None                      # type: EAObjectType
        self.PackageID = 0
        self.ParentID = 0
        self.Properties = None                      # type: EACollection
        self.PropertyType = None                    # type: EAPropertyType
        self.Requirements = None                    # type: EACollection
        self.Stereotype = ""
        self.StereotypeEx = ""
        self.Tag = ""
        self.TaggedValues = None                    # type: EACollection
        self.TaggedValuesEx = None                  # type: EACollection
        self.Tests = None                           # type: EACollection
        self.Type = ""

    def GetRelationSet(self, type: EAEnumRelationSetType):
        raise EAMethodCallError()

    def Refresh(self):
        raise EAMethodCallError()

    def Update(self):
        raise EAMethodCallError()

class EAParameter:
    def __init__(self):
        self.Alias = ""
        self.ClassifierID = ""
        self.Default = ""
        self.IsConst = ""
        self.Kind = ""
        self.Name = ""
        self.Notes = ""
        self.ObjectType = None                      # type: EAObjectType
        self.OperationID = 0
        self.ParameterGUID = ""
        self.Position = 0
        self.Stereotype = ""
        self.StereotypeEx = ""
        self.Type = ""

    def Update(self):
        raise EAMethodCallError()

class EAMethod:
    def __init__(self):
        self.Abstract  = False
        self.Behavior = ""
        self.ClassifierID = ""
        self.Code = ""
        self.Concurrency = ""
        self.FQStereotype = ""
        self.IsConst = False
        self.IsLeaf = False
        self.IsPure = False
        self.IsQuery = False
        self.IsRoot = False
        self.IsStatic = False
        self.IsSynchronized = False
        self.MethodGUID = ""
        self.MethodID = 0
        self.Name = ""
        self.Notes = ""
        self.ObjectType = None                  # type: EAObjectType
        self.Parameters = None                  # type: EACollection
        self.ParentID = 0
        self.Pos = 0
        self.PostConditions = None              # type: EACollection
        self.PreConditions = None               # type: EACollection
        self.ReturnIsArray = False
        self.ReturnType = ""
        self.StateFlags = ""
        self.Stereotype = ""
        self.StereotypeEx =""
        self.Style = ""
        self.StyleEx = ""
        self.TaggedValues = None                # type: EACollection
        self.Throws = ""
        self.Visibility = ""

    def Update(self):
        raise EAMethodCallError()


class EAProject:
    def __init__(self):
        pass


class EAReference:
    def __init__(self):
        pass


class EAPackage:
    def __init__(self):
        self.BatchLoad = 0
        self.BatchSave = 0
        self.CodePath = ""
        self.Connectors = None                  # type: EACollection
        self.Diagrams = None                    # type: EACollection
        self.Elements = None                    # type: EACollection
        self.Name = ""
        self.Notes = ""
        self.ObjectType = 5
        self.Owner = ""
        self.Packages = None                    # type: EACollection
        self.PackageId = 0
        self.PackageGUID = ""
        self.ParentId = 0
        self.StereotypeEx = ""

    def FindObject(self, dotted_id: str):
        raise EAMethodCallError()

    def Update(self):
        raise EAMethodCallError()

class EAAttribute:
    def __init__(self):
        self.Alias = ""
        self.AllowDuplicates = False
        self.AttributeGUID = ""
        self.AttributeID = 0
        self.ClassifierID = 0
        self.Container = ""
        self.Containment = ""
        self.Constraints = None                 # type: EACollection
        self.Default = ""
        self.FQStereotype = ""
        self.IsCollection = False
        self.IsConst = False
        self.IsDerived = False
        self.IsID = False
        self.IsOrdered = False
        self.IsStatic = False
        self.Length = ""
        self.LowerBound = ""
        self.Name = ""
        self.Notes =""
        self.ObjectType = None                  # type: EAObjectType
        self.ParentID = 0
        self.Pos = 0
        self.Precision = ""
        self.RedefinedProperty = ""
        self.Scale = ""
        self.Stereotype = ""
        self.StereotypeEx = ""
        self.SubsettedProperty = ""
        self.TaggedValues = None                # type: EACollection
        self.TaggedValuesEx = None              # type: EACollection
        self.Type = ""
        self.UpperBound = ""
        self.Visibility = ""
    
    def Update(self):
        raise EAMethodCallError()

class EARepository:
    def __init__(self):
        self.Authors = None                     # type: EACollection
        self.BatchAppend = False
        self.Clients = None                     # type: EACollection
        self.ConnectionString = ""
        self.Datatypes = None                   # type: EACollection
        self.EnableUIUpdates = False
        self.FlagUpdate = False
        self.InstanceGUID = ""
        self.IsSecurityEnabled = False
        self.Issues = None                      # type: EACollection
        self.Models = None                      # type: EACollection
        self.ProjectGUID = ""
        self.Terms = None                       # type: EACollection

    def CloseFile(self):
        raise EAMethodCallError()

    def GetAttributeByGuid(self, guid: str) -> EAAttribute:
        raise EAMethodCallError()

    def GetAttributeByID(self, id: str) -> EAAttribute:
        raise EAMethodCallError()

    def GetConnectorByGuid(self, guid: str):
        raise EAMethodCallError()

    def GetConnectorByID(self, connector_id: int):
        raise EAMethodCallError()

    def GetContextItem(self, obj):
        raise EAMethodCallError()

    def GetContextItemType(self):
        raise EAMethodCallError()

    def GetContextObject(self):
        raise EAMethodCallError()

    def GetCounts(self) -> str:
        raise EAMethodCallError()

    def GetCurrentDiagram(self) -> Diagram:
        raise EAMethodCallError()

    def GetDiagramByGuid(self, guid: str) -> Diagram:
        raise EAMethodCallError()

    def GetDiagramByID(self, id: int) -> Diagram:
        raise EAMethodCallError()

    def GetElementByGuid(self, guid: str) -> EAElement:
        raise EAMethodCallError()

    def GetElementByID(self, id: int) -> EAElement:
        raise EAMethodCallError()

    def GetElementsByQuery(self, query_name: str, search_term: str) -> EACollection:
        raise EAMethodCallError()

    def GetElementSet(self, id_list: str, options: int) -> EACollection:
        raise EAMethodCallError()

    def GetLastError(self) -> str:
        raise EAMethodCallError()

    def GetLocalPath(self, type: str, path: str) -> str:
        raise EAMethodCallError()

    def GetMethodByGuid(self, guid: str) -> EAMethod:
        raise EAMethodCallError()

    def GetMethodById(self, id: int) -> EAMethod:
        raise EAMethodCallError()

    def GetPackageByGuid(self, guid: str) -> EAPackage:
        raise EAMethodCallError()

    def GetPackageByID(self, id: int) -> EAPackage:
        raise EAMethodCallError()

    def GetProjectInterface(self) -> EAProject:
        raise EAMethodCallError()

    def GetReferenceList(self, type: str) -> EAReference:
        ''' Type:
            Diagram, Element, Constraint, Requirement, Connector
            Status, Cardinality, Effort, Metric, Scenario, Status
            Test, List:DifficultyType, List:PriorityType
            List:TestStatusType, List:ConstStatusType
        '''
        raise EAMethodCallError()

    def GetTreeSelectedElements(self) -> EACollection:
        raise EAMethodCallError()

    def GetTreeSelectedItem(self, object) -> EAObjectType:
        raise EAMethodCallError()

    def GetTreeSelectedItemType(self, object) -> EAObjectType:
        raise EAMethodCallError()

    def GetTreeSelectedObject(self, object):
        raise EAMethodCallError()

    def GetTreeSelectedPackage(self) -> EAPackage:
        raise EAMethodCallError()

    def OpenFile(self, filename: str) -> bool:
        raise EAMethodCallError()

    def SQLQuery(self, query: str) -> bool:
        raise EAMethodCallError()


class EAModel:
    def __init__(self):
        self.Name = ""
        self.PackageID = 0
        self.Packages = None                        # type: EACollection

    def Update(self):
        raise EAMethodCallError()


class EAApp:
    def __init__(self):
        self.Project = ""
        self.Repository = None                      # type: EARepository
        self.Visible = False                        # type: bool
