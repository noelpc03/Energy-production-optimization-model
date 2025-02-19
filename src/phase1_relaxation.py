import pulp
import matplotlib.pyplot as plt
import numpy as np

# Definir el problema
problem = pulp.LpProblem("LP_PowerPlant_Optimization", pulp.LpMinimize)

# Variables continuas para la cantidad de plantas
x_T = pulp.LpVariable("x_T", lowBound=0, upBound=10, cat='Continuous')
x_H = pulp.LpVariable("x_H", lowBound=0, upBound=10, cat='Continuous')
x_R = pulp.LpVariable("x_R", lowBound=0, upBound=10, cat='Continuous')

# Variables continuas para la generación por planta
G_T = pulp.LpVariable("G_T", lowBound=0)
G_H = pulp.LpVariable("G_H", lowBound=0)
G_R = pulp.LpVariable("G_R", lowBound=0)

# Restringir G_T, G_H, G_R según las plantas
problem += G_T >= 50 * x_T
problem += G_T <= 200 * x_T
problem += G_H >= 100 * x_H
problem += G_H <= 300 * x_H
problem += G_R >= 20 * x_R
problem += G_R <= 150 * x_R

# Función objetivo: Minimizar costos totales
problem += (
    x_T * 1_000_000 + x_H * 2_000_000 + x_R * 800_000 +
    50 * G_T + 30 * G_H + 20 * G_R
), "Total_Cost"

# Restricción de demanda
problem += (G_T + G_H + G_R >= 1000), "Demand"

# Restricción de emisiones de CO2
problem += (0.8 * G_T <= 500), "CO2_Limit"

# Resolver el problema con Simplex
problem.solve()

# Imprimir resultados
print("Estado de la solución:", pulp.LpStatus[problem.status])
print("Costo total:", pulp.value(problem.objective))
print("Plantas térmicas:", pulp.value(x_T))
print("Plantas hidroeléctricas:", pulp.value(x_H))
print("Plantas renovables:", pulp.value(x_R))
print("Generación térmica:", pulp.value(G_T))
print("Generación hidroeléctrica:", pulp.value(G_H))
print("Generación renovable:", pulp.value(G_R))

# Visualización de la generación
labels = ["Térmica", "Hidroeléctrica", "Renovable"]
generacion = [pulp.value(G_T), pulp.value(G_H), pulp.value(G_R)]

plt.figure(figsize=(8, 6))
plt.bar(labels, generacion, color=['red', 'blue', 'green'])
plt.xlabel("Tipo de Planta")
plt.ylabel("Generación (MW)")
plt.title("Distribución de la Generación de Energía")
plt.show()
