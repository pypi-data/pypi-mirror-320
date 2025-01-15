import NaxToPy as NP 
from NaxToPy import N2PLog
from NaxToPy.Core.N2PModelContent import N2PModelContent 
from NaxToPy.Modules.Fasteners.N2PGetFasteners import N2PGetFasteners
from NaxToPy.Modules.Fasteners.Joints.N2PJoint import N2PJoint
from NaxToPy.Modules.Fasteners._N2PFastenerAnalysis.Core.Functions.N2PGetResults import get_results  
from NaxToPy.Modules.Fasteners._N2PFastenerAnalysis.Core.Functions.N2PLoadModel import get_adjacency, import_results
import os 
import sys 
from time import time 
from typing import Union, Literal 

class N2PGetLoadFasteners: 

    """
    Class used to calculate joints' forces and bypass loads.

    The instance of this class must be prepared using its properties before calling it method calculate.
    """

    # N2PGetLoadFasteners constructor ----------------------------------------------------------------------------------
    def __init__(self): 

        """
        The constructor creates an empty N2PGetLoadFasteners instance. Its attributes must be added as properties.

        Calling example: 
            >>> import NaxToPy as n2p 
            >>> from NaxToPy.Modules.Fasteners.N2PGetFasteners import N2PGetFasteners
            >>> from NaxToPy.Modules.Fasteners.N2PGetLoadFasteners import N2PGetLoadFasteners
            >>> model1 = n2p.get_model(route.fem) # model loaded 
            >>> fasteners = N2PGetFasteners() 
            >>> fasteners.Model = model1 # compulsory input 
            >>> fasteners.Thresh = 1.5 # a custom threshold is selected (optional)
            >>> fasteners.GlobalIDList = [10, 11, 12, 13, 14] # Only some joints are to be analyzed (optional)
            >>> fasteners.GetAttachmentsBool = False # attachments will not be obtained (optional)
            >>> fasteners.calculate() # fasteners are obtained 
            >>> fasteners.ListJoints[0].Diameter = 6.0 # this joint is assigned a certain diameter 
            >>> loads = N2PGetLoadFasteners()
            >>> loads.GetFasteners = fasteners # compulsory input 
            >>> loads.ResultsFiles = [r"route1.op2", r"route2.op2", r"route3.op2"] # the desired results files are loaded
            >>> loads.AdjacencyLevel = 3 # a custom adjacency level is selected (optional)
            >>> loads.LoadCases = [1, 2, 133986] # list of load cases' ID to be analyzed (optional) 
            >>> loads.CornerData = True # the previous load cases have corner data (optional)
            >>> # some bypass parameters are changed (optional and not recommended)
            >>> loads.BypassParameters = {"max iterations" = 50, "PROJECTION TOLERANCE" = 1e-6} 
            >>> loads.DefaultDiameter = 3.6 #  joints with no previously assigned diameter will get this diameter (optional)
            >>> loads.AnalysisName = "Analysis_1" # name of the CSV file where the results will be exported (optional)
            >>> loads.ExportLocation = r"path" # results are to be exported to a certain path (optional)
            >>> loads.TypeExport = "Altair" # results will be exported in the Altair style (optional)
            >>> loads.calculate() # calculations will be made and results will be exported

        Instead of using loads.GetFasteners, the user could also set these attributes:
            >>> loads.Model = model1 # the same model is loaded, compulsory input 
            >>> loads.ListJoints = fasteners.ListJoints[0:10] # only a certain amount of joints is loaded, compulsory input 
            >>> loadFasteners.calculate() # calculations will be made with all of the default parameters and, therefore, 
            results will not be exported. 
        """
        
        self._results_files: list[str] = None 
        self._get_fasteners: N2PGetFasteners = None 
        self._list_joints: list[N2PJoint] = None 
        self._model: N2PModelContent = None 
        self._adjacency_level: int = 4
        self._load_cases: list[int] = None 
        self._corner_data: bool = False 
        self._bypass_parameters: dict = {"MATERIAL FACTOR METAL": 4.0, 
                                         "MATERIAL FACTOR COMPOSITE": 4.5, 
                                         "AREA FACTOR": 2.5, 
                                         "MAX ITERATIONS": 200, 
                                         "BOX TOLERANCE": 1e-3, 
                                         "PROJECTION TOLERANCE": 0.0}
        self._default_diameter: float = None 
        self._analysis_name: str = "JointAnalysis"
        self._export_location: str = None 
        self._type_export: Literal["NAXTOPY", "ALTAIR"] = "NAXTOPY"
        self._results: dict = None 
    # ------------------------------------------------------------------------------------------------------------------
    
    # Getters ----------------------------------------------------------------------------------------------------------
    @property
    def ResultsFiles(self) -> list[str]: 
        """
        List of paths of OP2 results files. It is a compulsory input unless the model loaded in model or in get_fasteners
        has results loaded in. 
        """

        return self._results_files
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def GetFasteners(self) -> N2PGetFasteners: 

        """
        N2PGetFasteners model. Either this, or both _list_joints and _model, is a compulsory input and an error will occur
        if this is not present.
        """

        return self._get_fasteners
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def Model(self) -> N2PModelContent: 

        """
        Model to be analyzed. Either both this and _list_joints, or _get_fasteners, are compulsory inputs and an error
        will occur if they are not present. 
        """

        return self._model 
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def ListJoints(self) -> list[N2PJoint]: 

        """
        List of N2PJoints to be analyzed. Either both this and _model, or get_fasteners, are compulsory inputs and an
        error will occur if they are not present.
        """

        return self._list_joints
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AdjacencyLevel(self) -> int: 

        """
        Number of adjacent elements that are loaded into the model. 4 by default.
        """

        return self._adjacency_level
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def LoadCases(self) -> list[int]: 

        """
        List of the IDs of the load cases to be analyzed. If no list is given, it is assumed that all load cases
        should be analyzed. 
        """
        
        return self._load_cases 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def CornerData(self) -> bool: 
        
        """
        Whether there is data on the corners or not to extract the results. False by default.
        """
        
        return self._corner_data 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BypassParameters(self) -> dict: 

        """
        Dictionary with the parameters used in the bypass loads calculation. Even though the user may change any of
        these parameters, it is not recomended. 
        """

        return self._bypass_parameters 
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def DefaultDiameter(self) -> float: 

        """
        Diameter to be applied to joints with no previously assigned diameter. 
        """
        
        return self._default_diameter
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AnalysisName(self) -> Literal["NAXTOPY", "ALTAIR"]: 

        """
        Name of the CSV file where the results are to be exported. 
        """
        
        return self._analysis_name
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ExportLocation(self) -> str: 

        """
        Path where the results are to be exported. 
        """
        
        return self._export_location
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def TypeExport(self) -> str: 

        """
        Whether the results are exported in the NaxToPy style or in the Altair style.
        """
        
        return self._type_export
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Results(self) -> dict: 
        
        """
        Results obtained in get_results_joints(). 
        """
        
        return self._results 
    # ------------------------------------------------------------------------------------------------------------------

    # Setters ----------------------------------------------------------------------------------------------------------
    @ResultsFiles.setter 
    def ResultsFiles(self, value: Union[list[str], str]): 

        # If "value" is a list, then it must be a list of op2 files. 
        if type(value) == list: 
            for i in value: 
                if not os.path.exists(i) or not os.path.isfile(i): 
                    N2PLog.Error.E531(i)
            self._results_files = value 
        elif os.path.exists(value): 
            # If "value" is a string and a file, it is a single op2 file. 
            if os.path.isfile(value): 
                self._results_files = [value]
            # If "value" is a string and not a file, it is a folder. 
            else: 
                self._results_files = import_results(value) 
        else: 
            N2PLog.Error.E531(value)
    # ------------------------------------------------------------------------------------------------------------------

    @GetFasteners.setter 
    def GetFasteners(self, value: N2PGetFasteners) -> None: 

        if self.Model is not None or self.ListJoints is not None: 
            N2PLog.Warning.W522() 

        self._get_fasteners = value 
        self._list_joints = self._get_fasteners._list_joints
        self._model = self._get_fasteners._model 
    # ------------------------------------------------------------------------------------------------------------------

    @Model.setter 
    def Model(self, value: N2PModelContent) -> None: 

        if self.GetFasteners is not None: 
            N2PLog.Warning.W523() 

        self._model = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @ListJoints.setter 
    def ListJoints(self, value: list[N2PJoint]) -> None: 

        if self.GetFasteners is not None: 
            N2PLog.Warning.W524() 

        self._list_joints = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @AdjacencyLevel.setter 
    def AdjacencyLevel(self, value: int) -> None: 

        self._adjacency_level = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @LoadCases.setter 
    def LoadCases(self, value: Union[list[int], tuple[int], set[int], int]) -> None: 
        
        if value is not None or value != []: 
            if type(value) == tuple or type(value) == set: 
                value = list(value) 
            elif type(value) == int: 
                value = [value]
            for i in value: 
                if type(i) != int: 
                    N2PLog.Error.E525(i) 

        self._load_cases = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @CornerData.setter 
    def CornerData(self, value: bool) -> None: 

        self._corner_data = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @BypassParameters.setter 
    def BypassParameters(self, value: dict) -> None: 
        
        valueUpper = {}
        for i, j in value.items(): 
            valueUpper[i.upper().strip()] = j 
        if "MATERIAL FACTOR METAL" in valueUpper.keys(): 
            if type(valueUpper["MATERIAL FACTOR METAL"]) != float and type(valueUpper["MATERIAL FACTOR METAL"]) != int: 
                valueUpper.pop("MATERIAL FACTOR METAL")
                N2PLog.Error.E528("MATERIAL FACTOR METAL")
        if "MATERIAL FACTOR COMPOSITE" in valueUpper.keys(): 
            if type(valueUpper["MATERIAL FACTOR COMPOSITE"]) != float and type(valueUpper["MATERIAL FACTOR COMPOSITE"]) != int: 
                valueUpper.pop("MATERIAL FACTOR COMPOSITE")
                N2PLog.Error.E528("MATERIAL FACTOR COMPOSITE")            
        if "AREA FACTOR" in valueUpper.keys(): 
            if type(valueUpper["AREA FACTOR"]) != float and type(valueUpper["AREA FACTOR"]) != int: 
                valueUpper.pop("AREA FACTOR")
                N2PLog.Error.E528("AREA FACTOR")
        if "MAX ITERATIONS" in valueUpper.keys(): 
            if type(valueUpper["MAX ITERATIONS"]) != int: 
                valueUpper.pop("MAX ITERATIONS")
                N2PLog.Error.E528("MAX ITERATIONS")
        if "BOX TOLERANCE" in valueUpper.keys(): 
            if type(valueUpper["BOX TOLERANCE"]) != float and type(valueUpper["BOX TOLERANCE"]) != int: 
                valueUpper.pop("BOX TOLERANCE")
                N2PLog.Error.E528("BOX TOLERANCE")
        if "PROJECTION TOLERANCE" in valueUpper.keys(): 
            if type(valueUpper["PROJECTION TOLERANCE"]) != float and type(valueUpper["PROJECTION TOLERANCE"]) != int: 
                valueUpper.pop("PROJECTION TOLERANCE")
                N2PLog.Error.E528("PROJECTION TOLERANCE")

        self._bypass_parameters.update(valueUpper)
    # ------------------------------------------------------------------------------------------------------------------
        
    @DefaultDiameter.setter 
    def DefaultDiameter(self, value: float) -> None: 

        self._default_diameter = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @AnalysisName.setter 
    def AnalysisName(self, value: str) -> None: 

        self._analysis_name = value 
    # ------------------------------------------------------------------------------------------------------------------

    @ExportLocation.setter 
    def ExportLocation(self, value: str) -> None: 

        self._export_location = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @TypeExport.setter 
    def TypeExport(self, value: Literal["NAXTOPY", "ALTAIR"]) -> None: 

        value = value.upper().replace(" ", "")
        if value == "ALTAIR" or value == "NAXTOPY": 
            self._type_export = value 
        else: 
            N2PLog.Warning.W525()
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to load only a part of the model ---------------------------------------------------------------------
    def get_model(self): 
        
        """
        Method used to load a new model with all of the results files and only certain elements.
        
        The following steps are followed: 

            1. A new model is created that includes only the elements that make up the joints, as well as all elements 
            adjacent to them in a certain radius as defined by the user. 
            2. Results files are imported to this new model. 
            3. Elements and their internal IDs are updated so that they correspond to the values of the new model. 

        Calling example: 
            >>> loads.get_model() 
        """
        
        self._model = get_adjacency(self.Model, self.ListJoints, self.AdjacencyLevel) 
        if self.ResultsFiles is not None: 
            self._model.import_results_from_files(self.ResultsFiles)

        if self.GetFasteners is not None: 
            listPlates = self._get_fasteners.ListPlates 
        else: 
            listPlates = [j for i in self.ListJoints for j in i.Plates]

        for i in listPlates: 
            i._elements = [dict(self.Model.ElementsDict)[(i.ElementsID[j], self.Model._N2PModelContent__StrPartToID[i.PartID[j]])] for j in range(len(i.ElementsID))]
        for i in self.ListJoints: 
            i.Bolt._elements = [dict(self.Model.ElementsDict)[(j, self.Model._N2PModelContent__StrPartToID[i.PartID])] for j in i.BoltElementsID]
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the load cases' results --------------------------------------------------------------------
    def get_results_joints(self): 

        """
        Method used to obtain the results of the model. If no load cases have been selected, then it is assumed that all 
        load cases are to be analyzed. In order to work, the list_joints and model attributes must have been previously 
        filled. If they have not, an error will occur. 

        The following steps are followed: 

            1. If no load cases have been selected by the user, all load cases in the model will be analyzed. 
            2. Results are obtained with the get_results() function. Its outputs are, (a), the results per se, and (b), 
            the list of broken load cases, that is, the list of load cases that lack an important result. 
            3. If there are some broken load cases, they are removed from the _load_cases attribute and. If all load 
            cases were broken (meaning that the current _load_cases attribute is empty), an error is displayed. 

        Calling example: 
            >>> loads.get_results_joints()
        """

        t1 = time() 
        if self.Model is None: 
            N2PLog.Error.E521() 
        if self.ListJoints is None: 
            N2PLog.Error.E523() 

        # If no load cases have been selected, all of them are 
        if self.LoadCases is None or self.LoadCases == []: 
            self._load_cases = [lc.ID for lc in self.Model.LoadCases]
            N2PLog.Info.I500()
        if self.LoadCases is None or self.LoadCases == []: 
            N2PLog.Error.E504()
        # Results and broken load cases are obtained 
        resultsList = get_results(self.Model, self.LoadCases, self.CornerData, self.ListJoints[0].Bolt.Type)
        self._results = resultsList[0]
        brokenLC = resultsList[1]
        # Broken load cases are removed 
        if len(brokenLC) != 0: 
            for i in brokenLC: 
                self._load_cases.remove(i)
        # If all load cases are broken, an error occurs 
        if self.LoadCases is None or self.LoadCases == []: 
            N2PLog.Critical.C520()
        N2PLog.Debug.D600(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to obtain the joint's forces -------------------------------------------------------------------------
    def get_forces_joints(self): 
        
        """
        Method used to obtain the 1D forces of each joint. In order to work, the results attribute must have been 
        previously filled (by having called get_results_joints()). If it has not, an error will occur. 

        Calling example: 
            >>> loads.get_forces_joints()
        """

        t1 = time() 
        if self.Results is None: 
            N2PLog.Error.E524() 

        for i, j in enumerate(self.ListJoints, start = 1): 
            j.get_forces(self.Results)
            self.__progress(i, len(self.ListJoints), "Processing forces.")
            if i < len(self.ListJoints): 
                sys.stdout.write("\r")
                sys.stdout.flush() 
        sys.stdout.write("\n")
        N2PLog.Debug.D606(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to obtain the joint's bypass loads -------------------------------------------------------------------    
    def get_bypass_joints(self): 

        """
        Method used to obtain the bypass loads of each joint. If an N2PJoint has no diameter, the default diameter is 
        assigned (in case it has been defined by the user). In order to work, the results attribute must have been 
        previously filled (by having called get_results_joints()). If it has not, an error will occur. 

        The following steps are followed: 

            1. If there are joints with no diameter, the default one is assigned.
            2. If there are still joints with no diameter or negative diameter (which could happen if some joints did 
            not have a diameter and no default diameter was given), these joints are removed from the list of joints, 
            as well as their associated N2PBolts and N2PPlates, and an error is displayed. 
            3. The bypass loads of each (remaining) N2PJoint is calculated. 

        Calling example: 
            >>> loads.get_bypass_joints(defaultDiameter = 4.8)
        """

        t1 = time()
        if self.Results is None: 
            N2PLog.Error.E524() 

        # Joints with no diameter are assigned one 
        for i in self.ListJoints: 
            if i.Diameter is None: 
                i._diameter = self.DefaultDiameter
        
        # Joints with no diameter are identified and removed 
        wrongJoints = [i for i in self.ListJoints if i.Diameter is None or i.Diameter <= 0]
        wrongJointsID = [i.ID for i in wrongJoints]
        if len(wrongJointsID) > 0: 
            N2PLog.Error.E517(wrongJointsID)
        
        for i in self.ListJoints: 
            if i in wrongJoints: 
                self._list_joints.remove(i)

        for i, j in enumerate(self.ListJoints, start = 1): 
            j.get_bypass_loads(self.Model, self.Results, self.CornerData, materialFactorMetal = self.BypassParameters["MATERIAL FACTOR METAL"], 
                               materialFactorComposite = self.BypassParameters["MATERIAL FACTOR COMPOSITE"], areaFactor = self.BypassParameters["AREA FACTOR"], 
                               maxIterations = self.BypassParameters["MAX ITERATIONS"], boxTol = self.BypassParameters["BOX TOLERANCE"], 
                               projTol = self.BypassParameters["PROJECTION TOLERANCE"])
            self.__progress(i, len(self.ListJoints), "Processing bypasses.")
            if i < len(self.ListJoints): 
                sys.stdout.write("\r")
                sys.stdout.flush()
        sys.stdout.write("\n")
        N2PLog.Debug.D607(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to export the obtained results to a CSV file ---------------------------------------------------------
    def export_results(self): 

        """
        Method used to export the obtained results to a CSV file. 

        Calling example: 
            >>> loads.export_results()
        """

        t1 = time()
        if self.ListJoints[0].Plates[0].AltairForce is None: 
            N2PLog.Error.E529() 
        elif self.ListJoints[0].Plates[0].BoxDimension is None: 
            N2PLog.Error.E530()
        [i.export_forces(self.Model, self.ExportLocation, self.AnalysisName, self.Results, self.TypeExport) for i in self.ListJoints]
        N2PLog.Debug.D608(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------
        
    # Method used to obtain the main fastener analysis -----------------------------------------------------------------
    def get_analysis_joints(self): 

        """
        Method used to do the previous analysis and, optionally, export the results. 

        Calling example: 
            >>> loads.get_analysis_joints()
        """

        t1 = time()
        self.get_forces_joints()
        self.get_bypass_joints()
        if self.ExportLocation is not None: 
            self.export_results()
        N2PLog.Debug.D602(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------
    
    # Method used to do the entire analysis ----------------------------------------------------------------------------
    def calculate(self): 

        """
        Method used to do all the previous calculations and, optionally, export the results. 

        Calling example: 
            >>> loads.calculate()
        """
        
        t1 = time()
        self.get_model()
        self.get_results_joints() 
        self.get_analysis_joints()
        N2PLog.Debug.D604(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------
        
    def __progress(self, count: int, total: int, suffix: str = "") -> None:

        """
        Method used to display a progress bar while the bypass loads are calculated. 

        Args:
            count: int -> current progress. 
            total: int -> total progress. 
            suffix: str -> optional suffix to be displayed alongside the progress bar. 
        """

        barLength = 60
        filledLength = int(round(barLength * count / total))
        percents = round(100.0 * count / total, 1)
        bar = "■" * filledLength + "□" * (barLength - filledLength)

        sys.stdout.write("\r[%s] %s%s ...%s" % (bar, percents, "%", suffix))
        sys.stdout.flush()
    # ------------------------------------------------------------------------------------------------------------------