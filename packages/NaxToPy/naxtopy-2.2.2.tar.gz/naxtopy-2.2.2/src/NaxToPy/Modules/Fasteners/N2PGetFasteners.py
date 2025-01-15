from NaxToPy import N2PLog
from NaxToPy.Core.N2PModelContent import N2PModelContent 
from NaxToPy.Modules.Fasteners.Joints.N2PBolt import N2PBolt 
from NaxToPy.Modules.Fasteners.Joints.N2PPlate import N2PPlate 
from NaxToPy.Modules.Fasteners.Joints.N2PJoint import N2PJoint
from NaxToPy.Modules.Fasteners.Joints.N2PAttachment import N2PAttachment
from NaxToPy.Modules.Fasteners._N2PFastenerAnalysis.Core.Functions.N2PGetAttachments import get_attachments
from time import time 
from typing import Union 

class N2PGetFasteners: 

    """
    Class used to obtain all necessary geometrical information of a model's N2PJoints, N2PBolts and N2PPlates. 

    The instance of this class must be prepared using its properties before calling it method calculate.
    """

    # N2PGetFasteners constructor --------------------------------------------------------------------------------------
    def __init__(self): 

        """
        The constructor creates an empty N2PGetFasteners instance. Its attributes must be added as properties.

        Calling example: 
            >>> import NaxToPy as n2p 
            >>> from NaxToPy.Modules.Fasteners.N2PGetFasteners import N2PGetFasteners
            >>> model1 = n2p.load_model("route.fem") # model loaded from N2PModelContent 
            >>> fasteners = N2PGetFasteners()
            >>> # Compulsory input 
            >>> fasteners.Model = model1 
            >>> # Custom threshold is selected (optional)
            >>> fasteners.Thresh = 1.5
            >>> # Only some joints are to be analyzed (optional)
            >>> fasteners.GlobalIDList = [10, 11, 12, 13, 14]
            >>> # attachments will not be obtained
            >>> fasteners.GetAttachmentsBool = False  # True by default
            >>> # fasteners are obtained
            >>> fasteners.calculate()
        """

        self._model: N2PModelContent = None 
        self._get_attachments_bool: bool = True 

        self._thresh: float = 2.0 
        self._solver_ids_and_parts: str = None
        self._solver_id_list: list[int] = None
        self._part_id: str = None
        self._global_id_list: list[int] = None

        self._list_joints: list[N2PJoint] = None  
        self._list_attachments: list[N2PAttachment] = None 
    # ------------------------------------------------------------------------------------------------------------------
        
    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def Model(self) -> N2PModelContent: 

        """
        Model to be analyzed. It is a compulsory input and an error will occur if it is not present. 
        """
        
        return self._model 
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def GetAttachmentsBool(self) -> bool: 

        """
        Sets if the get_attachments() method will be used inside method calculate().
        """
        
        return self._get_attachments_bool
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def Thresh(self) -> float: 

        """
        Tolerance used in the obtention of the N2Joints in C#. 2.0 by default.
        """

        return self._thresh
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def SolverIDsAndParts(self) -> str: 

        """
        String in the form "Part ID number: Solver ID1, SolverID2, ..." of the part ID and solver IDs of the 1D elements
        that make up the bolts to be loaded. Note that the part ID number is an integer, not a string. 
        """

        return self._solver_ids_and_parts
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def SolverIDList(self) -> list[int]: 

        """
        List of the Solver IDs of the 1D elements that make up the bolts to be loaded. If this is present, part_id must also be present. 
        """

        return self._solver_id_list
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def PartID(self) -> str: 

        """
        Part ID of the 1D elements to be loaded. If this is present, solver_id_list must also be present. 
        """

        return self._part_id
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def GlobalIDList(self) -> list[int]: 

        """
        List of the internal/global IDs of the 1D elements that make up the bolts to be loaded. 
        """

        return self._global_id_list
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ListJoints(self) -> list[N2PJoint]: 

        """
        List of all N2PJoints.
        """
        
        return self._list_joints
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ListPlates(self) -> list[N2PPlate]: 

        """
        Property that returns the list of N2PPlates. 
        """
        
        return [j for i in self.ListJoints for j in i.Plates]
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ListBolts(self) -> list[N2PBolt]: 

        """
        Property that returns the list of N2PBolts. 
        """
        
        return [i.Bolt for i in self.ListJoints]
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def ListAttachments(self) -> list[N2PAttachment]: 

        """
        List of all N2PAttachments. 
        """
        
        return self._list_attachments 
    # ------------------------------------------------------------------------------------------------------------------

    # Setters ----------------------------------------------------------------------------------------------------------
    
    @Model.setter 
    def Model(self, value: N2PModelContent) -> None: 

        self._model = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @GetAttachmentsBool.setter 
    def GetAttachmentsBool(self, value: bool) -> None: 

        self._get_attachments_bool = value 
    # ------------------------------------------------------------------------------------------------------------------
        
    @Thresh.setter
    def Thresh(self, value: float) -> None: 

        self._thresh = value 
    # ------------------------------------------------------------------------------------------------------------------

    @SolverIDsAndParts.setter 
    def SolverIDsAndParts(self, value: str) -> None: 

        self._solver_ids_and_parts = value 
    # ------------------------------------------------------------------------------------------------------------------

    @SolverIDList.setter 
    def SolverIDList(self, value: Union[list[int], tuple[int], set[int], int]) -> None: 

        if type(value) == tuple or type(value) == set: 
            value = list(value) 
        elif type(value) == int: 
            value = [value]

        self._solver_id_list = value 
    # ------------------------------------------------------------------------------------------------------------------

    @PartID.setter
    def PartID(self, value: str) -> None: 

        self._part_id = value
    # ------------------------------------------------------------------------------------------------------------------

    @GlobalIDList.setter
    def GlobalIDList(self, value: Union[list[int], tuple[int], set[int], int]) -> None: 

        if type(value) == tuple or type(value) == set: 
            value = list(value) 
        elif type(value) == int: 
            value = [value]

        self._global_id_list = value 
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to create all joints, plates and bolts ---------------------------------------------------------------
    def get_joints(self) -> None: 

        """
        This method is used to create all N2PJoints, N2PPlates and N2PBolts and assign them certain useful attributes. 
        In order to work, the n2joints and model attributes must have been previously filled. If they have not, an 
        error will occur. 

        The following steps are followed: 
            1. All N2Joints are created differently depending on the user's inputs. 
            1. All N2PJoints are created. Inside this, all N2PBolts and N2PPlates associated to each N2PJoint are also 
            created. 
            2. All N2PBolts, N2PPlates are assigned its corresponding N2PElements and N2PNodes. Also, N2PJoints are 
            assigned its bolt's N2PElements and N2PNodes, as well as its plates' N2PElements and N2PNodes. 

        Calling example: 
            >>> fasteners.get_joints()
        """

        t1 = time() 
        if self.Model is None: 
            N2PLog.Error.E521() 
        
        # Creation of the N2Joints 
        if self._solver_ids_and_parts is None: 
            if self._solver_id_list is None: 
                if self._part_id is None:  
                    if self._global_id_list is None: 
                        n2joints = list(self.Model._N2PModelContent__vzmodel.GetJoints(self._thresh)) 
                    else: 
                        n2joints = list(self.Model._N2PModelContent__vzmodel.GetJoints(self._thresh, global_id_list = self._global_id_list))
                else: 
                    N2PLog.Error.E518()
            else: 
                if self._part_id is None: 
                    N2PLog.Error.E519()
                else: 
                    n2joints = list(self.Model._N2PModelContent__vzmodel.GetJoints(self._thresh, solver_id_list = self._solver_id_list, 
                                                                                   part_id = self.Model._N2PModelContent__StrPartToID[self._part_id]))
        else: 
            n2joints = list(self.Model._N2PModelContent__vzmodel.GetJoints(self._thresh, solver_ids_and_parts = self._solver_ids_and_parts))            

        # N2PJoints are created from the N2Joints
        self._list_joints = [N2PJoint(i, self._model.ModelInputData) for i in n2joints]
        for i in self.ListJoints: 
            for j in i.Plates: 
                j._joint = i

        element_list = list(self.Model.ElementsDict.values())
        for i in self.ListPlates:
            i._elements = [element_list[j] for j in i.GlobalID] 
            
        for i in self.ListJoints: 
            i.Bolt._elements = [element_list[j] for j in i.Bolt.OneDimElemsIDList]

        N2PLog.Debug.D601(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain the distance from each N2PBolt to its N2PPlates' edge --------------------------------------
    def get_distance(self) -> None: 

        """
        Method used to obtain the distance from every N2PPlate's edge to its N2PJoint, the intersection between an 
        N2PPlate and its N2PJoint and the perpendicular direction to the N2PPlates. The get_joints() method must be 
        used before this one. Otherwise, an error will occur. 

        Calling example: 
            >>> fasteners.get_distance() 
        """

        t1 = time() 
        if self.ListJoints is None: 
            N2PLog.Error.E522() 

        [i.get_distance(self.Model) for i in self.ListJoints]
        N2PLog.Debug.D605(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to obtain a list of attachments ----------------------------------------------------------------------
    def get_attachments(self) -> None: 


        """
        Method used to obtain the list of N2PAttachments and calculate their pitch. The get_joints() method must be 
        used before this one. Otherwise, an error will occur. 

        Calling example: 
            >>> fasteners.get_attachments() 
        """

        t1 = time()
        if self.ListJoints is None: 
            N2PLog.Error.E522() 

        self._list_attachments = get_attachments(self.Model, self.ListJoints)
        for i in self.ListAttachments: 
            for j in i.Joints: 
                j._attachment = i
        [i.get_pitch() for i in self.ListAttachments]
        N2PLog.Debug.D603(time(), t1)
    # ------------------------------------------------------------------------------------------------------------------

    # Method used to use all previous methods --------------------------------------------------------------------------
    def calculate(self) -> None: 

        """
        Method used to do all the previous calculations. 

        Calling example: 
            >>> fasteners.calculate()
        """

        self.get_joints() 
        self.get_distance() 
        if self.GetAttachmentsBool: 
            self.get_attachments()
    # ------------------------------------------------------------------------------------------------------------------