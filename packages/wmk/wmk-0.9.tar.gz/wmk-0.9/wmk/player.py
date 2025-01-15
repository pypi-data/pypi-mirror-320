import pyglet
from typing import Optional, Callable, Any

class Player(pyglet.window.Window):
    """A window class for displaying and controlling frame-based content using Pyglet.
    
    This class provides a window interface for rendering frames and handling user input,
    making it suitable for video playback, game development, or any application requiring
    frame-by-frame display with user interaction.

    The Player class manages:
        * Frame rendering with automatic scaling
        * Keyboard and mouse input handling
        * FPS control and display
        * Window lifecycle management

    Example:
        Basic usage with a frame generator function::

            def generate_frames(player, dt):
                # Create or return your frame as a numpy array
                frame = create_frame()
                return frame

            # Create and run the player
            player = Player(
                frame_generator=generate_frames,
                fps_max=30,
                width=800,
                height=600,
                caption="My Player Window"
            )
            player.run()

    Args:
        frame_generator: Function that takes (player, dt) and returns a frame
        fps_max: Maximum frames per second (default: 30)
        fps_display: Whether to show FPS counter (default: False)
        mouse_sensitivity: Mouse movement multiplier (default: 1.0)
        **kwargs: Additional arguments passed to :class:`pyglet.window.Window`

    Note:
        The frame_generator function should return frames as numpy arrays in RGB format.
        Return None from the frame generator to gracefully exit the player.
    """

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

        # Store clock event for cleanup
        self._update_clock = pyglet.clock.schedule_interval(self.update, 1.0/fps_max)

    def on_draw(self) -> None:
        """
        Handle window drawing events.
        
        Called by Pyglet's event loop when the window needs to be redrawn.
        Draws the current sprite and FPS display if enabled.

        :inherited: from :class:`pyglet.window.Window`
        """
        self.clear()
        if self.sprite:
            self.sprite.draw()
        if self.fps_display:
            self.fps_display.draw()
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        Handle mouse movement events.

        Args:
            x: Current mouse X position
            y: Current mouse Y position
            dx: Change in X position since last event
            dy: Change in Y position since last event
        
        :inherited: from :class:`pyglet.window.Window`
        """
        self.mouse_movement['dx'] += dx * self.mouse_sensitivity
        self.mouse_movement['dy'] += dy * self.mouse_sensitivity

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """
        Handle mouse button press events.

        Args:
            x: Mouse X position at time of press
            y: Mouse Y position at time of press
            button: Button that was pressed
            modifiers: Keyboard modifiers active during press
        """
        self.keys_pressed.add(button)
    
    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """
        Handle keyboard key press events.

        Args:
            symbol: Key that was pressed
            modifiers: Keyboard modifiers active during press

        :inherited: from :class:`pyglet.window.Window`
        """
        self.keys_pressed.add(symbol)

    def update(self, dt: float) -> None:
        """
        Update the window state and content.

        Called periodically based on fps_max setting. Generates new frames
        and updates input states.

        Args:
            dt: Time elapsed since last update in seconds
        """
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
        del keys_pressed

        # Update sprite with new frame
        # Convert numpy array to pyglet image
        height, width = frame.shape[:2]
        img = pyglet.image.ImageData(width, height, 'RGB', frame.tobytes())
        scale_x = self.width / width
        scale_y = self.height / height
        # Create or update sprite
        if self.sprite:
            self.sprite.delete()  # Ensure old sprite is deleted before creating new one
            del self.sprite

        self.sprite = pyglet.sprite.Sprite(img)
        self.sprite.scale = min(scale_x, scale_y)

    def close(self) -> None:
        """
        Clean up resources used by the player.
        
        This method should be called when the player is no longer needed.

        :inherited: from :class:`pyglet.window.Window`
        """
        if self._update_clock:
            pyglet.clock.unschedule(self._update_clock)
        
        if self.sprite:
            self.sprite.delete()
            self.sprite = None
            
        if self.fps_display:
            self.fps_display = None
            
        # Remove event handlers
        self.remove_handlers(self.keyboard_state)
        self.remove_handlers(self.mouse_state)
        
        super().close()

    def __del__(self) -> None:
        """Ensure resources are cleaned up when the object is deleted."""
        self.close()

    def run(self) -> bool:
        """
        Run the game window and start the game loop.
        Activates the window, sets exclusive mouse mode, and starts the game loop using
        pyglet's application runner. The window will be closed and False returned when 
        the game loop ends or if an exception occurs.

        Returns:
            bool: False after the game loop ends.
            
        Note:

            Setting exclusive mouse mode captures the mouse pointer within the game window.

        :inherited: from :class:`pyglet.window.Window`
        """
        try:
            self.activate()
            self.set_exclusive_mouse(True)
            pyglet.app.run()
        finally:
            self.close()
            return False