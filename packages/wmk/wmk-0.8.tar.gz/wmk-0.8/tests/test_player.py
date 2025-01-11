import unittest
import numpy as np
import pyglet
from unittest.mock import Mock, patch
from wmk.player import Player

class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        self.frame_generator = Mock(return_value=self.mock_frame)
        self.player = Player(frame_generator=self.frame_generator, width=800, height=600)

    def test_player_initialization(self) -> None:
        self.assertEqual(self.player.width, 800)
        self.assertEqual(self.player.height, 600)
        self.assertEqual(self.player.fps_max, 30)
        self.assertEqual(self.player.mouse_sensitivity, 1.0)
        self.assertIsInstance(self.player.keyboard_state, pyglet.window.key.KeyStateHandler)
        self.assertIsInstance(self.player.mouse_state, pyglet.window.mouse.MouseStateHandler)
        self.assertEqual(self.player.mouse_movement, {'dx': 0, 'dy': 0})

    def test_player_initialization_with_custom_params(self) -> None:
        player = Player(frame_generator=self.frame_generator,
                        width=1024,
                        height=768,
                        fps_max=60,
                        mouse_sensitivity=2.0)
        self.assertEqual(player.fps_max, 60)
        self.assertEqual(player.mouse_sensitivity, 2.0)
        player.close()

    @patch('pyglet.sprite.Sprite')
    def test_render_frame(self, mock_sprite: Mock) -> None:
        self.player.render_frame(self.mock_frame)
        self.assertIsNotNone(self.player.sprite)

    def test_update(self) -> None:
        self.player.update(1/30)
        self.frame_generator.assert_called_once_with(self.player, 1/30)

    @patch('pyglet.app.exit')
    def test_update_exits_on_none_frame(self, mock_exit: Mock) -> None:
        self.frame_generator.return_value = None
        self.player.update(1/30)
        mock_exit.assert_called_once()

    def test_on_mouse_motion(self) -> None:
        self.player.on_mouse_motion(10, 20, 30, 40)
        self.assertEqual(self.player.mouse_movement, {'dx': 30, 'dy': 40})

    @patch('pyglet.app.run')
    def test_run(self, mock_run: Mock) -> None:
        result = self.player.run()
        mock_run.assert_called_once()
        self.assertFalse(result)

    def test_on_key_press(self) -> None:
        self.player.on_key_press(pyglet.window.key.A, 0)
        self.assertIn(pyglet.window.key.A, self.player.keys_pressed)

    def test_on_mouse_press(self) -> None:
        self.player.on_mouse_press(100, 100, pyglet.window.mouse.LEFT, 0)
        self.assertIn(pyglet.window.mouse.LEFT, self.player.keys_pressed)

    def test_update_removes_released_keys(self) -> None:
        # Add a key
        self.player.keys_pressed.add(pyglet.window.key.A)
        # Update should remove the key
        self.player.update(1/30)
        self.assertNotIn(pyglet.window.key.A, self.player.keys_pressed)

    def test_update_resets_mouse_movement(self) -> None:
        self.player.mouse_movement = {'dx': 10, 'dy': 20}
        self.player.update(1/30)
        self.assertEqual(self.player.mouse_movement, {'dx': 0, 'dy': 0})

    def tearDown(self) -> None:
        self.player.close()

if __name__ == '__main__':
    unittest.main()
