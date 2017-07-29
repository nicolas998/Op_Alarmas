#!/usr/bin/env python
from wmf import wmf 
import argparse
import textwrap
import os 
import alarmas as al
from multiprocessing import Pool
import glob
import pandas as pd 
import numpy as np 

def model_warper(L):
	#Ejecucion del modelo
	Res = cu.run_shia(L[1],L[2],L[3],L[4], 
		StorageLoc = L[5], ruta_storage=L[6], kinematicN=12)
	#Escribe resultados 
	ruta = ruta_Qsim + QsimName +'_'+L[0].replace(' ','_').replace('-','')+'.msg'
	Qsim = pd.DataFrame(Res['Qsim'][1:].T, 
		index=Rain.index, 
		columns=posControl)
	Qsim.to_msgpack(ruta)
	#Actualiza historico de caudales simulados
	ruta = ruta_qsim_h + QsimName +'_'+L[0].replace(' ','_').replace('-','')+'hist.csv'
	al.model_write_qsim(ruta, Res['Qsim'][1:].T[0], Rain.index[0], posControl)
	#Se actualizan los historicos de humedad de la parametrizacion asociada.
	al.model_write_Stosim(L[6],L[7])
	
	#imprime que ya ejecuto
	if args.verbose:
		print L[0]+' ejecutado'
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
parser.add_argument("-n", "--newhist", help="(Opcional) Con esta opcion el la funcion model_warper, genera archivos vacios para cada parametrizacion cuando no existe historia o si estaq quiere renovarse",
	action = 'store_true', default = False)
parser.add_argument("-i", "--fechai", help="(Opcional) string, Fecha de inicio de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
parser.add_argument("-f", "--fechaf", help="(Opcional) string, Fecha de fin de nuevo punto de historicos (YYYY-MM-DD HH:MM)")
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
ruta_sto = al.get_ruta(ListConfig, 'ruta_almsim')
ruta_stohist = al.get_ruta(ListConfig, 'ruta_almhist')
ruta_out_sto = al.get_ruta(ListConfig, 'ruta_out_alm')
ruta_out_slides = al.get_ruta(ListConfig, 'ruta_slides')
ruta_slides_bin, ruta_slides_hdr = wmf.__Add_hdr_bin_2route__(ruta_out_slides)
#Nombre de las simulaciones de caudal 
QsimName = al.get_ruta(ListConfig,'Qsim Name')
ruta_Qsim = al.get_ruta(ListConfig, 'ruta_qsim')
ruta_qsim_h = al.get_ruta(ListConfig, 'ruta_qsim_hist')

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
	'Factor de Seguridad FS',
	'Factor Corrector Zg']
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
	cu.set_Slides(wmf.models.sl_zs * float(DictParam['Factor Corrector Zg']), 'Zs')
print wmf.models.sl_zs.mean()

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
		print 'CI corridas'
	else:
		S = al.model_get_constStorage(List, cu.ncells)
		print 'CI constantes'
	#Arma la ejecucion
	Calib = DictCalib[DictStore[i]['Calib']]
	ListEjecs.append([i, Calib, rain_bin, Npasos, 1, S, ruta_sto+DictStore[i]['Nombre'],ruta_stohist+DictStore[i]['Nombre'][:-7]+'hist.msg'])


#Ejecucion
# Cantidad de procesos 
Nprocess = len(ListEjecs)
if Nprocess > 15:
	Nprocess = int(Nprocess/1.2)
#Ejecucion  en paralelo y guarda caudales 
if args.verbose:
	print 'Resumen Ejecucion modelo'
	print '\n'
p = Pool(processes=Nprocess)
R = p.map(model_warper, ListEjecs)
p.close()
p.join()
#Un brinco para uqe quede lindo el print de deslizamientos.
if args.verbose:
	print '\n'
	print 'Resumen deslizamientos'

############################ ESCRIBE EL BINARIO DE DESLIZAMIENTOS ##################

#Archivo plano que dice cuales son las param que simularon deslizamientos 
f = open(ruta_slides_hdr,'w')
f.write('## Parametrizaciones Con Simulacion de Deslizamientos \n')
f.write('Parametrizacion \t N_celdas_Desliza \n')
#Termina de escribir el encabezado y escribe el binario.
rec = 0
for c,i in enumerate(ListEjecs):
	if DictStore[i[0]]['Slides'] == 'True':
		#Determina la cantidad de celdas que se deslizaron
		Slides = np.copy(R[c]['Slides_Map'])
		Nceldas_desliz = Slides[Slides<>0].shape[0]
		f.write('%s \t %d \n' % (i[0], Nceldas_desliz))
		#si esta verbose dice lo que pasa 
		if args.verbose:
			print 'Param '+i[0]+' tiene '+str(Nceldas_desliz)+' celdas deslizadas.'
		#Escribe en el binario 
		rec = rec+1
		wmf.models.write_int_basin(ruta_out_slides, R[c]['Slides_Map'],rec,cu.ncells,1)
f.close()
