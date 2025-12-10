
import os

from matplotlib import font_manager as fm
from matplotlib import rc

# set global font to be Helvetica
current_dir = os.path.dirname(__file__)
helvetica_path = os.path.join(current_dir, 'fonts', 'Helvetica.ttf')
font = fm.FontProperties(fname=helvetica_path)
fm.fontManager.addfont(helvetica_path)
font = {'family': 'Helvetica'}
rc('font', **font)