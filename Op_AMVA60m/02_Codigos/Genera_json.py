#!/usr/bin/env python
import argparse
import textwrap
import os 
import pandas as pd 
import json
import alarmas as al
import warnings
warnings.filterwarnings('ignore')


#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Consulta_Caudal',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera un archivo json dedicado a alimentar el kml de despliegue del modelo en la 
	pagina del SIATA, este json contiene informacion de simulacion de una parametrizacion 
	escogida: Qsim, Qsim_max ultimas 24h, Qsim_max proxima hora.
        '''))
#Parametros obligatorios
parser.add_argument("rutaConfig",help="(Obligatorio) Ruta con la configuracion de la cuenca")
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')

#lee todos los argumentos
args=parser.parse_args()

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

#Lee el archivo de configuracion
ListConfig = al.get_rutesList(args.rutaConfig)
#Se define ruta sin extension del Qsim de la parametrizacion a incluir
ruta_qsim = al.get_ruta(ListConfig,'ruta_qsim2Json')
#Se define ruta sin extension del Qhist de la parametrizacion a incluir
ruta_qhist = al.get_ruta(ListConfig,'ruta_qhist2Json')
#Se define la ruta donde se escribe el Json.
ruta_out = al.get_ruta(ListConfig,'ruta_Json')

#-----------------------------------------------------------------------------------------------------
#Carga los caudales simulados de la parametrizacionn escogida
#-----------------------------------------------------------------------------------------------------
#Qsim historico dataframe
Qhist = pd.read_csv(ruta_qhist,sep=',',error_bad_lines=False)
#Qsim actual y next1hr dataframe
Qsim=pd.read_msgpack(ruta_qsim)
#Se toman los nodos desde Qsim
Nodos = Qsim.columns.values

#-----------------------------------------------------------------------------------------------------
#Genera el Diccionario con los caudales y escribe el json
#-----------------------------------------------------------------------------------------------------
Dict = {}
for n in Nodos:
    Dict.update({str(n):{}})
    #Qhist en la pos -1.
    Dict[str(n)].update({'Qultimo': float('%.3f' % Qhist[str(n)][len(Qhist[str(n)])-1])})
    Dict[str(n)].update({'Qmax_ult24h': float('%.3f' % Qhist[str(n)][-288:].max())})
    Dict[str(n)].update({'Qmax_next1h': float('%.3f' % Qsim[n].max())})
with open(ruta_out, 'w') as outfile:
    json.dump(Dict, outfile)
