import pygame
import time
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
from PIL import ImageOps
import math
import json

# Define vertices, edges, and faces of the cube
slabVertices = [
    [1, -0.5, -1],
    [1, 0.5, -1],
    [-1, 0.5, -1],
    [-1, -0.5, -1],
    [1, -0.5, 1],
    [1, 0.5, 1],
    [-1, -0.5, 1],
    [-1, 0.5, 1]
]

blockVertices = [
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, -1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, -1, 1],
    [-1, 1, 1]
]

faces = [
    (0, 1, 2, 3),
    (6, 3, 2, 7),
    (4, 6, 7, 5),
    (5, 4, 0, 1),
    (0, 4, 6, 3),
    (2, 1, 5, 7)
]

# Texture coordinates for each vertex
block_coords = [
    (1, 0),
    (0, 0),
    (0, 1),
    (1, 1)
]

slab_coords = [
    (1, 0),
    (0, 0),
    (0, .5),
    (1, .5)
]

def open_local(file_name):
   script_dir = os.path.dirname(os.path.abspath(__file__))
   file_path = os.path.join(script_dir, file_name)

   return open(file_path, 'r')

# Will return verticies only for now
def getVerticies(file):
    if file.endswith('.json'):
        openFile = open_local(file)
        data = json.load(openFile)
        verts = []
        faces = []

        of = 0
        for brush in data["elements"]:
            fx, fy, fz = brush["from"]
            tx, ty, tz = brush["to"]

            

            if ('rotation' in brush):
                angle = brush['rotation']['angle']
                axis = brush['rotation']['axis']
                origin = brush['rotation']['origin']

                frot = rotate_vector(np.array([fx, fy, fz]), axis, angle, origin)
                trot = rotate_vector(np.array([tx, ty, tz]), axis, angle, origin)
                fx = frot[0]
                fy = frot[1]
                fz = frot[2]

                tx = trot[0]
                ty = trot[1]
                tz = trot[2]
                
            
            #fx, fy, fz = center_vector(fx, fy, fz)
            #tx, ty, tz = center_vector(tx, ty, tz)


            verts.append([fx,fy,fz])
            verts.append([fx,ty,fz])
            verts.append([tx,ty,fz])
            verts.append([tx,fy,fz])
            verts.append([tx,fy,tz])
            verts.append([tx,ty,tz])
            verts.append([fx,ty,tz])
            verts.append([fx,fy,tz])

            faces.append((0+of, 1+of, 2+of, 3+of))
            faces.append((3+of, 2+of, 5+of, 4+of))
            faces.append((4+of, 5+of, 6+of, 7+of))
            faces.append((7+of, 6+of, 1+of, 0+of))
            faces.append((0+of, 7+of, 4+of, 3+of))
            faces.append((1+of, 6+of, 5+of, 2+of))

            of = of+8
        return verts, faces


def getParentModel(file):
    if file.endswith('.json'):
        openFile = open_local(file)
        data = json.load(openFile)
        parentFound = False
        parentPath = file
        while (parentFound == False):
            try:
                elementCheck = data["elements"]
                return parentPath
            except:
                parent = data["parent"]
                parentPath = parent.split(":")[0] + "/models/" + parent.split(":")[1] + ".json"
                openFile = open_local(parentPath)
                data = json.load(openFile)


def setTextures(filename):
    pathPrefix = '../../textures/block/'
    endTexture =''
    sideTexture =''
    itemName = ''
    type =''

    if filename.endswith('.json'):
        file = open(filename, "r")
        data = json.load(file)

        if 'block' in filename:
            type = 'block'
        elif 'slab' in filename:
            type = 'slab'
        else:
            type = 'block'
        
        try:
            for k,v in data["textures"].items():
                itemName = pathPrefix + v.split('k/')[1]
                match k:
                    case "end":
                        endTexture = itemName + ".png"
                    case "top":
                        endTexture = itemName + ".png"
                    case "bottom":
                        endTexture = itemName + ".png"
                    case "side":
                        sideTexture = itemName + ".png"
                    case "all":
                        endTexture = itemName + ".png"
                        sideTexture = itemName + ".png"
                    case _:
                        print("File Not Found")

            return type, [
                pygame.image.load(endTexture), #unseen
                pygame.image.load(sideTexture), #side
                pygame.image.load(sideTexture), #side
                pygame.image.load(sideTexture), #unseen
                pygame.image.load(sideTexture),  #unseen
                pygame.image.load(endTexture)   #top
            ], v.split('k/')[1]
        except:
            return "none", False, False
    else:
        return "none", False, False

