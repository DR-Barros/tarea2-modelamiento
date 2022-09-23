from random import randint, random
import glfw
from OpenGL.GL import *
import numpy as np
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath

#clase para guardar el control de la aplicación
class Controller:
    def __init__(self):
        self.camType = 0
        self.position = np.array([0, -1, 0.1])
        self.theta = 0
        self.phi = 0
        self.front = np.array([0, 1, 0])
        #doblar  toma valores -1 (izquierda), 0, 1 (derecha)
        self.doblar = 0
        self.view = tr.lookAt(np.array([0, 0, 0]), np.array([0, 0, 0]), np.array([0, 0, 1]))
    def derecha(self):
        self.doblar = 1
        self.phi = self.phi + np.pi/100
        self.front = np.array([
            np.sin(self.phi)*np.cos(self.theta),
            np.cos(self.phi)*np.cos(self.theta),
            np.sin(self.theta)
        ])
    def izquierda(self):
        self.doblar = -1
        self.phi = self.phi - np.pi/100
        self.front = np.array([
            np.sin(self.phi)*np.cos(self.theta),
            np.cos(self.phi)*np.cos(self.theta),
            np.sin(self.theta)
        ])
    def arriba(self):
        if self.theta <= np.pi/2-0.1:
            self.theta = self.theta + np.pi/100
            self.front = np.array([
                np.sin(self.phi)*np.cos(self.theta),
                np.cos(self.phi)*np.cos(self.theta),
                np.sin(self.theta)
            ]) 
    def abajo(self):
        if self.theta >= -np.pi/2+0.1:
            self.theta = self.theta - np.pi/100
            self.front = np.array([
                np.sin(self.phi)*np.cos(self.theta),
                np.cos(self.phi)*np.cos(self.theta),
                np.sin(self.theta)
            ])
    def camera(self, time):
        if self.camType == 0:
            self.view = tr.lookAt(
                controller.position - controller.front*0.01 + np.array([0, 0, 0.001]),
                controller.position + np.array([0, 0, 0.001]),
                np.array([0, 0, 1])
            )
        elif self.camType == 1:
            cX = 4
            cY = cX*2 
            if time%1600 < 200:
                posicionAt = np.array([cX, 2-cY*(time%1600)/200, 2])
                posicionFront = np.array([0.08, -0.05, 0.02])
            elif time%1600 < 800:
                posicionAt = np.array([cX*np.cos(np.pi*((time%1600)-200)/600), 2-cY-cX*np.sin(np.pi*((time%1600)-200)/600), 2])
                posicionFront = np.array([0.08*np.cos(np.pi*((time%1600)-200)/600), -0.05 -0.05*np.sin(np.pi*((time%1600)-200)/600), 0.02])
            elif time%1600<1000:
                posicionAt = np.array([-cX, 2-cY +cY*(time%1600-800)/200, 2])
                posicionFront = np.array([-0.08, -0.05, 0.02])
            else:
                posicionAt = np.array([-cX*np.cos(np.pi*((time%1600)-1000)/600), 2+cX*np.sin(np.pi*((time%1600)-1000)/600), 2])
                posicionFront = np.array([-0.08*np.cos(np.pi*((time%1600)-1000)/600), -0.05 -0.05*np.sin(np.pi*((time%1600)-200)/600), 0.02])

            self.view = tr.lookAt(
                posicionAt + posicionFront,
                posicionAt,
                np.array([0, 0, 1])
            )
            

        return self.view
        


#iniciamos el controlador
controller = Controller()

# funcion para facilitar inicialización
def createGPUShape(shape, pipeline):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

#Funcion crear esfera
def crearEsfera(N, r,g,b):
    vertices = []
    indices = []
    angulo = 2 * np.pi
    n = int(N/2)-1
    for i in range(N):
        indices += [N*n, i*n, ((i+1)*n)%(N*n)]
        rand = random()/8
        for j in range(n):
            theta = (j+1)/N * angulo
            omega = i/N * angulo
            vertices += [
                    np.sin(theta)*np.cos(omega), np.sin(theta)*np.sin(omega), np.cos(theta), abs(r-rand), abs(g-rand), abs(b-rand)
                ]
        for j in range(n-1):
            indices += [
                n*i+j, n*i+1+j, (n*(i+1)+j)%(N*n),
                n*i+1+j, (n*(i+1)+j)%(N*n), (n*(i+1)+1+j)%(N*n),
            ]
        indices += [N*n+1, (i*n-1)%(N*n), ((i+1)*n-1)%(N*n)]
    
    vertices += [
        0, 0, 1, r, g, b,
        0, 0, -1, r, g, b 
    ] 
    return bs.Shape(vertices, indices)

