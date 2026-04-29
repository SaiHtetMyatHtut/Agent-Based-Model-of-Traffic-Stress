# Traffic Congestion Graph Model

This project simulates traffic congestion on one simple road lane controlled by a traffic light. The model follows a professor-style time-step structure: define arrays, update cars arriving and cars waiting, calculate road capacity variables, then calculate traffic stress over time.

## Run

```powershell
uv sync
uv run python -m uvicorn server:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

If port `8000` is already occupied, run:

```powershell
uv run python -m uvicorn server:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

## Model Structure

- Main model file: `model.py`.
- Web/API wrapper: `server.py`.
- System: one road lane with one traffic light.
- Time step: one simulation step equals one second.
- Cars arriving: number of cars reaching the traffic light each second.
- Cars waiting: number of cars stopped because the light is red or the lane is too busy.
- Road capacity: based on lane count from 1 to 5.
- Traffic light: alternates between green and red.
- Graphs: traffic stress, cars arriving, cars waiting, cars passing the light, and equation inputs.

## Core Equations

```text
A[t] = arriving cars score = cars_arriving[t] / road_capacity_cars
B[t] = waiting cars score = cars_waiting[t] / road_capacity_cars
C[t] = road capacity score

X[t] = alpha * B[t] + (1 - alpha) * A[t]
Y[t] = (omega * A[t] + omega * B[t]) * (1 - C[t])
S[t] = instant traffic stress score = X[t] * (1 - Y[t])

traffic_stress[t] = traffic_stress[t-1] + eta * (S[t-1] - traffic_stress[t-1]) * dt
```

The structure is intentionally close to the class example: arrays are updated through a time loop, and the final output is a graph of stress over time.

## Report Fit

Suggested final report title:

```text
Data Analytics in Agent-Based Modeling for Traffic Congestion Prediction
```

Suggested structure:

- Introduction: traffic congestion as a human-environment system.
- Theory Selection: one road lane with traffic-light control.
- Literature Review: congestion, queue formation, road capacity, and traffic-light timing.
- Methodology: `model.py`, cars arriving, cars waiting, road capacity, red/green light phases, and stress equations.
- Results and Analysis: compare light traffic, busy traffic, wider roads, and longer traffic-light duration.
- Conclusion: explain how arrival rate, waiting cars, and road capacity affect congestion stress.
