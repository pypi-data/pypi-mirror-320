import win32com.client
import sys
import json
import re
import logging

from ...model.ea.element import EAPackage, EAApp, EARepository, EAElement, EAMethod, EAAttribute, EAParameter, EATaggedValue
from ...model.ea.diagram import Diagram

class EAInstance:
    GUID_PACKAGES = "packages"
    GUID_MODELS = "models"
    GUID_ELEMENTS = "elements"
    GUID_METHODS = "methods"
    GUID_ATTRIBUTES = "attributes"
    GUID_DIAGRAMS = "diagrams"
    GUID_PORTS = "ports"

    def __init__(self):
        self._app = None         # type: EAApp
        self._connect()
        self._guid = {
            EAInstance.GUID_PACKAGES: {},
            EAInstance.GUID_MODELS: {},
            EAInstance.GUID_ELEMENTS: {},
            EAInstance.GUID_METHODS: {},
            EAInstance.GUID_ATTRIBUTES: {},
            EAInstance.GUID_DIAGRAMS: {},
            EAInstance.GUID_PORTS: {},
        }
        self._project_prefix = ""
        self.logger = logging.getLogger()

    def getRootPackage(self) -> EAPackage:
        print(self.getRepository().Models)

    def setProjectPrefix(self, prefix):
        self._project_prefix = prefix

    def getApp(self) -> EAApp:
        return self._app

    def getRepository(self) -> EARepository:
        return self._app.Repository

    def getModel(self, name: str) -> EAPackage:
        guid = self.getGuid(EAInstance.GUID_MODELS, name)
        model = None
        if (guid != None):
            model = self.getRepository().GetPackageByGuid(guid)
            if (model == None):
                self.removeGuid(EAInstance.GUID_MODELS, name)
        if (model == None):
            for idx in range(0, self.getRepository().Models.Count):
                current_model = self.getRepository().Models.GetAt(idx)  # type: EAPackage
                self.addGuid(EAInstance.GUID_MODELS, current_model.Name, current_model.PackageGUID)
                if (current_model.Name == name):
                    model = current_model
                    break
        return model

    def _connect(self):
        try:
            self._app = win32com.client.gencache.EnsureDispatch('EA.App')  # type: EAApp
            #models = self.eaRep.models
        except Exception as e:
            #print(e)
            sys.stderr.write("Unable to connect to EA\n")
            raise e

    def findOrCreateModel(self, name: str) -> EAPackage:
        model = self.getModel(name)
        if (model == None):
            model = self.getRepository().Models.AddNew(name, "")  # type: EAPackage
            model.Update()
            self.getRepository().Models.Refresh()
            self.addGuid(EAInstance.GUID_MODELS, model.Name, model.PackageGUID)

        return model

    def findSubPackage(self, parent: EAPackage, name: str) -> EAPackage:
        for idx in range(0, parent.Packages.Count):
            currentPackage = parent.Packages.GetAt(idx)  # type: EAPackage
            if (currentPackage.Name == name):
                return currentPackage
        return None

    def findPackageRecursive(self, parent: EAPackage, name: str) -> EAPackage:
        if (parent.Name == name):
            return parent

        for idx in range(0, parent.Packages.Count):
            currentPackage = parent.Packages.GetAt(idx)  # type: EAPackage
            self.addGuid(EAInstance.GUID_PACKAGES,
                         currentPackage.Name, currentPackage.PackageGUID)
            childPackage = self.findPackageRecursive(currentPackage, name)
            if (childPackage != None):
                return childPackage
        return None
    
    def findPackage(self, package: EAPackage, referred_name:str) -> EAPackage:
        name_list = referred_name.split("/")
        if len(name_list) == 1:
            return self.findOneLevelPackage(package, referred_name)
        
        for name in name_list:
            if (name == ""):
                continue
            package = self.findSubPackage(package, name)
            if (package == None):
                return None
            #    raise ValueError("The %s of reference <%s> does not exist." % (short_name, referred_name))
        return package

    def findOneLevelPackage(self, parent: EAPackage, name: str) -> EAPackage:
        package = None
        guid = self.getGuid(EAInstance.GUID_PACKAGES, name)
        if (guid != ""):
            package = self.getRepository().GetPackageByGuid(guid)
        if (package == None):
            self.logger.debug("Find in recursive: %s" % name)
            package = self.findPackageRecursive(parent, name)
        return package

    def findOrCreatePackage(self, parent: EAPackage, name: str, skip_guid = False) -> EAPackage:
        if (skip_guid == False):
            package = self.findOneLevelPackage(parent, name)
        else:
            package = self.findSubPackage(parent, name)

        if (package == None):
            package = parent.Packages.AddNew(name, "")  # type: EAPackage
            package.Update()
            if (skip_guid == False):
                self.addGuid(EAInstance.GUID_PACKAGES, package.Name, package.PackageGUID)
        return package

    def getElementGuidKey(self, primary_key: str, secondary_key: str) -> str:
        return "%s-%s" % (primary_key, secondary_key)

    def findSubElement(self, parent: EAPackage, name: str, meta_type: str) -> EAPackage:
        for idx in range(0, parent.Elements.Count):
            current_element = parent.Elements.GetAt(idx)  # type: EAElement
            if (current_element.Name == name and current_element.MetaType == meta_type):
                return current_element
        return None

    def findElement(self, parent: EAPackage, name: str, meta_type: str) -> EAElement:
        guid = self.getGuid(EAInstance.GUID_ELEMENTS, self.getElementGuidKey(name, meta_type))
        element = None
        if (guid != ""):
            element = self.getRepository().GetElementByGuid(guid)
            if (element == None):
                self.removeGuid(EAInstance.GUID_ELEMENTS, self.getElementGuidKey(name, meta_type))
        if (element == None):
            for idx in range(0, parent.Elements.Count):
                current_element = parent.Elements.GetAt(idx)  # type: EAElement
                self.addGuid(EAInstance.GUID_ELEMENTS, self.getElementGuidKey(current_element.Name, current_element.MetaType), current_element.ElementGUID)
                if (current_element.Name == name and current_element.MetaType == meta_type):
                    element = current_element
                    break
        return element

    def removeElement(self, parent: EAPackage, name: str, meta_type: str):
        for idx in range(0, parent.Elements.Count):
            current_element = parent.Elements.GetAt(idx)  # type: EAElement
            print(current_element.Name)
            if (current_element.Name == name and current_element.MetaType == meta_type):
                #print(f"Find {name}")
                parent.Elements.DeleteAt(idx, False)
        
    def findOrCreateElement(self, parent: EAPackage, name: str, meta_type: str, skip_guid = False) -> EAElement:
        try:
            if (skip_guid == False):
                element = self.findElement(parent, name, meta_type)
            else:
                element = self.findSubElement(parent, name, meta_type)

            if (element == None):
                element = parent.Elements.AddNew(name, meta_type)  # type: EAElement
                self.addGuid(EAInstance.GUID_ELEMENTS, self.getElementGuidKey(element.Name, element.MetaType), element.ElementGUID)

            element.Update()
            parent.Elements.Refresh()
                
            return element
        except Exception as err:
            if (err.excepinfo[2] == "Element locked"):
                print("EA Element <%s> is locked" % name)
                raise err
            
    def findOrCreateObject(self, parent: EAPackage, name: str) -> EAElement:
        return self.findOrCreateElement(parent, name, "Object", True)
    
    """ def findMethod(self, parent: Element, name: str) -> Method:
        guid = self.getGuid(EAInstance.GUID_METHODS, name)
        method = None
        if (guid != ""):
            method = self.getRepository().GetMethodByGuid(guid)
            if (method == None):
                self.removeGuid(EAInstance.GUID_METHODS, name)
        if (method == None):
            for idx in range(0, parent.Methods.Count):
                current_method = parent.Methods.GetAt(idx)  # type: Method
                self.addGuid(EAInstance.GUID_METHODS, current_method.Name, current_method.MethodGUID)
                if (current_method.Name == name):
                    method = current_method
                    break
        return method """

    def findConnector(self, parent: EAElement, name: str) -> EAMethod:
        for idx in range(0, parent.Connectors.Count):
            current_connector = parent.Connectors.GetAt(idx)  # type: EAMethod
            #self.addGuid(EAInstance.GUID_METHODS, current_method.Name, current_method.MethodGUID)
            if (current_connector.Name == name):
                return current_connector
        return None

    def findOrCreateConnector(self, parent: EAElement, name: str, type: str) -> EAMethod:
        method = self.findMethod(parent, name)
        if (method == None):
            method = parent.Connectors.AddNew(name, type)  # type: EAMethod
            method.Update()
            parent.Methods.Refresh()
        return method
    
    def findMethod(self, parent: EAElement, name: str) -> EAMethod:
        for idx in range(0, parent.Methods.Count):
            current_method = parent.Methods.GetAt(idx)  # type: EAMethod
            #self.addGuid(EAInstance.GUID_METHODS, current_method.Name, current_method.MethodGUID)
            pattern = r'(?:\[[\w_]*\])?\s*' + '(%s)' % name
            match = re.match(pattern, current_method.Name)
            if (match):
                return current_method
            #if (current_method.Name == name):
            #    return current_method
        return None

    def findOrCreateMethod(self, parent: EAElement, name: str, return_type: str) -> EAMethod:
        method = self.findMethod(parent, name)
        if (method == None):
            method = parent.Methods.AddNew(name, return_type)  # type: EAMethod

        name = self.formatInterfaceID("M", method.MethodID, name)
        method.Name = name
        method.Update()
        parent.Methods.Refresh()
        #self.addGuid(EAInstance.GUID_METHODS, method.Name, method.MethodGUID)            
        return method

    def findParameter(self, parent: EAMethod, name: str) -> EAParameter:
        for idx in range(0, parent.Parameters.Count):
            current_parameter = parent.Parameters.GetAt(idx)  # type: EAParameter
            if (current_parameter.Name == name):
                return current_parameter
        return None

    def findOrCreateParameter(self, parent: EAMethod, name: str, data_type: str, direction: str) -> EAParameter:
        parameter = self.findParameter(parent, name)
        if (parameter == None):
            parameter = parent.Parameters.AddNew(name, "")  # type: EAParameter
        parameter.Kind = direction
        parameter.Type = data_type
        parameter.Update()
        parent.Parameters.Refresh()
        return parameter

    """ def findAttribute(self, parent: Element, name: str) -> Attribute:
        guid = self.getGuid(EAInstance.GUID_ATTRIBUTES, name)
        attribute = None
        if (guid != ""):
            attribute = self.getRepository().GetAttributeByGuid(guid)
            if (attribute == None):
                self.removeGuid(EAInstance.GUID_ATTRIBUTES, name)
        if (attribute == None):
            for idx in range(0, parent.Attributes.Count):
                current_attribute = parent.Attributes.GetAt(idx)  # type: Attribute
                self.addGuid(EAInstance.GUID_ATTRIBUTES, current_attribute.Name, current_attribute.AttributeGUID)
                if (current_attribute.Name == name):
                    attribute = current_attribute
                    break
        return attribute """

    def findAttribute(self, parent: EAElement, name: str) -> EAAttribute:
        for idx in range(0, parent.Attributes.Count):
            current_attribute = parent.Attributes.GetAt(idx)  # type: EAAttribute
            #pattern = r'(?:\[[\w_]*\])?\s*' + '(%s)' % name
            #match = re.match(pattern, current_attribute.Name)
            #if (match):
            #    return current_attribute
            if (current_attribute.Name == name):
                return current_attribute
        return None

    def findOrCreateAttribute(self, parent: EAElement, name: str, datatype: str) -> EAAttribute:
        attribute = self.findAttribute(parent, name)
        if (attribute == None):
            attribute = parent.Attributes.AddNew(name, datatype) # type: EAAttribute
        #attribute.Name = name
        attribute.Update()
        parent.Methods.Refresh()
        self.addGuid(EAInstance.GUID_ATTRIBUTES, attribute.Name, attribute.AttributeGUID)
        return attribute
    
    def updateEAObject(self, parent_pkg: EAPackage, obj: object) -> EAElement:
        '''
        Update the Object:
            New Object will be create if it does not exist. So Name attribute of obj variable is required to locate the object.

        '''

        if 'Name' not in obj.__dict__:
            raise KeyError("The Name of <%s> is required." % type(obj))

        self.logger.debug("Update EAObject <%s>" % obj.Name)
        
        ea_obj = self.findOrCreateObject(parent_pkg, obj.Name)

        for key, value in obj.__dict__.items():
            if key == 'Name':
                continue
            if value is None:
                continue
            self.logger.debug("Set Attribute <%s> to <%s>" % (key, value))
            ea_attr = self.findOrCreateAttribute(ea_obj, key, "")
            ea_attr.Default = value
            ea_attr.Visibility = "Private"
            ea_attr.Update()

        ea_obj.Update()

        return ea_obj

    def findPort(self, parent: EAElement, name: str) -> EAAttribute:
        guid = self.getGuid(EAInstance.GUID_PORTS, self.getElementGuidKey(parent.Name, name))
        port = None
        if (guid != ""):
            port = self.getRepository().GetElementByGuid(guid)
            if (port == None):
                self.removeGuid(EAInstance.GUID_PORTS, name)
        if (port == None):
            #print("find port slowly <%s, %s>" % (name, guid))
            for idx in range(0, parent.EmbeddedElements.Count):
                current_port = parent.EmbeddedElements.GetAt(idx)  # type: EAElement
                self.addGuid(EAInstance.GUID_PORTS, self.getElementGuidKey(parent.Name, current_port.Name), current_port.ElementGUID)
                if (current_port.Name == name):
                    port = current_port
                    break
        return port

    def findOrCreatePort(self, parent: EAElement, name: str, stereo_type: str, data_type_ref: int, direction: str) -> EAMethod:
        port = self.findPort(parent, name)
        if (port == None):
            port = parent.EmbeddedElements.AddNew(name, "Port") # type: EAAttribute
            self.addGuid(EAInstance.GUID_PORTS, self.getElementGuidKey(parent.Name, port.Name), port.ElementGUID)
        port.StereotypeEx = stereo_type
        port.PropertyType = data_type_ref
        #port.Type = data_type
        port.Update()

        self.findOrCreateTaggedValue(port, "direction", direction)

        parent.EmbeddedElements.Refresh()
        return port

    def findTaggedValue(self, parent: EAElement, name: str) -> EATaggedValue:
        tagged_value = None
        for idx in range(0, parent.TaggedValues.Count):
            current_tagged_value = parent.TaggedValues.GetAt(idx)  # type: EATaggedValue
            if (current_tagged_value.Name == name):
                tagged_value = current_tagged_value
                break
        return tagged_value

    def findOrCreateTaggedValue(self, parent: EAElement, name: str, value: str) -> EATaggedValue:
        tagged_value = self.findTaggedValue(parent, name)
        if (tagged_value == None):
            tagged_value = parent.TaggedValues.AddNew(name, value) # type: EATaggedValue
        tagged_value.Update()
        parent.TaggedValuesEx.Refresh()
        return tagged_value

    def findTaggedExValue(self, parent: EAElement, name: str) -> EATaggedValue:
        tagged_value = None
        for idx in range(0, parent.TaggedValuesEx.Count):
            current_tagged_value = parent.TaggedValuesEx.GetAt(idx)  # type: EATaggedValue
            if (current_tagged_value.Name == name):
                tagged_value = current_tagged_value
                break
        return tagged_value

    def findOrCreateTaggedExValue(self, parent: EAElement, name: str, value: str) -> EATaggedValue:
        tagged_value = self.findTaggedExValue(parent, name)
        if (tagged_value == None):
            tagged_value = parent.TaggedValuesEx.AddNew(name, value) # type: EATaggedValue
        tagged_value.Update()
        parent.TaggedValuesEx.Refresh()
        return tagged_value

    def findDiagram(self, parent: EAElement, name: str, diag_type: str) -> Diagram:
        guid = self.getGuid(EAInstance.GUID_DIAGRAMS, self.getElementGuidKey(name, diag_type))
        diagram = None
        if (guid != ""):
            try:
                diagram = self.getRepository().GetDiagramByGuid(guid)
            except:
                pass
            if (diagram == None):
                self.removeGuid(EAInstance.GUID_DIAGRAMS, name)
        if (diagram == None):
            for idx in range(0, parent.Diagrams.Count):
                current_diagram = parent.Diagrams.GetAt(idx)  # type: Diagram
                self.addGuid(EAInstance.GUID_DIAGRAMS, self.getElementGuidKey(current_diagram.Name, diag_type), current_diagram.DiagramGUID)
                if (current_diagram.Name == name and current_diagram.Type == diag_type):
                    diagram = current_diagram
        return diagram

    def findOrCreateDiagram(self, parent: EAElement, name: str, diag_type: str) -> Diagram:
        diagram = self.findDiagram(parent, name, diag_type)
        if (diagram == None):
            diagram = parent.Diagrams.AddNew(name, diag_type) # type: Diagram
            diagram.Update()
            parent.Diagrams.Refresh()
            self.addGuid(EAInstance.GUID_DIAGRAMS, self.getElementGuidKey(diagram.Name, diagram.Type), diagram.DiagramGUID)
        return diagram

    def getGuid(self, group_name, name) -> str:
        guid = ""
        if (name in self._guid[group_name]):
            guid = self._guid[group_name][name]
        return guid

    def addGuid(self, group: str, name: str, guid: str):
        self._guid[group][name] = guid

    def removeGuid(self, group: str, name: str):
        if (name in self._guid[group]):
            del self._guid[group][name]

    def _addGuidList(self, group: str, values):
        for key in values:
            self.addGuid(group, key, values[key])

    def loadGuidFromFile(self, filename: str):
        try:
            with open(filename) as f_in:
                data = json.load(f_in)
                for group in data:
                    if (group == EAInstance.GUID_PACKAGES):
                        self._addGuidList(group, data[group])
                    elif (group == EAInstance.GUID_ATTRIBUTES):
                        self._addGuidList(group, data[group])
                    elif (group == EAInstance.GUID_DIAGRAMS):
                        self._addGuidList(group, data[group])
                    elif (group == EAInstance.GUID_ELEMENTS):
                        self._addGuidList(group, data[group])
                    elif (group == EAInstance.GUID_METHODS):
                        self._addGuidList(group, data[group])
                    elif (group == EAInstance.GUID_MODELS):
                        self._addGuidList(group, data[group])
                    elif (group == EAInstance.GUID_PACKAGES):
                        self._addGuidList(group, data[group])
                    elif (group == EAInstance.GUID_PORTS):
                        self._addGuidList(group, data[group])
                    else:
                        raise ValueError("Invalid group <%s>" % group)
        except Exception as _:
            print("Invalid Json file <%s>" % filename)

    def saveGuidToFile(self, filename: str):
        with open(filename, 'w') as json_file:
            json.dump(self._guid, json_file, indent=4, sort_keys=True)