#Funcion crear anillo
def crearAnillo(N, R, r, g, b):
    vertices = []
    indices = []
    for i in range(N):
        theta = i/N * 2*np.pi
        vertices += [
            R*np.cos(theta), R*np.sin(theta), 0, r,g,b,
            (R+0.1)*np.cos(theta), (R+0.1)*np.sin(theta), 0, r,g,b,
        ]
        indices += [
            i, i+1, i+2,
            (i+N)%(N*2), (i+N+1)%(N*2), (i+N+2)%(N*2)
        ]
    return bs.Shape(vertices, indices)

#Crear sistema solar scene graph
def createSystem(pipeline):
    solShape = createGPUShape(crearEsfera(100, 1, 1, 0), pipeline)
    mercurioShape = createGPUShape(crearEsfera(100, 0,1,0), pipeline)
    venusShape = createGPUShape(crearEsfera(100, 0,1,1), pipeline)
    tierraShape = createGPUShape(crearEsfera(100, 0,0,1), pipeline)
    lunaShape = createGPUShape(crearEsfera(100, 1,1,1), pipeline)
    marteShape = createGPUShape(crearEsfera(100, 1,0,0), pipeline)
    jupiterShape = createGPUShape(crearEsfera(100, 1,0,1), pipeline)
    saturnoShape = createGPUShape(crearEsfera(100, 0.5,1,0.5), pipeline)
    anillo1Shape = createGPUShape(crearAnillo(25, 1, 1, 1, 1), pipeline)
    anillo2Shape = createGPUShape(crearAnillo(25, 1.15, 0.8, 0.8, 0.8), pipeline)
    anillo3Shape = createGPUShape(crearAnillo(25, 1.3, 0.6, 0.6, 0.6), pipeline)
    uranoShape = createGPUShape(crearEsfera(100, 1,0.5,0), pipeline)
    neptunoShape = createGPUShape(crearEsfera(100, 0.5,0.8,0), pipeline)
    plutonShape = createGPUShape(crearEsfera(100, 0.1,0.8,0.5), pipeline)
    cometaShape = createGPUShape(crearEsfera(100, 136/255, 9/255, 123/255), pipeline)

    solNode = sg.SceneGraphNode("solNode")
    solNode.transform = tr.uniformScale(1)
    solNode.childs += [solShape]

    mercurioNode = sg.SceneGraphNode("mercurioNode")
    mercurioNode.transform = tr.uniformScale(0.1)
    mercurioNode.childs += [mercurioShape]
    mercurioTranslation = sg.SceneGraphNode("mercurioTranslation")
    mercurioTranslation.transform = tr.translate(-1.5, 0, 0)
    mercurioTranslation.childs += [mercurioNode]

    venusNode = sg.SceneGraphNode("venusNode")
    venusNode.transform = tr.uniformScale(0.2)
    venusNode.childs += [venusShape]
    venusTranslation = sg.SceneGraphNode("venusTranslation")
    venusTranslation.transform = tr.translate(-2.2, 0, 0)
    venusTranslation.childs += [venusNode]

    tierraNode = sg.SceneGraphNode("tierraNode")
    tierraNode.transform = tr.uniformScale(0.22)
    tierraNode.childs += [tierraShape]
    lunaNode = sg.SceneGraphNode("lunaNode")
    lunaNode.transform = tr.uniformScale(0.08)
    lunaNode.childs += [lunaShape]
    lunaTranslation = sg.SceneGraphNode("lunaTranslation")
    lunaTranslation.transform = tr.translate(0.5, 0, 0)
    lunaTranslation.childs += [lunaNode]
    sistemaTierraLuna = sg.SceneGraphNode("sistemaTierraLuna")
    sistemaTierraLuna.transform = tr.translate(-3, 0, 0)
    sistemaTierraLuna.childs += [tierraNode, lunaTranslation]

    marteNode = sg.SceneGraphNode("marteNode")
    marteNode.transform = tr.uniformScale(0.2)
    marteNode.childs += [marteShape]
    marteTranslation = sg.SceneGraphNode("marteTranslation")
    marteTranslation.transform = tr.translate(-4.5, 0, 0)
    marteTranslation.childs += [marteNode]

    jupiterNode = sg.SceneGraphNode("jupiterNode")
    jupiterNode.transform = tr.uniformScale(0.52)
    jupiterNode.childs += [jupiterShape]
    jupiterTranslation = sg.SceneGraphNode("jupiterTranslation")
    jupiterTranslation.transform = tr.translate(-13, 0, 0)
    jupiterTranslation.childs += [jupiterNode]

    saturnoNode =sg.SceneGraphNode("saturnoNode")
    saturnoNode.transform = tr.uniformScale(0.50)
    saturnoNode.childs += [saturnoShape]
    anillo1Node = sg.SceneGraphNode("anillo1Node")
    anillo1Node.transform = tr.matmul([
        tr.rotationX(0.1 * np.pi),
        tr.uniformScale(0.54)
    ])
    anillo1Node.childs += [anillo1Shape]
    anillo2Node = sg.SceneGraphNode("anillo2Node")
    anillo2Node.transform = tr.matmul([
        tr.rotationX(0.1 * np.pi),
        tr.uniformScale(0.54)
    ])
    anillo2Node.childs += [anillo2Shape]
    anillo3Node = sg.SceneGraphNode("anillo3Node")
    anillo3Node.transform = tr.matmul([
        tr.rotationX(0.1 * np.pi),
        tr.uniformScale(0.54)
    ])
    anillo3Node.childs += [anillo3Shape]
    sistemaSaturno = sg.SceneGraphNode("sistemaSaturno")
    sistemaSaturno.transform = tr.translate(-23.8, 0, 0)
    sistemaSaturno.childs += [saturnoNode, anillo1Node, anillo2Node, anillo3Node]

    uranoNode = sg.SceneGraphNode("uranoNode")
    uranoNode.transform = tr.uniformScale(0.4)
    uranoNode.childs += [uranoShape]
    uranoTranslation = sg.SceneGraphNode("uranoTranslation")
    uranoTranslation.transform = tr.translate(-48.7, 0, 0)
    uranoTranslation.childs += [uranoNode]

    neptunoNode = sg.SceneGraphNode("neptunoNode")
    neptunoNode.transform = tr.uniformScale(0.4)
    neptunoNode.childs += [neptunoShape]
    neptunoTranslation = sg.SceneGraphNode("neptunoTranslation")
    neptunoTranslation.transform = tr.translate(-75.1, 0, 0)
    neptunoTranslation.childs += [neptunoNode]

    plutonNode = sg.SceneGraphNode("plutonNode")
    plutonNode.transform = tr.uniformScale(0.08)
    plutonNode.childs += [plutonShape]
    plutonTranslation = sg.SceneGraphNode("plutonTranslation")
    plutonTranslation.transform = tr.translate(-98.6, 0, 0)
    plutonTranslation.childs += [plutonNode]

    cometaNode =sg.SceneGraphNode("cometaNode")
    cometaNode.transform = tr.uniformScale(0.01)
    cometaNode.childs += [cometaShape]
    cometaTranslation =sg.SceneGraphNode("cometaTranslation")
    cometaTranslation.transform = tr.translate(0,0,0)
    cometaTranslation.childs += [cometaNode]

    systemNode = sg.SceneGraphNode("sistemaSolar")
    systemNode.childs +=[
        solNode, 
        mercurioTranslation,
        venusTranslation,
        sistemaTierraLuna,
        marteTranslation,
        jupiterTranslation,
        sistemaSaturno,
        uranoTranslation,
        neptunoTranslation,
        plutonTranslation,
        cometaTranslation
    ]

    return systemNode

