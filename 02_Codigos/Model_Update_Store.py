#!/usr/bin/env python
from wmf import wmf 
import argparse
import textwrap
import os 
import alarmas as al
import pandas as pd 
import datetime as dt 

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
ruta_out_sto = al.get_ruta(ListConfig, 'ruta_out_alm')
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
			#Obtiene las horas de la condicion
			hours = float(DictStore[k]['Condition'][-3:-1])
			#obtiene el archivo con los registros de lluvia de las ultimas N horas
			al.get_rain_last_hours(ruta_rain_hist,ruta_rain_temp,hours, DeltaT)
			#Invoca a la funcion que actualiza.
			if DictStore[k]['Condition'][:-3] == 'No Rain':				
				al.model_update_norain()
			elif DictStore[k]['Condition'][:-3] == 'No Rain Next':				
				al.model_update_norain_next()
			elif DictStore[k]['Condition'][:-3] == 'No Rain Last':
				al.model_update_norain_last(ruta_rain_temp, hours)
			#llama a la 
			print '-------'

