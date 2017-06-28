#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os
from wmf import wmf
import alarmas as al
from multiprocessing import Pool
import glob
import pylab as pl 

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Genera_Grafica_SlidesSim',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera los mapas de deslizamientos simulados por las parametrizaciones
	del modelo hidrologico.
        '''))
#Parametros obligatorios
parser.add_argument("date",help="(Obligatorio) Decha actual de ejecucion YYYY-MM-DD-HH:MM")
parser.add_argument("cuenca",help="Cuenca con la estructura que hace todo")
parser.add_argument("rutaConfig",help="(Obligatorio) Ruta con la configuracion de la cuenca")
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')
	
#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lectura de cuenca y variables
cu = wmf.SimuBasin(rute=args.cuenca, SimSlides = True)

#Lee el archivo de configuracion
ListConfig = al.get_rutesList(args.rutaConfig)
#Se define ruta donde se leeran los resultados a plotear
ruta_in = al.get_ruta(ListConfig,'ruta_slides')
#Lectura de rutas de salida del mapa
ruta_out = al.get_ruta(ListConfig,'ruta_map_slides2')
#Diccionario con info de plot: se lee la info de todos los parametrizaciones
ListPlotVar = al.get_modelConfig_lines(ListConfig, '-p', Calib_Storage='Plot',PlotType='Slides')

#construye las listas para plotear en paralelo para cada parametrizacion
#Ademas se acumula el numero de celdas acumuladas de todas las parametrizaciones.
ListaEjec = []; Vsum = np.zeros(cu.ncells)
#Se define ruta donde se leeran los resultados a plotear
#ruta_in = args.slides

for l in range(0,len(ListPlotVar)):
	#Obtiene las rutas de los archivos de salida
	ruta_out_png = ruta_out+ListPlotVar[l]+'_'+args.date+'.png'
	ruta_out_txt = ruta_out+ListPlotVar[l]+'_'+args.date+'.txt'
	#Lee los binarios de deslizamientos para la cuenca, para cada parametrizacion
	v,r = wmf.models.read_int_basin(ruta_in,l+1,cu.ncells)
	#Se organiza la lista con parametros necesarios para plotear los mapas con la funcion que sigue
	ListaEjec.append([ruta_in, ruta_out_png, ruta_out_txt, v, ListPlotVar[l]])
	#Se van acumulando las celdas deslizadas en cada parametrizacion
	Vsum += v

###Se agrega el mapa de celdas acumuladas entre los que se van a plotear desde la info en ListaEjec
#Obtiene las rutas de los archivos de salida
ruta_out_png = ruta_out+'ParsAcum'+args.date+'.png'
ruta_out_txt = ruta_out+'ParsAcum'+args.date+'.txt'
#Se organiza la lista con parametros necesarios para plotear los mapas con la funcion que sigue
ListaEjec.append([ruta_in, ruta_out_png, ruta_out_txt, Vsum, '999'])


#-------------------------------------------------------------------------------------------------------
#Se generan  los plots de deslizamientos de cada parametrizacion y el acumulado
#-------------------------------------------------------------------------------------------------------

def Plot_SlidesSim(Lista):
	#Plot 
	Coord=cu.Plot_basinClean(Lista[-2],ruta = Lista[1],
					show_cbar=True,
					cmap = pl.get_cmap('viridis',4),
					figsize = (10,12))
	#dice lo que hace
	if args.verbose:
		print 'Aviso: Plot de Humedad para '+Lista[-1]+' generado.'

#Ejecuta los plots
if len(ListaEjec) > 15:
	Nprocess = 15
else:
	Nprocess = len(ListaEjec)
p = Pool(processes = Nprocess)
p.map(Plot_SlidesSim, ListaEjec)
p.close()

#Guarda archuivo con coordenadas - por defecto es false, cuando se cambie revisar Coord.
if args.coord:
	f = open(ListaEjec[0][2], 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
