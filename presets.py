# Gotowe układy startowe do symulacji 3 ciał

import numpy as np


def get_presets():
    # Zwraca słownik z gotowymi konfiguracjami
    presets = {}

    # Ósemka - słynna orbita (Chenciner i Montgomery, 2000)
    presets["Ósemka (Figure-8)"] = {
        "masses": [1.0, 1.0, 1.0],
        "positions": [
            [-0.97000436, 0.24308753],
            [0.97000436, -0.24308753],
            [0.0, 0.0]
        ],
        "velocities": [
            [0.4662036850, 0.4323657300],
            [0.4662036850, 0.4323657300],
            [-0.9324073700, -0.8647314600]
        ]
    }

    # Trójkąt Lagrange'a - 3 równe masy w trójkącie równobocznym, kręcą się wokół środka
    offset = np.pi / 6
    r = 1.0
    v = 0.5
    presets["Trójkąt Lagrange'a"] = {
        "masses": [1.0, 1.0, 1.0],
        "positions": [
            [r * np.cos(0 + offset), r * np.sin(0 + offset)],
            [r * np.cos(2*np.pi/3 + offset), r * np.sin(2*np.pi/3 + offset)],
            [r * np.cos(4*np.pi/3 + offset), r * np.sin(4*np.pi/3 + offset)]
        ],
        "velocities": [
            [v * np.cos(np.pi/2 + offset), v * np.sin(np.pi/2 + offset)],
            [v * np.cos(np.pi/2 + 2*np.pi/3 + offset), v * np.sin(np.pi/2 + 2*np.pi/3 + offset)],
            [v * np.cos(np.pi/2 + 4*np.pi/3 + offset), v * np.sin(np.pi/2 + 4*np.pi/3 + offset)]
        ]
    }

    # Orbita Ćmy - periodyczna orbita, kształt skrzydeł ćmy
    presets["Orbita Ćmy (Moth I)"] = {
        "masses": [1.0, 1.0, 1.0],
        "positions": [
            [-1.0, 0.0],
            [1.0, 0.0],
            [0.0, 0.0]
        ],
        "velocities": [
            [0.46444377, 0.39605820],
            [0.46444377, 0.39605820],
            [-0.92888754, -0.79211640]
        ]
    }

    # Trójkąt Lagrange'a z różnymi masami - ciała o masach 1, 2, 3 obracają się sztywno
    m_lag = [1.0, 2.0, 3.0]
    M_total = sum(m_lag)
    omega = np.sqrt(M_total)
    # Wierzchołki trójkąta równobocznego o boku 1
    vert = np.array([
        [0.0,  1.0/np.sqrt(3)],
        [-0.5, -1.0/(2*np.sqrt(3))],
        [0.5, -1.0/(2*np.sqrt(3))]
    ])
    # Przesunięcie żeby środek masy był w (0,0)
    com = sum(m_lag[i] * vert[i] for i in range(3)) / M_total
    pos_lag = vert - com
    # Prędkości dla obrotu sztywnego: v = omega * (-y, x)
    vel_lag = omega * np.column_stack([-pos_lag[:, 1], pos_lag[:, 0]])
    presets["Trójkąt Lagrange'a (masy 1:2:3)"] = {
        "masses": m_lag,
        "positions": pos_lag.tolist(),
        "velocities": vel_lag.tolist()
    }

    # Orbita Broucke'a A1 - periodyczna orbita 3 ciał (Broucke 1975)
    presets["Orbita Broucke'a A1"] = {
        "masses": [1.0, 1.0, 1.0],
        "positions": [
            [-0.9892620043, 0.0],
            [2.2096177241, 0.0],
            [-1.2203557197, 0.0]
        ],
        "velocities": [
            [0.0, 1.9169244185],
            [0.0, 0.1910268738],
            [0.0, -2.1079512924]
        ]
    }

    return presets
