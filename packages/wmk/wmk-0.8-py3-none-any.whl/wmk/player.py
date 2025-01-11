import pyglet
from typing import Optional, Callable, Any

class Player(pyglet.window.Window):
    def __init__(self,
                 frame_generator: Callable[[Any, float], Any], 
                 fps_max: int = 30,
                 fps_display: bool = False,
                 mouse_sensitivity: float = 1.0,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.frame_generator: Callable = frame_generator
        self.keyboard_state = pyglet.window.key.KeyStateHandler()
        self.mouse_state = pyglet.window.mouse.MouseStateHandler()
        self.keys_pressed = set()
        self.mouse_movement = { 'dx': 0, 'dy': 0 }
        self.mouse_sensitivity: float = mouse_sensitivity
        self.fps_max: float = fps_max
        if fps_display:
            self.fps_display = pyglet.window.FPSDisplay(window=self, samples=10)
        else:
            self.fps_display = None

        self.push_handlers(self.keyboard_state)
        self.push_handlers(self.mouse_state)
        
        # Set up the sprite for frame display
        self.sprite: Optional[pyglet.sprite.Sprite] = None

        # Schedule the update function
        pyglet.clock.schedule_interval(self.update, 1.0/fps_max)

    def render_frame(self, frame: Any) -> None:
        # Convert numpy array to pyglet image
        height, width = frame.shape[:2]
        img = pyglet.image.ImageData(width, height, 'RGB', frame.tobytes())
        scale_x = self.width / width
        scale_y = self.height / height
        # Create or update sprite
        if self.sprite:
            self.sprite.delete()
        self.sprite = pyglet.sprite.Sprite(img)
        self.sprite.scale = min(scale_x, scale_y)

    def on_draw(self) -> None:
        self.clear()
        if self.sprite:
            self.sprite.draw()
        if self.fps_display:
            self.fps_display.draw()
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.mouse_movement['dx'] += dx * self.mouse_sensitivity
        self.mouse_movement['dy'] += dy * self.mouse_sensitivity

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        self.keys_pressed.add(button)
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        self.keys_pressed.add(symbol)

    def update(self, dt: float) -> None:
        frame = self.frame_generator(self, dt)
        if frame is None:
            pyglet.app.exit()
            return

        # Reset mouse movement
        self.mouse_movement['dx'] = 0
        self.mouse_movement['dy'] = 0
        # Reset keys pressed
        keys_pressed = self.keys_pressed
        self.keys_pressed = set()
        for key in keys_pressed:
            if self.keyboard_state[key] or self.mouse_state[key]:
                self.keys_pressed.add(key)

        self.render_frame(frame)

    def run(self) -> bool:
        self.activate()
        self.set_exclusive_mouse(True)
        pyglet.app.run()
        return False