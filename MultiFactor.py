import random
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os

class CVRP:
    def __init__(self, filename):
        self.dimension = None
        self.capacity = None
        self.nodes = []
        self.demands = {}
        self.depot = None
        self.optimal_value = None
        self.min_camiones = None

        self.read_data(filename)

    def read_data(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        section = None
        for line in lines:
            if line.startswith('DIMENSION'):
                self.dimension = int(line.split(':')[-1].strip())
            elif line.startswith('CAPACITY'):
                self.capacity = int(line.split(':')[-1].strip())
            elif line.startswith('NODE_COORD_SECTION'):
                section = 'NODE_COORD_SECTION'
            elif line.startswith('DEMAND_SECTION'):
                section = 'DEMAND_SECTION'
            elif line.startswith('DEPOT_SECTION'):
                section = 'DEPOT_SECTION'
            elif line.startswith('COMMENT'):
                print(filename)
                #cambiar ruta en mac
                if filename == 'C:/Users/Admin/PycharmProjects/pythonProject9/A-n80-k10.txt':
                    minCamiones = line[44:46].strip()

                    self.min_camiones = int(minCamiones)
                else :
                    minCamiones = line[44]
                    self.min_camiones = int(minCamiones)
                parts = line.split(':')
                if len(parts) > 2:
                    try:
                        optimoToJoin = line[62:65]
                        optimo = "".join(optimoToJoin)
                        self.optimal_value = int(optimo)


                    except ValueError:

                        try:

                            optimoToJoin = line[59:63]

                            print(optimoToJoin)

                            optimo = "".join(optimoToJoin)

                            self.optimal_value = int(optimo)

                        except:

                            optimoToJoin = line[60:64]

                            print(optimoToJoin)

                            optimo = "".join(optimoToJoin)

                            self.optimal_value = int(optimo)


            elif line.startswith('EOF'):
                break
            elif section == 'NODE_COORD_SECTION':
                parts = line.split()
                node_id = int(parts[0])
                x = float(parts[1])
                y = float(parts[2])
                self.nodes.append((x, y))
            elif section == 'DEMAND_SECTION':
                parts = line.split()
                node_id = int(parts[0])
                demand = int(parts[1])
                self.demands[node_id] = demand
            elif section == 'DEPOT_SECTION':
                parts = line.split()
                if len(parts) > 1 and int(parts[0]) == 1:
                    self.depot = int(parts[1])

        # Ensure the depot is set to the first node if not explicitly defined
        if self.depot is None:
            self.depot = 1

    def distance(self, node1, node2):
        x1, y1 = self.nodes[node1 - 1]
        x2, y2 = self.nodes[node2 - 1]
        return round(np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))

    def generate_initial_solution(self):
        solution = []
        remaining_capacity = self.capacity
        current_route = [self.depot]
        unvisited_nodes = set(range(2, self.dimension + 1))

        while unvisited_nodes:
            current_node = current_route[-1]
            nearest_node = min(unvisited_nodes, key=lambda x: self.distance(current_node, x))
            if self.demands[nearest_node] <= remaining_capacity:
                current_route.append(nearest_node)
                remaining_capacity -= self.demands[nearest_node]
                unvisited_nodes.remove(nearest_node)
            else:
                current_route.append(self.depot)
                solution.append(current_route)
                current_route = [self.depot]
                remaining_capacity = self.capacity

        if current_route != [self.depot]:
            current_route.append(self.depot)
            solution.append(current_route)

        # Asegurar que haya al menos min_routes rutas
        while len(solution) < self.min_camiones:
            solution.append([self.depot, self.depot])

        return solution


    def calculate_route_cost(self, route):
        cost = 0
        for i in range(len(route) - 1):
            cost += self.distance(route[i], route[i + 1])
        return cost

    def local_search(self, solution):
        improved = True
        while improved:
            improved = False
            for i in range(len(solution)):
                for j in range(1, len(solution[i]) - 2):
                    for k in range(j + 1, len(solution[i]) - 1):
                        new_solution = solution[i][:j] + solution[i][j:k + 1][::-1] + solution[i][k + 1:]
                        if self.calculate_route_cost(new_solution) < self.calculate_route_cost(solution[i]):
                            solution[i] = new_solution
                            improved = True

        # Fusionar rutas si hay más de min_routes y es posible mejorar la solución
        if len(solution) > self.min_camiones:
            routes_to_merge = len(solution) - self.min_camiones
            for _ in range(routes_to_merge):
                min_cost = float('inf')
                merge_index = None
                for i in range(len(solution) - 1):
                    merged_route = solution[i] + solution[i + 1][1:]
                    cost = self.calculate_route_cost(merged_route)
                    if cost < min_cost:
                        min_cost = cost
                        merge_index = i
                if merge_index is not None:
                    solution[merge_index] += solution[merge_index + 1][1:]
                    del solution[merge_index + 1]

        return solution

    def multi_start_heuristic(self, num_starts=100):
        best_solution = None
        best_cost = float('inf')

        for _ in range(num_starts):
            initial_solution = self.generate_initial_solution()
            improved_solution = self.local_search(initial_solution)
            cost = sum(self.calculate_route_cost(route) for route in improved_solution)
            if cost < best_cost:
                best_solution = improved_solution
                best_cost = cost

        return best_solution, best_cost

    def plot_solution(self, solution, best_cost):
        plt.figure(figsize=(12, 10))

        # Pintar los nodos con su número y demanda
        for node_id, (x, y) in enumerate(self.nodes, start=1):
            plt.scatter(x, y, c='blue')
            plt.text(x, y, f'{node_id}({self.demands[node_id]})', fontsize=9, ha='right', va='bottom')

        # Pintar las rutas con colores diferentes
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        for i, route in enumerate(solution):
            x_coords = [self.nodes[node - 1][0] for node in route]
            y_coords = [self.nodes[node - 1][1] for node in route]
            color = colors[i % len(colors)]
            plt.plot(x_coords, y_coords, color=color, marker='o', label=f'Ruta {i + 1}')

            # Calcular y pintar la distancia total de la ruta con espaciado vertical
            route_cost = self.calculate_route_cost(route)
            mid_x = (x_coords[0] + x_coords[-1]) / 2
            mid_y = (y_coords[0] + y_coords[-1]) / 2
            plt.text(mid_x + 10, mid_y + i * 5, f'Distancia: {route_cost}', fontsize=9, color=color, ha='center', va='center')  # Ajustar el espaciado según sea necesario

        depot_x, depot_y = self.nodes[self.depot - 1]
        plt.plot(depot_x, depot_y, 'rs', markersize=10)  # Pintar el depósito en rojo

        plt.title(f'Visualización de rutas CVRP (Multi-start k-best)\nDistancia Total: {best_cost:.2f}\nMin Camiones: {self.min_camiones}\nOptimo Recorrido: {self.optimal_value}')
        plt.xlabel("Coordenada X")
        plt.ylabel("Coordenada Y")
        plt.grid(True)
        plt.legend()

        plt.tight_layout()  # Ajustar el layout para evitar superposiciones
        plt.show()

def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter

    archivo = filedialog.askopenfilename(initialdir=os.getcwd(), title="Selecciona el archivo de datos del CVRP",
                                         filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))

    if archivo:
        cvrp_instance = CVRP(archivo)
        best_solution, best_cost = cvrp_instance.multi_start_heuristic(num_starts=100)

        # Imprime la mejor solución encontrada y su costo
        print(f"Mejor solución encontrada:")
        for i, route in enumerate(best_solution):
            route_cost = cvrp_instance.calculate_route_cost(route)
            print(f"Ruta {i + 1}: {route} - Distancia: {route_cost}")
        print(f"Costo total de la mejor solución: {best_cost}")

        # Pinta la solución
        cvrp_instance.plot_solution(best_solution, best_cost)
    else:
        print("No se seleccionó ningún archivo.")

# Ejemplo de uso
if __name__ == "__main__":
    seleccionar_archivo()

