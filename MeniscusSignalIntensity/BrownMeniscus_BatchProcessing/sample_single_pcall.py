import slicer
import DICOMLib
from DICOMLib import DICOMUtils
from DICOM import DICOMWidget #slicer.util.selectModule("DICOM")
from MeniscusSignalIntensity import MeniscusSignalIntensityLogic as mL



def meniscusSItoTable(inputVolume, medModel, latModel, anatomy):
    """This function is used to compute the model parameters and segment the meniscus
    from the input volume. It will return a table with the results."""


    #mL.compute_model_parameters(inputVolume, medModel, latModel, anatomy)
    #not necessarily intuitive.. but the swap to compute left- is to swap Med<->Lat
    medTrue = True
    latTrue = False


    if anatomy == 'right':
        # meniscus centroid and planes
        medAntPlane, medPostPlane = mL.generateCutPlaneCoords_fromMenicus(mWidget,
            medModel,
            True,
        )

        latAntPlane, latPostPlane = mL.generateCutPlaneCoords_fromMenicus(mWidget,
            latModel,
            False,
        )
        """using the anterior and posterior defined planes, cute each meniscus into
        anterior, mid and posterior sections."""

        medAntModel,medMidModel,medPostModel = mL.cutModelFromPlanes(mWidget,
            medModel,
            medAntPlane,
            medPostPlane,
            medTrue,
        )
        latAntModel, latMidModel,latPostModel =  mL.cutModelFromPlanes(mWidget,
            latModel,
            latAntPlane,
            latPostPlane,
            latTrue,
        )
    else:
        
        #LEFT CASE
        medAntPlane, medPostPlane = mL.generateCutPlaneCoords_fromMenicus(mWidget,
            latModel,
            True,
        )
        latAntPlane, latPostPlane =mL.generateCutPlaneCoords_fromMenicus(mWidget,
            medModel,
            False,
        )

            
        """using the anterior and posterior defined planes, cute each meniscus into
        anterior, mid and posterior sections."""

        medAntModel,medMidModel,medPostModel = mL.cutModelFromPlanes(mWidget,
            latModel,
            medAntPlane,
            medPostPlane,
            medTrue,
        )
        
        latAntModel, latMidModel,latPostModel = mL.cutModelFromPlanes(mWidget,
            medModel,
            latAntPlane,
            latPostPlane,
            latTrue,
        )


    #hide input model and color each output here?
    medModel.SetDisplayVisibility(False)
    latModel.SetDisplayVisibility(False)


    #vtk 0 to 1 coloring of the models
    medAntModel.GetDisplayNode().SetColor(1.0, 1.5, 0.0)  # red
    medMidModel.GetDisplayNode().SetColor(0.5, 0.0, 1.0)  # blue
    medPostModel.GetDisplayNode().SetColor(0.25, 0.5, 0.4)  # green

    latAntModel.GetDisplayNode().SetColor(1.0, 1.5, 0.0)  # red
    latMidModel.GetDisplayNode().SetColor(0.5, 0.0, 1.0)  # blue
    latPostModel.GetDisplayNode().SetColor(0.25, 0.5, 0.4)  # green

    medAntModel.SetDisplayVisibility(True)
    medMidModel.SetDisplayVisibility(True)
    medPostModel.SetDisplayVisibility(True)

    latAntModel.SetDisplayVisibility(True)
    latMidModel.SetDisplayVisibility(True)
    latPostModel.SetDisplayVisibility(True)


        
        #newTable = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
        #mNode.resultsTable = newTable
        

    resTable = mL.segmentFromModels(mWidget,
        outdir,
        inputVolume,
        medAntModel,
        medMidModel,
        medPostModel,
        medTrue,
        medModel.GetName(),
    )       

    mL.segmentFromModels(mWidget,
        outdir,
        inputVolume,
        latAntModel,
        latMidModel,
        latPostModel,
        latTrue,
        latModel.GetName(),
        resTable
    )



dcm_folder = 'P:\\DBarnes\\Meniscus\\Slicer_6mo_data\\BEAR_II_100_6_M_left_Sx_BEAR_CISS\\B2_100_6mo'
mm_stl = 'P:\\DBarnes\\Meniscus\\Slicer_6mo_data\\BEAR_II_100_6_M_left_Sx_BEAR_CISS\\BEAR_II_100_6_M_left_Sx_BEAR_CISS_MM.stl'
lm_stl = 'P:\\DBarnes\\Meniscus\\Slicer_6mo_data\\BEAR_II_100_6_M_left_Sx_BEAR_CISS\\BEAR_II_100_6_M_left_Sx_BEAR_CISS_LM.stl'
anatomy = 'left'

outdir ='P:\\DBarnes\\Meniscus\\Slicer_6mo_data\\_csvSignalIntensity'

db = slicer.dicomDatabase

DICOMLib.clearDatabase(slicer.dicomDatabase)
slicer.mrmlScene.Clear(0)

dicomBrowser = slicer.modules.DICOMWidget.browserWidget.dicomBrowser
dicomBrowser.importDirectory(dcm_folder, dicomBrowser.ImportDirectoryAddLink)
  # wait for import to finish before proceeding (optional, if removed then import runs in the background)
dicomBrowser.waitForImportFinished()


browserWidget = slicer.modules.DICOMWidget.browserWidget

patient = db.patients()[0]
studies = db.studiesForPatient(patient)
series = [db.seriesForStudy(study) for study in studies]
seriesUIDs = [uid for uidList in series for uid in uidList]

browserWidget.onSeriesSelected(seriesUIDs)
browserWidget.loadCheckedLoadables()

inputVolume = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
medModel = slicer.util.loadModel(mm_stl)
latModel = slicer.util.loadModel(lm_stl)

#mNode = mL.getParameterNode()
mWidget = slicer.modules.meniscussignalintensity.widgetRepresentation().self()

meniscusSItoTable(inputVolume, medModel, latModel, anatomy)
