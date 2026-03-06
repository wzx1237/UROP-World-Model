
from manim import *

class NewtonsCradle(Scene):
    def construct(self):
        # Define the positions of the balls and strings
        radius = 1.5
        distance_between_balls = 2 * radius
        initial_angle = 30 * DEGREES

        # Create the balls
        balls = [Sphere(radius=radius) for _ in range(5)]
        for i, ball in enumerate(balls):
            ball.set_color(GOLD)
            ball.move_to(RIGHT * (i + 1) * distance_between_balls)

        # Create the strings
        strings = []
        for i, ball in enumerate(balls):
            if i == 0:
                string = Line(ORIGIN, UP * radius, color=WHITE)
            else:
                string = Line(ball.get_center(), UP * radius, color=WHITE)
            string.add_updater(lambda m, dt: m.put_start_and_end_on(m.start, ball.get_center()))
            strings.append(string)

        # Add the balls and strings to the scene
        self.add(*balls, *strings)

        # Initial position of the first ball
        initial_position = balls[0].get_center()

        # Animation loop
        while True:
            # Move the first ball to its initial position
            self.play(MoveTo(balls[0], initial_position), run_time=1)

            # Release the first ball
            self.play(
                ApplyForceToMobject(balls[0], -DOWN * 10),
                run_time=0.5,
                rate_func=sine_half_wave
            )

            # Wait for the animation to finish
            self.wait(1)

            # Check if the last ball has lost too much momentum
            if abs(balls[-1].get_velocity()[1]) < 0.1:
                break

# Run the scene
newtons_cradle = NewtonsCradle()
newtons_cradle.render()
