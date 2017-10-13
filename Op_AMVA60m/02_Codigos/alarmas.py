#!/usr/bin/env python
#!/usr/bin/env python
import os 
import pandas as pd
from wmf import wmf
import numpy as np 
import glob 
import pylab as pl
import json
import warnings
warnings.filterwarnings('ignore')

########################################################################
# VARIABLES GLOBALES 

ruta_store = None
ruta_store_bck = None

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

def get_modelConfig_lines(RutesList, key, Calib_Storage = None, PlotType = None):
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
		if Calib_Storage == 'Plot':
			return get_modelPlot(List, PlotType=PlotType)
		return List
	else:
		return 'Aviso: no se encuentran lineas con el key de inicio especificado'

def get_modelPlot(RutesList, PlotType = 'Qsim_map'):
	for l in RutesList:
		key = l.split('|')[1].rstrip().lstrip()
		if key[3:] == PlotType:
			EjecsList = [i.rstrip().lstrip() for i in l.split('|')[2].split(',')]
			return EjecsList
	return key

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
		Cs = float(get_ruta(RutesList, c))
		Storage[i] = Cs
	return Storage.astype(float)

#NOTA: Lista de entrada para crear rutas de Qhist.
# Listlol=[]
# for L in ListEjecs:
     # Listlol.append(ruta_Qsim +'01_CaudalHistorico/'+ QsimName +'_'+L[0].replace(' ','_').replace('-','')+'_hist.msg')

def model_write_ruteQhist(listrutas_Qhist,FechaI,FechaF,pcont):
	#Genera archivos vacios para cada parametrizacion cuando no existe historia o si esta quiere renovarse.
	for i in listrutas_Qhist:
		DifIndex = pd.date_range(FechaI, FechaF, freq='5min')
		Qh = pd.DataFrame(np.zeros(shape=(DifIndex.size,pcont.size))*np.nan, 
			index=pd.date_range(FechaI, FechaF, freq='5min'))
		#Pregunta si esta
		try:
			Lold = os.listdir(i)
			pos = Lold.index(i)
			flag = raw_input('Aviso: El archivo historico : '+i+' ya existe, desea sobre-escribirlo, perdera la historia de este!! (S o N): ')
			if flag == 'S':
				flag = True
			else:
				flag = False
		except:
			flag = True
		#Guardado
		if flag:
			Qh.to_msgpack(i)
		else:
			pass

def model_write_qsim(rutaQsim,rutaQhist, pcont):
	###Se actualizan los historicos de Qsim de la parametrizacion asociada.
	#Lee el almacenamiento actual
	Qactual = pd.read_msgpack(rutaQsim)
	#Lee el historico
	Qhist = pd.read_msgpack(rutaQhist)
	# encuentra el pedazo que falta entre ambos
	if Qhist.index[-1]!=Qactual.index[0]:
		Gap = pd.date_range(Qhist.index[-1], Qactual.index[0], freq='5min')
		#Genera el pedazo con faltantes
		GapData = pd.DataFrame(np.zeros((Gap.size - 2, pcont.size))*np.nan, 
				index= Gap[1:-1])        
		#pega el gap con nans
		Qhist = Qhist.append(GapData)
	else:
		pass		

	#si no hay gap entre ellos, pega la info
	Qhist=Qhist.append(Qactual.iloc[[0]].sort_index(axis=1))
	#Guarda el archivo historico 
	Qhist.to_msgpack(rutaQhist)
	#Aviso
	print 'Aviso: Se ha actualizado el archivo de Qsim_historicos de: '+rutaQhist

#lista de rutas a crear.
# Listlol=[]
# for listt in ListEjecs:
    #Listlol.append(listt[7])
def model_write_ruteShist(listrutas_Shist,FechaI,FechaF):
	#Genera archivos vacios para cada parametrizacion cuando no existe historia o si esta quiere renovarse.
	for i in listrutas_Shist:
		DifIndex = pd.date_range(FechaI, FechaF, freq='5min')
		Sh = pd.DataFrame(np.zeros((DifIndex.size, 5))*np.nan, 
			index=pd.date_range(FechaI, FechaF, freq='5min'))
		#Pregunta si esta
		try:
			Lold = os.listdir(i)
			pos = Lold.index(i)
			flag = raw_input('Aviso: El archivo historico : '+i+' ya existe, desea sobre-escribirlo, perdera la historia de este!! (S o N): ')
			if flag == 'S':
				flag = True
			else:
				flag = False
		except:
			flag = True
		#Guardado
		if flag:
			Sh.to_msgpack(i)
		else:
			pass