#Crear fondo de estrellas
def createStars(pipeline):
    estrellasShape = createGPUShape(crearEsfera(100, 1, 1, 0), pipeline)
    sceneNode = sg.SceneGraphNode("fondo")
    contador = 0
    estrellas = []
    while contador < 1000:
        distancia = randint(150, 500)
        theta = random() * np.pi
        omega = (random() - 1)*2 * np.pi
        name = str(contador)
        estrellas += [sg.SceneGraphNode(name)]
        estrellas[contador].transform = tr.matmul([
            tr.translate(distancia*np.sin(theta)*np.cos(omega), distancia*np.sin(theta)*np.sin(omega), distancia*np.cos(theta)),
            tr.uniformScale(random())
        ])
        estrellas[contador].childs += [estrellasShape]
        sceneNode.childs += [estrellas[contador]]
        contador += 1
    

    return sceneNode

#Crear batalla de naves scene graph
def createFighter(pipeline):
    corvetteShape = createGPUShape(bs.readOFF(getAssetPath('Costum_Corvette.off'), (0.3 , 0.3 ,0.3)), pipeline)
    fromSPShape = createGPUShape(bs.readOFF(getAssetPath('FromSP.off'), (0.3 , 0.3 ,0.3)), pipeline)
    destroyerShape = createGPUShape(bs.readOFF(getAssetPath('Imperial_star_destroyer.off'), (0.5 , 0.5 ,0.5)), pipeline)
    kontosShape = createGPUShape(bs.readOFF(getAssetPath('Kontos.off'), (0.3 , 0.3 ,0.3)), pipeline)
    nabooFighterShape = createGPUShape(bs.readOFF(getAssetPath('NabooFighter.off'), (0.3 , 0.3 ,0.3)), pipeline)
    tieUVShape = createGPUShape(bs.readOFF(getAssetPath('tie_UV.off'), (0.3 , 0.3 ,0.3)), pipeline)
    triFigtherShape = createGPUShape(bs.readOFF(getAssetPath('Tri_Fighter.off'), (0.3 , 0.3 ,0.3)), pipeline)
    xWingShape = createGPUShape(bs.readOFF(getAssetPath('XJ5 X-wing starfighter.off'), (0.9 , 0.9 ,0.9)), pipeline)

    #Crear nodos por cada shape, con la escala de las naves

    corvetteNode = sg.SceneGraphNode("corvetteNode")
    corvetteNode.transform = tr.matmul([
        tr.rotationX(np.pi/2),
        tr.uniformScale(0.05)
    ])
    corvetteNode.childs += [corvetteShape]

    destroyerNode = sg.SceneGraphNode("destroyerNode")
    destroyerNode.transform = tr.matmul([
        tr.rotationX(np.pi/2),
        tr.uniformScale(0.05)
    ])
    destroyerNode.childs += [destroyerShape]

    tieUVNode = sg.SceneGraphNode("tieUVNode")
    tieUVNode.transform = tr.matmul([
        tr.rotationX(np.pi/2),
        tr.uniformScale(0.005)
    ])
    tieUVNode.childs += [tieUVShape]
    
    kontosNode = sg.SceneGraphNode("kontosNode")
    kontosNode.transform = tr.matmul([
        tr.rotationX(np.pi/2),
        tr.uniformScale(0.05)
    ])
    kontosNode.childs += [kontosShape]

    nabooNode = sg.SceneGraphNode("nabooNode")
    nabooNode.transform = tr.matmul([
        tr.rotationX(np.pi/2),
        tr.uniformScale(0.005)
    ])
    nabooNode.childs += [nabooFighterShape]
    


    xWingNode = sg.SceneGraphNode("xWingNode")
    xWingNode.transform = tr.matmul([
        tr.rotationX(np.pi/2),
        tr.uniformScale(0.005)
    ])
    xWingNode.childs += [xWingShape]

    #Rotacion de naves 

    #Tie
    tieUVTraslation = sg.SceneGraphNode("tieUVTraslation")
    tieUVTraslation.transform = tr.translate(0.03, 0, 0)
    tieUVTraslation.childs += [tieUVNode]

    tieUVRotation = sg.SceneGraphNode("tieUVRotation")
    tieUVRotation.transform = tr.rotationZ(0)
    tieUVRotation.childs += [tieUVTraslation]


    #crear destructores con un Tie rotando al rededor
    destroyer1 = sg.SceneGraphNode("destroyer1")
    destroyer1.transform = tr.identity()
    destroyer1.childs += [destroyerNode, tieUVRotation]

    destroyer2 = sg.SceneGraphNode("destroyer2")
    destroyer2.transform = tr.translate(-0.05, -0.02, -0.02)
    destroyer2.childs += [destroyerNode, tieUVRotation]

    destroyer3 = sg.SceneGraphNode("destroyer3")
    destroyer3.transform = tr.translate(0.05, -0.02, -0.02)
    destroyer3.childs += [destroyerNode, tieUVRotation]

    convoy = sg.SceneGraphNode("convoy")
    convoy.transform = tr.identity()
    convoy.childs += [destroyer1, destroyer2, destroyer3]

    tierraConvoy = sg.SceneGraphNode("tierraConvoy")
    tierraConvoy.transform = tr.identity()
    tierraConvoy.childs += [destroyer1, destroyer2, destroyer3]

    usuario =sg.SceneGraphNode("usuario")
    usuario.transform = tr.identity()
    usuario.childs += [xWingNode]

    sceneNode = sg.SceneGraphNode("naves")
    sceneNode.childs += [usuario, convoy, kontosNode]

    return sceneNode

