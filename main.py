from random import random
import glfw
from OpenGL.GL import *
import numpy as np
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath


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
        indices += [N*n+1, i*n, ((i+1)*n)%(N*n)]
    
    vertices += [
        0, 0, 1, r, g, b,
        0, 0, -1, r, g, b 
    ] 
    return bs.Shape(vertices, indices)


#Crear sistema solar scene graph
def createSystem(pipeline):
    solShape = createGPUShape(crearEsfera(100, 1, 1, 0), pipeline)

    solNode = sg.SceneGraphNode("solNode")
    solNode.transform = tr.uniformScale(0.5)
    solNode.childs += [solShape]

    systemNode = sg.SceneGraphNode("sistemaSolar")
    systemNode.childs +=[solNode]

    return systemNode




#Funcion que maneja el uso de teclas
def on_key(window, key, scancode, action, mods):
    #Si no se presiona una tecla no hace nada
    if action != glfw.PRESS:
        return
    
    global controller

    #Cierra la aplicación con escape
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)



def main():

    #inicializa glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)
    
    width = 1000
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
    glClearColor(0.05, 0.05, 0.1, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)


    #Quitar luego
    #Camara
    camera_theta = np.pi/4
    cam_radius = 10
    cam_x = cam_radius * np.sin(camera_theta)
    cam_y = cam_radius * np.cos(camera_theta)
    cam_z = cam_radius/2
    viewPos = np.array([cam_x, cam_y, cam_z])
    view = tr.lookAt(viewPos, np.array([0, 0, 0]),np.array([0, 0, 1]))
    #Proyeccion
    proyeccion = tr.perspective(60, float(1000)/float(1000), 0.1, 100)

    #Crear shapes en la GPU memory
    gpuAxis = createGPUShape(bs.createAxis(7), MVPpipeline)
    shapeNave = bs.readOFF(getAssetPath('tie_UV.off'), (0.3 , 0.3 ,0.3))
    gpuNave = createGPUShape(shapeNave, pipeline)
    sistemaSolar = createSystem(MVPpipeline)


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
        time = glfw.get_time()

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
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0, 5, 0))
        pipeline.drawCall(gpuNave)


        glUseProgram(MVPpipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(MVPpipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        MVPpipeline.drawCall(gpuAxis, GL_LINES)



        sg.drawSceneGraphNode(sistemaSolar, MVPpipeline, "model")







        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)



    # freeing GPU memory
    gpuAxis.clear()
    gpuNave.clear()
    sistemaSolar.clear()

    glfw.terminate()

if __name__ == "__main__":
    main()
