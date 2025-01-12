import pybullet as p
from typing import Tuple


class PhysicsEngine:
    def __init__(self, gravity: Tuple[float, float, float] = (0, -9.8, 0)) -> None:
        self.gravity = gravity
        p.connect(p.GUI)
        p.setGravity(*self.gravity)

    @staticmethod
    def add_rigid_body(shape, mass, position) -> int:
        return p.createCollisionShape(shape, mass, position)

    @staticmethod
    def update() -> None:
        p.stepSimulation()
