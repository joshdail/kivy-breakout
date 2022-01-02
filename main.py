from kivy.app import App
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window

Window.size = (550, 450)


# The blocks that the player has to break
class Block(Widget):

    def check_collision(self, ball):
        if self.collide_widget(ball):
            if ball.y <= self.y + self.height or ball.y + ball.height >= self.y:
                ball.velocity_y *= -1
            elif ball.x <= self.x + self.width or ball.x + ball.width >= self.x:
                ball.velocity_x *= -1
            return True
        return False


# The paddle that the player controls
class Paddle(Widget):

    def check_collision(self, ball):
        if self.collide_widget(ball):
            ball.velocity_y *= -1


class Ball(Widget):

    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # Moves the ball one step. This will be called in equal intervals to animate the ball

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class BreakoutGame(Widget):
    ball = ObjectProperty(None)
    paddle = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BreakoutGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.served = False
        self.won = False
        self.blocks = []

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Keycode is a tuple where [0] is numeric and [1] is text string
        if keycode[1] == 'spacebar' and not self.served:
            self.serve_ball()
        elif keycode[1] == 'right' and self.paddle.x <= self.width - self.paddle.width:
            self.paddle.x += 15
            if not self.served:
                self.ball.x += 15
        elif keycode[1] == 'left' and self.paddle.x >= 0:
            self.paddle.x -= 15
            if not self.served:
                self.ball.x -= 15

    def on_touch_move(self, touch):
        if touch.y <= self.width / 4:
            self.paddle.x = touch.x
            if not self.served:
                self.ball.x = self.paddle.x + 20

    def place_blocks(self):
        for i in range(5):
            for j in range(9):
                block = Block()
                block.x = block.width * j + 10 * j + 10
                block.y = 350 - (block.height * i) - 10 * i - 10
                block_index = (i + 1) * j
                self.add_widget(block, block_index)
                self.blocks.append(block)

    def serve_ball(self, vel=(2, 2)):
        self.ball.velocity = vel
        self.served = True

    def update(self, dt):
        self.ball.move()
        self.paddle.check_collision(self.ball)
        for block in self.blocks:
            if block.check_collision(self.ball):
                self.remove_widget(block)
                self.blocks.remove(block)

        # check wall collisions
        if self.ball.x <= 0 or self.ball.x >= self.width - self.ball.width:
            self.ball.velocity_x *= -1
        if self.ball.top >= self.height:
            self.ball.velocity_y *= -1
        if self.ball.top <= 0:
            self.reset_game()

        # Check if game is won
        if len(self.blocks) == 0:
            self.reset_game()
            self.won = True

    # Reset ball, paddle, and blocks
    def reset_game(self):
        self.ball.velocity_x = 0
        self.ball.velocity_y = 0
        self.ball.x = self.center_x - 5
        self.ball.y = 30
        self.paddle.x = self.center_x - 25
        self.paddle.y = 20
        if self.won:
            for block in self.blocks:
                self.remove_widget(block)
                self.blocks.remove(block)
            self.place_blocks()
        self.served = False


class BreakoutApp(App):

    def build(self):
        game = BreakoutGame()
        game.place_blocks()
        Clock.schedule_interval(game.update, 1.0/60.0)
        return game


if __name__ == '__main__':
    BreakoutApp().run()
