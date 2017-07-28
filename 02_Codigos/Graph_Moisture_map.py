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
        prog='Genera_Grafica_Moist_sim',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Genera la figura de la humedad simulada en tanques capilar 0 y gravitacional 2 
        para un periodo asignado de tiempo.
        '''))

#Parametros obligatorios
parser.add_argument("date",help="(Obligatorio) Decha actual de ejecucion YYYY-MM-DD-HH:MM")
parser.add_argument("cuenca",help="Archivo -nc de la cuenca con la cual se va a realizar el trabajo")
parser.add_argument("rutaConfig",help="(Obligatorio) Ruta con la configuracion de la cuenca")
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)
parser.add_argument("-r", "--record",help="Record de lectura en el binario para graficar", 
	default = 1, type = int)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')
	
#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lectura de cuenca y variables
cu = wmf.SimuBasin(rute=args.cuenca)

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lee el archivo de configuracion
ListConfig = al.get_rutesList(args.rutaConfig)
#Se define ruta donde se leeran los resultados a plotear
ruta_sto = al.get_ruta(ListConfig,'ruta_almsim')
#Lectura de rutas de salida de la imagen
ruta_Hsim = al.get_ruta(ListConfig,'ruta_map_humedad')
#Diccionario con info de plot: se lee la info de todos los parametrizaciones
ListPlotVar = al.get_modelConfig_lines(ListConfig, '-p', Calib_Storage='Plot',PlotType='Humedad_map')
DictStore = al.get_modelConfig_lines(ListConfig, '-s', 'Store')



#construye las listas para plotear en paralelo
ListaEjec = []

for l in ListPlotVar:
	#Se define ruta donde se leeran los resultados a plotear
	ruta_in = ruta_sto + DictStore['-s '+l]['Nombre']
	#Se crea un folder en el que se van a contener las imagenes de cada parametrizacion asignada
	#Mira la ruta del folder y si no existe la crea
	ruta_folder = ruta_Hsim+l+'/'
	Esta = glob.glob(ruta_folder)
	if len(Esta) == 0:
		os.system('mkdir '+ruta_folder)
	#Obtiene las rutas de los archivos de salida
	ruta_out_png = ruta_folder +'Humedad'+l+'_'+args.date+'.png'
	ruta_out_txt = ruta_folder +'Humedad'+l+'_'+args.date+'.txt'
	#Lee los binarios de humedad para la cuenca de cada parametrizacion
	v,r = wmf.models.read_float_basin_ncol(ruta_in,args.record, cu.ncells, 5)
	#Se organiza la lista con parametros necesarios para plotear los mapas con la funcion que sigue
	ListaEjec.append([ruta_in, ruta_out_png, ruta_out_txt, v, l])

#-------------------------------------------------------------------------------------------------------
#Se generan  los plots de humedad de cada parametrizacion 
#-------------------------------------------------------------------------------------------------------

def Plot_Hsim(Lista):
	#Plot
	VarToPlot=((Lista[-2][0]+Lista[-2][2])/(wmf.models.max_gravita+wmf.models.max_capilar))*100
	# si supera un umbral de saturacion se grafica, si no no.
	if VarToPlot.max() >= 0.05:
		fig = pl.figure(figsize=(10,12))
		bins=4
		ticks_vec=np.arange(0,VarToPlot.max(),int(VarToPlot.max())/bins)
		Coord,ax=cu.Plot_basinClean(VarToPlot,
						show_cbar=True,
						cmap = pl.get_cmap('viridis',8),
						#se configura los ticks del colorbar para que aparezcan siempre la misma cantidad y del mismo tamano
						cbar_ticks=ticks_vec,cbar_ticklabels=ticks_vec,cbar_ticksize=15,
						show=False)
		#ax.set_title('Moisture Map Par'+Lista[-1]+' '+args.date, fontsize=18 )
		pl.suptitle('Saturacion del suelo [%] Par'+Lista[-1]+' '+args.date, fontsize=16, x=0.5, y=0.09)
		ax.figure.savefig(Lista[1],bbox_inches='tight')
		print 'Aviso: Plot de Humedad para '+Lista[-1]+' generado.'
	else:
		print 'Aviso: No saturacion suficiente para Plot de Humedad: max '+str(VarToPlot.max())

#Ejecuta los plots
if len(ListaEjec) > 15:
	Nprocess = 15
else:
	Nprocess = len(ListaEjec)
p = Pool(processes = Nprocess)
p.map(Plot_Hsim, ListaEjec)
p.close()

#Guarda archuivo con coordenadas - por defecto es false, cuando se cambie revisar Coord.
if args.coord:
	f = open(ListaEjec[0][2], 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