def model_write_Stosim(ruta_Ssim,ruta_Shist):
	###Se actualizan los historicos de humedad de la parametrizacion asociada.
	#Lee el almacenamiento actual
	Sactual = pd.read_csv(ruta_Ssim[:-7]+'.StOhdr', header = 4, index_col = 5, parse_dates = True, usecols=(1,2,3,4,5,6))
	St = pd.DataFrame(Sactual[Sactual.index == Sactual.index[0]].values, index=[Sactual.index[0],])
	#Lee el historico
	Shist = pd.read_msgpack(ruta_Shist)
	# encuentra el pedazo que falta entre ambos
	if Shist.index[-1]!=Sactual.index[0]:
		Gap = pd.date_range(Shist.index[-1], Sactual.index[0], freq='5min')
		#Genera el pedazo con faltantes
		GapData = pd.DataFrame(np.zeros((Gap.size - 2, 5))*np.nan, 
				index= Gap[1:-1])        
		#pega el gap con nans
		Shist = Shist.append(GapData)
	else:
		pass		

	#si no hay gap entre ellos, pega la info
	Shist = Shist.append(St)
	#Guarda el archivo historico 
	Shist.to_msgpack(ruta_Shist)
	#Aviso
	print 'Aviso: Se ha actualizado el archivo de Ssim_historicos de: '+ruta_Shist


def model_update_norain():
	print 'no rain'

def model_update_norain_next():
	print 'no next'

def model_update_norain_last(RainRute, Hours):
	# Lee el archivo de lluvia 
	
	print 'no last'

def model_def_rutes(ruteStore, ruteStoreHist):
	ruta_store = ruteStore
	ruta_store_bck = ruteStoreHist

########################################################################
#FUNCIONES PARA GRAFICAR Y GENERAR RESULTADOS

def Graph_AcumRain(fechaI,fechaF,cuenca,rutaRain,rutaFigura,vmin=0,vmax=100,verbose=True):
	''' Si hay lluvia en el periodo definido devuelve 1 si no 0.
	Grafica si figure=True.
	Siempre se debe poner la ruta de la figura.
	##Falta poner ventanas mas grandes de pronostico de lluvia ya que el calentamiento con las par y CI actuales se toma unos 25 pasos.'''

	#Se lee la informacion
	rutebin, rutehdr = wmf.__Add_hdr_bin_2route__(rutaRain)
	cu = wmf.SimuBasin(rute=cuenca)
	DictRain = wmf.read_rain_struct(rutehdr)
	R = DictRain[u' Record']

	#Se cuadran las fechas para que casen con las de los archivos de radar.

	#Se obtienen las fechas con minutos en 00 o 05.
	####FechaF######
	#Obtiene las fechas por dias
	fecha_f = pd.to_datetime(fechaF)
	fecha_f = fecha_f - pd.Timedelta(str(fecha_f.second)+' seconds')
	fecha_f = fecha_f - pd.Timedelta(str(fecha_f.microsecond)+' microsecond')
	#corrige las fechas
	cont = 0
	while fecha_f.minute % 5 <>0 and cont<10:
		fecha_f = fecha_f - pd.Timedelta('1 minutes')
		cont+=1

	####FechaI######
	#Obtiene las fechas por dias
	fecha_i = pd.to_datetime(fechaI)
	fecha_i = fecha_i - pd.Timedelta(str(fecha_f.second)+' seconds')
	fecha_i = fecha_i - pd.Timedelta(str(fecha_f.microsecond)+' microsecond')
	#corrige las fechas
	cont = 0
	while fecha_i.minute % 5 <>0 and cont<10:
		fecha_i = fecha_i - pd.Timedelta('1 minutes')
		cont+=1

	#Evalua que las fechas solicitadas existan, si no para aqui y no se grafica nada - if solo sirve para ensayos.. operacionalmente no debe hacer nada.
	try:
		lol=R[fecha_i:fecha_f]

		#Ensaya si las fechas solicitadas cuentan con campo de radar en el binario historico, si no escoge la fecha anterior a esa. Este debe existir tambien, lo ideal es que se mantenga el dt, existan campos cada 5 min.
		####FechaF######
		Flag = True
		cont = 0
		while Flag:
			try:
				lol = R.index.get_loc(fecha_f)
				Flag = False
			except:
				print 'Aviso: no existe campo de lluvia para fecha_f en la serie entregada, se intenta buscar el de 5 min antes'
				fecha_f = fecha_f - pd.Timedelta('5 minutes')
			cont+=1
			if cont>1:
				Flag = False
		####FechaI######
		Flag = True
		cont = 0
		while Flag:
			try:
				lol = R.index.get_loc(fecha_i)
				Flag = False
			except:
				print 'Aviso: no existe campo de lluvia para fecha_i en la serie entregada, se intenta buscar el de 5 min antes'
				fecha_i = fecha_i - pd.Timedelta('5 minutes')
			cont+=1
			if cont>1:
				Flag = False

		#Escoge pos de campos con lluvia dentro del periodo solicitado.
		pos = R[fecha_i:fecha_f].values
		pos = pos[pos <>1 ]

		#~ #imprime el tamano de lo que esta haciendo 
		#~ if verbose:
			#~ print fecha_f - fecha_i

		#si hay barridos para graficar
		if len(pos)>0:
			#-------
			#Grafica
			#-------
			#Textos para la legenda
			#~ lab = np.linspace(vmin, vmax, 4)
			#~ texto = ['Bajo', 'Medio', 'Alto', 'Muy alto']
			#~ labText = ['%dmm\n%s'%(i,j) for i,j in zip(lab, texto)]
			#Acumula la lluvia para el periodo
			Vsum = np.zeros(cu.ncells)
			for i in pos:
				v,r = wmf.models.read_int_basin(rutebin,i, cu.ncells)
				v = v.astype(float); v = v/1000.0
				Vsum+=v	
			#Genera la figura 
			c = cu.Plot_basinClean(Vsum, cmap = pl.get_cmap('viridis',10), 
				vmin = vmin, vmax = vmax,#~ show_cbar=True,
				#~ cbar_ticksize = 16,
				#~ cbar_ticks= lab,
				#~ cbar_ticklabels = labText,
				#~ cbar_aspect = 17,
				ruta = rutaFigura,
				figsize = (10,12),show=False)
			c[1].set_title('Mapa Lluvia de Radar Acumulada', fontsize=16)
			if verbose:
				print 'Aviso: Se ha producido una grafica nueva con valores diferentes de cero para '+rutaFigura[49:-4]
				print fecha_f - fecha_i
			return 1

		#si no hay barridos
		else:
			#-------
			#Grafica
			#-------
			Vsum = np.zeros(cu.ncells)
			c = cu.Plot_basinClean(Vsum, cmap = pl.get_cmap('viridis',10), 
				vmin = vmin, vmax = vmax,#show_cbar=True,
				#~ cbar_ticksize = 16,
				#~ cbar_ticks= lab,
				#~ cbar_ticklabels = labText,
				#~ cbar_aspect = 17,
				ruta = rutaFigura,
				figsize = (10,12),show=False)
			#~ c[1].set_title('Mapa Lluvia de Radar Acumulada', fontsize=16)
			if verbose:
				print 'Aviso: Se ha producido un campo sin lluvia  para '+rutaFigura[49:-4]
				print fecha_f - fecha_i
			return 0
	except:
		#si no lo logra que no haga nada.
		print 'Aviso: no se puede construir una serie porque las fechas solicitada no existen, no se genera png de acumulado '+ str(fecha_f - fecha_i)
		pass

