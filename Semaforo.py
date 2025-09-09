import tkinter as tk
import random
import time

#Configuración
FILAS = 10
COLUMNAS = 10
TAM_CELDA = 40
FPS = 250            
VEHICLE_INTERVAL = 1500 

#Parametros para las reglas
d = 3      #distancia para "acercarse" 
n = 4      #umbral de contador para forzar cambio 
u = 6000   #tiempo mínimo en verde (ms) 
m = 1      #número pequeño de vehículos para evitar cambio si <= m 
r = 2      #distancia corta para la regla 3 
e = 2      #distancia corta "más allá" del semáforo para detectar detención 

YELLOW_DURATION = 2000  
SEMAFOROS_COLORES = ["green", "yellow", "red"]
EMOJI_CARRO = "🚗"
EMOJI_FONT = ("Segoe UI Emoji", 20)
COLOR_CARRIL = "lightgray"
COLOR_BLOQUE = "black"
COLOR_CARROS = {"abajo": "red", "arriba": "blue", "derecha": "purple", "izquierda": "orange"}

#Matriz original
matriz = [
    list("####--####"),
    list("####--####"),
    list("####--####"),
    list("##%*--*%##"),
    list("----------"),
    list("----------"),
    list("##%*--*%##"),
    list("####--####"),
    list("####--####"),
    list("####--####")
]

#Carriles (definidos hasta bordes para que los coches salgan del escenario)
carriles = {
    "abajo":    [(i,4) for i in range(0,FILAS)],              
    "arriba":   [(i,5) for i in range(FILAS-1,-1,-1)],       
    "derecha":  [(5,i) for i in range(0,COLUMNAS)],      
    "izquierda":[(4,i) for i in range(COLUMNAS-1,-1,-1)]   
}

#Vehículos por carril
carros_por_carril = {c: [] for c in carriles}

#Mapear carril en base a los ejes
carril_eje = {"abajo": "vertical", "arriba": "vertical",
              "derecha": "horizontal", "izquierda": "horizontal"}

#Estados de semáforo por eje
axis_state = {"vertical": "green", "horizontal": "red"}

#Para gestionar tiempos mínimos en verde 
last_green_change_ts = {"vertical": 0.0, "horizontal": 0.0}  

#Contadores por eje 
counter_axis = {"vertical": 0, "horizontal": 0}

#Estado de bloqueo mutuo
both_blocked = False

_control_locked = False
simulando = False

#Procesar matriz
pos_semaforos = []
estado_semaforo = {}  
percent_positions = []
for i in range(FILAS):
    for j in range(COLUMNAS):
        ch = matriz[i][j]
        if ch == "*":
            pos_semaforos.append((i, j))
            matriz[i][j] = 1
            estado_semaforo[(i, j)] = 2  
        elif ch == "-" or ch == "%":
            if ch == "%":
                percent_positions.append((i, j))
            matriz[i][j] = 1
        else:
            matriz[i][j] = 0

#Flechas manuales 
arrow_positions = {
    (3,2): "↓",
    (3,7): "←",
    (6,2): "→",
    (6,7): "↑"
}

