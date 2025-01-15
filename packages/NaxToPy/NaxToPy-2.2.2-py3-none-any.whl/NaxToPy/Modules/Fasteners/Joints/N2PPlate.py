from __future__ import annotations
from NaxToPy.Core.Classes.N2PNastranInputData import * 
from NaxToPy.Core.Classes.N2PAbaqusInputData import * 
from NaxToPy.Core.Classes.N2PElement import N2PElement
from NaxToPy.Core.Classes.N2PNode import N2PNode
import numpy as np
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from NaxToPy.Modules.Fasteners.Joints.N2PJoint import N2PJoint
    from NaxToPy.Modules.Fasteners.Joints.N2PBolt import N2PBolt

class N2PPlate: 

    """
    Class that represents a single plate. 

    Attributes: 
        id: int -> internal ID. 
        global_id: list[int] -> list of the global IDs of the N2PElements that make up the N2PPlate. 
        solver_id: list[int] -> list of the solver IDs of the N2PElements that make up the N2PPlate. 
        plate_central_cell_solver_id: int -> solver ID of one N2PElement that could represent the entire N2PPlate. 
        cards: list[N2PCard] -> list of the N2PCards of the N2PElements that make up the N2PPlate. It could contain 
        nulls/nones, like when dealing with .op2 files. 
        joint: N2PJoint -> N2PJoint associated to the N2PPlate. Several N2PPlates will be associated to the same 
        N2PJoint. 
        elements: list[N2PElement] -> list of N2PElements associated to the N2PPlate. 
        attachment_id: int -> ID that the plate receives when it goes through get_attachments
        intersection: list[float] -> intersection point between the N2PPlate and its N2PBolt. 
        distance: float -> distance from the N2PPlate's edge and its N2PBolt. 
        normal: list[float] -> perpendicular direction to the N2PPlate. 
        altair_force: dict[int, list[float]] -> dictionary in the form {Load Case ID: [FX, FY, FZ]} corresponding to 
        Altair's 1D force.
        plates_force: dict[int, list[list[float]]] -> dictionary in the form 
        {Load Case ID: [[FX, FY, FZ], [FX, FY, FZ]]} corresponding to the 1D forces that each the N2PElements 
        associated to the N2PBolt associated to the N2PPlate experience. 
        nx_bypass: dict[int, float] -> dictionary in the form {Load Case ID: Nx} corresponding to the bypass force in 
        the x axis. 
        nx_total: dict[int, float] -> dictionary in the form {Load Case ID: Nx} corresponding to the total force in the
        x axis. 
        ny_bypass: dict[int, float] -> dictionary in the form {Load Case ID: Ny} corresponding to the bypass force in 
        the y axis. 
        ny_total: dict[int, float] -> dictionary in the form {Load Case ID: Ny} corresponding to the total force in the
        y axis. 
        nxy_bypass: dict[int, float] -> dictionary in the form {Load Case ID: Nxy} corresponding to the bypass force in 
        the xy axis. 
        nxy_total: dict[int, float] -> dictionary in the form {Load Case ID: Nxy} corresponding to the total force in 
        the xy axis. 
        mx_total: dict[int, float] -> dictionary in the form {Load Case ID: Mx} corresponding to the total moment in 
        the x axis. 
        my_total: dict[int, float] -> dictionary in the form {Load Case ID: My} corresponding to the total moment in 
        the y axis. 
        mxy_total: dict[int, float] -> dictionary in the form {Load Case ID: Mxy} corresponding to the total moment in 
        the xy axis. 
        bypass_max: dict[int, float] -> dictionary in the form {Load Case: N} corresponding to the maximum bypass force. 
        bypass_min: dict[int, float] -> dictionary in the form {Load Case: N} corresponding to the minimum bypass force. 
        box_dimension: float -> dimension of the box used in the bypass calculations. 
        box_system: list[float] -> box coordinate system used in the bypass calculations. 
        box_points: dict[int, np.array] -> dictionary in the form {1: coords, 2: coords, ..., 8: coords} including each 
        point's coordinates that was used for the bypass calculations. 
        box_fluxes: dict[dict[int, list[float]]] -> dictionary in the form 
        {Load Case ID: {1: [FXX, FYY, FXY, MXX, MYY, MXY], 2: [], ..., 8: []}} including fluxes associated to each 
        box point. 
    """

    # N2PPlate constructor    ------------------------------------------------------------------------------------------
    def __init__(self, info, input_data_father): 

        self.__info__ = info 
        self.__input_data_father__ = input_data_father 

        self._id: int = int(self.__info__.ID)
        self._global_id: list[int] = list(self.__info__.GlobalIds)
        self._solver_id: list[int] = list(self.__info__.SolverIds)
        self._plate_central_cell_solver_id: int = int(self.__info__.PlateCentralCellSolverId)
        if self._plate_central_cell_solver_id not in self._solver_id: 
            self._solver_id.append(self._plate_central_cell_solver_id)
        self._cards: list[N2PCard] = [self.__input_data_father__._N2PNastranInputData__dictcardscston2p[i] for i in self.__info__.Cards if self.__info__.Cards[0] is not None]

        self._joint: N2PJoint = None 
        self._elements: list[N2PElement] = None 

        self._attachment_id: int = self.ID 

        self._intersection: list[float] = None 
        self._distance: float = None 
        self._normal: list[float] = None 

        self._altair_force: dict[int, list[float]] = {} 
        self._plates_force: dict[int, list[list[float]]] = {}
        self._nx_bypass: dict[int, float] = {}
        self._nx_total: dict[int, float] = {}
        self._ny_bypass: dict[int, float] = {}
        self._ny_total: dict[int, float] = {}
        self._nxy_bypass: dict[int, float] = {}
        self._nxy_total: dict[int, float] = {}
        self._mx_total: dict[int, float] = {}
        self._my_total: dict[int, float] = {}
        self._mxy_total: dict[int, float] = {}
        self._bypass_max: dict[int, float] = {}
        self._bypass_min: dict[int, float] = {}
        self._box_dimension: float = None
        self._box_system: list[float] = None 
        self._box_points: dict[int, np.array] = {}
        self._box_fluxes: dict[dict[int, list[float]]] = {}
    # ------------------------------------------------------------------------------------------------------------------
        
    # Getters ----------------------------------------------------------------------------------------------------------
    @property 
    def ID(self) -> int: 

        """
        Property that returns the id attribute, that is, the internal identificator. 
        """

        return self._id
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def GlobalID(self) -> list[int]: 

        """
        Property that returns the global_id attribute, that is, the global identificator. 
        """
        
        return self._global_id
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def SolverID(self) -> list[int]: 

        """
        Property that returns the solver_id attribute, that is, the solver IDs of the N2PElements that make up the 
        plate. 
        """
        
        return self._solver_id
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def PlateCentralCellSolverID(self) -> int: 

        """
        Property that returns the plate_central_cell_solver_id attribute, that is, the solver ID of one representative 
        N2PElement that makes up the plate. 
        """
        
        return self._plate_central_cell_solver_id
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Cards(self) -> list[N2PCard]: 

        """
        Property that returns the cards attribute, that is, the list of the N2PCards associated with the N2PPlate's 
        N2PElements. 
        """
        
        return self._cards
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Joint(self) -> N2PJoint:

        """
        Property that returns the joint attribute, that is, the N2PJoint associated to the plate. 
        """

        return self._joint
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Bolt(self) -> N2PBolt:

        """
        Property that returns the bolt attribute, that is, the N2PBolt associated to the plate. 
        """
    
        return self.Joint.Bolt
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Elements(self) -> list[N2PElement]: 

        """
        Property that returns the elements attribute, that is, the list of N2PElements that make up the plate. 
        """
        
        return self._elements
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def ElementsID(self) -> list[int]: 

        """
        Property that returns the list of the IDs of the N2PElements that make up a 
        plate. 
        """
        
        return [j.ID for j in self.Elements]
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def ElementsInternalID(self) -> list[int]: 

        """
        Property that returns the unique internal ID of the N2PElements that make up the plate.  
        """

        return [j.InternalID for j in self.Elements]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Nodes(self) -> list[N2PNode]: 

        """
        Property that returns the list of N2PNodes that make up the plate. 
        """
        
        return [j.Nodes for j in self.Elements]
    # ------------------------------------------------------------------------------------------------------------------

    @property 
    def PartID(self) -> list[str]: 

        """
        Property that returns the part ID of eache element that makes up the plate. 
        """

        return [j.PartID for j in self.Elements]
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AttachmentID(self) -> int: 

        """
        Property that returns the attachment_id attribute, that is, the plate's internal ID when it goes through the 
        get_attachments() function.
        """
        
        return self._attachment_id
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Intersection(self) -> list[float]: 

        """
        Property that returns the intersection attribute, that is, the point where the bolt pierces the plate. 
        """
    
        return self._intersection
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Distance(self) -> list[float]: 

        """
        Property that returns the distance attribute, that is, the distance between the bolt and the plate's edge. 
        """
        
        return self._distance
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def Normal(self) -> list[float]: 

        """
        Property that returns the normal attribute, that is, the direction perpendicular to the plate's plane. 
        """
        
        return self._normal
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def AltairForce(self) -> dict[int, list[float]]: 

        """
        Property that returns the altair_force attribute, that is, the 1D force that the plate experiences as 
        calculated by Altair. 
        """

        return self._altair_force
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def PlatesForce(self) -> dict[int, list[list[float]]]: 

        """
        Property that returns the plates_force attribute, that is, the 1D force that each N2PPlate's N2PElement 
        experiences.
        """

        return self._plates_force
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def NxBypass(self) -> dict[int, float]: 

        """
        Property that returns the nx_bypass attribute, that is, the bypass load that the plate experiences in the 
        x-axis. 
        """

        return self._nx_bypass
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def NxTotal(self) -> dict[int, float]: 

        """
        Property that returns the nx_total attribute, that is, the total load that the plate experiences in the x-axis. 
        """

        return self._nx_total
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def NyBypass(self) -> dict[int, float]: 

        """
        Property that returns the ny_bypass attribute, that is, the bypass load that the plate experiences in the 
        y-axis. 
        """

        return self._ny_bypass
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def NyTotal(self) -> dict[int, float]: 

        """
        Property that returns the ny_total attribute, that is, the total load that the plate experiences in the y-axis. 
        """

        return self._ny_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def NxyBypass(self) -> dict[int, float]: 

        """
        Property that returns the nxy_bypass attribute, that is, the bypass load that the plate experiences in the 
        xy-axis. 
        """

        return self._nxy_bypass
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def NxyTotal(self) -> dict[int, float]: 

        """
        Property that returns the nxy_total attribute, that is, the total load that the plate experiences in the 
        xy-axis. 
        """

        return self._nxy_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def MxTotal(self) -> dict[int, float]: 

        """
        Property that returns the mx_total attribute, that is, the total moment that the plate experiences in the 
        x-axis. 
        """

        return self._mx_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def MyTotal(self) -> dict[int, float]: 

        """
        Property that returns the my_total attribute, that is, the total moment that the plate experiences in the 
        y-axis. 
        """

        return self._my_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def MxyTotal(self) -> dict[int, float]: 

        """
        Property that returns the mxy_total attribute, that is, the total moment that the plate experiences in the 
        xy-axis. 
        """

        return self._mxy_total
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def BypassMax(self) -> dict[int, float]: 

        """
        Property that returns the bypass_max attribute, that is, the maximum bypass load that the plate experiences. 
        """

        return self._bypass_max
    # ------------------------------------------------------------------------------------------------------------------
    
    @property 
    def BypassMin(self) -> dict[int, float]: 

        """
        Property that returns the bypass_min attribute, that is, the minimum bypass load that the plate experiences. 
        """

        return self._bypass_min
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def BoxDimension(self) -> float: 

        """
        Property that returns the box_dimension attribute, that is, the length of the side of the box that is used in 
        the bypass loads calculation. 
        """
        
        return self._box_dimension
    # ------------------------------------------------------------------------------------------------------------------
    
    @property
    def BoxSystem(self) -> list[float]: 

        """
        Property that returns the box_system attribute, that is, the reference frame of the box used in the bypass 
        loads calculation. 
        """
        
        return self._box_system
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoxPoints(self) -> dict[int, np.array]: 

        """
        Property that returns the box_points attribute, that is, the coordinates of each point that makes up the box 
        used in the bypass loads calculation. 
        """
        
        return self._box_points
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def BoxFluxes(self) -> dict[dict[int, list[float]]]: 

        """
        Property that returns the box_fluxes attribute, that is, the fluxes (in every direction) that every point that 
        makes up the box used in the bypass loads calculation experience. 
        """
        
        return self._box_fluxes
    # ------------------------------------------------------------------------------------------------------------------