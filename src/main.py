from os import path

import kivy
from kivy.config import Config
from kivy.logger import Logger
from kivy.resources import resource_add_path
from kivy.factory import Factory
from kivy.core.window import Window

# PEP 396 - Module Version Numbers
__version__ = '0.1'
__author__ = 'Fernando M'

kivy.require('1.10.1')
resource_add_path(path.dirname(__file__))

PROJECT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
ICON_PATH = path.join('usr', 'share', 'pixmaps', 'debian-logo.png')
DEBUG_MODE = False
BASE_DIR = path.join(PROJECT_DIR, 'src')

Window.fullscreen = False
Config.set('graphics', 'resizable', True)
Config.set('graphics', 'height', '600')
Config.set('graphics', 'width', '800')
Config.set('kivy', 'log_level', 'debug')
Config.set('kivy', 'window_icon', ICON_PATH)

if __name__ in ('__main__', '__android__'):

	Factory.register('Application', module='config.application')
	Factory.Application().run()

	Logger.debug("Main: Exit from {}".format(__name__))
