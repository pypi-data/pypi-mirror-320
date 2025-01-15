from NaxToPy import N2PLog
import numpy as np 

# Method used to rotate a 2D tensor ------------------------------------------------------------------------------------
def rotate_tensor2D(fromSystem: list, toSystem: list, planeNormal: list, tensor: list) -> list: 

    """
    Method used to a 2D tensor from one coordinate system to another. 
    
    Args: 
        fromSystem: list -> original system.
        toSystem: list -> destination system. 
        planeNormal: list -> rotation plane. 
        tensor: list -> tensor to rotate. 

    Returns: 
        rotatedTensor: list 

    Calling example: 
        >>> from NaxToPy.Modules.Fasteners._N2PFastenerAnalysisNuevo.Core.Functions.N2PRotation import rotate_tensor2D
        >>> forcesRot = rotate_tensor2D(elementSystem, materialSystem, elementSystem[6:9], forces)
    """

    tensor = np.array(tensor) 
    alpha = angle_between_2_systems(fromSystem, toSystem, planeNormal) 
    # Definition of the rotation matrix 
    c = np.cos(alpha) 
    s = np.sin(alpha) 
    R = np.array([[c**2, s**2, 2*s*c], [s**2, c**2, -2*s*c], [-s*c, s*c, c**2 - s**2]])
    shape = tensor.shape 
    tensorReshaped = tensor.reshape((-1, 3)).T 
    rotatedTensor = np.matmul(R, tensorReshaped).T 
    return rotatedTensor.reshape(shape).tolist() 
# ----------------------------------------------------------------------------------------------------------------------

# Method used to rotate a vector (1D tensor) ---------------------------------------------------------------------------
def rotate_vector(vector: list, fromSystem: list, toSystem: list) -> np.ndarray: 

    """
    Method used to rotate a vector from a coordinate system to another.

    Args:
        vector: list -> vector to be rotated. 
        fromSystem: list -> original system. 
        toSystem: list -> destination system. 

    Returns:
        rotatedVector: ndarray 

    Calling example: 
        >>> from NaxToPy.Modules.Fasteners._N2PFastenerAnalysisNuevo.Core.Functions.N2PRotation import rotate_vector
        >>> transformedNode = rotate_vector(nodeVector, globalSystem, elementSystem)
    """

    # Verify if every input has a length which is a multiple of three 
    if len(vector) %3 != 0 or len(fromSystem) %3 != 0 or len(toSystem) %3 != 0: 
        N2PLog.Error.E512()
        return None 
    vectorSegments = [vector[i: i + 3] for i in range(0, len(vector), 3)]
    transformedSegments = [] 
    # Vectors are reshaped into matrices 
    matrixCurrent = np.array(fromSystem).reshape(3, -1) 
    matrixNew = np.array(toSystem).reshape(3, -1) 
    for i in vectorSegments: 
        i = np.array(i).reshape(-1, 3) 
        matrixRotation = np.linalg.inv(matrixCurrent) @ matrixNew 
        transformedSegments.append((matrixRotation @ i.T).T)
    rotatedVector = np.concatenate(transformedSegments).reshape(-1) 
    return rotatedVector 
# ----------------------------------------------------------------------------------------------------------------------

# Method used to project a vector --------------------------------------------------------------------------------------
def project_vector(vector: list, fromSystem: list, toSystem: list) -> np.ndarray: 

    """
    Method used to project a vector from a coordinate system to another.

    Args:
        vector: list -> vector to be projected.  
        fromSystem: list -> original system. 
        toSystem: list -> destination system. 

    Returns:
        projectedVector: ndarray 

    Calling example: 
        >>> from NaxToPy.Modules.Fasteners._N2PFastenerAnalysisNuevo.Core.Functions.N2PRotation import project_vector
        >>> forces = project_vector(elementForces, firstSystem, secondSystem)
    """

    fromSystem = np.array(fromSystem).reshape(3, -1)
    toSystem = np.array(toSystem).reshape(3, -1)
    vector = np.array(vector) 
    fromSystem = fromSystem/np.linalg.norm(fromSystem, axis = 1, keepdims = True)
    toSystem = toSystem/np.linalg.norm(toSystem, axis = 1, keepdims = True)

    M = np.matmul(fromSystem, toSystem.T)
    projectedVector = np.matmul(M, vector.reshape((-1, 3)).T).T

    return projectedVector.reshape(vector.shape)