#Funcion que maneja el uso de teclas
def on_key(window, key, scancode, action, mods):
    #Si no se presiona una tecla no hace nada
    if action != glfw.PRESS:
        return
    
    global controller

    #Cierra la aplicación con escape
    if key == glfw.KEY_0:
        controller.camType = 0
    if key == glfw.KEY_1:
        controller.camType = 1
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def main():

    #inicializa glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)
    
    width = 1500
    height = 1000

    window = glfw.create_window(width, height, "Tarea 2", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)
    
    glfw.make_context_current(window)

    #Conecta la funcion callback 'on_key' para manejar los eventos del teclado
    glfw.set_key_callback(window, on_key)

    #Ensamblando el shader program
    MVPpipeline = es.SimpleModelViewProjectionShaderProgram()
    pipeline = ls.SimpleFlatShaderProgram()


    #mandar a OpenGL a usar el shader program
    glUseProgram(pipeline.shaderProgram)

    #setiando el color de fondo
    glClearColor(0.05, 0.05, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    #Proyeccion
    proyeccion = tr.perspective(60, float(1500)/float(1000), 0.001, 200)

    #Crear shapes en la GPU memory
    gpuAxis = createGPUShape(bs.createAxis(7), MVPpipeline)
    sistemaSolar = createSystem(MVPpipeline)
    fondo = createStars(MVPpipeline)
    figther = createFighter(pipeline)


    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    #Luminocidad
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 5, 5, 5)
    
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    while not glfw.window_should_close(window):

        #usar GLFW para chequear input events
        glfw.poll_events()

        #contador de tiempo
        time = 10 * glfw.get_time()

        #iputs nave usuario
        global controller
        if controller.camType == 0:
            if glfw.get_key(window,glfw.KEY_SPACE) == glfw.PRESS:
                if glfw.get_key(window,glfw.KEY_D) == glfw.PRESS:
                    controller.derecha()
                elif glfw.get_key(window,glfw.KEY_A) == glfw.PRESS:
                    controller.izquierda()
                if glfw.get_key(window,glfw.KEY_W) == glfw.PRESS:
                    controller.arriba()
                elif glfw.get_key(window,glfw.KEY_S) == glfw.PRESS:
                    controller.abajo()
                if glfw.get_key(window,glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
                    controller.position = controller.position +controller.front*0.005
                else:
                    controller.position = controller.position +controller.front*0.0005


        view = controller.camera(time)

        #View y proyeccion
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, proyeccion)

        glUseProgram(MVPpipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(MVPpipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(MVPpipeline.shaderProgram, "projection"), 1, GL_TRUE, proyeccion)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


        #Modelos

        
        glUseProgram(pipeline.shaderProgram)
        #Naves

        convoy = sg.findNode(figther, "convoy")
        destroyer1 = sg.findNode(figther, "destroyer1")
        destroyer2 = sg.findNode(figther, "destroyer2")
        destroyer3 = sg.findNode(figther, "destroyer3")
        tieRotation = sg.findNode(figther, "tieUVRotation")
        tieRotation.transform = tr.rotationZ(time/10)
        cX = 4
        cY = cX*2
        if time%1600<200:
            convoy.transform = tr.translate(cX, 2-cY*(time%1600)/200, 2)
        elif time%1600<800:
            convoy.transform = tr.matmul([
                tr.translate(cX*np.cos(np.pi*((time%1600)-200)/600), 2-cY-cX*np.sin(np.pi*((time%1600)-200)/600), 2),
                tr.rotationZ(-np.pi*((time%1600)-200)/600)
            ])
            destroyer1.transform = tr.rotationY(-np.pi/16)
            destroyer2.transform = tr.matmul([
                tr.translate(-0.05, -0.02, -0.02),
                tr.rotationY(-np.pi/16)
            ])
            destroyer3.transform = tr.matmul([
                tr.translate(0.05, -0.02, -0.02),
                tr.rotationY(-np.pi/16)
            ])    
        elif time%1600<1000:
            convoy.transform = tr.matmul([
                tr.translate(-cX, 2-cY +cY*(time%1600-800)/200, 2),
                tr.rotationZ(-np.pi)
            ])
        else:
            convoy.transform = tr.matmul([
                tr.translate(-cX*np.cos(np.pi*((time%1600)-1000)/600), 2+cX*np.sin(np.pi*((time%1600)-1000)/600), 2),
                tr.rotationZ(-np.pi-np.pi*((time%1600)-1000)/600)
            ])
            destroyer1.transform = tr.rotationY(-np.pi/16)
            destroyer2.transform = tr.matmul([
                tr.translate(-0.05, -0.02, -0.02),
                tr.rotationY(-np.pi/16)
            ])
            destroyer3.transform = tr.matmul([
                tr.translate(0.05, -0.02, -0.02),
                tr.rotationY(-np.pi/16)
            ])


        sg.drawSceneGraphNode(figther, pipeline, "model")

        #nave usuario
        usuarioNave = sg.findNode(figther, "usuario")
        if controller.doblar == 0:
            usuarioNave.transform = tr.matmul([
                tr.translate(
                    controller.position[0],
                    controller.position[1],
                    controller.position[2],
                ),
                tr.rotationZ(-controller.phi),
                tr.rotationX(controller.theta),
            ])
        #doblar derecha
        elif controller.doblar == 1:
            usuarioNave.transform = tr.matmul([
                tr.translate(
                    controller.position[0],
                    controller.position[1],
                    controller.position[2],
                ),
                tr.rotationZ(-controller.phi),
                tr.rotationX(controller.theta),
                tr.rotationY(np.pi/8)
            ])
            controller.doblar = 0
        #doblar izquierda
        else:
            usuarioNave.transform = tr.matmul([
                tr.translate(
                    controller.position[0],
                    controller.position[1],
                    controller.position[2],
                ),
                tr.rotationZ(-controller.phi),
                tr.rotationX(controller.theta),
                tr.rotationY(-np.pi/8)
            ])
            controller.doblar = 0

       


        glUseProgram(MVPpipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(MVPpipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        MVPpipeline.drawCall(gpuAxis, GL_LINES)


        #Sistema Solar
        sol = sg.findNode(sistemaSolar, "solNode")
        sol.transform = tr.matmul([
            tr.rotationZ(time/27),
            tr.uniformScale(0.1)
        ])

        mercurio = sg.findNode(sistemaSolar, "mercurioNode")
        mercurio.transform = tr.matmul([
            tr.rotationZ(time/0.16),
            tr.uniformScale(0.1)
        ])
        mercuriotraslacion = sg.findNode(sistemaSolar, "mercurioTranslation")
        mercuriotraslacion.transform = tr.matmul([
            tr.rotationZ(time/58.5),
            tr.translate(-1.5, 0, 0)
        ])

        venus = sg.findNode(sistemaSolar, "venusNode")
        venus.transform = tr.matmul([
            tr.rotationZ(time/243),
            tr.uniformScale(0.2)
        ])
        venustraslacion = sg.findNode(sistemaSolar, "venusTranslation")
        venustraslacion.transform = tr.matmul([
            tr.rotationZ(time/224),
            tr.translate(-2.2, 0, 0)
        ])
        
        tierra = sg.findNode(sistemaSolar, "tierraNode")
        tierra.transform = tr.matmul([
            tr.rotationZ(time),
            tr.uniformScale(0.22)

        ])
        luna = sg.findNode(sistemaSolar, "lunaNode")
        luna.transform = tr.matmul([
            tr.rotationZ(time/29.5),
            tr.uniformScale(0.08)
        ])
        lunatraslacion = sg.findNode(sistemaSolar, "lunaTranslation")
        lunatraslacion.transform = tr.matmul([
            tr.rotationZ(time/29.5),
            tr.translate(0.5, 0, 0)
        ])
        sistTierraLuna = sg.findNode(sistemaSolar, "sistemaTierraLuna")
        sistTierraLuna.transform = tr.matmul([
            tr.rotationZ(time/365),
            tr.translate(-3, 0, 0)
        ])

        marte = sg.findNode(sistemaSolar, "marteNode")
        marte.transform = tr.matmul([
            tr.rotationZ(time),
            tr.uniformScale(0.2)
        ])
        martetraslacion = sg.findNode(sistemaSolar, "marteTranslation")
        martetraslacion.transform = tr.matmul([
            tr.rotationZ(time/668),
            tr.translate(-4.5, 0, 0)
        ])

        jupiter = sg.findNode(sistemaSolar, "jupiterNode")
        jupiter.transform = tr.matmul([
            tr.rotationZ(2.4 * time),
            tr.uniformScale(0.52)
        ])
        jupitertraslacion = sg.findNode(sistemaSolar, "jupiterTranslation")
        jupitertraslacion.transform = tr.matmul([
            tr.rotationZ(time/3942),
            tr.translate(-13, 0, 0)
        ])

        saturno = sg.findNode(sistemaSolar, "saturnoNode")
        saturno.transform = tr.matmul([
            tr.rotationZ(2.4 * time),
            tr.uniformScale(0.5)
        ])
        saturnotraslacion = sg.findNode(sistemaSolar, "sistemaSaturno")
        saturnotraslacion.transform = tr.matmul([
            tr.rotationZ(time/10767),
            tr.translate(-23.8, 0, 0)
        ])

        urano = sg.findNode(sistemaSolar, "uranoNode")
        urano.transform = tr.matmul([
            tr.rotationZ(1.4 * time),
            tr.uniformScale(0.4)
        ])
        uranotraslacion = sg.findNode(sistemaSolar, "uranoTranslation")
        uranotraslacion.transform = tr.matmul([
            tr.rotationZ(time/30660),
            tr.translate(-48.7, 0, 0)
        ])

        neptuno = sg.findNode(sistemaSolar, "neptunoNode")
        neptuno.transform = tr.matmul([
            tr.rotationZ(1.5 * time),
            tr.uniformScale(0.4)
        ])
        neptunotraslacion = sg.findNode(sistemaSolar, "neptunoTranslation")
        neptunotraslacion.transform = tr.matmul([
            tr.rotationZ(time/60225),
            tr.translate(-75.1, 0, 0)
        ])

        pluton = sg.findNode(sistemaSolar, "plutonNode")
        pluton.transform = tr.matmul([
            tr.rotationZ(time/367),
            tr.uniformScale(0.08)
        ])
        plutontraslacion = sg.findNode(sistemaSolar, "plutonTranslation")
        plutontraslacion.transform = tr.matmul([
            tr.rotationZ(time/90520),
            tr.translate(-98.6, 0, 0)
        ])
        
        cometa = sg.findNode(sistemaSolar, "cometaTranslation")
        cometa.transform = tr.translate((4- 2*np.cos(np.pi*time/10))*np.cos(np.pi*time/10), (4- 2*np.cos(np.pi*time/10))*np.sin(np.pi*time/10), 0)



        #sg.drawSceneGraphNode(sistemaSolar, MVPpipeline, "model")
        sg.drawSceneGraphNode(fondo, MVPpipeline, "model")
        


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)



    # freeing GPU memory
    gpuAxis.clear()
    sistemaSolar.clear()
    fondo.clear()
    figther.clear()

    glfw.terminate()

if __name__ == "__main__":
    main()
