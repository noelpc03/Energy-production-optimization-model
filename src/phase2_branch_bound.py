import pulp
import time
import pandas as pd
import matplotlib.pyplot as plt

def branch_and_bound(problem, vars_ent, max_iters=100):
    """ Implementación del método Branch and Bound """
    iteraciones = 0
    cola = [(problem, [])]  # Inicializar la cola con el problema original

    mejor_sol = None
    mejor_costo = float("inf")

    while cola and iteraciones < max_iters:
        iteraciones += 1
        nodo, ramas = cola.pop(0)

        # Resolver la relajación LP del nodo actual
        nodo.solve()

        if nodo.status != pulp.LpStatusOptimal:
            continue  # No hay solución óptima para este nodo

        # Obtener solución óptima relajada
        costo_actual = pulp.value(nodo.objective)
        valores_vars = {var.name: pulp.value(var) for var in vars_ent}

        # Si la solución es peor que la mejor encontrada, descartar
        if costo_actual >= mejor_costo:
            continue

        # Verificar si todas las variables enteras están en valores enteros
        if all(abs(val - int(val)) < 1e-6 for val in valores_vars.values()):
            mejor_sol = valores_vars
            mejor_costo = costo_actual
            continue  # No hay necesidad de seguir explorando

        # Seleccionar una variable no entera para bifurcar
        var_frac = next(var for var in vars_ent if abs(valores_vars[var.name] - int(valores_vars[var.name])) > 1e-6)

        # Crear dos nuevos subproblemas con restricciones adicionales
        nuevo_nodo1 = nodo.deepcopy()
        nuevo_nodo1 += var_frac <= int(valores_vars[var_frac.name])

        nuevo_nodo2 = nodo.deepcopy()
        nuevo_nodo2 += var_frac >= int(valores_vars[var_frac.name]) + 1

        cola.append((nuevo_nodo1, ramas + [f"{var_frac.name} <= {int(valores_vars[var_frac.name])}"]))
        cola.append((nuevo_nodo2, ramas + [f"{var_frac.name} >= {int(valores_vars[var_frac.name]) + 1}"]))

    return mejor_sol, mejor_costo, iteraciones


# ** Definir el problema inicial **
def crear_problema():
    problem = pulp.LpProblem("MILP_PowerPlant_Optimization", pulp.LpMinimize)

    x_T = pulp.LpVariable("x_T", lowBound=0, upBound=10, cat='Continuous')
    x_H = pulp.LpVariable("x_H", lowBound=0, upBound=10, cat='Continuous')
    x_R = pulp.LpVariable("x_R", lowBound=0, upBound=10, cat='Continuous')

    G_T = pulp.LpVariable("G_T", lowBound=0)
    G_H = pulp.LpVariable("G_H", lowBound=0)
    G_R = pulp.LpVariable("G_R", lowBound=0)

    problem += G_T >= 50 * x_T
    problem += G_T <= 200 * x_T
    problem += G_H >= 100 * x_H
    problem += G_H <= 300 * x_H
    problem += G_R >= 20 * x_R
    problem += G_R <= 150 * x_R

    problem += (x_T * 1_000_000 + x_H * 2_000_000 + x_R * 800_000 +
                50 * G_T + 30 * G_H + 20 * G_R), "Total_Cost"

    problem += (G_T + G_H + G_R >= 1000), "Demand"
    problem += (0.8 * G_T <= 500), "CO2_Limit"

    return problem, [x_T, x_H, x_R]


if __name__ == "__main__":
    problema, vars_ent = crear_problema()
    
    start_time = time.time()
    solucion, costo, iteraciones = branch_and_bound(problema, vars_ent)
    end_time = time.time()

    tiempo_total = end_time - start_time

    print("\n📌 **Resultados Branch and Bound**")
    print(f"📉 Costo Óptimo: {costo}")
    print(f"🕒 Iteraciones: {iteraciones}")
    print(f"⏳ Tiempo de ejecución: {tiempo_total:.4f} segundos")
    print(f"📊 Solución óptima encontrada: {solucion}")

    # ** Visualización de generación de energía **
    if solucion:
        etiquetas = ["Térmica", "Hidroeléctrica", "Renovable"]
        valores = [solucion["x_T"], solucion["x_H"], solucion["x_R"]]

        plt.figure(figsize=(8, 6))
        plt.bar(etiquetas, valores, color=['red', 'blue', 'green'])
        plt.xlabel("Tipo de Planta")
        plt.ylabel("Cantidad de Plantas")
        plt.title("Distribución de la Generación de Energía - Branch and Bound")
        plt.show()
