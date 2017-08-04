#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os 
import glob 
import alarmas as al

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Erase_pngs',
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
#ListConfig = al.get_rutesList(args.rutaConfig)
#rurta de las figuras 
#rutaFiguras = al.get_ruta(ListConfig, args.nameFiguras)

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#Lista las carpetas que coinciden con la ruta 
Lista = glob.glob(args.nameFiguras+'*')
#Itera sobre cada carpeta, organiza archivos y borra lo viejo 
for l in Lista:
	ListTemp = glob.glob(l+'/*')
	ListTemp.sort()
	#print len(ListTemp)
	if len(ListTemp)>= args.nfiles:
		for i in ListTemp[:-args.nfiles]:
			os.system('rm '+i)
		if args.verbose:
			print 'Aviso: Se han dejado solo '+str(args.nfiles)+' elementos en '+l
	else:
		if args.verbose:
			print 'Aviso: No hay suficientes archivos para borrar '+str(len(ListTemp))
	
	#~ os.system('convert -delay 10 -loop 0 '+l+'/*00.png '+l+'/animation24hr.gif ')
	#~ print 'animacion generada en'+l




