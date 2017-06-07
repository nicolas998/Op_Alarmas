#!/usr/bin/env python
from wmf import wmf 
import argparse
import textwrap
import os 
import alarmas as al
from multiprocessing import Pool
import glob
import pandas as pd 

def model_warper(L):
	#Ejecucion del modelo
	Res = cu.run_shia(L[1],L[2],L[3],L[4], 
		StorageLoc = L[5], ruta_storage=L[6], kinematicN=4)
	#Escribe resultados 
	ruta = ruta_Qsim + QsimName +'_'+L[0].replace(' ','_').replace('-','')+'.msg'
	Qsim = pd.DataFrame(Res['Qsim'][1:].T, 
		index=Rain.index, 
		columns=posControl)
	Qsim.to_msgpack(ruta)
	if args.verbose:
		print L[0]+' ejecutado.'
	return Res

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='RadarStraConv2Basin',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	(OPERACIONAL)
	Ejecuta el modelo de forma operacional, para su operacion 
	requiere de: la cuenca, el archivo de configuracion y 
	ruta donde se escriben los resultados de simulacion de caudales.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="(Obligatorio) Ruta de la cuenca en formato .nc")
parser.add_argument("rutaConfig",help="(Obligatorio) Ruta con la configuracion de la cuenca")
parser.add_argument("rutaQsim", help = "Ruta donde se guardan los caudales simulados")
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
#Lee archivo de configuracion y la cuenca, almacenamiento 
cu = wmf.SimuBasin(rute=args.cuenca, SimSlides = True)
ruta_sto = al.get_ruta(ListConfig, 'ruta_almacenamiento')
ruta_out_sto = al.get_ruta(ListConfig, 'ruta_out_alm')
#Nombre de las simulaciones de caudal 
QsimName = al.get_ruta(ListConfig,'Qsim Name')
ruta_Qsim = al.get_ruta(ListConfig, 'ruta_qsim')

#Set por defecto de la modelacion
wmf.models.show_storage = 1
wmf.models.separate_fluxes = 1
wmf.models.dt = 300
wmf.models.sl_fs = 0.5
wmf.models.sim_slides = 1
posControl = wmf.models.control[wmf.models.control<>0]


#Param de configuracion
Lparam = ['Dt[seg]','Dx[mts]',
	'Almacenamiento medio',
	'Separar Flujos',
	'ruta_almacenamiento',
	'Retorno',
	'Simular Deslizamientos',
	'Factor de Seguridad FS']
DictParam = {}
for i in Lparam:
	a = al.get_ruta(ListConfig, i)
	DictParam.update({i:a})

#Nueva configuracion
#Prepara el tiempo
wmf.models.dt = float(DictParam['Dt[seg]'])
wmf.models.retorno = float(DictParam['Retorno'])
# Prepara los que son binarios (1) si (0) no
if DictParam['Almacenamiento medio'] == 'True':
	wmf.models.show_storage = 1
if DictParam['Separar Flujos'] == 'True':
	wmf.models.separate_fluxes = 1
if DictParam['Simular Deslizamientos'] == 'True':
	wmf.models.sim_slides = 1
	wmf.models.sl_fs = float(DictParam['Factor de Seguridad FS'])

############################ LECTURA DE CALIBRACIONES #############################

#Lista de calibraciones
DictCalib = al.get_modelConfig_lines(ListConfig, '-c', 'Calib')
DictStore = al.get_modelConfig_lines(ListConfig, '-s', 'Store')

############################ EJECUCION ###########################################

#Prepara las ejecuciones
ListEjecs = []
Npasos = DataRain[u' Record'].shape[0]
for i in DictStore.keys():
	#trata de leer el almacenamiento 
	FileName = glob.glob(ruta_sto + DictStore[i]['Nombre'])
	if len(FileName):
		S = wmf.models.read_float_basin_ncol(ruta_sto+DictStore[i]['Nombre'],1,cu.ncells,5)[0]
	else:
		S = al.model_get_constStorage(List, cu.ncells)
	#Arma la ejecucion
	Calib = DictCalib[DictStore[i]['Calib']]
	ListEjecs.append([i, Calib, rain_bin, Npasos, 1, S, ruta_sto+DictStore[i]['Nombre']])

#Ejecucion
# Cantidad de procesos 
Nprocess = len(ListEjecs)
if Nprocess > 15:
	Nprocess = int(Nprocess/1.2)
#Ejecucion  en paralelo y guarda caudales 
p = Pool(processes=Nprocess)
R = p.map(model_warper, ListEjecs)
p.close()
