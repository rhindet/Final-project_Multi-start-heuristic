import math
import random
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def load_cvrp_data(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    dimension = None
    capacity = None
    depot = None
    customers = []
    min_camiones = None
    optimal_route = None

    section = None
    for line in lines:
        line = line.strip()
        if line.startswith('DIMENSION'):
            dimension = int(line.split(':')[-1].strip())
        elif line.startswith('CAPACITY'):
            capacity = int(line.split(':')[-1].strip())
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
                if parts[0] == 1:
                    depot = {'id': parts[0], 'location': (parts[1], parts[2])}
                else:
                    customers.append({'id': parts[0], 'location': (parts[1], parts[2])})
            else:
                print(f"Incorrect line in COORD_SECTION: {line}")
        elif section == 'DEMAND' and line:
            parts = list(map(int, line.split()))
            for customer in customers:
                if customer['id'] == parts[0]:
                    customer['demand'] = parts[1]
                    break

        elif line.startswith('COMMENT'):
                if filename == 'C:/Users/Admin/PycharmProjects/pythonProject9/A-n80-k10.txt':
                    minCamiones = line[44:46].strip()
                    min_camiones = int(minCamiones)
                else:
                    minCamiones = line[44]
                    min_camiones = int(minCamiones)
                try:
                    optimoToJoin = line[62:65]
                    optimo = "".join(optimoToJoin)

                    optimal_route = int(optimo)
                except ValueError:
                    try:
                        optimoToJoin = line[59:63]
                        print(optimoToJoin)
                        optimo = "".join(optimoToJoin)
                        optimal_route = int(optimo)
                    except:
                        optimoToJoin = line[60:64]
                        print(optimoToJoin)
                        optimo = "".join(optimoToJoin)
                        optimal_route = int(optimo)


    return dimension, capacity, depot, customers, min_camiones, optimal_route


def cvrp_randomized_heuristic(depot, customers, capacity, min_trucks):
    routes = []
    unassigned_customers = customers.copy()

    while unassigned_customers:
        route = []
        remaining_capacity = capacity

        route.append(depot['location'])
        last_customer = depot['location']

        while remaining_capacity > 0 and unassigned_customers:
            available_customers = [customer for customer in unassigned_customers if
                                   customer['demand'] <= remaining_capacity]
            if not available_customers:
                break

            random.shuffle(available_customers)
            closest_customer = available_customers[0]

            route.append(closest_customer['location'])
            remaining_capacity -= closest_customer['demand']
            unassigned_customers.remove(closest_customer)
            last_customer = closest_customer['location']

        route.append(depot['location'])
        routes.append(route)

        if len(routes) == min_trucks and unassigned_customers:
            remaining_capacity = capacity
            while unassigned_customers:
                route = [depot['location']]
                remaining_capacity = capacity
                while remaining_capacity > 0 and unassigned_customers:
                    available_customers = [customer for customer in unassigned_customers if
                                           customer['demand'] <= remaining_capacity]
                    if not available_customers:
                        break

                    random.shuffle(available_customers)
                    closest_customer = available_customers[0]

                    route.append(closest_customer['location'])
                    remaining_capacity -= closest_customer['demand']
                    unassigned_customers.remove(closest_customer)
                    last_customer = closest_customer['location']

                route.append(depot['location'])
                routes.append(route)
            break

    return routes


def calculate_total_distance(route):
    total_distance = 0
    for i in range(len(route) - 1):
        total_distance += distance(route[i], route[i + 1])
    return total_distance


def local_search_improvement(routes, depot, customers):
    improved = True
    while improved:
        improved = False
        for i in range(len(routes) - 1):
            for j in range(i + 1, len(routes)):
                route1 = routes[i][1:-1]
                route2 = routes[j][1:-1]

                improvements = []
                for customer1 in route1:
                    for customer2 in route2:
                        new_route1 = [depot['location']] + [c for c in route1 if c != customer1] + [customer2,
                                                                                                    depot['location']]
                        new_route2 = [depot['location']] + [c for c in route2 if c != customer2] + [customer1,
                                                                                                    depot['location']]
                        new_distance = calculate_total_distance(new_route1) + calculate_total_distance(new_route2)

                        if new_distance < calculate_total_distance(routes[i]) + calculate_total_distance(routes[j]):
                            improvements.append((i, j, customer1, customer2))

                if improvements:
                    idx1, idx2, best_customer1, best_customer2 = random.choice(improvements)
                    routes[idx1] = [depot['location']] + [c for c in route1 if c != best_customer1] + [best_customer2,
                                                                                                       depot[
                                                                                                           'location']]
                    routes[idx2] = [depot['location']] + [c for c in route2 if c != best_customer2] + [best_customer1,
                                                                                                       depot[
                                                                                                           'location']]
                    improved = True
                    break
            if improved:
                break

    return routes


def visualize_routes(routes, depot, customers, min_trucks, optimal_route):
    plt.figure(figsize=(14, 10))

    plt.plot(depot['location'][0], depot['location'][1], 'ks', markersize=10, label='Depot')

    for customer in customers:
        plt.plot(customer['location'][0], customer['location'][1], 'bo', markersize=5)
        plt.text(customer['location'][0], customer['location'][1],
                 f"ID: {customer['id']}\nDemand: {customer['demand']}", fontsize=9, ha='right')

    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    total_distance = 0
    offset = 10

    for i, route in enumerate(routes):
        route_x, route_y = zip(*route)
        plt.plot(route_x, route_y, color=colors[i % len(colors)], marker='o', label=f'Route {i + 1}')

        dist = calculate_total_distance(route)
        total_distance += dist
        plt.text(max(route_x) + 5, max(route_y) - i * offset, f"Route {i + 1}: {dist:.2f}", fontsize=12, ha='left',
                 color=colors[i % len(colors)])

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(
        f'CVRP Route Visualization (Random Heuristic with Local Search)\nTotal Distance: {total_distance:.2f}\nMin Trucks: {min_trucks}\nOptimal Route: {optimal_route}')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.xlim(0, max(max([c['location'][0] for c in customers]), depot['location'][0]) + 20)
    plt.ylim(0, max(max([c['location'][1] for c in customers]), depot['location'][1]) + 20)
    plt.show()


def select_file():
    root = tk.Tk()
    root.withdraw()

    file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select CVRP data file",
                                      filetypes=(("Text files", "*.txt"), ("All files", "*.*")))

    if file:
        execute_cvrp_with_local_search(file)
    else:
        print("No file selected.")


def execute_cvrp_with_local_search(filename):
    dimension, capacity, depot, customers, min_trucks, optimal_route = load_cvrp_data(filename)
    min_trucks = min_trucks

    initial_routes = cvrp_randomized_heuristic(depot, customers, capacity, min_trucks)

    print("Initially generated routes:")
    for i, route in enumerate(initial_routes):
        route_ids = []
        for coord in route:
            for customer in customers:
                if customer['location'] == coord:
                    route_ids.append(customer['id'])
                    break
        print(f"Route {i + 1}: {route_ids}")

    optimized_routes = local_search_improvement(initial_routes, depot, customers)

    print("\nOptimized routes with local search:")
    for i, route in enumerate(optimized_routes):
        route_ids = []
        for coord in route:
            for customer in customers:
                if customer['location'] == coord:
                    route_ids.append(customer['id'])
                    break
        print(f"Route {i + 1}: {route_ids}")

    visualize_routes(optimized_routes, depot, customers, min_trucks, optimal_route)


select_file()
