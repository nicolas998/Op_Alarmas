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
print '###################################### SET DE CAMPO DE LLUVIA ############################'

#-------------------------------------------------------------------
#GENERA EL CAMPO DE LLUVIA DE LOS ULTIMOS 15MIN Y LOS PROXIMOS 60
#-------------------------------------------------------------------
# Obtiene el datetime 
fecha_1 =  date + dt.timedelta(hours = 5) - dt.timedelta(days = 3)
fecha_2 =  date + dt.timedelta(hours = 5) 
# Lo convierte en texto 
fecha1 = fecha_1.strftime('%Y-%m-%d')
fecha2 = fecha_2.strftime('%Y-%m-%d')
hora_1 = fecha_1.strftime('%H:%M')
hora_2 = fecha_2.strftime('%H:%M')
# Ejecuta para obtener el campo de lluvia en la proxima hora 
lluvia_actual = ruta_out_rain + 'Lluvia_historica'
comando = ruta_codigos+'Rain_Rain2Basin.py '+fecha1+' '+fecha2+' '+ruta_cuenca+' '+ruta_campos+' '+lluvia_actual+' -t 300 -v -j -u 0.01 -1 '+hora_1+' -2 '+hora_2
os.system(comando)
