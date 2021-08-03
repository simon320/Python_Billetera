import pickle
import requests
import sys
import time
from requests.models import CaseInsensitiveDict


# CONFIGURACION DE FUNCIONES DE SERIALIZACION PARA BILLETERA E HISTORIAL
def escribe_archivo(): # Sobre-escribe billetera
    global cripto_dic
    archivo_serial = open("serial-billetera", "wb")
    pickle.dump(cripto_dic, archivo_serial)
    archivo_serial.close()
    del archivo_serial

def recupera_archivo():# Lee archivo de la billetera
    global cripto_dic
    archivo_serial2 = open("serial-billetera", "rb")
    cripto_dic = pickle.load(archivo_serial2)

def escribe_archivo2(): # Sobre-escribe historial
    global lista_historial
    archivo_serial = open("serial-historial", "wb")
    pickle.dump(lista_historial, archivo_serial)
    archivo_serial.close()
    del archivo_serial

def recupera_archivo2(): # Lee archivo del historial
    global lista_historial
    archivo_serial2 = open("serial-historial", "rb")
    lista_historial = pickle.load(archivo_serial2)

# CREANDO VARIABLES
cripto_dic = {} # Diccionario donde se cargaran las criptomonedas en billetera

lista_historial = [] # Lista donde se cargan las transacciones

movimiento = "" # Variable global para escribirmovimiento

codigo_dic = {'enviador' : 'eXYZ1243', 'destinatario' : 'dWER4532'} # Codigos para transacciones

cod = ""

opciones_menu =  (
    "Recibir cantidad", 
    "Transferir monto", 
    "Mostrar balance de una moneda", 
    "Mostrar balance general", 
    "Mostrar histórico de transacciones", 
    "Salir del programa"
)

# CREANDO COTIZADOR DE MONEDA
_ENDPOINT = "https://api.binance.com"
def _url(api):
    return _ENDPOINT + api

def get_price(criptomoneda):
    return requests.get(_url("/api/v3/ticker/price?symbol=" + criptomoneda))



# CREANDO LISTAS DE MONEDAS VALIDAS SEGUN "coinmarket"
monedas_lista=[]

COINMARKET_API_KEY = "5c9d25a1-b890-4060-9ef3-5f84a3788192"
headers = {'Accepts': 'application/json','X-CMC_PRO_API_KEY': COINMARKET_API_KEY}
data = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",headers=headers).json()

for cripto in data["data"]:
    monedas_lista.append(cripto["symbol"])



# CONFIGURANDO MENU DE OPCIONES
def menu_inicial():
    while True:
        print("""
        ¿Que deseas hacer?

        1. Recibir cantidad.
        2. Transferir monto.
        3. Mostrar balance de una moneda.
        4. Mostrar balance general.
        5. Mostrar histórico de transacciones.
        6. Salir del programa.""")
        
        # VALIDANDO OPCION
        opcion = input("\nElige una opcion: ")
        while not opcion.replace('.','',1).isdigit():
            print("Opcion incorrecta.")
            opcion = input("Por favor, ingrese un numero de opcion disponible: ")
        opcion = int(opcion)
        
        if opcion == 1:
            print("\n" + opciones_menu[0])
            recibir()
        elif opcion == 2:
            print("\n" + opciones_menu[1])
            transferencia()
        elif opcion == 3:
            print("\n" + opciones_menu[2])
            cotizacion()
        elif opcion == 4:
            print("\n" + opciones_menu[3])
            cotizacion_general()
        elif opcion == 5:
            print("\n" + opciones_menu[4])
            historial()
        elif opcion == 6:
            escribe_archivo()
            escribe_archivo2()
            print("\nGuardando movimientos...")
            time.sleep(1)
            print("\nFin del programa.\n")
            sys.exit()   


# CONFIGURANDO VALIDACION E INGRESO DE LA MONEDA
def es_moneda(cripto): # Valida que la moneda exista en "coinmarket"
        return cripto in monedas_lista
      
def ingresando_moneda(): # Ingresa y valida moneda
    global moneda
    moneda = input("Ingrese el nombre de la moneda: ")
    while not es_moneda(moneda):
            print("Moneda Invalida.")
            moneda=input("Por favor, ingrese un nombre correcto de moneda: ")
    else:
        print("\nEligio " + moneda + ".")


# CONFIGURANDO VALIDACION NUMERICA
def es_numero(): # Valida que sea una cantidad real
    global cantidad
    cantidad = input("Ingrese el monto: ")
    while not cantidad.replace('.','',1).isdigit():
        print("Monto incorrecto.")
        cantidad = input("Por favor, indique una cantidad real: ")

    cantidad = float(cantidad)
                       

# CONFIGURANDO VALIDACION DE CODIGO ENVIADOR Y DESTINATARIO
def es_codigo_destinatario(): # DESTINATARIO
    codigo = input("Ingrese el codigo del destinatario: ")
    while not codigo == codigo_dic['destinatario']:
        print("Codigo incorrecto.")
        codigo = input("Por favor, ingrese el codigo correcto del destinatario: ")


def es_codigo_enviador(): # ENVIADOR
    codigo = input("Ingrese el codigo del enviador: ")
    while not codigo == codigo_dic['enviador']:
        print("Codigo incorrecto.")
        codigo = input("Por favor, ingrese el codigo correcto del enviador: ")


# CONFIGURANDO ACTUALIZACION DEL MONTO DE LA MONEDA SI ES QUE SE TIENE EN BILLETERA, SI NO LA AGREGA
def incrementa_moneda(): # Crea o incrementa el monto
        if moneda in cripto_dic:
            cantidad_actual = cripto_dic.get(moneda) 
            cripto_dic[moneda] = cantidad_actual + cantidad
        else:
            cripto_dic[moneda] = cantidad
        print(cripto_dic)

