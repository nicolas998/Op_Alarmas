
#!/usr/bin/env python
import pandas as pd 
import datetime as dt 
import os 
from wmf import wmf
from multiprocessing import Pool
import numpy as np
import pickle 
import alarmas as al
import glob 
import time 

# Texto Fecha: el texto de fecha que se usa para guardar algunos archivos de figuras.
date = dt.datetime.now()
dateText = dt.datetime.now().strftime('%Y-%m-%d-%H:%M')

print '\n'
print '###################################### Fecha de Ejecucion: '+dateText+' #############################\n'

#Obtiene las rutas necesarias 
ruta_de_rutas = '/media/nicolas/Home/Op_Alarmas/Rutas.md'
RutasList = al.get_rutesList(ruta_de_rutas)

# rutas de objetos de entrada
ruta_cuenca = al.get_ruta(RutasList, 'ruta_cuenca')
ruta_campos = al.get_ruta(RutasList, 'ruta_campos')
ruta_codigos = al.get_ruta(RutasList, 'ruta_codigos')
ruta_configuracion_1 = al.get_ruta(RutasList, 'ruta_configuracion_1')
ruta_almacenamiento = al.get_ruta(RutasList, 'ruta_almacenamiento')
# Rutas de objetos de salida
ruta_out_rain = al.get_ruta(RutasList, 'ruta_rain')
ruta_out_rain_png = al.get_ruta(RutasList, 'ruta_rain_png')


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
#~ ListComandos = []

print 'Aviso: Se generan graficas de radar para los intervalos:'

# Grafica de la lluvia en los ultimos 3 dias 
fecha1 = date - dt.timedelta(hours = 72)
fecha1 = fecha1.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain_png + 'Acumulado_3dias.png'
r3dias=al.Graph_AcumRain(fecha1,fecha2,ruta_cuenca,lluvia_historica,ruta_figura,vmin=10,vmax=70)

# Grafica de la lluvia en los ultimas 24 horas
fecha1 = date - dt.timedelta(hours = 24)
fecha1 = fecha1.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain_png + 'Acumulado_1dia.png'
r1dia=al.Graph_AcumRain(fecha1,fecha2,ruta_cuenca,lluvia_historica,ruta_figura,vmin=5,vmax=70)

# Grafica en la ultima hora.
fecha1 = date - dt.timedelta(hours = 1)
fecha1 = fecha1.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain_png + 'Acumulado_1hora.png'
r1hr=al.Graph_AcumRain(fecha1,fecha2,ruta_cuenca,lluvia_historica,ruta_figura,vmin=1,vmax=20)

#Grafica en los proximos 30min
fecha1 = fecha2
fecha2= date + dt.timedelta(minutes = 30)
fecha2 = fecha2.strftime('%Y-%m-%d-%H:%M')
ruta_figura = ruta_out_rain_png + 'Acumulado_30siguientes.png'
r30minnext=al.Graph_AcumRain(fecha1,fecha2,ruta_cuenca,lluvia_actual,ruta_figura,vmin=1,vmax=5)


#~ ##Lanza los procesos de lluvia en paralelo
#~ p = Pool(processes = 4)
#~ p.map(os.system, ListComandos)
#~ p.close()
#~ p.join()
#~ #time.sleep(20)
#~ print '\n'

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
time.sleep(15)

#Actualiza las condiciones del modelo 
comando = ruta_codigos+'Model_Update_Store.py '+dateText+' '+ruta_configuracion_1+' -v'
os.system(comando)
print '\n'
 
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
print '###################################### PRODUCCION DE FIGURAS ############################\n'

# si hay lluvia en la ultima hora y en los proximos 30 min se generan figuras
if r1hr == 0 and r30minnext == 0:
	print 'Aviso: No se generan graficas de resultados de simulacion ya que no hay lluvia en la ultima hora ni los prox. 30 min.'
	pass
