#!/usr/bin/env python
from wmf import wmf 
import argparse
import textwrap
import os 
import alarmas as al
import pandas as pd 
import datetime as dt 

def model_update_norain_last(key, umbral = 1):
	#lee la lluvia temporal
	rainHist = pd.read_csv(ruta_rain_temp, 
		index_col=3, parse_dates=True, 
		infer_datetime_format=True, header=None,)
	#Suma la lluvia
	if rainHist[2].sum() < umbral:
		if DictUpdate['-t '+k[3:]]['Nombre'] <> 'None':
			#Remplaza el archivo
			comando = 'cp '+ruta_bck_sto+DictUpdate['-t '+key[3:]]['Nombre']+' '+ruta_sto+DictStore[key]['Nombre']
			os.system(comando)
			#Actualiza la fecha de actualizacion 
			DictUpdate['-t '+key[3:]]['LastUpdate'] = args.date

def model_update_norain_next(key, umbral = 1):
	#Suma la lluvia
	if Rain.sum()<umbral:
		if DictUpdate['-t '+k[3:]]['Nombre'] <> 'None':
			#remplaza
			comando = 'cp '+ruta_bck_sto+DictUpdate['-t '+key[3:]]['Nombre']+' '+ruta_sto+DictStore[key]['Nombre']
			os.system(comando)
			#Actualiza la fecha de actualizacion 
			DictUpdate['-t '+key[3:]]['LastUpdate'] = args.date

def model_update_norain(key, umbral = 1):
	#lee la lluvia temporal
	rainHist = pd.read_csv(ruta_rain_temp, 
		index_col=3, parse_dates=True, 
		infer_datetime_format=True, header=None,)
	#Suma la lluvia
	if rainHist[2].sum() < umbral and Rain.sum()<umbral:
		if DictUpdate['-t '+k[3:]]['Nombre'] <> 'None':
			#Remplaza
			comando = 'cp '+ruta_bck_sto+DictUpdate['-t '+key[3:]]['Nombre']+' '+ruta_sto+DictStore[key]['Nombre']
			os.system(comando)
			#Actualiza la fecha de actualizacion 
			DictUpdate['-t '+key[3:]]['LastUpdate'] = args.date



#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='RadarStraConv2Basin',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	(OPERACIONAL)
	Las condiciones de almacenamiento que tienen condicion para ser 
	actualizadas por condiciones base, son actualizadas de acuerdo a 
	la cantidad de tiempo establecido para la actualizacion y reglas.
        '''))
#Parametros obligatorios
parser.add_argument("date",help="(Obligatorio) Fecha de ejecucion (YYYY-MM-DD-HH:MM)")
parser.add_argument("rutaConfig",help="(Obligatorio) Ruta con la configuracion de la cuenca")
parser.add_argument("-u","--umbral", help="(Opcional) Umbral a partir del cual se considera que hay lluvia en el periodo evaluado",
	default = 1.0, type=float)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')

#lee todos los argumentos
args=parser.parse_args()

############################ CONFIGURACION DE LA CUENCA #############################

#Lee el archivo de configuracion
ListConfig = al.get_rutesList(args.rutaConfig)
#informacion de la lluvia
rutaRain = al.get_ruta(ListConfig, 'ruta_rainFile')
rain_bin, rain_hdr = wmf.__Add_hdr_bin_2route__(rutaRain)
DataRain = wmf.read_rain_struct(rain_hdr)
Rain = wmf.read_mean_rain(rain_hdr)
ruta_rain_hist = al.get_ruta(ListConfig, 'ruta_rainHistoryFile')
ruta_rain_temp =  '/var/tmp/RainTemp.hdr'

#Lee archivo de configuracion y la cuenca, almacenamiento 
ruta_sto = al.get_ruta(ListConfig, 'ruta_almacenamiento')
ruta_bck_sto = al.get_ruta(ListConfig, 'ruta_bkc_alm')

#Delta de tiempo
DeltaT = float(al.get_ruta(ListConfig, 'Dt[seg]'))

############################ DICCIONARIOS CON DATOS #############################

#Lista de calibraciones
DictStore = al.get_modelConfig_lines(ListConfig, '-s', 'Store')
DictUpdate = al.get_modelConfig_lines(ListConfig, '-t', 'Update')

############################ ACTUALIZACION ###########################################

#Fecha Actual pasada como parametro
DateNow = pd.to_datetime(args.date)
#Calcula la cantidad de horas desde la ultima actualizacion
for k in DictUpdate.keys():
	dat = pd.to_datetime(DictUpdate[k]['LastUpdate'])
	deltaT = DateNow - dat
	DictUpdate[k].update({'Horas': deltaT.total_seconds()/3600.0})
#si la cantidad de horas es inferior al umbral evalua si cumple la 
#regla establecida 
for k in DictStore.keys():
	#Evalua si esas condiciones se van a actualizar o no, y si cumplen
	#el tiempo sin ser actualizadas
	if DictStore[k]['Actualizar'] == 'True':
		if DictUpdate['-t '+k[3:]]['Horas'] > DictStore[k]['Tiempo']:
			
			#CASO 1: NO RAIN: no hay lluvia atras ni adelante.
			if DictStore[k]['Condition'][:-3] == 'No Rain':	
				#Obtiene las horas de la condicion
				hours = float(DictStore[k]['Condition'][-3:-1])
				al.get_rain_last_hours(ruta_rain_hist,ruta_rain_temp,hours, DeltaT)
				model_update_norain(k, args.umbral)
			
			#CASO 2: NO RAIN NEXT: No hay lluvia adelante.
			elif DictStore[k]['Condition'][:-3] == 'No Rain Next':				
				model_update_norain_next(k, args.umbral)
			
			#CASO 3: NO RAIN LAST: no hay lluvia atras.
			elif DictStore[k]['Condition'][:-3] == 'No Rain Last':
				#Obtiene las horas de la condicion
				hours = float(DictStore[k]['Condition'][-3:-1])
				al.get_rain_last_hours(ruta_rain_hist,ruta_rain_temp,hours, DeltaT)
				model_update_norain_last(k,args.umbral)
			
			#CASO 4: ...

#Actualiza las fechas dentro del archivo de configuracion 

#Obtiene las posiciones en la tabla
pos = []
key = '-t'
for c,i in enumerate(ListConfig):
	if i.startswith('|'+key) or i.startswith('| '+key):
		pos.append(c)
#Ordena las reglas 
Keys = DictUpdate.keys()
Keys.sort()
#Obtiene las nuevas 
for c,p in enumerate(pos):
	ListConfig[p] = '| '+Keys[c]+'|'+DictUpdate[Keys[c]]['Nombre']+'|'+DictUpdate[Keys[c]]['LastUpdate']+'|\n'
#Escribe el nuevo archivo 
f = open(args.rutaConfig,'w')
f.writelines(ListConfig)
f.close()
