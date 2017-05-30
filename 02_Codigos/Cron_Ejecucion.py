#!/usr/bin/env python
import pandas as pd 
import datetime as dt 
import os 
from multiprocessing import Pool
import numpy as np
import pickle 
import alarmas as al

# Texto Fecha: el texto de fecha que se usa para guardar algunos archivos de figuras.
date = dt.datetime.now()
dateText = dt.datetime.now().strftime('%Y%m%d%H%M')

#Obtiene las rutas necesarias 
ruta_de_rutas = '/home/nicolas/ProyectosGIT/Op_Alarmas/Rutas.md'
RutasList = al.get_rutesList(ruta_de_rutas)

# rutas de objetos de entrada
ruta_cuenca = al.get_ruta(RutasList, 'ruta_cuenca')
ruta_campos = al.get_ruta(RutasList, 'ruta_campos')
ruta_codigos = al.get_ruta(RutasList, 'ruta_codigos')
# Rutas de objetos de salida
ruta_out_rain = al.get_ruta(RutasList, 'ruta_rain')

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################### CONSULTA DE LA LLUVIA Y EXTRAPOLACION ############################'

#-------------------------------------------------------------------
#GENERA EL CAMPO DE LLUVIA DE LOS ULTIMOS 15MIN Y LOS PROXIMOS 60
#-------------------------------------------------------------------
# Obtiene el datetime 
fecha_1 =  dt.datetime.now() + dt.timedelta(hours = 5) - dt.timedelta(minutes = 15)
fecha_2 =  dt.datetime.now() + dt.timedelta(hours = 5) + dt.timedelta(minutes = 60) 
# Lo convierte en texto 
fecha1 = fecha_1.strftime('%Y-%m-%d')
fecha2 = fecha_2.strftime('%Y-%m-%d')
hora_1 = fecha_1.strftime('%H:%M')
hora_2 = fecha_2.strftime('%H:%M')
# Ejecuta para obtener el campo de lluvia en la proxima hora 
lluvia_actual = ruta_out_rain + 'Lluvia_actual'
comando = ruta_codigos+'Rain_Rain2Basin.py '+fecha1+' '+fecha2+' '+ruta_cuenca+' '+ruta_campos+' '+lluvia_actual+' -t 300 -v -j -u 0.01 -1 '+hora_1+' -2 '+hora_2
os.system(comando)

#-------------------------------------------------------------------
#GENERA GRAFICAS DE CAMPOS
#-------------------------------------------------------------------
RainData = pd.read_csv(lluvia_actual,skiprows=5,
	index_col=2, 
	parse_dates=True, 
	infer_datetime_format=True, usecols = (1,2,3))

# Grafica de la lluvia en la ultima hora 

# Grafica de la lluvia en los ultimos 15min

# Grafica de la lluvia en la proxima hora



#Grafica de la 
NoCero = al.get_CamposNoCero(lluvia_actual+'.hdr')



