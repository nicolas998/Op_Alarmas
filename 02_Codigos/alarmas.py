#!/usr/bin/env python

import os 
import pandas as pd
from wmf import wmf
import numpy as np 
import glob 

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
    return 'Aviso: no hay ruta especifica para la cuenca'	


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
		f.write('%s\n' % FechaI.to_pydatetime().strftime('%Y%m%d%H%M'))
		f.write('%s\n' % FechaF.to_pydatetime().strftime('%Y%m%d%H%M'))
		f.close()
	return Vsum, FechaI, FechaF
	
def Rain_Cumulated_Dates(rutaAcum, rutaNC):
	#Obtiene las fechas
	f = open(rutaAcum, 'r')
	L = f.readlines()
	f.close()
	f1 = L[1][:-1]
	f2 = L[2][:-1]
	Df = {'Fecha1': L[1][:-1], 'Fecha2': L[2][:-1]}
	Df1 = {'Fecha1': {'atras': pd.to_datetime(f1)-pd.Timedelta('1 hours'),
		'adelante':pd.to_datetime(f1)+pd.Timedelta('1 hours')},
		'Fecha2': {'atras': pd.to_datetime(f2)-pd.Timedelta('1 hours'),
		'adelante':pd.to_datetime(f2)+pd.Timedelta('1 hours')}}
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
		Fechas.append(List[Diff.argmin()])
	Fechas[1] = List[Diff.argmin()+1]
	return Fechas
			
		
		
