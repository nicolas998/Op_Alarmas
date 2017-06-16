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
dateText = dt.datetime.now().strftime('%Y-%m-%d-%H:%M')

print '\n'
print '###################################### Fecha de Ejecucion: '+dateText+' #############################\n'

#Obtiene las rutas necesarias 
ruta_de_rutas = '/home/nicolas/ProyectosGIT/Op_Alarmas/Rutas.md'
RutasList = al.get_rutesList(ruta_de_rutas)

# rutas de objetos de entrada
ruta_cuenca = al.get_ruta(RutasList, 'ruta_cuenca')
ruta_campos = al.get_ruta(RutasList, 'ruta_campos')
ruta_codigos = al.get_ruta(RutasList, 'ruta_codigos')
ruta_configuracion_1 = al.get_ruta(RutasList, 'ruta_configuracion_1')
ruta_almacenamiento = al.get_ruta(RutasList, 'ruta_almacenamiento')
# Rutas de objetos de salida
ruta_out_rain = al.get_ruta(RutasList, 'ruta_rain')

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################### CONSULTA DE LA LLUVIA Y EXTRAPOLACION ############################\n'

#-------------------------------------------------------------------
#GENERA EL CAMPO DE LLUVIA DE LOS ULTIMOS 15MIN Y LOS PROXIMOS 60
#-------------------------------------------------------------------
# Obtiene el datetime 
fecha_1 =  date + dt.timedelta(hours = 5) - dt.timedelta(minutes = 10)
fecha_2 =  date + dt.timedelta(hours = 5) + dt.timedelta(minutes = 60) 
# Lo convierte en texto 
fecha1 = fecha_1.strftime('%Y-%m-%d')
fecha2 = fecha_2.strftime('%Y-%m-%d')
hora_1 = fecha_1.strftime('%H:%M')
hora_2 = fecha_2.strftime('%H:%M')
# Ejecuta para obtener el campo de lluvia en la proxima hora 
lluvia_actual = ruta_out_rain + 'Lluvia_actual'
comando = ruta_codigos+'Rain_Rain2Basin.py '+fecha1+' '+fecha2+' '+ruta_cuenca+' '+ruta_campos+' '+lluvia_actual+' -t 300 -j -u 0.0005 -1 '+hora_1+' -2 '+hora_2
os.system(comando)
# Imprime mensaje de exito
print 'Aviso: Lluvia actual + extrapolacion generados en: '
print lluvia_actual+'\n'

#-------------------------------------------------------------------
#ACTUALIZA EL CAMPO DE LLUVIA HISTORICO DE LA CUENCA 
#-------------------------------------------------------------------
#Luvia historica 
lluvia_historica = ruta_out_rain + 'Lluvia_historica'
#Fechas de inicio y fin 
fecha_1 =  date + dt.timedelta(hours = 5) - dt.timedelta(minutes = 5)
fecha_2 =  date + dt.timedelta(hours = 5) + dt.timedelta(minutes = 0)
# Lo convierte en texto 
fecha1 = fecha_1.strftime('%Y-%m-%d')
fecha2 = fecha_2.strftime('%Y-%m-%d')
hora_1 = fecha_1.strftime('%H:%M')
hora_2 = fecha_2.strftime('%H:%M')
# Ejecuta para actualizar el campo de lluvia 
comando = ruta_codigos+'Rain_Rain2Basin.py '+fecha1+' '+fecha2+' '+ruta_cuenca+' '+ruta_campos+' '+lluvia_historica+' -t 300 -j -u 0.0005 -o True -n -1 '+hora_1+' -2 '+hora_2
os.system(comando)
#imprime aviso 
print 'Aviso: Lluvia historica actualizada en: '
print lluvia_historica+'\n'

#-------------------------------------------------------------------
#GENERA GRAFICAS DE CAMPOS
#-------------------------------------------------------------------
fecha2 = date.strftime('%Y-%m-%d-%H:%M')
ListComandos = []

# Grafica de la lluvia en los ultimos 3 dias 
fecha1 = date - dt.timedelta(hours = 72)
fecha1 = fecha1.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain + 'Acumulado_3dias.png'
comando = ruta_codigos+'Graph_Rain_Campo.py '+fecha1+' '+fecha2+' '+ruta_cuenca+' '+lluvia_historica+' '+ruta_figura+' -1 10 -2 70 -v'
ListComandos.append(comando)

# Grafica de la lluvia en los ultimas 24 horas
fecha1 = date - dt.timedelta(hours = 24)
fecha1 = fecha1.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain + 'Acumulado_1dia.png'
comando = ruta_codigos+'Graph_Rain_Campo.py '+fecha1+' '+fecha2+' '+ruta_cuenca+' '+lluvia_historica+' '+ruta_figura+' -1 5 -2 10 -v'
ListComandos.append(comando)

# Grafica en la ultima hora.
fecha1 = date - dt.timedelta(hours = 1)
fecha1 = fecha1.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain + 'Acumulado_1hora.png'
comando = ruta_codigos+'Graph_Rain_Campo.py '+fecha1+' '+fecha2+' '+ruta_cuenca+' '+lluvia_historica+' '+ruta_figura+' -1 1 -2 5 -v'
ListComandos.append(comando)

#Grafica en los proximos 30min
fecha1 = date + dt.timedelta(minutes = 30)
fecha1 = fecha1.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain + 'Acumulado_30siguientes.png'
comando = ruta_codigos+'Graph_Rain_Campo.py '+fecha2+' '+fecha1+' '+ruta_cuenca+' '+lluvia_actual+' '+ruta_figura+' -1 1 -2 5 -v'
ListComandos.append(comando)

#Lanza los procesos de lluvia en paralelo
p = Pool(processes = 4)
p.map(os.system, ListComandos)
p.close()
print '\n'

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################### EJECUCION DEL MODELO ############################\n'

#Explicacion: Se pueden configurar diferentes ejecuciones con diferentes productos 
#	de lluvia, este caso es uno de ejemplo.

#Ejecucion del modelo en el ultimo intervalo de tiempo
comando = ruta_codigos+'Model_Ejec.py '+ruta_cuenca+' '+ruta_configuracion_1+' -v'
os.system(comando)
#Actualiza las condiciones del modelo 
comando = ruta_codigos+'Model_Update_Store.py '+dateText+' '+ruta_configuracion_1+' -v'
os.system(comando)
print '\n'

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################### PRODUCCION DE FIGURAS ############################\n'

#Figura de la evolucion de los caudales en el cauce
ListaEjec = []
for i in range(13):
	fechaNueva = date + dt.timedelta(minutes = 5*i)
	fechaNueva = fechaNueva.strftime('%Y-%m-%d-%H:%M')
	comando = ruta_codigos+'Graph_StreamFlow_map.py '+fechaNueva+' '+ruta_cuenca+' '+ruta_configuracion_1+' -r '+str(i+1)
	ListaEjec.append(comando)
#Ejecuta lass figuras en paralelo 
p = Pool(processes = 10)
p.map(os.system, ListaEjec)
p.close()

#figura de la evolucion de los deslizamientos 


#figura de la humedad???

