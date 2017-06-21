#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os 
from wmf import wmf 
import pylab as pl

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Genera_Grafica_Qsim',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera los mapas de deslizamientos simulados por las parametrizaciones
	del modelo hidrologico.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="Cuenca con la estructura que hace todo")
parser.add_argument("slides",help="Ruta a la carpeta con binarios donde estan los slides")
parser.add_argument("ruta",help="Ruta donde se guarda la figura con slides")
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)

#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lectura de cuenc ay variables
cu = wmf.SimuBasin(rute=args.cuenca, SimSlides = True)
wmf.models.slide_allocate(cu.ncells, 10)
R = np.copy(wmf.models.sl_riskvector)
R[R == 2] = 1
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Configura rutas
if args.ruta.endswith('.png'):
	ruta_texto = args.ruta[:-4] + '.txt'
	ruta_plot = args.ruta
else:
	ruta_texto = args.ruta + '.txt'
	ruta_plot = args.ruta + '.png'

L = os.listdir(args.slides)
for l in L:
	#ruta de la imagen 
	rutaImagen = args.ruta + l + '.png'
	#plot
	s, r = wmf.models.read_int_basin(args.slides + l,1,cu.ncells)	
	r2 = R + s
	Coord = cu.Plot_basinClean(r2, rutaImagen, cmap = pl.get_cmap('viridis',3), figsize = (30,15))
	
	
#Guarda archuivo con coordenadas
if args.coord:
	f = open(ruta_texto, 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
