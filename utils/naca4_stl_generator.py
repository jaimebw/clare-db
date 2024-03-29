#!/usr/bin/python
# -*- coding: utf-8 -*- 
# Miroslav Kabát
# Github orginal repo: https://github.com/MiroslavKabat/pythonNacaProfileGeneratorSTL
# New edit by Jaime Bowen Varela
# MIT License 2022
#----------------------------

import os, fnmatch
import sys
import math

class CVertex(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class CTriangle(object):
    def __init__(self, vertices):
        self.vertices = vertices
        self.UpdateVectors()

    def UpdateVectors(self):
        ver = self.vertices
        if len(ver) == 3:
            u = []
            u.append( ver[1].x - ver[0].x )
            u.append( ver[1].y - ver[0].y )
            u.append( ver[1].z - ver[0].z )
            
            v = []
            v.append( ver[2].x - ver[0].x )
            v.append( ver[2].y - ver[0].y )
            v.append( ver[2].z - ver[0].z )

            w = []
            w.append( u[1] * v[2] - u[2] * v[1] )
            w.append( u[2] * v[0] - u[0] * v[2] )
            w.append( u[0] * v[1] - u[1] * v[0] )

            self.i = w[0]
            self.j = w[1]
            self.k = w[2]
            pass
        else:
            pass

class CNACA(object):
    def __init__(self, foil, nPts, length, chordLength, angle):
        self.foil = foil
        self.nPts = nPts
        self.length = length
        self.angle = (-1) * angle
        self.chordLength = chordLength
        self.vertices = []
        
        self.m = float(int(str(foil)[0]))/100  # max camber
        self.p = float(int(str(foil)[1]))/10   # chordwise position of max camber
        self.t = float(int(str(foil)[2:]))/100 # thickness

        self.updateVertices()
        
    def updateVertices(self):
        nPts = self.nPts
        length = self.length
        angle = self.angle
        m = self.m
        p = self.p
        t = self.t

        verticesFront = []
        verticesBack = []

        verticesFrontTop = []
        verticesFrontBot = []
        verticesBackTop = []
        verticesBackBot = []

        for i in range(0, nPts + 1):
            xpos = 1 - math.cos((i) * (math.pi / 2 / nPts))    
            
            x = xpos
            xc = xpos
            yt = 5 * t * (0.2969*(x**0.5)-0.126*(x**1)-0.3516*(x**2.0)+0.2843*(x**3.0)-0.1015*(x**4.0))

            if p != 0 and m != 0:
                if xc <= p:
                    yc = m/(0+p)**2 * (2*p*x-x**2)
                    dycdx = 2*m/((0+p)**2)*(p-xpos)
                else:
                    yc = m/(1-p)**2 * ((1-2*p)+2*p*x-x**2)
                    dycdx = 2*m/((1-p)**2)*(p-xpos)
            else:
                yc = 0
                dycdx = 0

            atandydx = math.atan(dycdx)
            
            xd = xc + yt * math.sin(atandydx)
            yd = yc - yt * math.cos(atandydx)
            xu = xc - yt * math.sin(atandydx)
            yu = yc + yt * math.cos(atandydx)

            verticesFrontTop.append(CVertex(xu, yu, length/2.0))
            verticesFrontBot.append(CVertex(xd, yd, length/2.0))
            verticesBackTop.append(CVertex(xu, yu, -length/2.0))
            verticesBackBot.append(CVertex(xd, yd, -length/2.0))
        pass
        verticesFrontBot = sorted(verticesFrontBot, key=lambda vertex: vertex.x, reverse=True)
        verticesBackBot = sorted(verticesBackBot, key=lambda vertex: vertex.x, reverse=True)

        verticesFront.extend(verticesFrontBot)
        verticesFront.extend(verticesFrontTop[1:])
        verticesBack.extend(verticesBackBot)
        verticesBack.extend(verticesBackTop[1:])
        
        listVertices = [ verticesFront, verticesBack ]

        self.vertices = listVertices
        
        self.transSize()
        self.transRot()
        

    def transSize(self):
        for lsVer in self.vertices:
            for ver in lsVer:
                ver.x = ver.x * self.chordLength
                ver.y = ver.y * self.chordLength

    def transRot(self):
        angleRad = self.angle / 180.0 * math.pi
        for lsVer in self.vertices:
            for ver in lsVer:
                newX = ver.x * math.cos(angleRad) - ver.y * math.sin(angleRad)
                newY = ver.x * math.sin(angleRad) + ver.y * math.cos(angleRad)
                ver.x = newX
                ver.y = newY

def triangleGenerator(VerFs, VerBs):
    """
    Generacion de triangulos para el stl. Tomando los vertices anteriores

    """

    triangles = []
    i = 0
    for verF in VerFs:
        
        # 1. foil
        vertices = []
        vertices.append( verF )
        if i + 1 == len(VerFs):
            vertices.append(VerBs[0])
            pass
        else:
            idx = i + 1 
            vertices.append(VerBs[idx])
            pass
        vertices.append( VerBs[i] )
        triangles.append(CTriangle(vertices))

        # 2. foil
        vertices = []
        vertices.append( verF )
        if i + 1 == len(VerFs):
            vertices.append(VerFs[0])
            vertices.append(VerBs[0])
            pass
        else:
            idx = i + 1 
            vertices.append(VerFs[idx])
            vertices.append(VerBs[idx])
            pass
        triangles.append(CTriangle(vertices))
        """
        # Esto parte genera las uniones de los lados del perfil, y no interesan esos puntos

        # 3. sides front
        if i >= len(VerFs) / 2.0:
            pass
        else:
            vertices = []
            vertices.append( verF )
        
            idxO = len(VerFs)-1-i
            idx1 = len(VerFs)-2-i
            
            vertices.append(VerFs[idxO])
            vertices.append(VerFs[idx1])
            pass
        triangles.append(CTriangle(vertices))
        # 4. sides front
        if i + 2 >= len(VerFs) / 2.0:
            pass
        else:
            vertices = []
            vertices.append( verF )
        
            idxO = i + 1
            idx1 = len(VerFs)-2-i
            
            vertices.append(VerFs[idx1])
            vertices.append(VerFs[idxO])
            pass
        triangles.append(CTriangle(vertices))

        # 5. sides back
        if i >= len(VerBs) / 2.0:
            pass
        else:
            vertices = []
            vertices.append( VerBs[i] )
        
            idxO = len(VerBs)-1-i
            idx1 = len(VerBs)-2-i
            
            vertices.append(VerBs[idx1])
            vertices.append(VerBs[idxO])
            pass
        triangles.append(CTriangle(vertices))
        # 6. sides back
        if i + 2 >= len(VerBs) / 2.0:
            pass
        else:
            vertices = []
            vertices.append( VerBs[i] )
        
            idxO = i + 1
            idx1 = len(VerBs)-2-i
            
            vertices.append(VerBs[idxO])           
            vertices.append(VerBs[idx1])
            pass
        triangles.append(CTriangle(vertices))

        """
        i = i + 1 
    return triangles

def export_to_stl(triangles, naca):
    pointCount='10'
    nacaModelName='naca'

    stlFile = open('naca' + str(naca.foil) + '.stl','w')
    stlFile.truncate()

    stlFile.write('solid {0}\n'.format(nacaModelName))

    for tri in triangles:
        stlFile.write(' facet normal {0} {1} {2}\n'.format(tri.i, tri.j, tri.k))
        
        stlFile.write('     outer loop\n')
        for ver in tri.vertices:
            # Cambiado z por y para que se pueda meter directamente a Open Foam
            stlFile.write('         vertex {0} {1} {2} \n'.format(ver.x, ver.z, ver.y))
        stlFile.write('     endloop\n')

        stlFile.write(' endfacet\n')
    stlFile.write('endsolid {0}\n'.format(nacaModelName))
    stlFile.close()
    pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("foil",type = str,help = "Four digit NACA to be created")
    parser.add_argument("-n","--n_points",type = int, help = "Number of points to create the .stl file. It is a 100 by default",default= 100)
    parser.add_argument("-l","--length",type = float,help = "Length of the profile. It is 1.0 by default",default = 1.0)
    parser.add_argument("-cl","--chord_length",type = float, help = "Length of the chord of the profile. It is 1.0 by default",default= 1.0)
    parser.add_argument("-aoa","--angle",type = float,help = "Angle of attack of the profile. It is 0 rad by default",default=0.0)
    args = parser.parse_args()
    NACA = CNACA(args.foil, args.n_points, args.length, args.chord_length, args.angle)
    export_to_stl(triangleGenerator(NACA.vertices[0], NACA.vertices[1]), NACA)