#Relacionar semáforos con índices en cada path
def manhattan(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

stops_by_carril = {c: [] for c in carriles}
for sem in pos_semaforos:
    for carril, path in carriles.items():
        for i in range(len(path)-1):
            if manhattan(path[i], sem) == 1:
                stops_by_carril[carril].append((i, sem))

for carril in stops_by_carril:
    stops_by_carril[carril].sort(key=lambda x: x[0])

#asignar primer semáforo por carril 
carril_semaforo, semaforo_carril = {}, {}
for carril, stops in stops_by_carril.items():
    if stops:
        carril_semaforo[carril] = stops[0][1]
        semaforo_carril[stops[0][1]] = carril

#sincroniza estados visuales de semáforos
def sync_semaforos_a_ejes():
    for carril, sem in carril_semaforo.items():
        eje = carril_eje[carril]
        color = axis_state[eje]
        idx = 0 if color == "green" else 1 if color == "yellow" else 2
        estado_semaforo[sem] = idx

sync_semaforos_a_ejes()

#Tkinter configuracion
root = tk.Tk()
root.title("Simulación de tráfico (reglas auto-organizantes)")

canvas = tk.Canvas(root, width=COLUMNAS*TAM_CELDA, height=FILAS*TAM_CELDA+40)
canvas.pack()

def dibujar_matriz():
    canvas.delete("all")
    for i in range(FILAS):
        for j in range(COLUMNAS):
            x0, y0 = j*TAM_CELDA, i*TAM_CELDA
            x1, y1 = x0+TAM_CELDA, y0+TAM_CELDA
            color = COLOR_CARRIL if matriz[i][j]==1 else COLOR_BLOQUE
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="white")

    #semáforos
    for (f,c), idx in estado_semaforo.items():
        x0, y0 = c*TAM_CELDA+6, f*TAM_CELDA+6
        x1, y1 = x0+TAM_CELDA-12, y0+TAM_CELDA-12
        canvas.create_rectangle(x0, y0, x1, y1, fill=SEMAFOROS_COLORES[idx], outline="black")

    #flechas
    for (f,c), arrow in arrow_positions.items():
        x = c*TAM_CELDA + TAM_CELDA//2
        y = f*TAM_CELDA + TAM_CELDA//2
        canvas.create_text(x, y, text=arrow, font=("Arial", 16, "bold"), fill="black")

    #coches
    for carril, path in carriles.items():
        for car in carros_por_carril[carril]:
            pos_idx = car['pos']
            if 0 <= pos_idx < len(path):
                f,c = path[pos_idx]
                x = c*TAM_CELDA + TAM_CELDA//2
                y = f*TAM_CELDA + TAM_CELDA//2
                try:
                    canvas.create_text(x, y, text=EMOJI_CARRO, font=EMOJI_FONT, fill=COLOR_CARROS[carril])
                except Exception:
                    canvas.create_text(x, y, text="C", font=("Arial", 14), fill=COLOR_CARROS[carril])


    v_count = len(carros_por_carril["abajo"]) + len(carros_por_carril["arriba"])
    h_count = len(carros_por_carril["derecha"]) + len(carros_por_carril["izquierda"])
    canvas.create_text(8, FILAS*TAM_CELDA+6, anchor="w",
                       text=f"Vertical:{v_count} Horizontal:{h_count}   V={axis_state['vertical']} H={axis_state['horizontal']}",
                       font=("Arial", 12))

    canvas.create_text(300, FILAS*TAM_CELDA+6, anchor="w",
                       text=f"counters -> V:{counter_axis['vertical']} H:{counter_axis['horizontal']}",
                       font=("Arial", 12), fill="blue")

#Movimiento de cada coche
def move_cars_step():
    for carril, path in carriles.items():
        cars = carros_por_carril[carril]
        if not cars:
            continue

        #ordenar por posición 
        cars_sorted = sorted(cars, key=lambda x: x['pos'], reverse=True)
        occupied = set(c['pos'] for c in cars_sorted) 
        new_cars = []
        taken = set() 

        for car in cars_sorted:
            pos = car['pos']
            passed = car['passed']
            next_idx = car['next_stop_idx']
            next_pos = pos + 1

            if next_pos >= len(path):
                continue

            if next_pos in occupied or next_pos in taken:
                new_cars.append({'pos': pos, 'passed': passed, 'next_stop_idx': next_idx, 'next_stop_sem': car['next_stop_sem']})
                taken.add(pos)
                continue

            if (not passed) and (next_idx is not None) and (pos == next_idx):
                sem_pos = car['next_stop_sem']

                #solo avanza si semáforo está verde 
                if sem_pos and estado_semaforo.get(sem_pos, 2) == 0:
                    new_cars.append({'pos': next_pos, 'passed': True, 'next_stop_idx': None, 'next_stop_sem': None})
                    taken.add(next_pos)
                else:
                    #semaforo no esta en verde se queda donde esta
                    new_cars.append({'pos': pos, 'passed': passed, 'next_stop_idx': next_idx, 'next_stop_sem': sem_pos})
                    taken.add(pos)
            else:
                #avanza normalmnente
                new_cars.append({'pos': next_pos, 'passed': passed, 'next_stop_idx': next_idx, 'next_stop_sem': car['next_stop_sem']})
                taken.add(next_pos)

        carros_por_carril[carril] = sorted(new_cars, key=lambda x: x['pos'])

