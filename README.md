# Problem Trzech Ciał — Symulator 2D

Projekt zaliczeniowy z fizyki na Politechnice Warszawskiej.

Program symuluje klasyczny **problem trzech ciał** — układ trzech mas oddziałujących grawitacyjnie zgodnie z prawem powszechnego ciążenia Newtona. Problem ten, w przeciwieństwie do zagadnienia dwóch ciał, nie ma ogólnego rozwiązania analitycznego (Poincaré, 1889) i w większości przypadków jest chaotyczny. Istnieje jednak skończona liczba znanych orbit periodycznych, które program pozwala obejrzeć.

## O projekcie

- **Uczelnia:** Politechnika Warszawska
- **Przedmiot:** Fizyka
- **Cel:** demonstracja numerycznego rozwiązywania równań ruchu Newtona dla układu trzech ciał oraz wizualizacja znanych stabilnych konfiguracji orbitalnych.

## Co potrafi

- Symulacja grawitacji Newtona dla 3 ciał w 2D
- Całkowanie metodą **Runge-Kutta 4. rzędu** z adaptacyjnym krokiem (mniejszy krok przy bliskich spotkaniach)
- Gotowe układy orbitalne:
  - **Ósemka (Figure-8)** — orbita Chencinera-Montgomery'ego (2000)
  - **Trójkąt Lagrange'a** — 3 równe masy w trójkącie równobocznym
  - **Orbita Ćmy (Moth I)** — z katalogu Šuvakova-Dmitrašinovića (2013)
  - **Trójkąt Lagrange'a z masami 1:2:3** — uogólniony Lagrange
  - **Orbita Broucke'a A1** — periodyczna orbita kolinearna
- Ręczna edycja mas, pozycji i prędkości każdego ciała
- Animowane orbity z efektem zanikającego śladu
- Zoom i auto-dopasowanie widoku

## Wymagania

- Python 3.8+
- PyQt5
- pyqtgraph
- numpy

Instalacja:

```bash
pip install PyQt5 pyqtgraph numpy
```

## Uruchomienie

```bash
python main.py
```

## Struktura projektu

```
three_body/
├── main.py         # punkt wejścia aplikacji
├── config.py       # stałe fizyczne i parametry symulacji
├── physics.py      # silnik fizyczny (grawitacja + RK4)
├── presets.py      # gotowe układy startowe
├── gui.py          # okno i panel sterowania (PyQt5)
└── README.md
```

## Trochę fizyki

Każde z trzech ciał porusza się zgodnie z drugą zasadą dynamiki Newtona pod wpływem przyciągania grawitacyjnego od dwóch pozostałych:

```
        m_j * (r_j - r_i)
a_i = G * Σ ─────────────────
       j≠i  |r_j - r_i|³
```

Równania ruchu są całkowane numerycznie metodą RK4. Dodatkowo używamy małego parametru *softening* w mianowniku (`r² → r² + ε²`), żeby uniknąć osobliwości przy bardzo bliskich zbliżeniach ciał.

## Sterowanie

- **Start / Pauza / Reset** — uruchamianie symulacji
- **Lista presetów** — wybór gotowego układu
- **Pola ciał 1, 2, 3** — ręczna zmiana masy, pozycji i prędkości
- **Zoom +/−, Dopasuj** — sterowanie widokiem (można też używać kółka myszy)

## Źródła

- Chenciner, A., Montgomery, R. (2000). *A remarkable periodic solution of the three-body problem in the case of equal masses.* Annals of Mathematics.
- Šuvakov, M., Dmitrašinović, V. (2013). *Three classes of Newtonian three-body planar periodic orbits.* Physical Review Letters.
- Broucke, R. (1975). *On relative periodic solutions of the planar general three-body problem.* Celestial Mechanics.
