#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os 
import pandas as pd
import pylab as pl
import glob 
import alarmas as al

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Plot_Rain_Campo',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Borra la cantidad de figuras historicas que se le indiquen 
        '''))
#Parametros obligatorios
parser.add_argument("rutaConfig",help="Ruta al archivo de configuracion")
parser.add_argument("nameFiguras",help="Ruta indicada en el archivo de configuracion donde se encuentran las figuras a borrar")
parser.add_argument("-n", "--nfiles",help="Cantidad de archivos que deja vivos", default = 288, type = int)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')

#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lee el archivo de configuracion 
ListConfig = al.get_rutesList(args.rutaConfig)
#rurta de las figuras 
rutaFiguras = al.get_ruta(ListConfig, args.nameFiguras)


#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lista las carpetas con figuras de esas 
Lista = glob.glob(rutaFiguras+'*')
print Lista
#Itera sobre las carpetas, las organiza y borra lo viejo 
for l in Lista:
	ListTemp = glob.glob(l+'/*')
	ListTemp.sort()
	print len(ListTemp)
	for i in ListTemp[:args.nfiles]:
		os.system('rm '+i)
	print 'Aviso: Se han dejado solo '+str(args.nfiles)+' elementos para '
	print l




