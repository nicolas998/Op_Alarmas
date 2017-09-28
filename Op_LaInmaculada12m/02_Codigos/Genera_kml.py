#!/usr/bin/env python
import argparse
import textwrap
import os 
from wmf import wmf
from osgeo import ogr
import pickle
import numpy as np 

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Consulta_Caudal',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Actualiza el kml obtenido por el modelo para que sea legible en la pagina del SIATA.
        '''))
#Parametros obligatorios
parser.add_argument("cuencaNC",help="Binario con la cuenca que se le va a obtener el kml")
parser.add_argument("umbral",help="Umbral para la generacion de red hidrica en la cuenca", type = float)
parser.add_argument("dx",help="Delta de x plano para la estimacion de longitud de cauces", type = float)
parser.add_argument("ruta",help="ruta donde se guarda el kml")
parser.add_argument("precip",help="ruta a mapa de precipitacion o constante de precipitacion")
parser.add_argument("-g","--geomorfo", 
	help = "ruta donde se encuentra el diccionario con las propiedades geomorfologicas para cada elemento", 
	default = None)
parser.add_argument("-t","--tiempoC", 
	help = "ruta donde se encuentran las figuras de tiempo de concentracion para desplegar en la pagina (esta la dan los de sistemas)",
	default = None)
parser.add_argument('-1','--coefMax', nargs='+', 
	help='Coeficientes de regionalizacion maxima defecto:[6.71, 3.29]', default = [6.71, 3.29], type = float)
parser.add_argument('-2','--expoMax', nargs='+', 
	help='Exponentes de regionalizacion maxima defecto:[0.82, 0.64]', default = [0.82, 0.64], type = float)
parser.add_argument('-3','--coefMin', nargs='+', 
	help='Exponentes de regionalizacion minima defecto:[0.4168, 0.2]', default = [0.4168, 0.2], type = float)
parser.add_argument('-4','--expoMin', nargs='+', 
	help='Exponentes de regionalizacion minima defecto:[1.058, 0.98]', default = [1.058, 0.98], type = float)
parser.add_argument('-s','--shpinfo', help ="Shp con informacion de nombres de cauces, veredas, mpios y demas")
parser.add_argument('-p','--posiciones', 
	help="Posiciones en las que se encuentran dentro del shp: 'Municipio','Tipo_Canal', 'N_Cauce', 'Barrio', 'Vereda'",
	nargs='+', default = [10,11,12,13,14], type = int)

	
#lee todos los argumentos
args=parser.parse_args()
print args.expoMax
#-----------------------------------------------------------------------------------------------------
#Carga la cuenca y escribe un kml
#-----------------------------------------------------------------------------------------------------
#Carga la cuenca
cu = wmf.SimuBasin(0,0,0,0, rute=args.cuencaNC)
#Mira si la precipitacion es una ruta o un numero
try:
	Precip = float(args.precip)
except:
	Precip, p = wmf.read_map_raster(args.precip)
	Precip = cu.Transform_Map2Basin(Precip, p)
#Calcula caudales medios y regionalizacion de maximos 
cu.GetQ_Balance(Precip)
Qmax = cu.GetQ_Max(cu.CellQmed, args.coefMax, args.expoMax)
Qmin = cu.GetQ_Min(cu.CellQmed, args.coefMin, args.expoMin)
Qmin[Qmin<0] = 0
DictQ = {'Qmed': cu.CellQmed}
for c,k in enumerate(['2.33', '5', '10', '25', '50', '100']):
    DictQ.update({'Qmin'+k:Qmin[c]})
    DictQ.update({'Qmax'+k:Qmax[c]})
#Guarda el kml base
cu.Save_Net2Map(args.ruta, umbral=args.umbral, DriverFormat = 'kml', 
    NumTramo=True, 
    dx = args.dx,
    Dict = DictQ,
    formato = '%.3f')

#-----------------------------------------------------------------------------------------------------
#Corrige el encabezado y cambia colores 
#-----------------------------------------------------------------------------------------------------
#Leer kml 
f = open(args.ruta,'r')
LinKml = f.readlines()
f.close()
#Diccionario con colores para horton
DictColorHort = {'viejo':{'1': 'ffF1AE53', '2': 'ffC77E26', '3': 'ff9E4C22', '4': 'ff712010', '5': '03234D'},
	'nuevo':{'1': '#53AEF1', '2': '#267EC7', '3': '#224C9E', '4': '#102071', '5': '#03234D'}}

flag = True
while flag:
	try:
		#Coloca el estuilo de la corriente 
		pos = LinKml.index('\t<Style><LineStyle><color>ff0000ff</color></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n')        
		horton = LinKml[pos+3].split('>')[1].split('<')[0]
		LinKml[pos] ='\t<Style><LineStyle><color>'+DictColorHort['viejo'][horton]+'</color><width>'+horton+'</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>\n' 
		#Coloca el description 
		codigo = str(int(float(LinKml[pos+4].split('>')[1].split('<')[0])))
		Longitud = '.4f',float(LinKml[pos+2].split('>')[1].split('<')[0])
		Longitud = str(Longitud[1])
		LinKml[pos+2] = '\t\t<SimpleData name="Long[km]">'+Longitud+'</SimpleData>\n'
		LinKml[pos+4] = '\t\t<SimpleData name="Codigo">'+codigo+'</SimpleData>\n'
		LinKml.insert(pos+4,'\t\t<SimpleData name="color_linea">'+DictColorHort['nuevo'][horton]+'</SimpleData>\n')
		LinKml.insert(pos+4,'\t\t<SimpleData name="grosor_linea">'+horton+'</SimpleData>\n')
		nombre = '<name> Resultados Simulacion Hidrologica Tramo '+codigo+' </name>\n'
		LinKml.insert(pos,nombre)
	except:
		flag = False

#Encabezado estatico
LinKml[4] = LinKml[4].replace('float', 'string')
LinKml[5] = LinKml[5].replace('int', 'string')
LinKml[6] = LinKml[6].replace('int', 'string')
LinKml[6] = LinKml[6].replace('Tramo', 'Codigo')
LinKml.insert(7,'\t<SimpleField name="color_linea" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="grosor_linea" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Municipio" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Tipo_Canal" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="N_Cauce" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Barrio" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Vereda" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Comuna" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="Resolucion" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="AreaCuenca" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="CentroX" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="CentroY" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="AlturaMax" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="AlturaMin" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="LongCauce" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="LongCuenca" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="PendCauce" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="PendCuenca" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="TiempoC" type="string"></SimpleField>\n', )
LinKml.insert(7,'\t<SimpleField name="FiguraTiempoC" type="string"></SimpleField>\n', )


for i in range(7,40):
    LinKml[i] = LinKml[i].replace('float','string')

#Encuentra los nodos y su ubicacion
Flag = True
Nodos = []
NodosSolos = []
cont = 1
while Flag:
    try:
        pos = LinKml.index( '\t\t<SimpleData name="Codigo">'+str(cont)+'</SimpleData>\n')
        Nodos.append([cont, pos])
        NodosSolos.append(cont)
        cont += 1
    except:
        if cont == 1:
            cont = 2
        else:
            Flag = False

#-----------------------------------------------------------------------------------------------------
#La adjunta la informacion de barrios, vereda, etc.
#-----------------------------------------------------------------------------------------------------
if args.shpinfo <> None:
	#Lectura del shpfile
	D = ogr.Open(args.shpinfo)
	L = D.GetLayer()
	Nodos = []
	for i in range(L.GetFeatureCount()):
	    f = L.GetFeature(i)
	    Nodos.append(int(f.GetFieldAsString(1).split(' ')[-1]))
	#Mete los valores en el kml
	Flag = True
	cont = 1
	try:
		pos = LinKml.index( '\t\t<SimpleData name="Codigo">'+str(cont)+'</SimpleData>\n')
	except:
		cont += 1
		pos = LinKml.index( '\t\t<SimpleData name="Codigo">'+str(cont)+'</SimpleData>\n')
	while Flag:
		try:
			# Encuentra la posicion para ese index
			pos = LinKml.index( '\t\t<SimpleData name="Codigo">'+str(cont)+'</SimpleData>\n')
			#Incluye info de barrios y demas
			posShp = Nodos.index(cont)
			f = L.GetFeature(posShp)
			#Toma los fields de la descripcion
			ListaNombres = ['Municipio','Tipo_Canal', 'N_Cauce', 'Barrio', 'Vereda']
			for i,n in zip(range(10, 15), ListaNombres):
				if f.GetFieldAsString(i) <> '':
					LinKml.insert(pos, '\t\t<SimpleData name="'+n+'">'+f.GetFieldAsString(i)+'</SimpleData>\n')
			# Actualiza para buscar el siguiente 
			cont += 1
		except:
			Flag = False

#-----------------------------------------------------------------------------------------------------
#Le adjunta la informacion de geomorfologia y de figura de Tc
#-----------------------------------------------------------------------------------------------------
if args.geomorfo <> None:
	#Lee el diccionario con la info geomorfo
	f = open(args.geomorfo,'r')
	DictGeo = pickle.load(f)
	f.close()
	#Mete la geomorfologia
	Flag = True
	cont = 1
	try:
		pos = LinKml.index( '\t\t<SimpleData name="Codigo">'+str(cont)+'</SimpleData>\n')
	except:
		cont += 1
		pos = LinKml.index( '\t\t<SimpleData name="Codigo">'+str(cont)+'</SimpleData>\n')
	while Flag:
		try:
			# Encuentra la posicion para ese index
			pos = LinKml.index( '\t\t<SimpleData name="Codigo">'+str(cont)+'</SimpleData>\n')
			
			#Obtiene geomorfologica y Tc para el nodo
			DG = DictGeo[str(cont)]['Geo']
			Tc = np.median(DictGeo[str(cont)]['Tc'].values())
			#Parametros geomorfologicos
			L1 = ['Area[km2]','Centro_[X]','Centro_[Y]','Hmax_[m]','Hmin_[m]',
				'Long_Cau [km]', 'Long_Cuenca [km]', 'Pend_Cauce [%]',
				'Pend_Cuenca [%]']
			L2 = ['AreaCuenca','CentroX','CentroY','AlturaMax','AlturaMin',
				'LongCauce','LongCuenca','PendCauce','PendCuenca']
			for k1,k2 in zip(L1, L2):
				var = '%.3f' % DG[k1]
				LinKml.insert(pos, '\t\t<SimpleData name="'+k2+'">'+var+'</SimpleData>\n')
			#tiempo de concentracion
			var = '%.3f' % Tc
			LinKml.insert(pos, '\t\t<SimpleData name="TiempoC">'+var+'</SimpleData>\n')
			var = args.tiempoC + 'Tc_'+str(cont)+'.html'
			LinKml.insert(pos, '\t\t<SimpleData name="FiguraTiempoC">'+var+'</SimpleData>\n')
			# Actualiza para buscar el siguiente 
			cont += 1
		except:
			Flag = False
		
#-----------------------------------------------------------------------------------------------------
#Escribe el kml bueno
#-----------------------------------------------------------------------------------------------------
#Escribe nuevo kml
f = open(args.ruta,'w')
f.writelines(LinKml)
f.close()

print wmf.cu.dxp
