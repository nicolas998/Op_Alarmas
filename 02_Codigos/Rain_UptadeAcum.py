#!/usr/bin/env python
from wmf import wmf 
import argparse
import netCDF4
import textwrap
import os 
import alarmas as al
import pandas as pd 
import numpy as np 

#Funcion lectura de archivo netCDF
def Read_netCDf_fromDate(Date):
	try:
		file1 = Date.to_pydatetime().strftime('%Y%m%d%H%M')+'_010_120.nc'
		g = netCDF4.Dataset(args.rutaNC + file1)
		RadProp = [g.ncols, g.nrows, g.xll, g.yll, g.dx, g.dx]      
		rvec = cu.Transform_Map2Basin(g.variables['Rain'][:].T/ (12*1000), RadProp) 
		g.close()
	except:
		file1 = Date.to_pydatetime().strftime('%Y%m%d%H%M')+'_010_120_extrapol.nc'
		g = netCDF4.Dataset(args.rutaNC + file1)
		RadProp = [g.ncols, g.nrows, g.xll, g.yll, g.dx, g.dx]      
		rvec = cu.Transform_Map2Basin(g.variables['Rain'][:].T/ (12*1000), RadProp) 
		g.close()
	return rvec

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='RadarStraConv2Basin',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	(OPERACIONAL)
	A partir del binario acumulado obtenido por Rain_Basin2Acum
	y del encabezado con fechas, actualiza el binario acumulado 
	agregando un campo al final (el que sigue en la fecha) y quitando 
	el primer campo (la fecha inicial), hecho esto actualiza tambien 
	el encabezado.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="(Obligatorio) Ruta de la cuenca en formato .nc")
parser.add_argument("rutaAcum",help="(Obligatorio) Ruta donde esta el acumulado")
parser.add_argument("rutaNC", help = "Ruta donde se encuentran los netCDF con la lluvia de radar")
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')

#lee todos los argumentos
args=parser.parse_args()

############################ Obtiene el campo y Fechas #############################

# Lectura de la cuenca
cu = wmf.SimuBasin(rute = args.cuenca)
#rutas
rutabin, rutahdr = wmf.__Add_hdr_bin_2route__(args.rutaAcum)
# Lee el campo acumulado 
Vsum,r = wmf.models.read_float_basin(rutabin,1,cu.ncells)
# Obtiene las fechas inicial y final.
Fechas = al.Rain_Cumulated_Dates(rutahdr, args.rutaNC)


################### Actualiza el campo y archivo de fechas ##########################

#Lee archivos viejo y nuevo cde fechas
rvec_old = Read_netCDf_fromDate(Fechas[0])
rvec_new = Read_netCDf_fromDate(Fechas[4])
#si lo ponene a hablar
if args.verbose:
	print 'Lluvia en: '+ Fechas[0].to_pydatetime().strftime('%Y%m%d%H%M')+': '+str(rvec_old.mean())
	print 'Lluvia en: '+ Fechas[4].to_pydatetime().strftime('%Y%m%d%H%M')+': '+str(rvec_new.mean())
#Actualiza el binario de lluvia de radar.
Vsum = Vsum - rvec_old + rvec_new
#Sobre escribe el archivo binario de lluvia acumulada 
Temp = np.zeros((1, cu.ncells))
Temp[0] = Vsum
wmf.models.write_float_basin(rutabin, Temp, 1, cu.ncells, 1)

#Actualiza archivo de fechas
FechaI = Fechas[0] + pd.Timedelta('5 minutes')
FechaF = Fechas[4] + pd.Timedelta('5 minutes')

#Archivo
f = open(rutahdr, 'w')
f.write('Fecha y hora de inicio y fin del binario acumulado:\n')
f.write('Fecha1: %s\n' % FechaI.to_pydatetime().strftime('%Y%m%d%H%M'))
f.write('Fecha2: %s\n' % FechaF.to_pydatetime().strftime('%Y%m%d%H%M'))
f.write('Lluvia Media: %.4f \n' % Vsum.mean())
f.close()

