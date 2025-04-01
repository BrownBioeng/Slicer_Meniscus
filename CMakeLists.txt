cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(MeniscusMetrics)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/MeniscusMetrics")
set(EXTENSION_CONTRIBUTORS "Amy Morton (BUH)")
set(EXTENSION_DESCRIPTION "ACL R meniscus measurements toolset")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/MeniscusMetrics.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/MeniscusMetrics/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(MeniscusSignalIntensity)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
