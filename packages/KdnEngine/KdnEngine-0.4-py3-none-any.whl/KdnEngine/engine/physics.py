import pybullet as p
from typing import Tuple


class PhysicsEngine:
    def __init__(self, gravity: Tuple[float, float] = (0, 9.8)) -> None:
        self.gravity = gravity

    def apply_gravity(self, velocity: Tuple[float, float]) -> Tuple[float, float]:
        vx, vy = velocity
        gx, gy = self.gravity
        return vx + gx, vy + gy

    def update(self) -> None:
        p.stepSimulation()
        # Add physics update logic here
