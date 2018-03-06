from maya import cmds

SUFFIXES = {
    "mesh": "GEO",
    "joint": "JNT",
    "camera": None,
    "ambientLight": "LGT",
    "directionalLight": "LGT",
    "pointLight": "LGT",
    "spotLight": "LGT",
    "areaLight": "LGT",
    "volumeLight": "LGT",
    "aiAreaLight": "LGT",
    "aiPhotometricLight": "LGT",
    "aiSkyDomeLight": "LGT",
    "aiLightPortal": "LGT",
    "aiMeshLight": "LGT",
}

DEFAULT_SUFFIX = "GRP"

def rename(selection=False):
    """
    This function will rename any objects to have the correct suffix
    :param
    selection: Whether or we use the current selection
    :return:
    a list of all the objects we operated on
    """
    objects = cmds.ls(selection=selection, dag=True, long=True)

    # This function cannot run is there is no selection and no objects
    if selection and not objects:
        raise RuntimeError("You don't have anything selected! How dare you?!")

    objects.sort(key=len, reverse=True)

    for obj in objects:
        shortName = obj.split("|")[-1]

        children = cmds.listRelatives(obj, children=True, fullPath=True) or []

        if len(children) == 1:
            child = children[0]
            objType = cmds.objectType(child)

        else:
            objType = cmds.objectType(obj)

        '''
        if objType == "mesh":
            suffix = "GEO"
        elif objType == "joint":
            suffix = "JNT"
        elif objType == "camera":
            # print "Skipping camera"
            continue
        #elif cmds.objExists('*Light*'):
        #    suffix = "LGT"
        else:
            suffix = "GRP"
        '''

        suffix = SUFFIXES.get(objType, DEFAULT_SUFFIX)

        if not suffix:
            continue

        if obj.endswith('_' + suffix):
            continue

        # newName = shortName + "_" + suffix
        newName = "%s_%s" % (shortName, suffix)
        cmds.rename(obj, newName)

        index = objects.index(obj)
        objects[index] = obj.replace(shortName, newName)

    return objects