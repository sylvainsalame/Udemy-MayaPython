## switch from Arnold to Renderman shaders

import maya.cmds as mc

# rootGrp  = mc.ls(sl = True,l=1)
rootGrp = mc.ls('group1')

grps = mc.listRelatives(rootGrp, ad=1, type='transform', f=1)

# grps = mc.ls(sl = 1,l =1)
if not grps:
    mc.error('===please select===')
ShapeInfo = []
SGInfo = []
shadeInfo = []

for grp in grps:
    shapesInSel = mc.listRelatives(grp, s=1, ni=1, f=1, type='mesh')
    if not shapesInSel:
        pass
    if shapesInSel and shapesInSel[0] not in ShapeInfo:
        SG = mc.listConnections(shapesInSel[0], s=0, d=1, type='shadingEngine')
        if SG:
            shaders = mc.ls(mc.listConnections(SG[0]), materials=1)
            if shaders and mc.nodeType(shaders[0]) not in ['PxrSurface'] and shaders[0] not in shadeInfo:
                ShapeInfo.append(shapesInSel[0])
                SGInfo.append(SG[0])
                shadeInfo.append(shaders[0])
if not ShapeInfo:
    pass
for i in range(len(ShapeInfo)):
    AiShaderNode = shadeInfo[i] + '_RIS'
    if mc.ls(AiShaderNode):
        mc.delete(AiShaderNode)
    PxrShader = mc.shadingNode('PxrSurface', asShader=True, n=AiShaderNode)
    for shaders in SGInfo:
        SGnode = SGInfo[i] + '.surfaceShader'
        mc.connectAttr(PxrShader + '.outColor', SGnode, f=1)
    # newShaders = mc.listConnections(shadeInfo,s=1,d=0)
    fileBaseColor = cmds.listConnections('%s.baseColor' % (shadeInfo[0]), type='file')
    if fileBaseColor:
        for fileNode in fileBaseColor:
            FilePath = cmds.getAttr("%s.fileTextureName" % fileBaseColor[0])
            PxrText = fileBaseColor[i] + '_RIS'
            PxrTextNode = mc.shadingNode('PxrTexture', asShader=True, n=PxrText)
            mc.setAttr(PxrTextNode + '.filename', FilePath, type='string')
            mc.setAttr(PxrTextNode + '.filter', 5)
            mc.connectAttr(PxrTextNode + '.resultRGB', PxrShader + '.diffuseColor', f=1)
    # newShaders = mc.hyperShade(listUpstreamNodes = shadeInfo[0]) diffuseColor
    Attrs = ['.outColor']
    for file in newShaders:
        for attr in Attrs:
            shaderAttr = file + attr
            if not mc.ls(shaderAttr):
                ##print shaders + '_Not Done'
                continue
            mc.connectAttr(shaderAttr, PxrShader + '.diffuseColor', f=1)
            cons = mc.listConnections(shaderAttr, s=1, d=0, plugs=1)
            print cons
            if cons:
                mc.connectAttr(cons[0], shaderAttr)
            try:
                mc.setAttr(shaderAttr, 0)
            except:
                pass
                # print shaders + '_Done'
    switchNode = SGInfo[i] + '_Switch'
    if mc.ls(switchNode):
        mc.delete(switchNode)
    switchNode = mc.createNode('aiRaySwitch', n=switchNode)
    # connect
    mc.connectAttr((shadeInfo[i] + '.outColor'), (switchNode + '.camera'), f=1)
    opaq = mc.getAttr(ShapeInfo[i] + '.aiOpaque')
    checkState = opaq
    if opaq == 1:
        greyNode = shaders + '_Grey'
        mc.createNode('aiStandard', n=greyNode)
        mc.connectAttr(greyNode + '.outColor', switchNode + '.shadow', f=1)
        mc.connectAttr(greyNode + '.outColor', switchNode + '.refraction', f=1)
    else:
        mc.connectAttr(newShaders[0] + '.outColor', switchNode + '.shadow', f=1)
        mc.connectAttr(newShaders[0] + '.outColor', switchNode + '.refraction', f=1)
    checkAttr = switchNode + '.reflection'
    cons = mc.listConnections(checkAttr, s=1, d=0, plugs=1)
    if cons:
        mc.disconnectAttr(cons[0], checkAttr)
    mc.connectAttr(newShaders[0] + '.outColor', checkAttr, f=1)
    checkAttr = switchNode + '.diffuse'
    cons = mc.listConnections(checkAttr, s=1, d=0, plugs=1)
    if cons:
        mc.disconnectAttr(cons[0], checkAttr)
    mc.connectAttr(newShaders[0] + '.outColor', checkAttr, f=1)
    checkAttr = switchNode + '.glossy'
    cons = mc.listConnections(checkAttr, s=1, d=0, plugs=1)
    if cons:
        mc.disconnectAttr(cons[0], checkAttr)
    mc.connectAttr(newShaders[0] + '.outColor', checkAttr, f=1)
    # last
    checkAttr = SGInfo[i] + '.surfaceShader'
    cons = mc.listConnections(checkAttr, s=1, d=0, plugs=1)
    if cons:
        mc.disconnectAttr(cons[0], checkAttr)
    mc.connectAttr(switchNode + '.outColor', checkAttr, f=1)