def Genera_json(rutaQhist,rutaQsim,ruta_out,verbose=True):
    '''Actualiza el .json para desplegar informacion enla pagina de SIATA, o lo genera si este no existe.
    Esta funcion es de uso operacional, la idea es que se ejecute desde otro codigo con las entradas.'''
    #Carga los caudales simulados de la parametrizacionn escogida
    #Qsim historico dataframe
    Qhist = pd.read_msgpack(rutaQhist)
    #Qsim actual y next1hr dataframe
    Qsim=pd.read_msgpack(rutaQsim)
    #Se toman los nodos desde Qsim
    Nodos = Qsim.columns.values

    #Genera el Diccionario con los caudales y escribe el json
    Dict = {}
    for n in Nodos:
        Dict.update({str(n):{}})
        #Qsim en la pos -1.
        Dict[str(n)].update({'Qultimo': float('%.3f' % Qsim[n][0])})
        #Qhist en la pos -1.
    #    Dict[str(n)].update({'Qultimo': float('%.3f' % Qhist[str(n)][len(Qhist[str(n)])-1])})
    #    Dict[str(n)].update({'Qmax_ult24h': float('%.3f' % Qhist[str(n)][-288:].max())})
        Dict[str(n)].update({'Qmax_next1h': float('%.3f' % Qsim[n].max())})
    with open(ruta_out, 'w') as outfile:
        json.dump(Dict, outfile)
    if verbose:
        print'Aviso: Se actualiza correctamente el .json'

def Genera_riskvectorMap(rutaConfig,cuenca,figSZ):  
    ''' Genera un mapa en .png con el risk_vector, esta funcion no es de uso operacional.
        Por lo que necesita leer directamente el ConfigFile.'''
    #Lee el archivo de configuracion
    ListConfig = get_rutesList(rutaConfig)
    #Lectura de rutas de salida de la imagen
    ruta_out = get_ruta(ListConfig,'ruta_map_riskvector')

    #Lectura de cuenca 
    cu = wmf.SimuBasin(rute=cuenca, SimSlides = True)
    wmf.models.slide_allocate(cu.ncells, 10)
    #Se marcan con 1 las celdas incondicionalmente inestables.
    R = np.copy(wmf.models.sl_riskvector)
    #Plot
    cu.Plot_basinClean(R,figsize=(figSZ[0],figSZ[1]),cmap = pl.get_cmap('viridis',3),ruta=ruta_out)


