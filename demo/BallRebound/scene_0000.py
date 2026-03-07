
from manim import *

config.frame_rate = 30


class BouncingBall(VGroup):
    def __init__(
        self,
        *,
        radius_m,
        initial_height_m,
        rebound_factor,
        gravity_m_s2,
        friction,
        ground_y,
        scale,
        x0,
        fill_color,
        stroke_color=WHITE,
    ):
        super().__init__()
        self.scale_units = scale
        self.radius = radius_m * scale
        self.initial_height = initial_height_m * scale
        self.rebound_factor = rebound_factor
        self.gravity = gravity_m_s2 * scale
        self.friction = friction
        self.ground_y = ground_y
        self.x0 = x0

        self.ball = Circle(radius=self.radius, stroke_color=stroke_color, stroke_width=2)
        self.ball.set_fill(fill_color, opacity=1.0)
        self.add(self.ball)

        self.vy = 0.0
        self.stopped = False
        self.reset()

        self.add_updater(self._physics_step)

    def reset(self):
        self.vy = 0.0
        self.stopped = False
        self.move_to([self.x0, self.ground_y + self.radius + self.initial_height, 0])

    def _physics_step(self, mob, dt):
        if self.stopped:
            return

        self.vy -= self.gravity * dt
        self.vy *= max(0.0, 1.0 - self.friction * dt)

        mob.shift(UP * (self.vy * dt))

        y = mob.get_center()[1]
        if y - self.radius <= self.ground_y:
            mob.move_to([mob.get_center()[0], self.ground_y + self.radius, 0])

            if abs(self.vy) < 0.15:
                self.vy = 0.0
                self.stopped = True
            else:
                self.vy = -self.vy * self.rebound_factor


class TwoBallsBounce(Scene):
    def construct(self):
        gravity = 9.81
        friction = 0.1
        fps = 30
        total_frames = 100
        loop = True

        scale = 3.0
        ground_y = -3.0

        ground = Line(
            start=[-7, ground_y, 0],
            end=[7, ground_y, 0],
            stroke_width=6,
            color=GRAY_B,
        )
        self.add(ground)

        metal_ball = BouncingBall(
            radius_m=0.1,
            initial_height_m=1.0,
            rebound_factor=0.85,
            gravity_m_s2=gravity,
            friction=friction,
            ground_y=ground_y,
            scale=scale,
            x0=-2.0,
            fill_color=GRAY_C,
            stroke_color=GRAY_A,
        )

        wood_ball = BouncingBall(
            radius_m=0.1,
            initial_height_m=1.0,
            rebound_factor=0.65,
            gravity_m_s2=gravity,
            friction=friction,
            ground_y=ground_y,
            scale=scale,
            x0=2.0,
            fill_color="#8B5A2B",
            stroke_color=MAROON_B,
        )

        self.add(metal_ball, wood_ball)

        balls = [metal_ball, wood_ball]

        if loop:
            controller = Dot(radius=0.01, fill_opacity=0.0, stroke_opacity=0.0)

            def loop_updater(m, dt):
                if all(b.stopped for b in balls):
                    for b in balls:
                        b.reset()

            controller.add_updater(loop_updater)
            self.add(controller)

        self.wait(total_frames / fps)