# ----------------------------------------------------------------------------------------------------------------------

# Method used to obtain the angle between two systems ------------------------------------------------------------------
def angle_between_2_systems(fromSystem: list, toSystem: list, planeNormal: list) -> float:

    """
    Method used to return the rotation angle, in radians, between two coordinate systems, given also the rotation plane. 
    Args:
        fromSystem: list -> first system. 
        toSystem: list -> second system. 
        planeNormal: list -> rotation plane. 

    Returns:
        alpha: float -> angle, in radians, that the two systems form.

    Calling example: 
        >>> from NaxToPy.Modules.Fasteners._N2PFastenerAnalysisNuevo.Core.Functions.N2PRotation import angle_between_2_systems
        >>> alpha = angle_between_2_systems(system1D, materialSystem, materialSystem[6:9])
    """

    fromSystem = np.array(fromSystem).reshape(3, -1)
    toSystem = np.array(toSystem).reshape(3, -1)
    planeNormal = np.array(planeNormal)

    fromSystem = fromSystem / np.linalg.norm(fromSystem, axis = 1, keepdims = True)
    toSystem = toSystem / np.linalg.norm(toSystem, axis = 1, keepdims = True)
    planeNormal = planeNormal / np.linalg.norm(planeNormal)

    toX = toSystem[0]
    projToX = toX - np.dot(toX, planeNormal) * planeNormal

    cosX = np.dot(fromSystem[0], projToX)
    if cosX > 1:
        cosX = 1
    elif cosX < -1:
        cosX = -1

    alpha = np.arccos(cosX)

    cosY = np.dot(fromSystem[1], projToX)
    if cosY < 0:
        alpha = - alpha

    return alpha
# ----------------------------------------------------------------------------------------------------------------------

# Method used to do the necessary transformations to later interpolate adequately -------------------------------------- 
def transformation_for_interpolation(cornerPoints: np.ndarray, centroid: np.ndarray, point: np.ndarray, elementSystem = np.ndarray, 
                                     globalSystem = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
    
    """
    Method used to transform the nodes of an element and a point in it from the global system to the element system of 
    the element centered in the centroid.

    Args:
        cornerPoints: ndarray -> nodes of the element to be transformed.
        centroid: ndarray -> centroid of the element.
        point: ndarray -> point to be transformed.
        elementSystem: ndarray -> element coordinate system 
        globalSystem: list = [[1, 0, 0], [0, 1, 0], [0, 0, 1]] -> global coordinate system 

    Returns:
        transformedNodes, transformedPoint

    Calling example: 
        >>> from NaxToPy.Modules.Fasteners._N2PFastenerAnalysisNuevo.Core.Functions.N2PRotation import transformation_for_interpolation
        >>> cornerCoordElem, pointCoordElem = transformation_for_interpolation(cornerCoordsGlobal, centroid, 
                                                                               boxPoints, elementSystemBoxPoint)
    """

    # Definition of the nodes and point with regards to the Global Refererence frame located in the centroid
    nodesVector = [i - centroid for i in cornerPoints]
    pointVector = point - centroid 

    # Transformation from the Global Reference Frame to the Element System with regards to the centroid.
    transformedNodes = [rotate_vector(i, globalSystem, elementSystem) for i in nodesVector]
    transformedNodes = np.array([i.tolist() for i in transformedNodes])

    transformedPoint = rotate_vector(pointVector, globalSystem, elementSystem)

    return transformedNodes, transformedPoint
# ----------------------------------------------------------------------------------------------------------------------