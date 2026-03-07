from manim import *
import numpy as np


class ReboundingBalls(Scene):
    def construct(self):
        floor_y = -3.2
        left_x = -6.6
        right_x = 6.6

        floor = Line([left_x, floor_y, 0], [right_x, floor_y, 0], color=GRAY)
        self.add(floor)

        metal_ball = Circle(radius=0.18, color=BLUE, fill_opacity=1.0).move_to([-1.5, 2.5, 0])
        wood_ball = Circle(radius=0.18, color=RED, fill_opacity=1.0).move_to([1.5, 2.5, 0])
        self.add(metal_ball, wood_ball)

        g = np.array([0.0, -9.8, 0.0])
        e_metal = 0.9
        e_wood = 0.6
        e_wall = 0.85

        v_metal = np.array([0.6, 0.0, 0.0])
        v_wood = np.array([-0.4, 0.0, 0.0])

        def make_updater(ball, v_ref, restitution):
            r = ball.radius

            def updater(mobj, dt):
                nonlocal v_ref
                if dt <= 0:
                    return

                v_ref = v_ref + g * dt
                mobj.shift(v_ref * dt)

                x, y, _ = mobj.get_center()

                if y - r <= floor_y:
                    y = floor_y + r
                    mobj.move_to([x, y, 0])
                    if v_ref[1] < 0:
                        v_ref[1] = -restitution * v_ref[1]
                        v_ref[0] *= 0.98

                if x - r <= left_x:
                    x = left_x + r
                    mobj.move_to([x, y, 0])
                    if v_ref[0] < 0:
                        v_ref[0] = -e_wall * v_ref[0]

                if x + r >= right_x:
                    x = right_x - r
                    mobj.move_to([x, y, 0])
                    if v_ref[0] > 0:
                        v_ref[0] = -e_wall * v_ref[0]

            return updater

        metal_ball.add_updater(make_updater(metal_ball, v_metal, e_metal))
        wood_ball.add_updater(make_updater(wood_ball, v_wood, e_wood))

        self.wait(10)

        metal_ball.clear_updaters()
        wood_ball.clear_updaters()
        self.wait(1)