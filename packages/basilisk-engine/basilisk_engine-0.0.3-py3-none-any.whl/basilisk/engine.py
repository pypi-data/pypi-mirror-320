import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import moderngl as mgl
from .config import Config
from .input.mouse import Mouse
import time

class Engine():
    win_size: tuple
    """Size of the engine window in pixels"""
    ctx: mgl.Context
    """ModernGL context used by the engine"""
    scene: any
    """Scene currently being updated and rendered by the engine"""
    clock: pg.Clock
    """Pygame clock used to keep track of time between frames"""
    config: Config
    """Object containing all global attributes"""
    delta_time: float
    """Time in seconds that passed between the last frame"""
    time: float
    """Total time the engine has been running"""
    running: bool
    """True if the engine is still running"""
    events: list
    """List of all pygame"""
    keys: list
    """bool list containing the state of all keys this frame"""
    previous_keys: list
    """bool list containing the state of all keys at the previous frame"""
    mouse: Mouse
    """Object containing information about the user's mouse"""
    root: str
    """Path to the root directory containing internal data"""

    def __init__(self, win_size=(800, 800), title="Basilisk Engine", vsync=False, grab_mouse=True, headless=False) -> None:
        """
        Basilisk Engine Class. Sets up the engine enviornment and allows the user to interact with Basilisk
        Args:
            win_size: tuple
                The initial window size of the engine
            title: str
                The title of the engine window
            vsync: bool
                Flag for running engine with vsync enabled
            headless: bool
                Flag for headless rendering
        """
        # Save the window size
        self.win_size = win_size

        pg.init()  
        # Initialize pygame and OpenGL attributes
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # Pygame display init
        if headless:
            pg.display.set_mode((300, 50), vsync=vsync, flags=pg.OPENGL | pg.DOUBLEBUF)
            pg.display.iconify()
        else:
            pg.display.set_mode(self.win_size, vsync=vsync, flags=pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
        pg.display.set_caption(title)
        pg.display.set_icon(pg.image.load("basilisk.png"))

        # MGL context setup
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)

        # Global attributes referenced by the handlers
        self.headless = headless
        self.set_configurations()
        self.root = os.path.dirname(__file__)
        print(self.root)

        # Time variables
        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0

        # Initialize input lists
        self.keys = pg.key.get_pressed()
        self.previous_keys = self.keys
        self.mouse = Mouse(grab=grab_mouse)

        # Scene being used by the engine
        self.scene = None

        # Set the scene to running
        self.running = True

    def update(self) -> None:
        """
        Updates all input, physics, and time variables. Renders the current scene.
        """

        # Tick the clock and get delta time
        self.delta_time = self.clock.tick() / 1000
        self.time += self.delta_time
        pg.display.set_caption(f"FPS: {round(self.clock.get_fps())}")

        # Get inputs and events
        self.events = pg.event.get()
        self.keys = pg.key.get_pressed()
        self.mouse.update(self.events)
        
        # Loop through all pygame events
        for event in self.events:
            if event.type == pg.QUIT: # Quit the engine
                self.quit()
                return
            if event.type == pg.VIDEORESIZE:
                # Updates the viewport
                self.win_size = (event.w, event.h)
                self.ctx.viewport = (0, 0, event.w, event.h)
                self.scene.camera.use()
                self.scene.frame.set_textures()


        # Update the scene if possible
        if self.scene: self.scene.update()
        # Render after the scene and engine has been updated
        self.render()

        # Update the previous input lists for the next frame
        self.previous_keys = self.keys

    def render(self) -> None:
        """
        Renders the scene currently being used by the engine
        """
        
        # Set the ctx for rendering
        self.ctx.screen.use()
        self.ctx.clear()

        # Render the scene
        if self.scene:self.scene.render()

        # Flip pygame display buffer
        pg.display.flip()

    def set_configurations(self):
        """
        Sets global configurations. These attributs are not used by the engine, just the handlers
        """

        # Create a config object
        self.config = Config()

        # Set the attributes on the config object
        setattr(self.config, "chunk_size", 40)
        setattr(self.config, "render_distance", 5)

    def quit(self) -> None:
        """
        Stops the engine and releases all memory
        """

        pg.quit()
        self.ctx.release()
        self.running = False

    @property
    def scene(self): return self._scene
    
    @scene.setter
    def scene(self, value):
        self._scene = value
        if self._scene: self._scene.set_engine(self)