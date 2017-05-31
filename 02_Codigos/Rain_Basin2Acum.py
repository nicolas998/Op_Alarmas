#!/usr/bin/env python
from wmf import wmf 
import argparse
import textwrap
import os 
import alarmas as al

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='RadarStraConv2Basin',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	(NO OPERACIONAL)
	A partir de una cuenca, y un binario de rain de la cuenca 
	obtiene el acumulado de lluvia para ese periodo, ademas 
	entrega el acumulado para el periodo, la fecha inicio y
	la fecha final.
	Nota: Este codigo no se usa de forma operacional, solo se 
		usa para establecer campos de lluvia acumulados iniciales.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="(Obligatorio) Ruta de la cuenca en formato .nc")
parser.add_argument("rutaRain",help="(Obligatorio) Ruta donde estan los nc")
parser.add_argument("rutaRes", help = "Ruta donde se guardan las imagenes procesadas")
parser.add_argument("-v","--verbose",help="Informa sobre la fecha que esta agregando", 
	action = 'store_true')

#lee todos los argumentos
args=parser.parse_args()

############################ suma el Campo #############################

# Lectura de la cuenca
cu = wmf.SimuBasin(rute = args.cuenca)
#Suma el campo para el periodo
Vsum, f1, f2 = al.Rain_Cumulated(args.rutaRain, cu, rutaAcum=args.rutaRes)