#Generación de coches
def spawn_car():
    if not simulando:
        return
    carril = random.choice(list(carriles.keys()))
    if any(car['pos'] == 0 for car in carros_por_carril[carril]):
        root.after(VEHICLE_INTERVAL, spawn_car)
        return

    #calcular primer stop para el carril
    next_stop_idx = None
    next_stop_sem = None
    for idx, sem_pos in stops_by_carril[carril]:
        if idx >= 0: 
            next_stop_idx = idx
            next_stop_sem = sem_pos
            break

    car = {'pos': 0, 'passed': False, 'next_stop_idx': next_stop_idx, 'next_stop_sem': next_stop_sem}
    carros_por_carril[carril].append(car)
    root.after(VEHICLE_INTERVAL, spawn_car)

#Contadores de vehiculos por eje
def contar_vehiculos_por_eje():
    v = len(carros_por_carril["abajo"]) + len(carros_por_carril["arriba"])
    h = len(carros_por_carril["derecha"]) + len(carros_por_carril["izquierda"])
    return v, h

#Deteccion  de vehiculos que hayan apado el semaforo
def vehicles_beyond_sem_stopped(carril, sem_idx, max_dist):
    cars = sorted(carros_por_carril[carril], key=lambda x: x['pos'])
    positions = set(c['pos'] for c in cars)
    res = []
    for car in cars:
        pos = car['pos']
        if pos > sem_idx and (pos - sem_idx) <= max_dist:
            if (pos + 1) in positions or (pos + 1) >= len(carriles[carril]):
                res.append(car)
    return res

