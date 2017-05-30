#!/usr/bin/env python
import argparse
import textwrap
import numpy as np
import os 
from wmf import wmf 

#Parametros de entrada del trazador
parser=argparse.ArgumentParser(
	prog='Plot_Rain_Campo',
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=textwrap.dedent('''\
	Genera un campo de lluvia a partir de binarios de radar generados.
        '''))
#Parametros obligatorios
parser.add_argument("cuenca",help="Numero del nodo dentro de la red hidrica a plotear")
parser.add_argument("rainbin",help="Ruta al archivo binario con los campos de lluvia")
parser.add_argument("ruta",help="Ruta donde se guarda la figura con la humedad")
parser.add_argument("-1", "--vmin",help="Minimo valor del imshow", default = 0, type = float)
parser.add_argument("-2", "--vmax",help="Maximo valor del imshow", default = 100, type = float)
parser.add_argument("-c", "--coord",help="Escribe archivo con coordenadas", default = False, type = bool)

#lee todos los argumentos
args=parser.parse_args()

