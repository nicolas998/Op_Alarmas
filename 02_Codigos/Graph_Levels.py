#!/usr/bin/env python
from wmf import wmf
import numpy as np 
import pylab as pl 
import pandas as pd
import os 
import glob
import osgeo.ogr
import argparse
import textwrap
import alarmas as al
from multiprocessing import Pool

import MySQLdb
import csv
import matplotlib
import matplotlib.font_manager
from datetime import timedelta
import datetime as dt
import pickle
import matplotlib.dates as mdates
import warnings
warnings.filterwarnings('ignore')


#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Genera_Grafica_Niveles',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera graficas de niveles simulados por el modelo vs. el nivel observado en contraste con 
	los niveles de riesgo por inundaciones.
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

#Lee el archivo de configuracion
ListConfig = al.get_rutesList(args.rutaConfig)

#Se define ruta de donde se leeran los resultados a plotear
ruta_in1 = al.get_ruta(ListConfig,'ruta_qsim_hist')
ruta_in2 = al.get_ruta(ListConfig,'ruta_qsim')
#Lectura de rutas de salida de la imagen
ruta_out = al.get_ruta(ListConfig,'ruta_serie_qsim')


#-----------------
#Argumentos fijos.
#-----------------

nodo=75
codeest=106
lcolors=['g','orange','orangered','indigo']
cmap=pl.cm.nipy_spectral#nipy_spectral#winter#autumn#summer#PuBuGn
backcolor='dimgray'
c_ylim=10


#Mira la ruta del folder y si no existe la crea
ruta_folder = ruta_out+'/'
Esta = glob.glob(ruta_folder)
if len(Esta) == 0:
	os.system('mkdir '+ruta_folder)
#Obtiene las ruta de archivo de salida
ruta_out_png = ruta_folder+'LevelsSim'+'_'+args.date+'.png'

#Se organiza la lista con parametros necesarios para plotear  con la funcion que sigue
ListaEjec=[ruta_in1,ruta_in2,nodo,codeest,lcolors,cmap,backcolor,c_ylim,ruta_out_png]


#-------------------------------------------------------------------------------------------------------
#Funcion para grafica de niveles
#-------------------------------------------------------------------------------------------------------

