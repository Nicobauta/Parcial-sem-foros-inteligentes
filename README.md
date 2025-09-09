# Simualación Semaforos Autootganizados

---

## Team
- Kevin García
- Nicolas Bautista
- Sara Romero

--- 

## Overview

Este proyecto implementa una simulacion de semaforos autoorganizados usando Python y TKinter y modela semaforos que gestionana el flujo vehicular de forma autonoma siguiendo un conjunto de reglas predefinidas.

La simulacion se ejecuta en una interfaz grafica de TKinter, el sistema modela una interseccion representada en una cuadricula de 10x10 en la que los vehiculos aparecen aleatoriamente cada 1500 milisegundos (1.5 segundos), en cualquiera de los cuatro carriles (norte, sur, este y oeste ) y respetan el estado del semaforo, el sistema no depende de tiempos fijos, sino que responde dinamicamente a la cantifaf de vehiculos, priorizando el flujo de trafico mas cargado.

---

## Core Concepts

### Interseccion y Carriles 
- La cuadricula representa una interseccion 10x10.  
- Existen 4 carriles principales, y los carros que circulan cada carril tienen un color:
  - Abajo (Rojo).
  - Arriba (Azul).
  - Derecha (Morado).
  - Izquierda (Naranja).
- Los carros (🚗) aparecen de manera aleatoria y se desplazan por su carril hasta salir de la cuadricula. 

### Semaforos
- Cada eje (Vertical y Horizontal) esta regulado por dos semaforos sincronizados.
- Los colores siguen el ciclo Verde -> Amarillo -> Rojo.  
- El estado de un eje depende del conteo de vehiculos y reglas de autoorganizacion.  

### Reglas de Control (Autoorganizacion)
El sistema implementa reglas inspiradas en modelos de trafico inteligentes como el SOTL-request 

**1.** Contador de carros: En cada paso de tiempo, agregar a un contador el número de vehículos que se acercan o esperan ante una luz roja a una distancia d. Cuando este contador exceda un umbral n, cambiar el semáforo. (Siempre que el semáforo cambia, reiniciar el contador en cero).

**2.** Tiempo minimo en verde: Los semáforos deben permanecer un mínimo tiempo u en verde.

**3.** Evitar cambios innecesarios: Si pocos vehículos (m o menos, > 0) están por cruzar una luz verde a una corta distancia r, no cambiar el semáforo.

**4.** Prioridad al eje con carros aproximandose: Si no hay un vehículo que se acerque a una luz verde a una distancia d y por lo menos un vehículo se aproxima a una luz roja a una distancia d, entonces cambiar el semáforo.

**5.** Carros detenidos mas alla del cruce con un semaforo verde :Si hay un vehículo detenido en el camino a una corta distancia e más allá de una luz verde, cambiar el semáforo.

**6.**  Bloqueo en ambas direcciones: Si hay vehículos detenidos en ambas direcciones a una corta distancia e más allá de la intersección, entonces cambiar ambas luces a rojo. Cuando una de las direcciones se libere, restaurar la luz verde en esa dirección.

---
### Flujo de la Simulacion
1. los vehiculos se generan en intervalos aleatorios.
2. Los vehiculos avanzan por su carril hasta encontrar un semaforo en rojo o a otro carro detenido.
3. El sistema evalua las reglas y actualiza los semaforos.
4. La interfaz grafica muestra:
   - Interseccion y carriles.
   - Los semaforos en tiempo real.
   - Los carros en movimiento.

--
## Execution and Output
Cuando se ejecuta el programa:
- Se abre una ventana de simulacion.
- El usuario puede controlar la simulacion con 2 botones:
    - Iniciar -> Comienza el flujo de la simulacion.
    - Detener -> pausa la simulacion.
 
---
## Technical Details
- Lenguaje: Python
- Librerias:
    - TKinter -> interfaz grafica
    - random -> Generacion de carros aleatorios
    - time -> control de tiempos de la aparicion de carros

**Parametros configurables:**
- FPS: Velocicdad de actualizacion de la animacion.
- VEHICLE_INTERVAL: Intervalo de aparicion de carros.
- u: tiempo minimo en verde.
- n: umbral de autos para forzar el cambio.
- d: distancia para detectar carros cerca al semaforo.
- m: Minimo de carros para permitir el cambio.

---

## Uso
Ejecutar la implementación directamente:

```python
python Semaforo.py
```
