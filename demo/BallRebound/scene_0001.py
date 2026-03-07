from manim import *
import numpy as np


class BallReboundSimulation(Scene):
    def construct(self):
        g = 9.81
        time_scale = 0.6

        ground_y = -3.0
        radius = 0.18

        metal_e = 0.85
        wood_e = 0.60

        initial_height = 2.6

        ground = Line(LEFT * 6, RIGHT * 6).shift(UP * ground_y)
        self.add(ground)

        metal_ball = Circle(radius=radius, color=GRAY_B, stroke_width=2)
        metal_ball.set_fill(GRAY_D, opacity=1.0)
        metal_ball.move_to(np.array([-1.2, ground_y + radius + initial_height, 0.0]))

        wood_ball = Circle(radius=radius, color="#8B4513", stroke_width=2)
        wood_ball.set_fill("#A0522D", opacity=1.0)
        wood_ball.move_to(np.array([1.2, ground_y + radius + initial_height, 0.0]))

        self.add(metal_ball, wood_ball)
        self.wait(0.2)

        def fall_time(h):
            return max(0.15, time_scale * np.sqrt(2 * max(h, 0) / g))

        def rise_time(h):
            return max(0.15, time_scale * np.sqrt(2 * max(h, 0) / g))

        metal_h = initial_height
        wood_h = initial_height

        bounces = 8
        for _ in range(bounces):
            metal_ground_pos = np.array([metal_ball.get_x(), ground_y + radius, 0.0])
            wood_ground_pos = np.array([wood_ball.get_x(), ground_y + radius, 0.0])

            self.play(
                metal_ball.animate(rate_func=rate_functions.ease_in_quad).move_to(metal_ground_pos),
                wood_ball.animate(rate_func=rate_functions.ease_in_quad).move_to(wood_ground_pos),
                run_time=max(fall_time(metal_h), fall_time(wood_h)),
            )

            metal_h = metal_h * (metal_e**2)
            wood_h = wood_h * (wood_e**2)

            metal_peak_pos = np.array([metal_ball.get_x(), ground_y + radius + metal_h, 0.0])
            wood_peak_pos = np.array([wood_ball.get_x(), ground_y + radius + wood_h, 0.0])

            self.play(
                metal_ball.animate(rate_func=rate_functions.ease_out_quad).move_to(metal_peak_pos),
                wood_ball.animate(rate_func=rate_functions.ease_out_quad).move_to(wood_peak_pos),
                run_time=max(rise_time(metal_h), rise_time(wood_h)),
            )

            if metal_h < 0.05 and wood_h < 0.05:
                break

        self.wait(1.5)