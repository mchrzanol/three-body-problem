# Stałe używane w całej aplikacji

G = 1.0  # stała grawitacji (w umownych jednostkach)
SOFTENING = 1e-4  # mała wartość żeby nie dzielić przez zero
SIM_TIME_PER_FRAME = 0.01  # ile "czasu fizyki" na jedną klatkę
DT_MAX = 2e-4  # największy krok RK4
DT_MIN = 1e-6  # najmniejszy krok RK4
ADAPTIVE_FACTOR = 0.04  # zmniejsza krok gdy ciała są blisko
TRAIL_LENGTH = 600  # ile punktów śladu zostawiać
TRAIL_SEGMENTS = 30  # na ile kawałków podzielić ślad (do efektu zanikania)
FPS = 60  # klatki na sekundę
