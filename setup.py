from distutils.core import setup, Extension

# define the extension module
pokerstars_players_module = Extension('pokerstars_players', sources=['pokerstars_players.c'])

# run the setup
setup(ext_modules=[pokerstars_players_module])