def Plot_Levels(Lista):
	#Leer ultima hora de historico Qsim para cada par.
	ruta1=Lista[0]+'*'
	readh=glob.glob(ruta1)
	#Leer las simulacion actual+extrapolacion
	ruta2=Lista[1]+'_caudal/*'
	reads=glob.glob(ruta2)
	#Guarda series completas e hist para sacar Nash
	Qact=[];Qhist=[]
	for rqhist,rqsim in zip(np.sort(readh),np.sort(reads)):
		#Q HIST
		df=pd.read_msgpack(rqhist)
		#ultima hora, 12 pasos de 5 min.
		qhist=df[Lista[2]][-12:]
		Qhist.append(qhist)
		#Q ACT
		qsim=pd.read_msgpack(rqsim)
		qEst=qsim[Lista[2]]
		#ult hr+ extrapolacion
		Qact.append(qhist.append(qEst))

	#-------------------------------------------------------------------------------------------------------
	#Consulta a base de datos: Nobs y Ns de alerta'
	#-------------------------------------------------------------------------------------------------------
	#Se usa las fechas de una serie sim para consultar en bd.
	serieN=Qact[0]
	FI=serieN.index.strftime('%Y-%m-%d')[0]
	FF=serieN.index.strftime('%Y-%m-%d')[-1]
	HI=serieN.index[0].strftime('%H:%M')
	HF=serieN.index[-1].strftime('%H:%M')

	# codigo de la estacion.
	codeest=Lista[3]
	# coneccion a bd con usuario operacional
	host   = '192.168.1.74'
	user   = 'siata_Oper'
	passwd = 'si@t@64512_operacional'
	bd     = 'siata'
	#Consulta a tabla estaciones
	Estaciones="SELECT Codigo,Nombreestacion, offsetN,N,action_level,minor_flooding,moderate_flooding,major_flooding  FROM estaciones WHERE codigo=("+str(codeest)+")"
	dbconn = MySQLdb.connect(host, user,passwd,bd)
	db_cursor = dbconn.cursor()
	db_cursor.execute(Estaciones)
	result = np.array(db_cursor.fetchall())
	#definicion de niveles de alerta y demas.
	nombreest=result[0][1] 
	n1=3.26*((float(result[0][4])/100)**2.35)
	n2=3.26*((float(result[0][5])/100)**2.35)
	n3=3.26*((float(result[0][6])/100)**2.35)
	n4=3.26*((float(result[0][7])/100)**2.35)
	#definicion de tipo N para consultar campo.
	tipo=int(result[0][3])
	if tipo == 1:#radar
		niv='ni'
	elif tipo == 0:#ultrasonido
		niv='pr'
	#Consulta a tabla datos
	sql_datos ="SELECT DATE_FORMAT(fecha,'%Y-%m-%d'), DATE_FORMAT(hora, '%H:%i:%s'), (" +str(result[0][2])+"-"+niv+"), calidad FROM datos WHERE cliente = ("+str(codeest)+") and fecha between '"+FI+"' and '"+FF+"' and hora between '"+HI+"' and '"+HF+"'"
	dbconn = MySQLdb.connect(host, user,passwd,bd)
	db_cursor = dbconn.cursor()
	db_cursor.execute(sql_datos)
	result_data = np.array(db_cursor.fetchall())
	data = pd.DataFrame(result_data)

	#Se organizan consulta en serie de tiempo.
	fe=[data[0][i]+'-'+data[1][i] for i in range(len(data))]; fe=np.array(fe)
	dates=[dt.datetime.strptime(i,'%Y-%m-%d-%H:%M:%S') for i in fe]
	nobs=[float(data[2][i]) for i in range(len(data))];nobs=np.array(nobs)
	calidad=[int(data[3][i]) for i in range(len(data))];calidad=np.array(calidad)
	Nobs=pd.Series(nobs,index=dates)
	#Corregir Nobs por calidad - falta incluir todos los codigos de calidad dudosa.
	try:
		Nobs[np.where((calidad!=1)&(calidad!=2))[0]]==np.nan
	except:
		pass
	Nobs[Nobs>600.0]==np.nan
	#Convertir a caudal con curva de calibracion de 3 aguas.
	Qobs=3.26*((Nobs/100)**2.35)

	#-------------------------------------------------------------------------------------------------------
	#Grafica comparativa de niveles, con escala de colores y backgroud de siata.
	#------------------------------------------------------------------------------------------------------
	fig= pl.figure(figsize=(12,9))
	ax= fig.add_subplot(111)

	# Grafica niveles de riesgo.
	ylim4=n4+(n4*0.2)
	levels=[n1,n2,n3,n4,ylim4]
	lnames=['Q1','Q2', 'Q3', 'Q4']
	lcolors=Lista[4]
	#plot
	for i in range(0,len(levels)):
		try:
			ax.fill_between(x=[Qobs.index[0],serieN.index[-1]], 
							y1=[levels[i],levels[i]],
							y2=[levels[i+1],levels[i+1]], 
							color = lcolors[i], 
							alpha = 0.22,
							label=lnames[i])
		except:
			pass

	#Grafica de niveles.
	#Colormap
	#-------------------------------------------------------------------------------------------------------
	parameters = np.linspace(0,len(Qact),len(Qact))
	# norm is a class which, when called, can normalize data into the [0.0, 1.0] interval.
	norm = matplotlib.colors.Normalize(
		vmin=np.min(parameters),
		vmax=np.max(parameters))
	#choose a colormap
	c_m = Lista[5]
	# create a ScalarMappable and initialize a data structure
	s_m = pl.cm.ScalarMappable(cmap=c_m, norm=norm)
	s_m.set_array([])
	#-------------------------------------------------------------------------------------------------------

	#PLOT

	#Pars
	for i,parameter in zip(np.arange(0,len(Qact)),parameters):
		#NASH
		nash=wmf.__eval_nash__(Qobs,Qhist[i])
		ax.plot(Qact[i],lw=1.8,linestyle='--', label='P0'+str(i+1)+'- NS:%.2f'%(nash),color=s_m.to_rgba(parameter))
	#Text ans ticks color.
	backcolor=Lista[6]  
	#Obs
	ax.plot(Qobs,c='k',lw=3, label='Qobs')
	ax.set_title('Est. %s. %s ___ Fecha: %s'%(codeest,nombreest,serieN.index.strftime('%Y-%m-%d')[0]), fontsize=17,color=backcolor)
	ax.set_ylabel('Caudal  $[{m}^3.{s}^{-1}]$', fontsize=17,color=backcolor)
	#     ax.set_xticklabels(serieN.index.strftime('%H:%M'))
	#     myFmt = mdates.DateFormatter('%H:%m')
	#     ax.xaxis.set_major_formatter(myFmt)
	ax.tick_params(labelsize=14)
	ax.grid()
	ax.autoscale(enable=True, axis='both', tight=True)
	#setting default color of ticks and edges
	ax.tick_params(color=backcolor, labelcolor=backcolor)
	for spine in ax.spines.values():
		spine.set_edgecolor('gray')
	#color of legend text
	leg = ax.legend(ncol=3,loc=(0.26,-0.255),fontsize=12)
	for text in leg.get_texts():
		pl.setp(text, color = backcolor)
	#ylim para la grafica
	ylim=Qobs.mean()*10
	ax.set_ylim(0,ylim)
	#Se guarda la figura.
	ax.figure.savefig(Lista[-1],bbox_inches='tight')

	#dice lo que hace
	if args.verbose:
		print 'Aviso: Plot de Humedad para '+Lista[-1]+' generado.'

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------


# Ejecuta imagen
Plot_Levels(ListaEjec)

#Guarda archuivo con coordenadas - por defecto es false, cuando se cambie revisar Coord.
if args.coord:
	f = open(ListaEjec[0][2], 'w')
	for t,i in zip(['Left', 'Right', 'Bottom', 'Top'], Coord):
		f.write('%s, \t %.4f \n' % (t,i))
	f.close()
