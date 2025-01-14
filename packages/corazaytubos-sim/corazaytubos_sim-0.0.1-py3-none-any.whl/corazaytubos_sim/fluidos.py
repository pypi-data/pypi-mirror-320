import pandas as pd
import math
from thermo.chemical import Chemical 
from tabulate import tabulate

fluidos =['methane', 'ethane', 'propane', 'butane', 'isopentane', 
                 'hexane', 'heptane', 'octane', 'nonane', 'decane']



def  fluidos_db():
    """
    Muestra la lista de fluidos disponibles dentro del simulador
    No requiere de ningún parametro
    """
    print("Lista de fluidos de hidrocarburos disponible: \n")
    for i, fluido in enumerate (fluidos, 1):
        print(f"{i}.- {fluido}")



def propiedades_fluidos():
    """
    La función mostrará una tabla de la lista de fluidos con las siguientes propiedades termodinamicas e información:
    Formula del fluido, Peso Molecular (PM), Terperatura critica (Tc en Kelvin), Presión critica (Pc en Pascales)

    No requiere de parametros de entrada
    """
    prop_fluidos = []
    for prop in fluidos:
        chemical = Chemical(prop)
        prop_fluidos.append({
            "Fluido_Nombre": prop.title(),
            "Formula": chemical.formula,
            "Tc (K)": chemical.Tc,
            "Pc (Pa)": chemical.Pc,
            "PM (g/mol)":chemical.MW
        })
    df=pd.DataFrame(prop_fluidos)
    print("Las propiedades de los fludios son las siguientes: \n")
    print(df)



def elegir_fluido():
    """
    Muestra la lista de fludios disponibles
    Ingresar dos número de acuerdo al dinice de la lista
    """

    #print("Lista de fluidos de hidrocarburos disponible: \n")
    #for i, fluido in enumerate (fluidos, 1):
    #    print(f"{i+1}.- {fluido}")
    fluidos_db()
    try:
        seleccion1 = int(input("Selecciona el número del primer fluido (se tomorá esta selección como el fluido frio): \n"))-1
        seleccion2 = int(input("Selecciona el número del segúndo fluido: (se tomará esta selección como el fluido caliente): \n"))-1

        #verificar que las selecciones sean validas
        if seleccion1 not in range(len(fluidos)) or seleccion2 not in range(len(fluidos)):
            print("Selección inválida. Inténtalo de nuevo.\n")
            return elegir_fluido()  # Llamar de nuevo a la función si la selección no es válida
        if seleccion1 == seleccion2:
            print("Por favor, selecciona dos fluidos diferentes. \n")
            return elegir_fluido()
        
        fluido1 = fluidos[seleccion1]
        fluido2 = fluidos[seleccion2]
        print(f"Has seleccionado: {fluido1} como fluido frio y {fluido2} como fluido caliente \n")

        return fluido1, fluido2
    except ValueError:
        print("Entrada inválida. Por favor, ingresa un número.\n")
        return elegir_fluido()  # Llamar de nuevo a la función si ocurre un error de tipo




