#Juan Diego Solorzano 18151
#Labortorio 1: Relleno de poligonos

import struct
from collections import namedtuple

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
white = bytes([255, 255, 255])
black = bytes([0, 0, 0])

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

def glCreateWindow(width, height):
        win = Render(width, height)
        return win

def cross(v0, v1):
  #Producto cruz de 3 vectores
  return V3(
    v0.y * v1.z - v0.z * v1.y,
    v0.z * v1.x - v0.x * v1.z,
    v0.x * v1.y - v0.y * v1.x,
  )

def bbox(*vertices):
  #Bounding box desde 2 vectores
  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]
  xs.sort()
  ys.sort()

  return V2(xs[0], ys[0]), V2(xs[-1], ys[-1])

def barycentric(A, B, C, P):
  #Conseguir coordenadas baricentricas desde los 3 vectores con producto cruz 
  cx, cy, cz = cross(
    V3(B.x - A.x, C.x - A.x, A.x - P.x), 
    V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if abs(cz) < 1:
      #es triangulo degenerado (regresar lo que sea)
    return -1, -1, -1

  u = cx/cz
  v = cy/cz
  w = 1 - (u + v)

  return w, v, u

class Render(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clearC = bytes([0, 0, 0])
        self.color = bytes([255, 255, 255])
        self.xw = 0
        self.yw = 0
        self.widthw = width
        self.heightw = height
        self.framebuffer = []
        self.poin = True
        self.glClear()

    def glInit(self, width, height):
        return
    
    #Area para pintar
    def glViewPort(self, x, y, width, height):
        self.xw = x
        self.yw = y
        self.widthw = width
        self.heightw = height

    #Pintar imagen   
    def glClear(self):
        self.framebuffer = [
            [self.clearC for x in range(self.width)]
            for y in range(self.height)
        ]

    #Color para pintar imagen
    def glClearColor(self, r, g, b):
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        self.clearC = bytes([b, g, r])
        self.glClear()

    #Crear archivo de la imagen
    def glFinish(self, filename):
        f = open(filename, 'bw')

        #file header
        f.write(char('B'))
        f.write(char('M'))
        f.write(dword(14 + 40 + self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(14 + 40))

        #image header
        f.write(dword(40))
        f.write(dword(self.width))
        f.write(dword(self.height))
        f.write(word(1))
        f.write(word(24))
        f.write(dword(0))
        f.write(dword(self.width * self.height * 3))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))
        f.write(dword(0))

        #pixel data
        for x in range(self.width):
            for y in range(self.height):
                f.write(self.framebuffer[x][y])

        f.close()

    #Pintar punto
    def glVertex(self, x, y, color):
        if self.poin:
            xn = (x + 1)*(self.widthw/2) + self.xw
            yn = (y + 1)*(self.heightw/2) + self.yw
            xn = int(xn)
            yn = int(yn)
        else:
            xn = x
            yn = y
        self.framebuffer[yn][xn] = color

    #Color del punto
    def glColor(self, r, g, b):
        r = int(r * 255)
        g = int(g * 255)
        b = int(b * 255)
        self.color = bytes([b, g, r])

    def triangle(self, A, B, C, color):
        #bounding box
        bbox_min, bbox_max = bbox(A, B, C)

        for x in range(bbox_min.x, bbox_max.x + 1):
            for y in range(bbox_min.y, bbox_max.y + 1):
                w, v, u = barycentric(A, B, C, V2(x, y))
                #Ver si el punto esta dentro del triangulo basado en las caracteristicas dadas de las coordenadas (0 es valido)
                if w < 0 or v < 0 or u < 0:
                    #no lo pinta
                    continue
                #pintar punto
                self.glVertex(x, y, color)

    #Pintar una linea de un punto a otro. Se optimizo el algoritmo evitando el uso de round y divisiones
    def glLine(self, x1n, y1n, x2n, y2n):
        #Cambiar valores
        dy = abs(y2n - y1n)
        dx = abs(x2n - x1n)
        emp = dy > dx

        if emp:
            x1n, y1n = y1n, x1n
            x2n, y2n = y2n, x2n

        if x1n > x2n:
            x1n, x2n = x2n, x1n
            y1n, y2n = y2n, y1n

        dy = abs(y2n - y1n)
        dx = abs(x2n - x1n)
        #Variable para ver cuando subir de y
        offset = 0
        threshold = dx
        y = y1n
        #Pintar puntos
        for x in range(x1n, x2n):
            if emp:
                self.glVertex(y, x, white)
            else:
                self.glVertex(x, y, white)

            offset += dy * 2
            if offset >= threshold:
                #Sumar si linea va para arriba, restar si va para abajo
                y += 1 if y1n < y2n else -1
                threshold += 2 * dx

print("SR1: Point")

bitmap = glCreateWindow(1000, 1000)
bitmap.glClearColor(0, 0, 0)
bitmap.glColor(1, 1, 1)
bitmap.poin = False
#Poligono 1
bitmap.triangle(V2(165, 380), V2(185, 360), V2(193, 383), white)
bitmap.triangle(V2(185, 360), V2(207, 345), V2(180, 330), white)
bitmap.triangle(V2(207, 345), V2(233, 330), V2(230, 360), white)
bitmap.triangle(V2(230, 360), V2(250, 380), V2(220, 385), white)
bitmap.triangle(V2(220, 385), V2(205, 410), V2(193, 383), white)
bitmap.triangle(V2(193, 383), V2(185, 360), V2(230, 360), white)
bitmap.triangle(V2(185, 360), V2(207, 345), V2(230, 360), white)
bitmap.triangle(V2(230, 360), V2(220, 385), V2(193, 383), white)

#Poligono 2
bitmap.triangle(V2(288, 286), V2(321, 335), V2(374, 302), white)
bitmap.triangle(V2(288, 286), V2(339, 251), V2(374, 302), white)

#Poligono 3 
bitmap.triangle(V2(377, 249), V2(411, 197), V2(436, 249), white)


#Poligono 4 
bitmap.triangle(V2(413, 177), V2(448, 159), V2(466, 180), white)
bitmap.triangle(V2(448, 159), V2(517, 144), V2(466, 180), white)
bitmap.triangle(V2(448, 159), V2(517, 144), V2(502, 88), white)
bitmap.triangle(V2(517, 144), V2(553, 53), V2(502, 88), white)
bitmap.triangle(V2(517, 144), V2(553, 53), V2(552, 214), white)
bitmap.triangle(V2(750, 145), V2(761, 179), V2(672, 192), white)
bitmap.triangle(V2(750, 145), V2(660, 52), V2(672, 192), white)
bitmap.triangle(V2(553, 53), V2(535, 36), V2(660, 52), white)
bitmap.triangle(V2(676, 37), V2(535, 36), V2(660, 52), white)
bitmap.triangle(V2(553, 53), V2(552, 214), V2(660, 52), white)
bitmap.triangle(V2(659, 214), V2(552, 214), V2(660, 52), white)
bitmap.triangle(V2(672, 192), V2(659, 214), V2(660, 52), white)
bitmap.triangle(V2(580, 230), V2(632, 230), V2(615, 214), white)
bitmap.triangle(V2(580, 230), V2(597, 215), V2(615, 214), white)

#Poligono 5 
bitmap.triangle(V2(682, 175), V2(735, 148), V2(708, 120), black)
bitmap.triangle(V2(682, 175), V2(735, 148), V2(739, 170), black)

bitmap.glFinish('resultado.bmp')
