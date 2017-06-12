#!/usr/bin/env python

import os 
import pandas as pd
from wmf import wmf
import numpy as np 
import glob 

########################################################################
# VARIABLES GLOBALES 



########################################################################
# FUNCIONES PARA OBTENER RUTAS 

def get_rutesList(rutas):
	f = open(rutas,'r')
	L = f.readlines()
	f.close()
	return L

def get_ruta(RutesList, key):
    for i in RutesList:
        if i.startswith('- **'+key+'**'):
            return i.split(' ')[-1][:-1] 
    return 'Aviso: no se ha podido leer el key especificado'	

def get_rain_last_hours(ruta, rutaTemp, hours, DeltaT = 300):
	#calcula los pasos 
	Min = DeltaT/60.0
	MinInHours = 60.0 / Min
	Pasos = int(hours * MinInHours)
	#Escribe la cola de informacion 
	comando = 'tail '+ruta+' -n '+str(Pasos)+' > '+rutaTemp
	os.system(comando)

def get_modelConfig_lines(RutesList, key, Calib_Storage = None):
	List = []
	for i in RutesList:
		if i.startswith('|'+key) or i.startswith('| '+key):
			List.append(i)
	if len(List)>0:
		if Calib_Storage == 'Calib':
			return get_modelCalib(List)
		if Calib_Storage == 'Store':
			return get_modelStore(List)
		if Calib_Storage == 'Update':
			return get_modelStoreLastUpdate(List)
		return List
	else:
		return 'Aviso: no se encuentran lineas con el key de inicio especificado'

def get_modelCalib(RutesList):
	DCalib = {}
	for l in RutesList:
		c = [float(i) for i in l.split('|')[3:-1]]
		name = l.split('|')[2]
		DCalib.update({name.rstrip().lstrip(): c})
	return DCalib

def get_modelStore(RutesList):
	DStore = {}
	for l in RutesList:
		l = l.split('|')
		DStore.update({l[1].rstrip().lstrip():
			{'Nombre': l[2].rstrip().lstrip(),
			'Actualizar': l[3].rstrip().lstrip(),
			'Tiempo': float(l[4].rstrip().lstrip()),
			'Condition': l[5].rstrip().lstrip(),
			'Calib': l[6].rstrip().lstrip(),
            'BackSto': l[7].rstrip().lstrip(),
            'Slides': l[8].rstrip().lstrip()}})
	return DStore

def get_modelStoreLastUpdate(RutesList):
	DStoreUpdate = {}
	for l in RutesList:
		l = l.split('|')
		DStoreUpdate.update({l[1].rstrip().lstrip():
			{'Nombre': l[2].rstrip().lstrip(),
			'LastUpdate': l[3].rstrip().lstrip()}})
	return DStoreUpdate

########################################################################
# FUNCIONES PARA LIDIAR CON CAMPOS DE LLUVIA

def Rain_NoCero(rutaRain):
	f = open(rutarain,'r')
	L = f.readlines()
	f.close()
	return float(L[3].split()[-1])

def Rain_Cumulated(rutaCampo, cu, rutaAcum = None):
	rutabin, rutahdr = wmf.__Add_hdr_bin_2route__(rutaCampo)
	#Lee el esquema del campo 
	D = pd.read_csv(rutahdr,skiprows=5,
		index_col=2, parse_dates=True, 
		infer_datetime_format=True, 
		usecols = (1,2,3))
	Nrecords = D[u' Record'][-1]
	#Acumula la precipitacion para esa consulta
	Vsum = np.zeros(cu.ncells)
	for i in range(1,18):
		v,r = wmf.models.read_int_basin(rutabin,i, cu.ncells)
		v = v.astype(float); v = v/1000.0
		Vsum+=v
	#Entrga Fecha Inicial y Fecha final.
	FechaI = D[u' Record'].index[0]
	FechaF = D[u' Record'].index[-1]
	FechaI = FechaI + pd.Timedelta('5 hours')
	FechaF = FechaF + pd.Timedelta('5 hours')
	#si hay ruta de guardado guarda
	if rutaAcum <> None:
		#Obtiene rutas binaria y hdr
		rutabin, rutahdr = wmf.__Add_hdr_bin_2route__(rutaAcum)
		#Escribe el binario 
		Temp = np.zeros((1, cu.ncells))
		Temp[0] = Vsum
		wmf.models.write_float_basin(rutabin, Temp, 1, cu.ncells, 1)
		#Escribe el encabezado con fecha inicio y fecha fin del binario
		f = open(rutahdr, 'w')
		f.write('Fecha y hora de inicio y fin del binario acumulado:\n')
		f.write('Fecha1: %s\n' % FechaI.to_pydatetime().strftime('%Y%m%d%H%M'))
		f.write('Fecha2: %s\n' % FechaF.to_pydatetime().strftime('%Y%m%d%H%M'))
		f.write('Lluvia Media: %.4f \n' % Vsum.mean())
		f.close()
	return Vsum, FechaI, FechaF
	
