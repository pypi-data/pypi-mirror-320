import IPython
import textom
import matplotlib.pyplot as plt

from .src import handle as hdl
from .src import misc as msc

def main():
    """Launches TexTOM in iPython mode
    """
    msc.fancy_title()
    plt.ion()
    # Create a dictionary of all public functions and classes from textom
    textom_namespace = {k: v for k, v in vars(textom).items() if not k.startswith("_")}
    # Start IPython with the namespace
    IPython.start_ipython(argv=[], user_ns=textom_namespace)

def config():
    """Opens the config file to modify
    """
    config_path = hdl.get_file_path('textom','config.py')
    hdl.open_with_editor(config_path)

def documentation():
    """Opens the TexTOM documentation in a pdf viewer
    """
    doc_path = hdl.get_file_path('textom','documentation/textom_documentation.pdf')
    hdl.open_pdf(doc_path)