def temperaturas_operacion():
    """
    función para ingresar las temperaturas de operación (entrada y salida) de los fluidos. 
    Se ingresan en grados Fahrenheit y la función los transforma a grados Celcius para el calculo de propiedades"
    """
    fluidosSelec = elegir_fluido()
    tabla_temp = []
    temp1_ff = float(input(f"Indica la temperatura de entrada de {fluidosSelec[0]} en grados Fahrenheit: \n"))
    temp1_ffcelcius = float((temp1_ff-32)/1.8)
    temp1_ffkelvin = temp1_ffcelcius+273.15
    temp2_ff = float(input(f"Indica la temperatura de salida de {fluidosSelec[0]}: en grados Fahrenheit \n"))
    temp2_ffcelcius = float((temp2_ff-32)/1.8) 
    temp2_ffkelvin = temp2_ffcelcius+273.15
    tabla_temp.append(
        {
            "fluido":fluidosSelec[0],
            "temperatura entrada (°F)":temp1_ff,
            "temperautra salida (°F)":temp2_ff
        }
    )
    temp1_fc = float(input(f"Indica la temperatura de entrada de {fluidosSelec[1]}: en grados Fahrenheit \n"))
    temp1_fccelcius = float((temp1_fc-32)/1.8)
    temp1_fckelvin = temp1_fccelcius+273.15
    temp2_fc = float(input(f"Indica la temperatura de salida de {fluidosSelec[1]}: en grados Fahrenheit \n"))
    temp2_fccelcius = float((temp2_fc-32)/1.8)
    temp2_fckelvin = temp2_fccelcius+273.15
    tabla_temp.append(
        {
            "fluido":fluidosSelec[1],
            "temperatura entrada (°F)":temp1_fc,
            "temperautra salida (°F)":temp2_fc
        }
    )
    temperaturas_df = pd.DataFrame(tabla_temp)
    print("las temperaturas son las siguientes: \n")
    
    print(f"{tabulate(temperaturas_df, headers=temperaturas_df.columns.values,tablefmt='grid' )} \n")    

    return temperaturas_df

def propiedades_fluidos():
    lista_fluidos_seleccionados = temperaturas_operacion()
    detalles=[]
    for _, compuesto in lista_fluidos_seleccionados.iterrows():
        compuesto_nombre= compuesto["fluido"]
        temp_entradacelcius = (compuesto["temperatura entrada (°F)"]-32)/1.8
        temp_salidacelcius = (compuesto["temperautra salida (°F)"]-32)/1.8
        temp_promedio = (temp_entradacelcius+temp_salidacelcius)/2
        temp_promediokelvin = temp_promedio+273.15

        #estimar las propiedades termodinamicas (viscosidad, conductividad eléctrica y calor especifico) a la temperatura promedio aritmetica de cada fluido
        compuesto_calculo = Chemical(compuesto_nombre,T=temp_promediokelvin)
        viscosidad = compuesto_calculo.mu
        calor_especifico = compuesto_calculo.Cp
        conductividad_termica = compuesto_calculo.k
        

def calculate_mldt_contracorriente():
    """
    dertermina la temperatura media logaritmica para un intercamabiador de calor con una configuración a contracorriente
    requiere de dos parametros
    fluido uno y fluido
    """
    fluidosSelec = elegir_fluido()
    try:
        temp_ff1 = float(input(f"Indica la temperatura de entrada del fluido frio {fluidosSelec[0]}: "))
        temp_ff2 = float(input(f"Indica la temperatura de salida del fluido frio {fluidosSelec[0]}: "))
        temp_fc1 = float(input(f"Indica la temperatura de entrada del fluido caliente {fluidosSelec[1]}: "))
        temp_fc2 = float(input(f"Indica la temperatura de salida del fluido caliente {fluidosSelec[1]}: "))
        if temp_ff2>temp_fc2:
            print("Esto no es posible, la temperatura de salida del fluido frio no puede ser superior a la temperatura de salida del fluido caliente. Por vaor intentalo de nuevo\n")
            return calculate_mldt_contracorriente()
        u_t1 = temp_ff1
        u_t2 = temp_ff2
        u_T1 = temp_fc1
        u_T2 = temp_fc2
        try:
            delta_T1 = u_T2-u_t1
            delta_T2 =  u_T1-u_t2
            mldt = (delta_T2-delta_T1)/math.log(delta_T2/delta_T1)
            print(f"La temperatura media logaritmica es {mldt} °F")
        except ValueError:
            print("Error: las diferencias de temperatura deben ser positivas.\n")
            return calculate_mldt_contracorriente()
        mldtValue = mldt
        print(f"La temperatura media logaritmica es {mldtValue} °F")
        return mldtValue 
    except ValueError:
        print("Entrada inválida. Por favor, ingresa un número.\n")
        return calculate_mldt_contracorriente()


propiedades_fluidos()
 



