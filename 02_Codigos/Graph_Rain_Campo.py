#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os 
from wmf import wmf 
import pandas as pd
import pylab as pl

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Plot_Rain_Campo',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera un campo de lluvia a partir de binarios de radar generados.
        '''))
#Parametros obligatorios
parser.add_argument("fechaI",help="(YYYY-MM-DD-HH:MM) Fecha de inicio de imagenes")
parser.add_argument("fechaF",help="(YYYY-MM-DD-HH:MM) Fecha de fin de imagenes")
parser.add_argument("cuenca",help="Numero del nodo dentro de la red hidrica a plotear")
parser.add_argument("rutaRain",help="Ruta al archivo binario con los campos de lluvia")
parser.add_argument("rutaFigura",help="Ruta donde se guarda la figura con el campo de lluvia")
parser.add_argument("-1", "--vmin",help="Minimo valor del imshow", default = 0, type = float)
parser.add_argument("-2", "--vmax",help="Maximo valor del imshow", default = 100, type = float)
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')
	
#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------------------------------------
# LECTURA DE IONFORMACION
#-------------------------------------------------------------------------------------------------------------------------------------
rutebin, rutehdr = wmf.__Add_hdr_bin_2route__(args.rutaRain)
cu = wmf.SimuBasin(rute=args.cuenca)
DictRain = wmf.read_rain_struct(rutehdr)
R = DictRain[u' Record']

#-------------------------------------------------------------------------------------------------------------------------------------
# OBTIENE EL PERIODO PARA GRAFICAR
#-------------------------------------------------------------------------------------------------------------------------------------
#Obtiene las fechas por dias
fecha_f = pd.to_datetime(args.fechaF)
fecha_f = fecha_f - pd.Timedelta(str(fecha_f.second)+' seconds')
fecha_f = fecha_f - pd.Timedelta(str(fecha_f.microsecond)+' microsecond')
cont = 0
while fecha_f.minute % 5 <>0 and cont<30:
	fecha_f = fecha_f + pd.Timedelta('1 minutes')
	cont+=1
#Corrige la fecha para que este dentro del rango de fechas
Flag = True
cont = 0
while Flag and cont<30:
	try:
		pos = R.index.get_loc(fecha_f)
		Flag = False
	except:
		fecha_f = fecha_f - pd.Timedelta('5 minutes')
	cont+=1
#corrige fecha de inicio
fecha_i = pd.to_datetime(args.fechaI)
fecha_i = fecha_i - pd.Timedelta(str(fecha_f.second)+' seconds')
fecha_i = fecha_i - pd.Timedelta(str(fecha_f.microsecond)+' microsecond')
Flag = True
#Corrige la fecha para que este dentro del rango de fechas
while Flag:
	try:
		pos = R.index.get_loc(fecha_i)
		Flag = False
	except:
		fecha_i = fecha_i - pd.Timedelta('5 minutes')
#Obtiene el periodo
pos = R[fecha_i:fecha_f].values
pos = pos[pos <>1 ]

#-------------------------------------------------------------------------------------------------------------------------------------
# GENERA LA GRAFICA
#-------------------------------------------------------------------------------------------------------------------------------------
#Textos para la legenda
lab = np.linspace(args.vmin, args.vmax, 4)
texto = ['bajo', 'medio', 'alto', 'muy alto']
labText = ['%dmm\n%s'%(i,j) for i,j in zip(lab, texto)]
#se fija si si hay algo para graficar 
if len(pos)>0:
	#Acumula la lluvia para el periodo
	Vsum = np.zeros(cu.ncells)
	for i in pos:
		v,r = wmf.models.read_int_basin(rutebin,i, cu.ncells)
		v = v.astype(float); v = v/1000.0
		Vsum+=v	
	#Genera la figura 
	c = cu.Plot_basinClean(Vsum, cmap = pl.get_cmap('viridis',10), 
		show_cbar=True, vmin = args.vmin, vmax = args.vmax,
		cbar_ticksize = 16,
		cbar_ticks= lab,
		cbar_ticklabels = labText,
		cbar_aspect = 17,
		ruta = args.rutaFigura
		)
	if args.verbose:
		print 'Aviso: Se ha producido una grafica nueva con valores diferentes de cero'
else:
	Vsum = np.zeros(cu.ncells)
	c = cu.Plot_basinClean(Vsum, cmap = pl.get_cmap('viridis',10), 
		show_cbar=True, vmin = args.vmin, vmax = args.vmax,
		cbar_ticksize = 16,
		cbar_ticks= lab,
		cbar_ticklabels = labText,
		cbar_aspect = 17,
		ruta = args.rutaFigura
		)
	if args.verbose:
		print 'Aviso: Se ha producido un campo sin lluvia.'
