"""
For debugging in Slicer, use the following to manipulate the module objects:

mWidget = slicer.modules.meniscussignalintensity.widgetRepresentation().self()
mLogic = mWidget.logic
mNode = mLogic.getParameterNode()
"""


import logging
import os
from typing import Annotated, Optional

import vtk

import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode, vtkMRMLModelNode, vtkMRMLMarkupsPlaneNode


#
# MeniscusSignalIntensity
#


class MeniscusSignalIntensity(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _(
            "MeniscusSignalIntensity"
        )  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Meniscus")]
        self.parent.dependencies = (
            []
        )  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Amy Morton, Dominique Barnes (Brown University)"]

        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _(
            """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#MeniscusSignalIntensity">module documentation</a>.
"""
        )
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _(
            """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""
        )

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
    """Add data sets to Sample Data module."""
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # MeniscusSignalIntensity
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="Meniscus",
        sampleName="MRI medial and later Meniscus",
        thumbnailFileName=os.path.join(iconsPath, "MeniscusSignalIntensity.png"),
        # Download URL and target file name
        uris="https://github.com/BrownBioeng/Slicer_Meniscus/releases/tag/csa_si",
        fileNames="103.sag.ciss.reformat.1.5x1.5.nrrd",
        # checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="MeniscusSignalIntensity2",
    )


#
# MeniscusSignalIntensityParameterNode
#


@parameterNodeWrapper
class MeniscusSignalIntensityParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    medialModel - Previously segmented meniscus model. MED
    lateralModel - Previously segmented meniscus model. LAT
    isRight - for handling of roi extets

    #TO DO : determine angle discretization increments
    """

    inputVolume: vtkMRMLScalarVolumeNode
    medialModel: vtkMRMLModelNode
    lateralModel: vtkMRMLModelNode
    isRight: bool = True

    medAntPlane: vtkMRMLMarkupsPlaneNode
    medPostPlane: vtkMRMLMarkupsPlaneNode
    latAntPlane: vtkMRMLMarkupsPlaneNode
    latPostPlane: vtkMRMLMarkupsPlaneNode

    #debating adding in all the cut models (6) 
    medAntModel: vtkMRMLModelNode
    medMidModel: vtkMRMLModelNode
    medPostModel: vtkMRMLModelNode
    latAntModel: vtkMRMLModelNode
    latMidModel: vtkMRMLModelNode
    latPostModel: vtkMRMLModelNode


    # resultsTable: vtkMRMLTableNode

    # TO DO : (future) determine angle discretization increments
    # angleDiscretization: Annotated[float, WithinRange(0, 180)] = 90.0


#
# MeniscusSignalIntensityWidget
#


class MeniscusSignalIntensityWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(
            self.resourcePath("UI/MeniscusSignalIntensity.ui")
        )
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = MeniscusSignalIntensityLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose
        )
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose
        )


        # Buttons
        '''for debugging- temporarily add another ui button -
        TO DO: remove the intermediary buttons into one fx once the logic is working'''
        self.ui.planeComputeButton.connect("clicked(bool)", self.onComputePlanesButton)
        self.ui.cutModelButton.connect("clicked(bool)", self.onCutModelsButton)
        self.ui.meniscusVolumeSignalButton.connect(
            "clicked(bool)", self.meniscusVolumeSignalVals
        )

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(
                self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanCalcModelP
            )

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass(
                "vtkMRMLScalarVolumeNode"
            )
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(
        self, inputParameterNode: Optional[MeniscusSignalIntensityParameterNode]
    ) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(
                self._parameterNode,
                vtk.vtkCommand.ModifiedEvent,
                self._checkCanCalcModelP,
            )
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(
                self._parameterNode,
                vtk.vtkCommand.ModifiedEvent,
                self._checkCanCalcModelP,
            )
            self._checkCanCalcModelP()

    def _checkCanCalcModelP(self, caller=None, event=None) -> None:
        if (
            self._parameterNode
            and self._parameterNode.inputVolume
            and self._parameterNode.medialModel
            and self._parameterNode.lateralModel
        ):
            self.ui.planeComputeButton.toolTip = _("Compute meniscus metrics")
            self.ui.planeComputeButton.enabled = True
        else:
            self.ui.planeComputeButton.toolTip = _("Select input volume and model")
            self.ui.planeComputeButton.enabled = False

    def _checkCanCutModel(self, caller=None, event=None) -> None:
        if (
            self._parameterNode
            and self._parameterNode.medAntPlane
            and self._parameterNode.medPostPlane
            and self._parameterNode.medialModel
            and self._parameterNode.lateralModel
            and self._parameterNode.latAntPlane
            and self._parameterNode.latPostPlane
        ):
            self.ui.cutModelButton.toolTip = _("Compute meniscus metrics")
            self.ui.cutModelButton.enabled = True
        else:
            self.ui.cutModelButton.toolTip = _("Select input volume and model")
            self.ui.cutModelButton.enabled = False

    def onComputePlanesButton(self) -> None:
        """Run processing when user clicks "Apply" button."""
        with slicer.util.tryWithErrorDisplay(
            _("Failed to compute results."), waitCursor=True
        ):

            # workflow:
            # input volume and model

            """compute_model_parameters:
            '   - model bounds:
            '       - medial bound(x) mean(y,z) of the model bounds
            '       - lateral bound extents each: Ant, Post
            '   those 3 control points form plane each : (ant, post)
            '
            """

            # meniscus centroid and planes
            self.logic.compute_model_parameters(
                self.ui.inputVolSelector.currentNode(),
                self.ui.inputMedialSelector.currentNode(),
                self.ui.right_rb.isChecked(),
                True,
            )

            self.logic.compute_model_parameters(
                self.ui.inputVolSelector.currentNode(),
                self.ui.inputLateralSelector.currentNode(),
                self.ui.right_rb.isChecked(),
                False,
            )

    def onCutModelsButton(self) -> None:
        """using the anterior and posterior defined planes, cute each meniscus into
        anterior, mid and posterior sections."""
        with slicer.util.tryWithErrorDisplay(
            _("Failed to compute results."), waitCursor=True
        ):
            self.logic.cutModelFromPlanes(
                self.ui.inputMedialSelector.currentNode(),
                self._parameterNode.medAntPlane,
                self._parameterNode.medPostPlane,
                True,
            )
            self.logic.cutModelFromPlanes(
                self.ui.inputLateralSelector.currentNode(),
                self._parameterNode.latAntPlane,
                self._parameterNode.latPostPlane,
                False,
            )
            #hide input model and color each output here?
            self._parameterNode.medialModel.SetDisplayVisibility(False)
            self._parameterNode.lateralModel.SetDisplayVisibility(False)

        
            self._parameterNode.medAntModel.GetDisplayNode().SetColor(255, 140, 0)  # red
            self._parameterNode.medMidModel.GetDisplayNode().SetColor(140, 0, 255)  # blue
            self._parameterNode.medPostModel.GetDisplayNode().SetColor(70, 125, 110)  # green
            
            self._parameterNode.latAntModel.GetDisplayNode().SetColor(255, 140, 0)  # red
            self._parameterNode.latMidModel.GetDisplayNode().SetColor(140, 0, 255)  # blue
            self._parameterNode.latPostModel.GetDisplayNode().SetColor(70, 125, 110)  # green

            self._parameterNode.medAntModel.SetDisplayVisibility(True)
            self._parameterNode.medMidModel.SetDisplayVisibility(True)
            self._parameterNode.medPostModel.SetDisplayVisibility(True)

            self._parameterNode.latAntModel.SetDisplayVisibility(True)
            self._parameterNode.latMidModel.SetDisplayVisibility(True)
            self._parameterNode.latPostModel.SetDisplayVisibility(True)
        

        self.logic.segmentFromModels(
            self._parameterNode.inputVolume,
            self._parameterNode.medAntModel,
            self._parameterNode.medMidModel,
            self._parameterNode.medPostModel,
            True,
        )        
        '''self.logic.segmentFromModels(
            self._parameterNode.inputVolume,
            self._parameterNode.latAntModel,
            self._parameterNode.latMidModel,
            self._parameterNode.latPostModel,
            True,
        )        
        '''

            
    def meniscusVolumeSignalVals(self) -> None:
        '''with slicer.util.tryWithErrorDisplay(
            _("Failed to compute results."), waitCursor=True
        ):
            #self.logic.'''





