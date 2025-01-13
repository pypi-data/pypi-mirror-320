import numpy as np
import pandas as pd
from scipy.stats import kstest
import sys
import time
from IPython.display import display

class DataAnalisis():
    def __init__(self, ruta):
        self.ruta = ruta
        self.media = []
        self.mediana = []
        self.moda = []
        self.borrar = []
        self.bfil = []
        self.dataset=0
        self.var1=0.3
        self.var2=0.05
    def info():
        print('Estos son tus pasos a seguir para hacer tu limpieza de dataset:\n\n')
        time.sleep(1)
        print('1. Introduce tu ruta en la clase. --> ex:  Variable = libreria.DataAnalisis(ruta)\n\n')
        print('2. Lee tus datos con pandas')
        print('   - CSV: usa la función Variable.csv()')
        print('   - Excel: usa la función Variable.excel()\n')
        time.sleep(2)
        print('3. Inicia la limpieza del dataset usando el método Variable.analizar()\n')
        time.sleep(1)
        print('4. Para visualizar el dataframe usa la funcion Variable.visualizar()')
        time.sleep(1)
        print('5. Para guardar el dataframe usa Variable.guardar()')
    def limpieza(self):
        for i in self.borrar:
            self.dataset.drop(i,inplace=True, axis=1)
        for i in self.media:
            self.dataset[i].fillna(self.dataset[i].mean(), inplace=True)
        for i in self.moda:
            self.dataset[i].fillna(self.dataset[i].mode().iloc[0], inplace=True)
        for i in self.mediana:
            self.dataset[i].fillna(self.dataset[i].median(), inplace=True)
        for i in self.bfil:
            self.dataset[i].fillna(self.dataset[i].bfill(), inplace=True)
            self.dataset[i].fillna(self.dataset[i].ffill(), inplace=True)
            self.dataset[i].fillna(self.dataset[i].mode().iloc[0], inplace=True)
        print('La limpieza se ha realizado correctamente\n\n')    
    def excel(self):
        try:
            self.dataset = pd.read_excel(self.ruta)
            print("El archivo se ha cargado correctamente.")
        except FileNotFoundError:
            print(f"Error: El archivo con la ruta '{self.ruta}' no se ha encontrado.")
            sys.exit()
        except Exception as e:
            print("Error inesperado")
            sys.exit()
    def personalizado(self):
        self.media = []
        self.mediana = []
        self.moda = []
        self.borrar = []
        self.bfil = []
        for i in self.dataset.columns:
            porcentaje=(self.dataset[i].isna().mean())
            if self.dataset[i].dtype == 'int64' or self.dataset[i].dtype == 'float64':
                stat, p_value = kstest(self.dataset[i], 'norm', args=(self.dataset[i].mean(), self.dataset[i].std())) 
                if p_value > self.var2: 
                    if np.abs(self.dataset[i].skew())>1:
                        print(f'\nLa columna {i} es numérica y tine una distribución sesgada y un porcentaje de datos' 
                        f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                        
                    else:
                        print(f'\nLa columna {i} es numérica y tine una distribución normal y un porcentaje de datos' 
                        f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                    
                else:
                    print(f'\nLa columna {i} es numérica y tine no distribución normal ni sesgada, tiene un porcentaje de datos' 
                            f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                respuesta=input('0:Borrarla\n1:Moda\n2:Mediana\n3:Media\n4:Rellenarlo con los de alrededor\n' )
                if int(respuesta)not in [0,1,2,3,4]:
                    print('La respuesta no es posible. Responda una respuesta correcta.')
                    respuesta=input('0:Borrarla\n1:Moda\n2:Mediana\n3:Media\n4:Rellenarlo con los de alrededor\n' )
                if int(respuesta)==0:
                    self.borrar.append(i)
                elif int(respuesta)==1:
                    self.moda.append(i)
                elif int(respuesta)==2:
                    self.mediana.append(i)
                elif int(respuesta)==3:
                    self.media.append(i)
                elif int(respuesta)==4:
                    self.bfil.append(i)
                else:
                    sys.exit("ERROR: Respuesta no posible")
                    
            else:
                print(f'\nLa columna {i} es categórica y tiene un porcentaje de datos' 
                        f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                respuesta=input('0:Borrarla\n1:Moda\n2:Rellenarlo con los de alrededor\n' )
                if int(respuesta)!=0 and int(respuesta)!=1 and int(respuesta)!=2:
                    print('La respuesta no es posible. Responda una respuesta correcta.')
                    respuesta=input('0:Borrarla\n1:Moda\n2:Rellenarlo con los de alrededor\n' )
                if int(respuesta)==0:
                    self.borrar.append(i)
                elif int(respuesta)==1:
                    self.moda.append(i)
                elif int(respuesta)==2:
                    self.bfil.append(i)
                else:
                    sys.exit("ERROR: Respuesta no posible")
        print('Iniciando limpieza...\n')
        self.limpieza()

    def csv(self):
        try:
            self.dataset = pd.read_csv(self.ruta)
            print("El archivo se ha cargado correctamente.")
        except FileNotFoundError:
            print(f"Error: El archivo con la ruta '{self.ruta}' no se ha encontrado.")
            sys.exit()
        except Exception as e:
            print("Error inesperado")
            sys.exit()
            
    def analizar(self):
        try:
            with open('valores.txt', 'r') as file:
                for linea in file:
                    palabras = linea.split(',')
                    try:
                        self.var1=float(palabras[0])
                        self.var1=float(palabras[1])
                    except ValueError:
                        pass
        except FileNotFoundError:
            pass
        self.dataset=pd.DataFrame(self.dataset)
        for i in self.dataset.columns:
            if ((self.dataset[i].isna().mean()))>self.var1:
                self.borrar.append(i)
            elif self.dataset[i].dtype == 'int64' or self.dataset[i].dtype == 'float64':
                stat, p_value = kstest(self.dataset[i], 'norm', args=(self.dataset[i].mean(), self.dataset[i].std())) 
                if p_value > self.var2: 
                    if np.abs(self.dataset[i].skew())>1:
                        self.mediana.append(i)
                    else:
                        self.media.append(i)
                else:
                    self.bfil.append(i)
                
            else:
                self.moda.append(i)
        print('Tu DataFrame ha sido analizado y se recomienda hacer la siguiente imputación:\n')
        if self.borrar:
            print(f'Borrar las columnas {self.media}\n')
        if self.media:
            print(f'Rellenas las columnas {self.media} con la media\n')
        if self.mediana:
            print(f'Rellenas las columnas {self.mediana} con la mediana\n')
        if self.bfil:
            print(f'Rellenas las columnas {self.bfil} con los datos de alrededor\n')
        if self.moda:
            print(f'Rellenas las columnas {self.moda} con la moda\n')
        respuesta=input('Si desea seguir las recomendaciones escriba -->si<--, si NO desea seguir las recomendaciones escriba -->no<--\n')
        if respuesta=='si':
            print('Iniciando limpieza recomendada...\n')  
            self.limpieza()
        elif respuesta=='no':
            print('Iniciando limpieza personalizada...\n')
            self.personalizado()
        else:
            print('ERROR: respuesta incorrecta\n\n')
    def visualizar(self):
        if isinstance(self.dataset, pd.DataFrame):
            display(self.dataset)
        else:
            print('No se ha cargado el dataset')
    def guardar(self):
        try:
            self.dataset.to_csv(self.ruta)
            print('Se ha guardado correctamente.')
        except Exception as e:
            print('Ha habido un error: %s',e)



    

   