#Evaluación de reglas y decisiones
def evaluate_rules_and_update():
    global both_blocked

    #sincronizar semáforos visuales con los estados
    sync_semaforos_a_ejes()

    #1) actualizar contadores por eje: contar coches que se acercan/esperan ante roja a distancia d
    for axis in ("vertical", "horizontal"):
        total_near_red = 0
        for carril, path in carriles.items():
            if carril_eje[carril] != axis:
                continue
            for car in carros_por_carril[carril]:
                sem_idx = car['next_stop_idx']
                sem_pos = car['next_stop_sem']
                if sem_idx is None or sem_pos is None:
                    continue
                if estado_semaforo.get(sem_pos, 2) == 2 and sem_idx >= car['pos'] and (sem_idx - car['pos']) <= d:
                    total_near_red += 1
        if total_near_red > 0:
            counter_axis[axis] += total_near_red
        else:
            counter_axis[axis] = max(0, counter_axis[axis] - 1)

    #6) detectar bloqueo en ambas direcciones
    blocked_vertical = False
    blocked_horizontal = False
    for carril in ("abajo", "arriba"):
        stops = stops_by_carril.get(carril, [])
        if not stops: continue
        sem_idx, sem_pos = stops[0]
        if vehicles_beyond_sem_stopped(carril, sem_idx, e):
            blocked_vertical = True
    for carril in ("derecha", "izquierda"):
        stops = stops_by_carril.get(carril, [])
        if not stops: continue
        sem_idx, sem_pos = stops[0]
        if vehicles_beyond_sem_stopped(carril, sem_idx, e):
            blocked_horizontal = True

    if blocked_vertical and blocked_horizontal:
        both_blocked = True
        axis_state["vertical"] = "red"
        axis_state["horizontal"] = "red"
        sync_semaforos_a_ejes()
        return
    else:
        if both_blocked and not (blocked_vertical and blocked_horizontal):
            both_blocked = False
            vq, hq = contar_vehiculos_por_eje()
            if vq >= hq:
                axis_state["vertical"] = "green"; axis_state["horizontal"] = "red"
                last_green_change_ts["vertical"] = int(time.time()*1000)
            else:
                axis_state["vertical"] = "red"; axis_state["horizontal"] = "green"
                last_green_change_ts["horizontal"] = int(time.time()*1000)
            sync_semaforos_a_ejes()
            return

    #En caso de que no se presente un bloqueo mutuo realizar la evaluacion de reglas
    now_ms = int(time.time()*1000)
    metrics = {}
    for axis in ("vertical", "horizontal"):
        approaching_red = 0
        approaching_green = 0
        about_to_cross_green = 0
        stopped_beyond = 0
        for carril, path in carriles.items():
            if carril_eje[carril] != axis:
                continue
            stops = stops_by_carril.get(carril, [])
            if not stops:
                continue
            sem_idx, sem_pos = stops[0]
            for car in carros_por_carril[carril]:
                pos = car['pos']
                if estado_semaforo.get(sem_pos,2) == 2 and sem_idx >= pos and (sem_idx - pos) <= d:
                    approaching_red += 1
                if estado_semaforo.get(sem_pos,2) == 0 and sem_idx >= pos and (sem_idx - pos) <= d:
                    approaching_green += 1
                if estado_semaforo.get(sem_pos,2) == 0 and sem_idx >= pos and (sem_idx - pos) <= r:
                    about_to_cross_green += 1
            sb = vehicles_beyond_sem_stopped(carril, sem_idx, e)
            if sb:
                stopped_beyond += len(sb)
        metrics[axis] = {
            "approaching_red": approaching_red,
            "approaching_green": approaching_green,
            "about_to_cross_green": about_to_cross_green,
            "stopped_beyond": stopped_beyond,
            "counter": counter_axis[axis],
            "time_since_green": now_ms - last_green_change_ts.get(axis, 0)
        }

    #Decision a tomar
    v_metric = metrics["vertical"]
    h_metric = metrics["horizontal"]
    candidate = None
    if v_metric["counter"] >= n:
        candidate = "vertical"
    if h_metric["counter"] >= n:
        if candidate is None:
            candidate = "horizontal"
        else:
            candidate = "vertical" if v_metric["counter"] >= h_metric["counter"] else "horizontal"

    #aplicar reglas 3 y 4 en caso de nohaber un candidato
    if candidate is None:
        current_green = "vertical" if axis_state["vertical"] == "green" else "horizontal"
        other = "horizontal" if current_green == "vertical" else "vertical"
        curr_met = metrics[current_green]
        oth_met = metrics[other]
        #regla 3: si pocos vehículos a punto de cruzar (<=m) no cambiar
        if curr_met["about_to_cross_green"] <= m:
            #regla 4: si nadie acercándose al verde y hay al rojo -> cambiar
            if curr_met["approaching_green"] == 0 and oth_met["approaching_red"] > 0:
                candidate = other

    #regla 5: vehículo detenido más allá de la intersección en el eje verde -> cambiar
    if candidate is None:
        current_green = "vertical" if axis_state["vertical"] == "green" else "horizontal"
        curr_met = metrics[current_green]
        other = "horizontal" if current_green == "vertical" else "vertical"
        if curr_met["stopped_beyond"] > 0:
            candidate = other

    #Ejecutar cambio si corresponde
    if candidate is not None:
        current_green = "vertical" if axis_state["vertical"] == "green" else "horizontal"
        if metrics[current_green]["time_since_green"] < u:
            return
        if axis_state[candidate] == "green":
            return
        axis_state[current_green] = "yellow"
        sync_semaforos_a_ejes()
        def after_yellow(s_from=current_green, s_to=candidate):
            axis_state[s_from] = "red"
            axis_state[s_to] = "green"
            last_green_change_ts[s_to] = int(time.time()*1000)
            counter_axis[s_to] = 0  
            sync_semaforos_a_ejes()
        root.after(YELLOW_DURATION, after_yellow)

#Bucle principal
def step():
    if simulando:
        move_cars_step()
        evaluate_rules_and_update()
        sync_semaforos_a_ejes()
        dibujar_matriz()
        root.after(FPS, step)

def iniciar():
    global simulando
    if not simulando:
        for c in carros_por_carril:
            carros_por_carril[c].clear()
        counter_axis["vertical"] = 0
        counter_axis["horizontal"] = 0
        now_ms = int(time.time()*1000)
        last_green_change_ts["vertical"] = now_ms if axis_state["vertical"] == "green" else 0
        last_green_change_ts["horizontal"] = now_ms if axis_state["horizontal"] == "green" else 0
        sync_semaforos_a_ejes()
        simulando = True
        root.after(100, spawn_car)
        root.after(100, step)

def detener():
    global simulando
    simulando = False

#Botones
frame = tk.Frame(root); frame.pack(pady=6)
tk.Button(frame, text="Iniciar", command=iniciar).pack(side="left", padx=6)
tk.Button(frame, text="Detener", command=detener).pack(side="left", padx=6)

#Dibujo inicial
dibujar_matriz()
root.mainloop()