#
# MeniscusSignalIntensityLogic
#


class MeniscusSignalIntensityLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)

    def getParameterNode(self):
        return MeniscusSignalIntensityParameterNode(super().getParameterNode())

    def compute_model_parameters(
        self,
        inputVolume: vtkMRMLScalarVolumeNode,
        inputModel: vtkMRMLModelNode,
        isRight: bool = True,
        isMed: bool = True,
        showResult: bool = True,
    ) -> None:

        if not inputVolume or not inputModel:
            raise ValueError("Input or output volume is invalid")

        # centroid, and corner extents for cut planes
        self._generateCutPlaneCoords_fromMenicus(inputModel, isMed, isRight)


    def _generateCutPlaneCoords_fromMenicus(self, modelNode, isMed, isRight) -> None:

        # Workflow:
        # bounds from model
        # centroid mean(x,y,z) of the model bounds
        # corner extents for cut planes

        # Get the model node and its polydata
        # modelNode = self._parameterNode.inputModel
        modelPolyData = modelNode.GetPolyData()

        # Get the bounds of the polydata
        bounds = [0.0] * 6
        modelPolyData.GetBounds(bounds)

        import numpy as np

        # construct min and max coordinates of bounding box
        bb_min = np.array([bounds[0], bounds[2], bounds[4]])
        bb_max = np.array([bounds[1], bounds[3], bounds[5]])

        bb_center = (bb_min + bb_max) / 2
        bb_size = bb_max - bb_min

        """ determine planes for cases:
            |     R     |    L     |
            |   ((  ))    ((  ))   |
            |  lat  med | med lat  |
        """
        # lateral extents in lateral roi.. can this be queried anatomically,
        # or do we need to convert ras to ijk based on above diagram?

        # R A S
        mid_IS = (bb_min[2] + bb_max[2]) / 2

        mcenter_markup = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLMarkupsFiducialNode"
        )

        if isMed:
            sML = "Med"
            if isRight:
                medLatExtent = bb_min[0]
                medCentroid = np.array([bb_max[0], bb_center[1], mid_IS])
            else:
                medLatExtent = bb_max[0]
                medCentroid = np.array([bb_min[0], bb_center[1], mid_IS])
        else:
            sML = "Lat"
            if isRight:
                medLatExtent = bb_max[0]
                medCentroid = np.array([bb_min[0], bb_center[1], mid_IS])
            else:
                medLatExtent = bb_min[0]
                medCentroid = np.array([bb_max[0], bb_center[1], mid_IS])

        mcenter_markup.SetName(f"'{sML}' Meniscus Centroid")
        mcenter_markup.AddControlPoint(bb_center[0], bb_center[1], bb_center[2])
        mcenter_markup.SetLocked(True)

        pAnt = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode")
        pAnt.SetName(f"'{sML}' Meniscus Ant Plane")
        pPost = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode")
        pPost.SetName(f"'{sML}' Meniscus Post Plane")

        aVp = vtk.vtkPlaneSource()
        aVp.SetOrigin(medCentroid[0], medCentroid[1], medCentroid[2])
        aVp.SetPoint1(medLatExtent, bb_max[1], bb_max[2])
        aVp.SetPoint2(medLatExtent, bb_max[1], bb_min[2])

        pAnt.SetOrigin(aVp.GetOrigin())
        aNorm = aVp.GetNormal()
        a_np = np.array(aNorm)

        pAnt.SetNormal(a_np)  
        pAnt.SetDisplayVisibility(False)

        pVp = vtk.vtkPlaneSource()
        pVp.SetOrigin(medCentroid[0], medCentroid[1], medCentroid[2])
        pVp.SetPoint1(medLatExtent, bb_min[1], bb_max[2])
        pVp.SetPoint2(medLatExtent, bb_min[1], bb_min[2])

        pPost.SetOrigin(pVp.GetOrigin())
        pNorm = pVp.GetNormal()
        p_np = np.array(pNorm)

        pPost.SetNormal(p_np)
        pPost.SetDisplayVisibility(False)

        # Create a new ROI node and set its parameters
        roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
        roiNode.SetName("ROI from Meniscus Model")
        roiNode.SetCenter(bb_center)
        roiNode.SetSize(bb_size)

        roiNode.SetLocked(True)  # Lock the ROI to prevent user modifications
        roiNode.SetDisplayVisibility(False)

        #set parameter nodes by planes
        if isMed:
            self.getParameterNode().medAntPlane = pAnt
            self.getParameterNode().medPostPlane = pPost
        else:
            self.getParameterNode().latAntPlane = pAnt
            self.getParameterNode().latPostPlane = pPost


    def cutModelFromPlanes(
        self,
        inputModel: vtkMRMLModelNode,
        antPlane: vtkMRMLMarkupsPlaneNode,
        postPlane: vtkMRMLMarkupsPlaneNode,
        isMed: bool = True,
    ) -> None:
        """Cut the input model using the ant, post planes."""

        #Output models"
        antModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
        mixModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
        postModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
        midModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")

        antModel.SetName(f"{inputModel.GetName()}_ant")
        postModel.SetName(f"{inputModel.GetName()}_post")
        midModel.SetName(f"{inputModel.GetName()}_mid")

        if isMed:
            outAntNegID = antModel.GetID()
            outAntPosID = mixModel.GetID()
            
            nextInputID = outAntPosID

            outPostPosID = postModel.GetID()
            outPostNegID = midModel.GetID()

        else:
            outAntNegID = mixModel.GetID()
            outAntPosID = antModel.GetID()

            nextInputID = outAntNegID

            outPostPosID = midModel.GetID()
            outPostNegID = postModel.GetID()
            

        #First, cut the anterior horn from the body
        planeModeler = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode") #
        planeModeler.SetToolName("Plane cut")
        planeModeler.SetNodeReferenceID("PlaneCut.InputModel", inputModel.GetID())
        planeModeler.SetNodeReferenceID("PlaneCut.InputPlane", antPlane.GetID())

        planeModeler.SetNodeReferenceID("PlaneCut.OutputNegativeModel", outAntNegID)
        planeModeler.SetNodeReferenceID("PlaneCut.OutputPositiveModel", outAntPosID)
        slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(planeModeler)


        #Next, use the 'negative leftovers from above, cut the post horn from the body
        #Can I recycle the plaenModeler and just update the input model and plane?
        planeModeler.SetNodeReferenceID("PlaneCut.InputModel",nextInputID)
        planeModeler.SetNodeReferenceID("PlaneCut.InputPlane", postPlane.GetID())
        planeModeler.SetNodeReferenceID("PlaneCut.OutputPositiveModel", outPostPosID)
        planeModeler.SetNodeReferenceID("PlaneCut.OutputNegativeModel", outPostNegID)
        slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(planeModeler)
        
        '''
        inputModel.SetVisibility(False)

        # Set the color of the model node
        antModel.GetNodeID().GetDisplayNode().SetColor(255,100,0)  # orange
        postModel.GetDisplayNode().SetColor(0,255,0)  # green
        midModel.GetDisplayNode().SetColor(0,100,255)  # blue
        '''
        if isMed:
            self.getParameterNode().medAntModel = antModel
            self.getParameterNode().medMidModel = midModel
            self.getParameterNode().medPostModel = postModel
        else:
            self.getParameterNode().latAntModel = antModel
            self.getParameterNode().latMidModel = midModel
            self.getParameterNode().latPostModel = postModel

        #Remove the planeModeler node from the scene
        slicer.mrmlScene.RemoveNode(planeModeler)
        slicer.mrmlScene.RemoveNode(mixModel)

    def segmentFromModels(
        self,
        inputVolume: vtkMRMLScalarVolumeNode,
        antModel: vtkMRMLModelNode,
        midModel: vtkMRMLModelNode,
        postModel: vtkMRMLModelNode,
        isMed: bool = True,
    ) -> None:
        """create Segmentation nodes the input volume using the ant, mid, post models.
        https://github.com/jzeyl/3D-Slicer-Scripts/blob/master/1_set%20up%20volume%20and%20segmentation%20nodes.py
        
        

        segNode = slicer.vtkMRMLSegmentationNode()
        slicer.mrmlScene.AddNode(segNode)
        segNode.CreateDefaultDisplayNodes()
        
        theSegmentation = segNode.GetSegmentation()
        theSegmentation.AddEmptySegment("test")

        slicer.modules.segmentations.logic().CreateSegmentFromModelNode(antModel, segNode)
        segNode.SetReferenceImageGeometryParameterFromVolumeNode(inputVolume)
        """


    @staticmethod
    def showVolumeIn3D(volumeNode: slicer.vtkMRMLVolumeNode):
        logic = slicer.modules.volumerendering.logic()
        displayNode = logic.CreateVolumeRenderingDisplayNode()
        displayNode.UnRegister(logic)
        slicer.mrmlScene.AddNode(displayNode)
        volumeNode.AddAndObserveDisplayNodeID(displayNode.GetID())
        logic.UpdateDisplayNodeFromVolumeNode(displayNode, volumeNode)
        #slicer.mrmlScene.RemoveNode(slicer.util.getNode("Volume rendering ROI"))
        

#
# MeniscusSignalIntensityTest
#


class MeniscusSignalIntensityTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_MeniscusSignalIntensity1()

    def test_MeniscusSignalIntensity1(self):
        """Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData

        registerSampleData()
        inputVolume = SampleData.downloadSample("MeniscusSignalIntensity1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = MeniscusSignalIntensityLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay("Test passed")
