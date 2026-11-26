"""Entrena y guarda los modelos XGBoost (6 h) que usa el dashboard.

Uso, desde la carpeta raíz del repositorio:

    python dashboard/entrenar_modelos.py

Escribe en dashboard/modelos/ un archivo .json con el modelo y otro _info.json con
datos de apoyo (rango probable, número de árboles) por estación. Solo hay que volver
a ejecutarlo si cambian los datos limpios de data/clean.
"""

import json
import time

import motor


def main():
    motor.CARPETA_MODELOS.mkdir(parents=True, exist_ok=True)
    for estacion, nombre in motor.ESTACIONES.items():
        inicio = time.time()
        modelo, info = motor.entrenar(estacion)
        modelo.save_model(motor.ruta_modelo(estacion))
        motor.ruta_info(estacion).write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{nombre}: {info['arboles']} árboles, rango probable "
              f"{100 * info['error_p05_m']:+.1f} / {100 * info['error_p95_m']:+.1f} cm "
              f"({time.time() - inicio:.0f} s)")


if __name__ == "__main__":
    main()
