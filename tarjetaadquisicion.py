import sys
import csv
import glob
import time
import serial
import threading
from multiprocessing import Queue

class TarjetaAdquisicion():
	"""docstring for TarjetaAdquisicion"""
	def __init__(self,queue = Queue(),baudrate = 57600):
		self.miFila = queue
		self.miNombrePuerto = '/dev/ttyAMA0'
		self.miPuerto = serial.Serial()
		self.miPuerto.baudrate = baudrate
		self.miPuerto.timeout = 10
		self.miPuerto.port = self.miNombrePuerto
		self.miPuerto.open()
		self.miPuerto.setDTR(False)
		self.miPuerto.dtr = False
		time.sleep(0.5)
		#self.miPuerto.open()
		#miPuerto = serial.Serial('/dev/ttyUSB0',57600,timeout=10)
		self.caracterDeInicio = 'I'
		self.caracterDeFinalizacion = 'T'
		self.limitesParaMensaje = '{}'
		self.timeout = 20				# 10 segundos
		self.miListaInformacion = []
		self.tiempo = []
		self.voltaje  = []
		self.corriente = []
		self.temperatura = []
		self.rpm = []
		self.estado = 0
		self.informacionIngresada = []

		"""
			estado = 0, inicial
			estado = 1, listo con informacion
			estado = 2, -
		"""

	def inicializar(self):
		self.timeout = 20				# 10 segundos
		self.miListaInformacion = []
		self.tiempo = []
		self.voltaje  = []
		self.corriente = []
		self.temperatura = []
		self.rpm = []
		del self.miListaInformacion 
		self.miListaInformacion = []

	def iniciarTransmision(self):
		#print('Iniciando transmisión')
		self.miPuerto.write(self.caracterDeInicio.encode())

	def finalizarTransmision(self):
		#print('Finalizando transmisión')
		self.miPuerto.write(self.caracterDeFinalizacion.encode())

	def obtenerPuertosDisponibles(self):
		puertosUSB = glob.glob('/dev/ttyUSB*')
		puertosACM = glob.glob('/dev/ttyACM*')
		return puertosUSB + puertosACM

	def establecerPuerto(nombreDePuerto):
		if nombreDePuerto in self.obtenerPuertosDisponibles():
			self.miNombrePuerto = nombreDePuerto
		else:
			pass

	def recibirInformacion(self):
		self.iniciarTransmision()
		self.miTareaParalela = threading.Thread(target=self.recepcionParalela, args=("task",))
		self.miTareaParalela.start()
		
	def recepcionParalela(self,argumentoOpcional = ''):
		miInformacion = []
		self.miTareaParalela = threading.currentThread()
		while getattr(self.miTareaParalela, "do_run", True):
			miInformacion.append(self.recibirFrameCompleto())
		#print('finalizando adentro')
		self.__finalizarRecepcionDeInformacion(miInformacion)

	def __finalizarRecepcionDeInformacion(self,informacionRecibidaAGuardar):
		self.finalizarTransmision()
		#self.convertirACSV(informacionRecibidaAGuardar,'datos Recibidos')

	def exportarDatosACSV(self):
		self.convertirACSV(self.miListaInformacion,self.informacionIngresada[0])

	def detenerInformacion(self):
		#print('finalizando con comando')
		self.miTareaParalela.do_run = False
		self.miTareaParalela.join()

	def actualizarDatos(self):
		self.centralizarInformacion()
		self.generarListas()
		#print('Genere despues paso:',)
		return (self.tiempo,self.voltaje,self.corriente,self.temperatura,self.rpm)

	def obtenerUltimosDatos(self):
		return (self.tiempo,self.voltaje,self.corriente,self.temperatura,self.rpm)

	def recibirFrameCompleto(self):
		estado = 0
		""" 
			estado = 0, iniciando
			estado = 1, en medio de recepcion frame
			estado = -1 fuera de frame
		"""
		miInformacion = ''
		tiempoAuxiliar = time.time()
		while (estado>=0):
			caracterActual = self.miPuerto.read(1).decode('utf-8')
			if caracterActual == self.limitesParaMensaje[0]:
				tiempoAuxiliar = time.time()
				estado = 1
			if estado == 1:
				miInformacion+=caracterActual
			if caracterActual == self.limitesParaMensaje[1]:
				estado = -1
			if (time.time()-tiempoAuxiliar>self.timeout):
				print('Se sobrepaso el tiempo maximo de espera')
				break
		miInformacion = miInformacion[1:-1]
		miInformacionIntermedia = miInformacion.split(',')
		miDiccionario = {'Tiempo':time.time()}
		for data in miInformacionIntermedia:
			if data[0]=='v':
				miDiccionario['Voltaje'] = float(data[1:])
			if data[0]=='i':
				miDiccionario['Corriente'] = float(data[1:])
			if data[0]=='t':
				miDiccionario['Temperatura'] = float(data[1:])
			if data[0]=='r':
				miDiccionario['RPM'] = float(data[1:])
		self.miFila.put(miDiccionario)
		return miDiccionario

	def convertirACSV(self,miInformacion,name):
		nombreStandar = name.replace(' ','_')+'.csv'
		with open(nombreStandar, 'w', newline='') as csvfile:
			#escritor = csv.writer(csvfile, delimiter=';',quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for informa in self.informacionIngresada:
				csvfile.write("#"+informa+"\n")
			fieldnames = ['Tiempo','Voltaje','Corriente','Temperatura','RPM']
			writer = csv.DictWriter(csvfile, delimiter=';',quotechar='|',fieldnames=fieldnames)
			writer.writeheader()
			for info in miInformacion:
			#	escritor.writerow(['Spam'] * 5 + ['Baked Beans'])
				writer.writerow(info)

	def actualizarCampos(self,campos):
		self.informacionIngresada = campos
		#print('Actualizado campos a ',self.informacionIngresada)
		tenemosInformacionParaExportar = False
		# Si hay informacion valiosa se retorna true
		if len(self.miListaInformacion)>1:
			tenemosInformacionParaExportar = True
		else:
			tenemosInformacionParaExportar = False
		return tenemosInformacionParaExportar

	def centralizarInformacion(self):
		contadorDeActualizacion = 0
		while self.miFila.qsize()>0:
			self.miListaInformacion.append(self.miFila.get())
			contadorDeActualizacion += 1
		#print('En un paso di: ',contadorDeActualizacion)
	
	def generarListas(self):
		estado = -1
		self.tiempo = []
		self.voltaje = []
		self.corriente = []
		self.temperatura = []
		self.rpm = []
		for info in self.miListaInformacion:
			self.tiempo.append(info['Tiempo'])
			self.voltaje.append(info['Voltaje'])
			self.corriente.append(info['Corriente'])
			self.temperatura.append(info['Temperatura'])
			self.rpm.append(info['RPM'])
		## Aqui borraba
		longitudt = len(self.tiempo)
		longitudV = len(self.voltaje)
		longitudC = len(self.corriente)
		longitudT = len(self.temperatura)
		longitudR = len(self.rpm)
		if (longitudt == longitudV)&(longitudV == longitudC)&(longitudC == longitudT)&(longitudT == longitudR)&(longitudR == longitudt):
			estado = longitudt
		else:
			estado = -1
		return estado

	def cerrarTarjeta(self):
		self.miPuerto.close()

	def obtenerDatosDeCSV(self,fileName,columna):
		pass

