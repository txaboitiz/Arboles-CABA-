#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 10:47:12 2020

@author: txominaboitiz
"""

# arbolado_parques_veredas.py (modif)

#%%

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import unicodedata


# Encontre esta funcion en https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
def strip_accents(s):
   '''
    Elimina las tildes de un string
    '''
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def estandarizar_sp(s):
    '''
    Estandariza el formato del nombre cientifico de una especie

    Parameters
    ----------
    s : str
        El nombre cientifico (no importan las mayusculas, ni tampoco si tiene tildes)

    Returns
    -------
    sp_norm : str
        Nombre cientifico en formato estandar (Genero sp), sin tildes.

    '''
    sp = strip_accents(s)
    sp_norm = sp.capitalize()
    return sp_norm

def generar_dict_df():
    '''
    Lee los archivos de parques y veredas y genera un diccionario con los
        dataframes extraidos de cada archivo

    Returns
    -------
    dict_df : dict
        Contiene los dataframse de parques y veredas:
            dict_df['parques'] = df_parques
            dict_df['veredas'] = df_veredas
        

    '''
    # Seteo el directorio y nombres de archivos
    directorio = 'Data'
    archivo_parques = 'arbolado-en-espacios-verdes.csv'
    archivo_veredas = 'arbolado-publico-lineal-2017-2018.csv'
    # Genero los dataframes y el diccionario
    df_parques = pd.read_csv(os.path.join(directorio, archivo_parques))
    df_veredas = pd.read_csv(os.path.join(directorio, archivo_veredas))
    dict_df = {
        'parques': df_parques,
        'veredas': df_veredas
        }
                             
    return dict_df

def df_sp_col(dict_df, sp, dict_cols, ambiente):
    '''
    Genera un dataframe secundario a partir de uno original,
        filtrando por especie y por columna.

    Parameters
    ----------
    dict_df : dict
        Diccionario que contiene a los dataframes de parques y veredas
    sp : str
        Nombre de la especie, tal cual figura en el dataframe que se 
            quiere utilizar
    dict_cols: dict
        Diccionario que contiene las listas de columnas para cada ambiente.
    ambiente : str
        Ambiente ('parques' o 'veredas') que se quiere seleccionar. 
            Este parametro sera la clave utilizada para seleccionar 
            el dataframe deseado dentro de dict_df, y las columnas 
            dentro de dict_cols

    Raises
    ------
    Exception
        Si ambiente != 'parques' y ambiente != 'veredas', la funcion 
        se corta porque esas son las unicas opciones validas.

    Returns
    -------
    df_sp_col : dataframe
        Dataframe filtrado de acuerdo a los parametros ingresados

    '''
    if ambiente not in ['parques', 'veredas']:
        raise Exception('Valor del parametro ambiente no es valido.\n ambiente = "parques" o ambiente = "veredas"')
    if ambiente == 'parques':
        nombre = 'nombre_cie'
    elif ambiente == 'veredas':
        nombre = 'nombre_cientifico'
    # Selecciono el df y las columnas a utilizar, en funcion del ambiente
    df = dict_df[ambiente]
    cols = dict_cols[ambiente]
    # Genera un dataframe a partir de la condicion de que el nombre cientifico estandarizado
    #   sea igual a sp. Filtra por lista col_ambiente
    df_sp_col = df[df[nombre].map(lambda x: estandarizar_sp(x)) == sp][cols].copy()
    return df_sp_col
        
def renombrar_columnas(df, dict_cols, ambiente):
    '''
    Renombra un conjunto columnas seleccionadas dentro de un dataframe

    Parameters
    ----------
    df : dataframe
        DF donde se renombraran las columnas
    dict_cols: dict
        Contiene las listas de columnas de los dos ambientes y tambien
            la lista de nombres nuevos de las columnas
        IMPORTANTE: El orden respectivo de las variables en cada lista debe
            ser el mismo. De lo contrario, al renombrar las columnas se 
            mezclaran las variables.
    ambiente: str
        Ambiente correspondiente al df que se quiere modificar ('parques' o 'veredas')
        
    Raises
    ------
    Exception
        Si ambiente != 'parques' y ambiente != 'veredas', se corta 
            porque esas son las unicas dos claves que se pueden usar para
            buscar las columnas en su respectivo df.
    Exception
        Si len(col_originales) != len(col_nuevas) se presentaria un error 
            por uno de los siguientes motivos:
                - Faltan nombres de columnas en una de las dos listas
                - Una de las dos listas tiene nombres de mas
        
    Returns
    -------
    df_modif : dataframe
        DF con los nombres de columnas actualizados

    '''
    if ambiente not in ['parques', 'veredas']:
        raise Exception('Valor del parametro ambiente no es valido. \n ambiente = "parques" o ambiente = "veredas"')
    col_originales = dict_cols[ambiente]
    col_nuevas = dict_cols['nuevas']
    if len(col_originales) != len(col_nuevas):
        raise Exception('Las listas col_originales y col_nuevas deben tener la misma longitud')
    num_col = len(col_originales)
    # diccionario con columnas originales como clave y columnas nuevas como valor        
    columnas = {col_originales[i]: col_nuevas[i] for i in range(num_col)}
    df_modif = df.rename(columns = columnas)
    return df_modif

def agregar_col_ambiente(df, ambiente):
    '''
    Agrega la columna "ambiente" a un df, todas las filas tendran el mismo valor
    (especificado por el parametro "ambiente")

    Parameters
    ----------
    df : dataframe
        DF al cual se le quiere agregar la columna
    ambiente : str
        Tipo de ambiente

    Returns
    -------
    None.

    '''
    df['ambiente'] = [ambiente for i in df.index]
    return

def unificar_datos(dict_df, sp):
    '''
    Unifica los datos de una especie particular, provenientes de dos
        dataframes distintos (parques y veredas).
        Selecciona las columnas deseadas, unifica los nombres de las
        columnas, y agrega la columna "ambiente" con el ambiente 
        correspondiente

    Parameters
    ----------
    dict_df : dict
        Diccionario que contiene a los dataframes de parques y veredas
    sp : str
        Nombre cientifico de la especie en formato estandar (Genero sp)
        
    Raises
    ------
    Exception
        Salta error si no se encuentran datos para sp en por lo menos uno
            de los dataframes (parques y veredas). En tal caso, aclara
            en que tabla no se encontraron datos.

    Returns
    -------
    df_sp : dataframe
        DF unificado

    ''' 
    # Genero las listas de nombres de columnas para ingresar en las funciones.
    #   Cada lista tiene que tener el mismo orden respectivo de variables, para
    #   unificar adecuadamente los nombres
    # Al juntar las listas en un diccionario, las puedo pasar como 
    #   un unico parametro en las funciones, y elijo que lista usar especificando
    #   el ambiente como parametro adicional
    dict_cols = {
        'parques': ['altura_tot', 'diametro'],
        'veredas': ['altura_arbol', 'diametro_altura_pecho'],
        'nuevas': ['altura', 'diametro']
        }
    
    # Genero los df de cada ambiente para la tipa
    df_sp_parques = df_sp_col(dict_df, sp, dict_cols, ambiente = 'parques')
    df_sp_veredas = df_sp_col(dict_df, sp, dict_cols, ambiente = 'veredas')
    
    # Cortar la funcion si sp no esta en alguna de las dos tablas
    if df_sp_parques.empty and df_sp_veredas.empty:
        raise Exception(f'No se encontraron datos para {sp} en ninguna de las dos tablas')
    elif df_sp_parques.empty:
        raise Exception(f'No se encontraron datos para {sp} en la tabla de parques')
    elif df_sp_veredas.empty:
        raise Exception(f'No se encontraron datos para {sp} en la tabla de veredas')
        
    # Renombro las columnas de los df para que sean consistentes
    df_sp_parques = renombrar_columnas(df_sp_parques, dict_cols, ambiente = 'parques')
    df_sp_veredas = renombrar_columnas(df_sp_veredas, dict_cols, ambiente = 'veredas')
     
    # Agrego la columna de ambientes a cada tabla, con ambiente especifico
    agregar_col_ambiente(df_sp_parques, 'parque')
    agregar_col_ambiente(df_sp_veredas, 'vereda') 
    
    # Junto
    df_sp = pd.concat([df_sp_parques, df_sp_veredas])
    return df_sp

def plot_box(df_sp, sp):
    '''
    Genera una figura con dos sub-boxplots a partir del dataframe unificado de
        una especie:
            - Diametro vs ambiente
            - Altura vs ambiente

    Parameters
    ----------
    df_sp : dataframe
        Dataframe unificado de una especie
    sp : str
        Nombre de la especie en formato estandar (Genero sp). Este str se 
            utilizara para identificar la especie en el titulo del grafico

    Returns
    -------
    None.

    '''
    # Formatea el nombre de la especie para que se imprima adecuadamente en italica
    #   (el string debe tener formato "palabra1\ palabra2\ ...\ palabran")
    sp_italics = sp.split().copy()
    sp_italics = '\ '.join(sp_italics)
    
    # Boxplot
    plt.figure(figsize = (11,7))
    titulo = f'Comparaciones de variables morfológicas entre distintos ambientes en ${sp_italics}$'
    plt.suptitle(titulo, fontsize = 14)
    plt.subplot(1,2,1)
    sns.boxplot(x = 'ambiente', y = 'diametro', data = df_sp)
    plt.title('Diámetro vs ambiente')
    plt.ylabel('Diámetro (cm)')
    plt.xlabel('Ambiente')
    plt.subplot(1,2,2)
    sns.boxplot(x = 'ambiente', y = 'altura', data = df_sp)
    plt.title('Altura vs ambiente')
    plt.ylabel('Altura (m)')
    plt.xlabel('Ambiente')
    plt.show()
    return


def main():
    verif = str(input('Si quiere graficar los datos de Tipuana tipu, ingrese "y".\n Si quiere graficar para otra especie, ingrese "n": '))
    if verif not in 'yn':
        error = 'ERROR: \nLa opcion ingresada es invalida. Intente de nuevo'
        print('-' * len(error))
        print('ERROR:\nLa opcion ingresada es invalida. Intente de nuevo')
        main()
    elif verif == 'y':
        sp = 'Tipuana tipu'
    else:
        nombre = str(input('Ingrese el nombre cientifico de la especie: '))
        # Estandariza el nombre de especie ingresado, para aumentar flexibilidad de uso
        sp = estandarizar_sp(nombre)
    # Genero diccionario con los dos dataframes (parques y veredas). De esta manera,
    #   van juntos a todos lados.
    dict_df = generar_dict_df()
    df_sp = unificar_datos(dict_df, sp)
    plot_box(df_sp, sp)
    return

#%%

if __name__ == '__main__':
    main()



