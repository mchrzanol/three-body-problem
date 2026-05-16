# Silnik fizyki - liczy grawitację i ruch ciał metodą RK4

import numpy as np
from config import G, SOFTENING, DT_MAX, DT_MIN, ADAPTIVE_FACTOR


class PhysicsEngine:
    # Klasa odpowiedzialna za symulację grawitacji

    def __init__(self, masses, positions, velocities):
        self.n = len(masses)
        self.masses = np.array(masses, dtype=np.float64)
        self.positions = np.array(positions, dtype=np.float64)
        self.velocities = np.array(velocities, dtype=np.float64)

    def compute_accelerations(self, positions):
        # Liczy przyspieszenia działające na każde ciało
        # diff[i,j] = wektor od ciała i do ciała j
        diff = positions[None, :, :] - positions[:, None, :]
        r_sq = np.sum(diff * diff, axis=2) + SOFTENING * SOFTENING
        np.fill_diagonal(r_sq, 1.0)  # żeby nie dzielić przez 0
        inv_r3 = r_sq ** -1.5
        np.fill_diagonal(inv_r3, 0.0)  # ciało nie przyciąga samo siebie
        return G * np.einsum('j,ijd,ij->id', self.masses, diff, inv_r3)

    def min_distance(self):
        # Najmniejsza odległość między parą ciał
        diff = self.positions[None, :, :] - self.positions[:, None, :]
        r_sq = np.sum(diff * diff, axis=2)
        np.fill_diagonal(r_sq, np.inf)
        return float(np.sqrt(r_sq.min()))

    def rk4_step(self, dt):
        # Jeden krok metody Runge-Kutta 4 rzędu
        pos = self.positions.copy()
        vel = self.velocities.copy()

        k1_v = self.compute_accelerations(pos)
        k1_x = vel.copy()

        k2_v = self.compute_accelerations(pos + 0.5 * dt * k1_x)
        k2_x = vel + 0.5 * dt * k1_v

        k3_v = self.compute_accelerations(pos + 0.5 * dt * k2_x)
        k3_x = vel + 0.5 * dt * k2_v

        k4_v = self.compute_accelerations(pos + dt * k3_x)
        k4_x = vel + dt * k3_v

        self.positions = pos + (dt / 6.0) * (k1_x + 2*k2_x + 2*k3_x + k4_x)
        self.velocities = vel + (dt / 6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)

    def advance(self, total_time):
        # Symulacja przez zadany czas, z dopasowywaniem kroku
        t = 0.0
        while t < total_time:
            min_r = self.min_distance()
            # Mniejszy krok gdy ciała się zbliżają
            dt = min(DT_MAX, ADAPTIVE_FACTOR * min_r, total_time - t)
            if dt < DT_MIN:
                dt = DT_MIN
            self.rk4_step(dt)
            t += dt
