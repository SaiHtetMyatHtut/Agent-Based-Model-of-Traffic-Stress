from __future__ import annotations

from typing import Any

import numpy as np


DEFAULT_CONFIG = {
    "simulation_minutes": 5,
    "cars_per_second": 6.0,
    "road_lanes": 3,
    "traffic_light_seconds": 45,
    "seed": 7,
    "dt": 0.05,
    "eta": 0.85,
    "alpha": 0.65,
    "omega": 0.55,
}


def config_from_mapping(data: dict[str, Any] | None) -> dict[str, Any]:
    data = data or {}
    config = dict(DEFAULT_CONFIG)
    config["simulation_minutes"] = int(np.clip(int(data.get("simulation_minutes", config["simulation_minutes"])), 1, 12))
    config["cars_per_second"] = float(np.clip(float(data.get("cars_per_second", config["cars_per_second"])), 0.2, 24.0))
    config["road_lanes"] = int(np.clip(int(data.get("road_lanes", config["road_lanes"])), 1, 5))
    config["traffic_light_seconds"] = int(
        np.clip(int(data.get("traffic_light_seconds", config["traffic_light_seconds"])), 15, 120)
    )
    config["seed"] = int(np.clip(int(data.get("seed", config["seed"])), 0, 999_999))
    return config


def rounded_list(values: np.ndarray) -> list[float]:
    return np.round(values.astype(float), 5).tolist()


def run_simulation(config: dict[str, Any]) -> dict[str, Any]:
    rng = np.random.default_rng(config["seed"])

    total_steps = int(config["simulation_minutes"] * 60)
    dt = config["dt"]
    eta = config["eta"]
    alpha_param = config["alpha"]
    omega = config["omega"]

    road_capacity_cars = config["road_lanes"] * 12
    cars_can_pass_each_second = max(1, config["road_lanes"] * 2)
    road_capacity_score = config["road_lanes"] / 5

    cars_arriving = np.zeros(total_steps)
    cars_waiting = np.zeros(total_steps)
    cars_passing = np.zeros(total_steps)
    road_capacity = np.ones(total_steps) * road_capacity_score

    traffic_light = np.empty(total_steps, dtype=object)

    A = np.zeros(total_steps)
    B = np.zeros(total_steps)
    C = np.zeros(total_steps)
    X = np.zeros(total_steps)
    Y = np.zeros(total_steps)
    S = np.zeros(total_steps)
    traffic_stress = np.zeros(total_steps)

    waiting_queue = 0

    for t in range(total_steps):
        arriving_now = int(rng.poisson(config["cars_per_second"]))
        waiting_queue += arriving_now

        green_light = (t // config["traffic_light_seconds"]) % 2 == 0
        
        if green_light:
            traffic_light[t] = "green"
            passed_now = min(waiting_queue, cars_can_pass_each_second)
            waiting_queue -= passed_now
        else:
            traffic_light[t] = "red"
            passed_now = 0

        cars_arriving[t] = arriving_now
        cars_waiting[t] = waiting_queue
        cars_passing[t] = passed_now

        A[t] = min(cars_arriving[t] / road_capacity_cars, 1)
        B[t] = min(cars_waiting[t] / road_capacity_cars, 1)
        C[t] = road_capacity[t]

        X[t] = alpha_param * B[t] + (1 - alpha_param) * A[t]
        Y[t] = (omega * A[t] + omega * B[t]) * (1 - C[t])
        S[t] = X[t] * (1 - Y[t])

    traffic_stress[0] = 0.1
    for t in range(1, total_steps):
        traffic_stress[t] = traffic_stress[t - 1] + eta * (S[t - 1] - traffic_stress[t - 1]) * dt

    time_steps = np.arange(total_steps)

    frames = []
    for t in range(total_steps):
        frames.append(
            {
                "step": int(t),
                "time_seconds": int(t),
                "signal": {
                    "phase": traffic_light[t],
                    "seconds_remaining": int(config["traffic_light_seconds"] - (t % config["traffic_light_seconds"])),
                },
                "metrics": {
                    "cars_arriving": int(cars_arriving[t]),
                    "cars_waiting": int(cars_waiting[t]),
                    "cars_passing": int(cars_passing[t]),
                    "stress": round(float(traffic_stress[t]), 5),
                },
            }
        )

    summary = {
        "total_steps": total_steps,
        "total_arriving_cars": int(np.sum(cars_arriving)),
        "total_passing_cars": int(np.sum(cars_passing)),
        "cars_left_waiting": int(cars_waiting[-1]),
        "road_capacity_cars": int(road_capacity_cars),
        "cars_can_pass_each_second": int(cars_can_pass_each_second),
        "peak_waiting_cars": int(np.max(cars_waiting)),
        "peak_stress": round(float(np.max(traffic_stress)), 5),
        "average_waiting_cars": round(float(np.mean(cars_waiting)), 2),
        "throughput_cars_per_second": round(float(np.sum(cars_passing) / total_steps), 3),
    }

    return {
        "config": dict(config),
        "summary": summary,
        "frames": frames,
        "timeline": {
            "step": time_steps.astype(int).tolist(),
            "time_seconds": time_steps.astype(int).tolist(),
            "cars_arriving": cars_arriving.astype(int).tolist(),
            "cars_waiting": cars_waiting.astype(int).tolist(),
            "road_capacity": rounded_list(road_capacity),
            "cars_passing": cars_passing.astype(int).tolist(),
            "traffic_stress": rounded_list(traffic_stress),
            "stress": rounded_list(traffic_stress),
            "A": rounded_list(A),
            "B": rounded_list(B),
            "C": rounded_list(C),
            "X": rounded_list(X),
            "Y": rounded_list(Y),
            "S": rounded_list(S),
        },
        "equations": {
            "A": "arriving cars score = cars_arriving[t] / road_capacity_cars",
            "B": "waiting cars score = cars_waiting[t] / road_capacity_cars",
            "C": "road capacity score, from 0.2 for 1 lane to 1.0 for 5 lanes",
            "X": "alpha * B[t] + (1 - alpha) * A[t]",
            "Y": "(omega * A[t] + omega * B[t]) * (1 - C[t])",
            "S": "instant traffic stress score = X[t] * (1 - Y[t])",
            "traffic_stress": "smoothed traffic stress = traffic_stress[t-1] + eta * (S[t-1] - traffic_stress[t-1]) * dt",
        },
    }
