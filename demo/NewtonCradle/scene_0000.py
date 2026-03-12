
from manim import *
import numpy as np

config.background_color = "#111318"


class NewtonsCradle(MovingCameraScene):
    def construct(self):
        g = 9.81
        L = 4.2
        omega = np.sqrt(g / L)

        theta0 = np.deg2rad(30.0)
        loss = 0.85

        T = 2 * np.pi / omega
        q = T / 4.0
        h = T / 2.0

        R = 0.28
        spacing = 2.0 * R

        pivot_y = 5.2
        rest_y = pivot_y - L

        pivots = []
        rest_xs = []
        for i in range(5):
            x = (i - 2) * spacing
            pivots.append(np.array([x, pivot_y, 0.0]))
            rest_xs.append(x)

        t_tracker = ValueTracker(0.0)

        def get_angles(t):
            t = max(0.0, float(t))
            a = [0.0] * 5

            if t < q:
                a[0] = -theta0 * np.cos(omega * t)
                return a

            t1 = t - q
            m = int(np.floor(t1 / h))
            dt = t1 - m * h

            amp = theta0 * (loss ** (m + 1))
            s = amp * np.sin(omega * dt)

            if m % 2 == 0:
                a[4] = s
            else:
                a[0] = -s

            return a

        def ball_pos(i, t):
            th = get_angles(t)[i]
            p = pivots[i]
            return np.array([p[0] + L * np.sin(th), p[1] - L * np.cos(th), 0.0])

        def make_ball():
            base = Circle(
                radius=R,
                stroke_width=2.5,
                stroke_color=GREY_D,
                fill_opacity=1.0,
            ).set_fill(color=GREY_B)

            glow1 = Circle(
                radius=0.45 * R,
                stroke_width=0,
                fill_opacity=0.35,
                fill_color=WHITE,
            ).shift(0.22 * R * LEFT + 0.22 * R * UP)

            glow2 = Circle(
                radius=0.18 * R,
                stroke_width=0,
                fill_opacity=0.25,
                fill_color=WHITE,
            ).shift(0.38 * R * LEFT + 0.35 * R * UP)

            return VGroup(base, glow1, glow2)

        balls = VGroup()
        for i in range(5):
            b = make_ball()
            b.move_to(np.array([rest_xs[i], rest_y, 0.0]))
            b.add_updater(lambda mob, i=i: mob.move_to(ball_pos(i, t_tracker.get_value())))
            balls.add(b)

        strings = VGroup()
        for i in range(5):
            def make_string(ii=i):
                return always_redraw(
                    lambda: Line(
                        pivots[ii],
                        ball_pos(ii, t_tracker.get_value()) + R * UP,
                        stroke_width=2.0,
                        stroke_color=GREY_C,
                    )
                )

            strings.add(make_string(i))

        self.camera.frame.shift(DOWN * 0.2)

        self.add(strings, balls)

        total_time = 20.0
        self.play(
            t_tracker.animate.set_value(total_time),
            run_time=total_time,
            rate_func=linear,
        )
        self.wait(0.5)