def calculate_normal(v1, v2, v3):
    normal = [
        (v2[1] - v1[1]) * (v3[2] - v1[2]) - (v2[2] - v1[2]) * (v3[1] - v1[1]),
        (v2[2] - v1[2]) * (v3[0] - v1[0]) - (v2[0] - v1[0]) * (v3[2] - v1[2]),
        (v2[0] - v1[0]) * (v3[1] - v1[1]) - (v2[1] - v1[1]) * (v3[0] - v1[0])
    ]
    length = (normal[0]**2 + normal[1]**2 + normal[2]**2)**0.5
    if length == 0:
        return (0, 0, 0)
    else:
        return (normal[0] / length, normal[1] / length, normal[2] / length)

def draw_shape(faces, vertices, texture_coords):
    for i, face in enumerate(faces):
        #glBindTexture(GL_TEXTURE_2D, texture_ids[i])
        glBegin(GL_QUADS)
        glNormal3fv(calculate_normal(vertices[face[0]], vertices[face[1]], vertices[face[2]])) # Calculate and set normal vector for lighting
        for j, vertex in enumerate(face):
            glTexCoord2fv(texture_coords[j])
            glVertex3fv(vertices[vertex])
        glEnd()

def export_image(image_name):
    data = glReadPixels(1, 0, 128, 128, GL_RGBA, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGBA", (128, 128), data)
    image.save("../../export/block/" + image_name+".png", 'PNG')



textures = [
                pygame.image.load("texture1.png"), #unseen
                pygame.image.load("texture1.png"), #side
                pygame.image.load("texture1.png"), #side
                pygame.image.load("texture1.png"), #unseen
                pygame.image.load("texture1.png"),  #unseen
                pygame.image.load("texture1.png")   #top
            ]

def main():
    global texture_ids
    pygame.init()
    display = (512 , 512)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    #glScalef(1,-1,1); 
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING) # Enable lighting
    glEnable(GL_LIGHT0) # Enable light source
    glEnable(GL_LIGHT1) # Enable light source
    glScalef(1,-1,1); 

    light_position = (0, 0, 10, 10) # Light position (x, y, z, w)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position) # Set light position

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, (display[0] / display[1]), 0.1, 500.0)
    ambient_color = (1, 1, 1, 1.0) # Ambient light color (RGBA)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_color) # Set ambient light color

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0.0, 0.0, -20)
    
    glRotatef(30, 1, 0, 0)
    glRotatef(45, 0, 1, 0)

    parentPath = getParentModel("create\models\item\cogwheel.json")

    newverts, newfaces = getVerticies(parentPath)

    texture_ids = glGenTextures(len(textures))
    for i, texture in enumerate(textures):
        glBindTexture(GL_TEXTURE_2D, texture_ids[i])
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture.get_width(), texture.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, pygame.image.tostring(texture, "RGBA", 1))

        glLightfv(GL_LIGHT0, GL_POSITION, light_position) # Set light position
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_color) # Set ambient light color
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glRotatef(1, 3, 1, 1)  # Rotate the cube slowly
        draw_shape(newfaces, newverts, block_coords)
        pygame.display.flip()
        pygame.time.wait(10)
main()

#parentPath = getParentModel("create\models\item\\andesite_encased_shaft.json")

#print(getVerticies(parentPath))