if __name__ == '__main__':
	misDiccionariosDePrueva = []
	misDiccionariosDePrueva.append({'Voltaje':220,'Corriente':230,'Temperatura':81,'RPM':1600})
	misDiccionariosDePrueva.append({'Voltaje':221,'Corriente':231,'Temperatura':82,'RPM':1500})
	misDiccionariosDePrueva.append({'Voltaje':222,'Corriente':232,'Temperatura':83,'RPM':1400})
	misDiccionariosDePrueva.append({'Voltaje':223,'Corriente':233,'Temperatura':84,'RPM':1300})
	misDiccionariosDePrueva.append({'Voltaje':224,'Corriente':234,'Temperatura':85,'RPM':1200})
	miFilaExterna = Queue()
	miData = TarjetaAdquisicion(miFilaExterna)
	time.sleep(2)
	print(miData.obtenerPuertosDisponibles())
	
	miData.recibirInformacion()
	tiempo = time.time()
	while True:
		print('En fila: ',miFilaExterna.qsize())
		miData.centralizarInformacion()
		print('En lista: ',len(miData.miListaInformacion))
		time.sleep(0.2)
		if (time.time()-tiempo)>6:
			break
	miData.detenerInformacion()
	miData.cerrarTarjeta()

	nombre = 'motor 00'
	miData.convertirACSV(misDiccionariosDePrueva,nombre)
	
