#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os
from wmf import wmf
import alarmas as al
from multiprocessing import Pool
import glob

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
        prog='Genera_Grafica_Qsim',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Genera la figura de caudales simulados para un periodo asignado de tiempo, de forma 
        adicional presenta el hietograma de precipitacion.
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
#Lee el archivo de configuracion
ListConfig = al.get_rutesList(args.rutaConfig)
#Lectura de rutas
ruta_qsim = al.get_ruta(ListConfig,'ruta_map_qsim')
ruta_sto = al.get_ruta(ListConfig,'ruta_almacenamiento')
#Dicctionario con info de plot
ListPlotVar = al.get_modelConfig_lines(ListConfig, '-p', Calib_Storage='Plot',PlotType='Qsim_map')
DictStore = al.get_modelConfig_lines(ListConfig, '-s', 'Store')

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lectura de cuenca y variables
cu = wmf.SimuBasin(rute=args.cuenca)
#lectura de constantes 
qmed = cu.Load_BasinVar('stream')
horton = cu.Load_BasinVar('horton')
cauce = cu.Load_BasinVar('cauce')

#construye las listas para plotear en paralelo
ListaEjec = []
for l in ListPlotVar:
	ruta_in = ruta_sto + DictStore['-s '+l]['Nombre']
	#Mira la ruta del folder y si no existe la crea
	ruta_folder = ruta_qsim + 'StreamMaps-'+l+'/'
	Esta = glob.glob(ruta_folder)
	if len(Esta) == 0:
		os.system('mkdir '+ruta_folder)
	#Obtiene las rutas de los archivos de salida
	ruta_out_png = ruta_folder + 'StreamFlow_'+l+'_'+args.date+'.png'
	ruta_out_txt = ruta_folder + 'StreamFlow_'+l+'_'+args.date+'.txt'
	v,r = wmf.models.read_float_basin_ncol(ruta_in,args.record, cu.ncells, 5)
	ListaEjec.append([ruta_in, ruta_out_png, ruta_out_txt, v[-1], l])

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def Plot_Qsim_Campo(Lista):
	#obtiene la razon entre Qsim y Qmed 
	Razon = Lista[-2] / qmed
	#Prepara mapas de grosor y de razon 
	RazonC = np.ones(cu.ncells)
	Grosor = np.ones(cu.ncells)
	for c,i in enumerate([20,50,80,200]):
		for h in range(1,6):        
			camb = 6 - h
			RazonC[(Razon >= i*camb) & (horton == h)] = c+2
			Grosor[(Razon >= i*camb) & (horton == h)] = np.log((c+1)*10)**1.4
	#Plot 	
	Coord = cu.Plot_Net(Grosor, RazonC,  
		tranparent = True, 
		ruta = Lista[1],
		clean = True, 
		colorbar = False,
		show_cbar = False, 
		figsize = (10,12), 
		umbral = cauce, 
		escala = 1.5,
		cmap = wmf.pl.get_cmap('viridis',5),
		vmin = None,
		vmax = None,
		show = True)
	#dice lo que hace
	if args.verbose:
		print 'Aviso: Plot de StreamFlow para '+Lista[-1]+' generado.'

#Ejecuta los plots
if len(ListaEjec) > 15:
	Nprocess = 15
else:
	Nprocess = len(ListaEjec)
p = Pool(processes = Nprocess)
p.map(Plot_Qsim_Campo, ListaEjec)
p.close()

#Guarda archuivo con coordenadas
if args.coord:
	f = open(ListaEjec[0][2], 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