def reduce_moneda(): # Reduce el monto
        if moneda in cripto_dic:
            cripto_dic[moneda] -= cantidad
        else:
            cripto_dic[moneda] = cantidad
        print(cripto_dic)

# Configurando registro Fecha/Movimiento
def fecha_movimiento():
    global lista_historial
    global movimiento
    global cod


    tiempo_seg = time.time()
    fecha = time.ctime(tiempo_seg)

    data = get_price(moneda + "USDT").json()
    dolares = cripto_dic.get(moneda) * float(data.get("price"))
    
    data_transaccion = f"""    Se {movimiento} la cuenta con codigo:{codigo_dic.get(cod)},
    {cantidad} {moneda} que equivale a Us${dolares}. 
    Fecha del movimiento {fecha}."""
    lista_historial.append(data_transaccion) # Agrega a la lista el nuevo movimiento registrado
    print(data_transaccion) # Refleja los cambios
    escribe_archivo2() # Carga los cambios al archivo (serial-historial)


# DEFINIENDO OPCIONES-FUNCIONES DEL PROGRAMA
# Opcion 1 Recibir Criptomoneda
def recibir(): # Funcion para recibir un monto de alguna moneda
    ingresando_moneda() # Ingresa y valida moneda
    es_numero() # Valida que sea una cantidad real
    es_codigo_enviador() # Valida codigo

    global movimiento
    global cod
    movimiento = "recibieron desde"
    cod = 'enviador'

    deposito = input(f"Se van a depocitar {cantidad} {moneda} en su cuenta.\n¿Desea continuar? (s/n): ")
    if deposito == "s": # Confirma movimiento
        incrementa_moneda() # Actualiza el monto
        escribe_archivo() # Carga los cambios al archivo (serial-billetera)
        print("\nGuardando movimientos...")
        time.sleep(2)
        print("Operacion exitosa.")
        fecha_movimiento() # Registra fecha de transaccion
        time.sleep(2)
    else:
        print("Operacion cancelada.")

# Opcion 2 Transferir Criptomoneda
def transferencia(): # Funcion para enviar un monto de alguna moneda que se tenga en billetera
    ingresando_moneda() # Ingresa y valida moneda

    if moneda in cripto_dic: # Chequea que se tenga la moneda a transferir
        es_numero() # Valida que sea una cantidad real

        cantidad_actual = cripto_dic.get(moneda)
        if cantidad_actual >= cantidad: # Valida que se cuente con la cantidad
            es_codigo_destinatario() # Valida codigo

            global movimiento
            global cod
            movimiento = "transfirieron a"
            cod = 'destinatario'

            deposito = input(f"Se van a depocitar {cantidad} {moneda} en la cuenta de destinatario escogido.\n¿Desea continuar? (s/n): ")
            if deposito == "s":# Confirma movimiento
                reduce_moneda() # Actualiza el monto

                if cripto_dic[moneda] == 0.0: # Si la moneda queda en 0 la elimina del Diccionario
                    cripto_dic.pop(moneda)

                escribe_archivo() # Carga los cambios al archivo (serial-billetera)
                print("\nGuardando movimientos...")
                time.sleep(2)
                print("Operacion exitosa.")
                fecha_movimiento() # Registra fecha de transaccion
                time.sleep(2)
            else:
                print("Operacion cancelada.")
        else:
            print(f"Uds solo posee {cantidad_actual} de {moneda}.")
            time.sleep(2)
    else:
        print(f"Uds no posee {moneda}")
        time.sleep(2)

# Opcion 3 Mostrar cotizacion de una moneda
def cotizacion():
    ingresando_moneda() # Ingresa y valida moneda
    data = get_price(moneda + "USDT").json()
    print(f"El precio de {moneda} es Us$",data["price"]) # Imprime cotizacion alctual segun "Binance"
    if moneda in cripto_dic: # Si la moneda consultada se encuentra en billetera imprime cantidad y dolares al cambio
        print("Usted cuenta con ",cripto_dic.get(moneda), " " ,moneda)
        dolares = cripto_dic.get(moneda) * float(data.get("price"))
        print(f"En dolares al cambio actual cuenta con Us${dolares}")
    else:
        print(f"Usted no posee {moneda}")
    time.sleep(2)

# Opcion 4 Mostrar cotizacion de una moneda
def cotizacion_general():
    total_dolares = 0 # Variable que aloja el total de los dolares al cambio
    moneda_en_billetera = cripto_dic.keys() # Crea una lista de las monedas actuales
    for cripto in moneda_en_billetera: # Itera sobre cada moneda e imprime moneda, cantidad y cotizacion
        print("    En",cripto,"posee",cripto_dic.get(cripto),"unidades.")
        data = get_price(cripto + "USDT").json()
        print(f"Cotizacion actual {cripto} Us$",data["price"])
        dolares = cripto_dic.get(cripto) * float(data.get("price"))
        print(f"En dolares al cambio actual cuenta con Us${dolares}\n")
        total_dolares += dolares
    print("Usted cuenta con un total de Us$",total_dolares, "en criptomonedas.")
    time.sleep(2)


# Opcion 5 Historial de transacciones
def historial():
    for transaccion in lista_historial: # Itera e imprime sobre la lista de transacciones
        print (transaccion,"\n")


# COMIENZO DEL PROGRAMA
recupera_archivo() # Carga la billetera
recupera_archivo2() # Carga el historial de transacciones

print("\nBienvenido a su billetera digital Desktop\n") # Titulo del Programa
menu_inicial()