else:
	#~ print 'Aviso: Se ejectuan figuras.'
	#Lectura del archivo de configuracion
	ConfigFile = al.get_rutesList(ruta_configuracion_1)

	#Figura de la evolucion de los caudales en el cauce

	#Ruta donde se borraran graficas viejas los caudales en png
	ruta_erase_png = al.get_ruta(ConfigFile, 'ruta_map_qsim')

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
	p.join()

	print '\n'
	print 'Se ejecutan figuras con mapa de StreamFlow'
	print '\n'

	#elimina figuras viejas 
	comando = ruta_codigos+'Graph_Erase_Last.py '+ruta_configuracion_1+' '+ruta_erase_png+' -n 301 -v'
	os.system(comando)


	#Figura de la humedad simulada en el tiempo actual
	#Ruta donde se guardan los caudales en png
	ruta_erase_png = al.get_ruta(ConfigFile, 'ruta_map_humedad')
	#lista de ejecuciones
	ListaEjec = []
	fechaNueva = date 
	fechaNueva = fechaNueva.strftime('%Y-%m-%d-%H:%M')
	comando = ruta_codigos+'Graph_Moisture_map.py '+fechaNueva+' '+ruta_cuenca+' '+ruta_configuracion_1+' -r '+str(i+1)
	ListaEjec.append(comando)
	#Ejecuta las figuras en paralelo 
	p = Pool(processes = 3)
	p.map(os.system, ListaEjec)
	p.close()
	p.join()

	print '\n'
	print 'Se ejecutan figuras con mapa de Humedad'
	print '\n'

	#elimina figuras viejas 
	comando = ruta_codigos+'Graph_Erase_Last.py '+ruta_configuracion_1+' '+ruta_erase_png+' -n 288 -v'
	os.system(comando)


	#Figura de los deslizamiento simuados en el tiempo acumulado - 5 min.

	#Ruta donde se guardan los caudales en png
	ruta_erase_png = al.get_ruta(ConfigFile, 'ruta_map_slides')

	ListaEjec = []
	fechaNueva = date
	fechaNueva = fechaNueva.strftime('%Y-%m-%d-%H:%M')
	comando = ruta_codigos+'Graph_Slides_map.py '+fechaNueva+' '+ruta_cuenca+' '+ruta_configuracion_1
	ListaEjec.append(comando)
	#Ejecuta las figuras en paralelo 
	p = Pool(processes = 3)
	p.map(os.system, ListaEjec)
	p.close()
	p.join()
	print '\n'
	print 'Se ejecutan figuras con mapa de Deslizamientos'
	print '\n'


	#elimina figuras viejas 
	comando = ruta_codigos+'Graph_Erase_Last.py '+ruta_configuracion_1+' '+ruta_erase_png+' -n 288 -v'
	os.system(comando)
#~ 
	#Figura comparativa de niveles simulados vs. observado y los de alerta.

	#Ruta donde se guardan los caudales en png
	ruta_erase_png = al.get_ruta(ConfigFile, 'ruta_serie_qsim')

	ListaEjec = []
	fechaNueva = date
	fechaNueva = fechaNueva.strftime('%Y-%m-%d-%H:%M')
	comando = ruta_codigos+'Graph_Levels.py '+fechaNueva+' '+ruta_cuenca+' '+ruta_configuracion_1
	ListaEjec.append(comando)
	#Ejecuta las figuras en paralelo 
	p = Pool(processes = 3)
	p.map(os.system, ListaEjec)
	p.close()
	p.join()

	print '\n'
	print 'Se ejecutan figuras comparativas de niveles simulados'
	print '\n'

	#elimina figuras viejas 
	comando = ruta_codigos+'Graph_Erase_Last.py '+ruta_configuracion_1+' '+ruta_erase_png+' -n 288 -v'
	os.system(comando)

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
dateText = dt.datetime.now().strftime('%Y-%m-%d-%H:%M')

print '\n'
print '###################################### FIN DEL CRON: '+dateText+' #############################\n'
