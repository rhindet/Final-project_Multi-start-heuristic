import math
import random
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os


def distancia(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def cargar_datos_cvrp(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        lines = f.readlines()

    dimension = None
    capacidad = None
    deposito = None
    clientes = []
    min_camiones = None
    optimoRecorrido = None

    section = None
    for line in lines:

        line = line.strip()
        if line.startswith('DIMENSION'):
            dimension = int(line.split(':')[-1].strip())
        elif line.startswith('CAPACITY'):
            capacidad = int(line.split(':')[-1].strip())
        elif line.startswith('DEPOT_SECTION'):
            section = 'DEPOT'
        elif line.startswith('NODE_COORD_SECTION'):
            section = 'COORD'
        elif line.startswith('DEMAND_SECTION'):
            section = 'DEMAND'
        elif line.startswith('EOF'):
            break
        elif section == 'COORD' and line:
            parts = list(map(int, line.split()))
            if len(parts) >= 3:
                if parts[0] == 1:  # Si es el nodo 1, asignar como depósito
                    deposito = {'id': parts[0], 'ubicacion': (parts[1], parts[2])}
                else:
                    clientes.append({'id': parts[0], 'ubicacion': (parts[1], parts[2])})
            else:
                print(f"Línea incorrecta en COORD_SECTION: {line}")
        elif section == 'DEMAND' and line:
            parts = list(map(int, line.split()))
            for cliente in clientes:
                if cliente['id'] == parts[0]:
                    cliente['demanda'] = parts[1]
                    break
        elif line.startswith('COMMENT'):
                if nombre_archivo == 'C:/Users/Admin/PycharmProjects/pythonProject9/A-n80-k10.txt':
                    minCamiones = line[44:46].strip()
                    min_camiones = int(minCamiones)
                else:
                    minCamiones = line[44]
                    min_camiones = int(minCamiones)
                try:
                    optimoToJoin = line[62:65]
                    optimo = "".join(optimoToJoin)

                    optimoRecorrido = int(optimo)
                except ValueError:
                    try:
                        optimoToJoin = line[59:63]
                        print(optimoToJoin)
                        optimo = "".join(optimoToJoin)
                        optimoRecorrido = int(optimo)
                    except:
                        optimoToJoin = line[60:64]
                        print(optimoToJoin)
                        optimo = "".join(optimoToJoin)
                        optimoRecorrido = int(optimo)

            #min_camiones = int(line.split(':')[-1].strip())

    return dimension, capacidad, deposito, clientes,min_camiones,optimoRecorrido


def cvrp_heuristica_voraz(deposito, clientes, capacidad, min_camiones):
    rutas = []
    no_asignados = clientes.copy()

    while no_asignados:
        ruta = []
        capacidad_restante = capacidad

        ruta.append(deposito['ubicacion'])  # Iniciar la ruta desde el depósito
        ultimo_cliente = deposito['ubicacion']

        while capacidad_restante > 0 and no_asignados:
            cliente_mas_cercano = None
            distancia_minima = float('inf')

            for cliente in no_asignados:
                dist = distancia(ultimo_cliente, cliente['ubicacion'])
                if dist < distancia_minima and cliente['demanda'] <= capacidad_restante:
                    distancia_minima = dist
                    cliente_mas_cercano = cliente

            if cliente_mas_cercano:
                ruta.append(cliente_mas_cercano['ubicacion'])
                capacidad_restante -= cliente_mas_cercano['demanda']
                no_asignados.remove(cliente_mas_cercano)
                ultimo_cliente = cliente_mas_cercano['ubicacion']
            else:
                break

        ruta.append(deposito['ubicacion'])  # Regresar al depósito
        rutas.append(ruta)

        # Si hemos alcanzado el número mínimo de camiones y aún quedan clientes sin asignar,
        # aseguramos que al menos se usen min_camiones distribuyendo los clientes restantes en rutas adicionales.
        if len(rutas) == min_camiones and no_asignados:
            capacidad_restante = capacidad
            while no_asignados:
                ruta = [deposito['ubicacion']]
                capacidad_restante = capacidad
                while capacidad_restante > 0 and no_asignados:
                    cliente_mas_cercano = None
                    distancia_minima = float('inf')

                    for cliente in no_asignados:
                        dist = distancia(ultimo_cliente, cliente['ubicacion'])
                        if dist < distancia_minima and cliente['demanda'] <= capacidad_restante:
                            distancia_minima = dist
                            cliente_mas_cercano = cliente

                    if cliente_mas_cercano:
                        ruta.append(cliente_mas_cercano['ubicacion'])
                        capacidad_restante -= cliente_mas_cercano['demanda']
                        no_asignados.remove(cliente_mas_cercano)
                        ultimo_cliente = cliente_mas_cercano['ubicacion']
                    else:
                        break

                ruta.append(deposito['ubicacion'])
                rutas.append(ruta)
            break

    return rutas


def calcular_distancia_total(ruta):
    distancia_total = 0
    for i in range(len(ruta) - 1):
        distancia_total += distancia(ruta[i], ruta[i + 1])
    return distancia_total


def buscar_mejora_local(rutas, deposito, clientes):
    mejorado = True
    while mejorado:
        mejorado = False
        for i in range(len(rutas) - 1):
            for j in range(i + 1, len(rutas)):
                ruta1 = rutas[i][1:-1]  # Excluir depósito de inicio y fin
                ruta2 = rutas[j][1:-1]

                mejor_ruta1 = ruta1[:]
                mejor_ruta2 = ruta2[:]
                mejor_distancia = calcular_distancia_total(rutas[i]) + calcular_distancia_total(rutas[j])

                for idx_cliente1, cliente1 in enumerate(ruta1):
                    for idx_cliente2, cliente2 in enumerate(ruta2):
                        # Intercambiar clientes entre las rutas
                        nueva_ruta1 = [deposito['ubicacion']] + [c for c in ruta1 if c != cliente1] + [cliente2,
                                                                                                       deposito[
                                                                                                           'ubicacion']]
                        nueva_ruta2 = [deposito['ubicacion']] + [c for c in ruta2 if c != cliente2] + [cliente1,
                                                                                                       deposito[
                                                                                                           'ubicacion']]
                        nueva_distancia = calcular_distancia_total(nueva_ruta1) + calcular_distancia_total(nueva_ruta2)

                        if nueva_distancia < mejor_distancia:
                            mejor_ruta1 = nueva_ruta1[1:-1]  # Excluir depósito de inicio y fin
                            mejor_ruta2 = nueva_ruta2[1:-1]
                            mejor_distancia = nueva_distancia

                if mejor_ruta1 != ruta1 or mejor_ruta2 != ruta2:
                    # Aplicar la mejor mejora encontrada
                    rutas[i] = [deposito['ubicacion']] + mejor_ruta1 + [deposito['ubicacion']]
                    rutas[j] = [deposito['ubicacion']] + mejor_ruta2 + [deposito['ubicacion']]
                    mejorado = True

    return rutas


def visualizar_rutas(rutas, deposito, clientes, min_camiones, optimoRecorrido):
    plt.figure(figsize=(14, 10))

    # Dibujar depósito
    plt.plot(deposito['ubicacion'][0], deposito['ubicacion'][1], 'ks', markersize=10, label='Depósito')

    # Dibujar clientes con etiquetas de ID y demanda
    for cliente in clientes:
        plt.plot(cliente['ubicacion'][0], cliente['ubicacion'][1], 'bo', markersize=5)
        plt.text(cliente['ubicacion'][0], cliente['ubicacion'][1], f"ID: {cliente['id']}\nDemanda: {cliente['demanda']}", fontsize=9, ha='right')

    # Dibujar rutas y calcular distancias
    colores = ['r', 'g', 'b', 'c', 'm', 'y', 'k']  # Diferentes colores para las rutas
    distancia_total = 0
    offset = 10  # Ajusta este valor para cambiar el espaciado vertical entre etiquetas
    for i, ruta in enumerate(rutas):
        ruta_x, ruta_y = zip(*ruta)
        plt.plot(ruta_x, ruta_y, color=colores[i % len(colores)], marker='o', label=f'Ruta {i + 1}')

        # Calcular y mostrar la distancia total de la ruta
        dist = calcular_distancia_total(ruta)
        distancia_total += dist
        plt.text(max(ruta_x) + 5, max(ruta_y) - i * offset, f"Ruta {i + 1}: {dist:.2f}", fontsize=12, ha='left',
                 color=colores[i % len(colores)])

    # Agregar etiquetas al lado del título
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(f'Visualización de Rutas del CVRP (Local Search)\nDistancia Total: {distancia_total:.2f}\nMin Camiones: {min_camiones}\nOptimo Recorrido: {optimoRecorrido}')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.xlim(0, max(max([c['ubicacion'][0] for c in clientes]), deposito['ubicacion'][0]) + 20)
    plt.ylim(0, max(max([c['ubicacion'][1] for c in clientes]), deposito['ubicacion'][1]) + 20)
    plt.show()

def ejecutar_cvrp_con_mejora_local(nombre_archivo):
    dimension, capacidad, deposito, clientes, minCamiones, optimoRecorrido = cargar_datos_cvrp(nombre_archivo)
    min_camiones = minCamiones  # Número mínimo de camiones

    rutas_voraz = cvrp_heuristica_voraz(deposito, clientes, capacidad, min_camiones)

    print("Rutas generadas por heurística voraz:")
    for i, ruta in enumerate(rutas_voraz):
        ruta_ids = []
        for coord in ruta:
            for cliente in clientes:
                if cliente['ubicacion'] == coord:
                    ruta_ids.append(cliente['id'])
                    break
        print(f"Ruta {i + 1}: {ruta_ids}")
    rutas_mejoradas = buscar_mejora_local(rutas_voraz, deposito, clientes)




    print("\nRutas generadas después de la mejora local:")
    for i, ruta in enumerate(rutas_mejoradas):
        ruta_ids = []
        for coord in ruta:
            for cliente in clientes:
                if cliente['ubicacion'] == coord:
                    ruta_ids.append(cliente['id'])
                    break
        print(f"Ruta {i + 1}: {ruta_ids}")

    visualizar_rutas(rutas_mejoradas, deposito, clientes,min_camiones,optimoRecorrido)


def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter

    archivo = filedialog.askopenfilename(initialdir=os.getcwd(), title="Selecciona el archivo de datos del CVRP",
                                         filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))

    if archivo:
        ejecutar_cvrp_con_mejora_local(archivo)
    else:
        print("No se seleccionó ningún archivo.")

# Nombre del archivo donde se encuentran los datos del CVRP
#nombre_archivo = 'A-n38-k5.txt'
#ejecutar_cvrp_con_mejora_local(nombre_archivo)
seleccionar_archivo()
