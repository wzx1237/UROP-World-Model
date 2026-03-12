
from manim import *
import numpy as np


class NewtonsCradle(Scene):
    def construct(self):
        n_balls = 5
        spacing = 0.75
        ball_radius = 0.18
        string_length = 2.2

        frame = RoundedRectangle(width=6.5, height=0.8, corner_radius=0.15)
        frame.set_stroke(WHITE, width=4)
        frame.move_to(UP * 2.6)

        pivot_y = frame.get_bottom()[1]
        start_x = -spacing * (n_balls - 1) / 2
        pivots = [np.array([start_x + i * spacing, pivot_y, 0.0]) for i in range(n_balls)]

        angles = [ValueTracker(0.0) for _ in range(n_balls)]

        def offset(theta):
            return string_length * np.array([np.sin(theta), -np.cos(theta), 0.0])

        balls = VGroup()
        for i in range(n_balls):
            b = Circle(radius=ball_radius)
            b.set_fill(GREY_D, opacity=1)
            b.set_stroke(GREY_A, width=2)
            b.add_updater(lambda m, i=i: m.move_to(pivots[i] + offset(angles[i].get_value())))
            balls.add(b)

        strings = VGroup(
            *[
                always_redraw(lambda i=i: Line(pivots[i], balls[i].get_center(), stroke_width=2))
                for i in range(n_balls)
            ]
        )

        self.play(FadeIn(frame), FadeIn(strings), FadeIn(balls), run_time=1.0)

        pull_angle = 0.85

        self.play(angles[0].animate.set_value(pull_angle), run_time=0.8, rate_func=smooth)

        for _ in range(4):
            self.play(angles[0].animate.set_value(0.0), run_time=0.55, rate_func=linear)
            self.play(angles[-1].animate.set_value(-pull_angle), run_time=0.45, rate_func=linear)
            self.play(angles[-1].animate.set_value(0.0), run_time=0.55, rate_func=linear)
            self.play(angles[0].animate.set_value(pull_angle), run_time=0.45, rate_func=linear)

        self.play(angles[0].animate.set_value(0.0), run_time=0.6, rate_func=linear)
        self.wait(1.5)