def Rain_Cumulated_Dates(rutaAcum, rutaNC):
	#Obtiene las fechas
	f = open(rutaAcum, 'r')
	L = f.readlines()
	f.close()
	f1 = L[1].split()[1]
	f2 = L[2].split()[1]
	Df = {'Fecha1': L[1].split()[1], 'Fecha2': L[2].split()[1]}
	Df1 = {'Fecha1': {'atras': pd.to_datetime(f1)-pd.Timedelta('30 minutes'),
		'adelante':pd.to_datetime(f1)+pd.Timedelta('30 minutes')},
		'Fecha2': {'atras': pd.to_datetime(f2)-pd.Timedelta('30 minutes'),
		'adelante':pd.to_datetime(f2)+pd.Timedelta('30 minutes')}}
	Fechas = []
	for k in ['Fecha1','Fecha2']:
		#Obtuiene fechas atras y adelante
		f11 = Df1[k]['atras'].to_pydatetime().strftime('%Y%m%d')
		f12 = Df1[k]['adelante'].to_pydatetime().strftime('%Y%m%d')
		#Lista lo que hay alrededor
		List = glob.glob(rutaNC+f11+'*.nc')
		List.extend(glob.glob(rutaNC+f12+'*.nc'))
		List.sort()
		List = np.array([pd.to_datetime(i[43:55]) for i in List])
		#Diferenciass de fecha
		Diff = np.abs(List - pd.to_datetime(Df[k]))
		for i in range(4):
			try:
				Fechas.append(List[Diff.argmin()+i])
			except:
				Fechas.append(pd.to_datetime('200001010000'))
	#Fechas[1] = List[Diff.argmin()+1]
	return Fechas
			
		
########################################################################
# FUNCIONES PARA SET DEL MODELO 

def model_get_constStorage(RutesList, ncells):
	Storage = np.zeros((5, ncells))
	for i,c in enumerate(['Inicial Capilar','Inicial Escorrentia','Inicial Subsup','Inicial Subterraneo','Inicial Corriente']):
		Cs = float(get_ruta(List, c))
		Storage[i] = Cs
	return Storage.astype(float)

def model_write_qsim(ruta,Qsim, index, pcont):
	#se fija si ya esta
	L = glob.glob(ruta)
	if len(L)>0:
		Existe = True
		Nuevo = False
	else:
		Existe = False
		Nuevo = True
	#Obtiene el caudale n un Data Frame
	D = {}
	for c,i in enumerate(pcont):
		D.update({i:Qsim[c]})
	date = index.to_pydatetime().strftime('%Y-%m-%d-%H:%M')
	Qsim = {date:D}
	Qsim = pd.DataFrame(Qsim).T
	#Escribe el Caudal
	with open(ruta, 'a') as f:
		Qsim.to_csv(f, header=Nuevo,float_format='%.3f')

def model_update_norain():
	print 'no rain'

def model_update_norain_next():
	print 'no next'

def model_update_norain_last(RainRute, Hours):
	# Lee el archivo de lluvia 
	
	print 'no last'
