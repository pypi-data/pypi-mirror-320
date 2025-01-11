from IPython.display import Javascript

def is_running_in_colab():
    try:
        import google.colab
        return True
    except ImportError:
        raise RuntimeError(
            "This package is designed for Google Colab only.\n"
            "Please run this in a Colab notebook."
        )

def create_template():
    """Create an AOC template in the current Colab notebook"""
    if not is_running_in_colab():
        raise RuntimeError("This package only works in Google Colab")
    
    template = '''# @title AOC Setup and Imports {display-mode: "form"}
# @markdown Check to install packages
install_packages = True  # @param {type:"boolean"}

if install_packages:
    %pip install aocd

# @markdown Setup AOC credentials and helper function
from google.colab import userdata
import os
from aocd import get_data

AOC_SESSION = userdata.get('AOC_SESSION')
os.environ['AOC_SESSION'] = AOC_SESSION

def get_aocd_data(day=1, year=2023):
    """Fetch AOC data for given day and year"""
    return get_data(day=day, year=year)
'''
    return Javascript(f'''
        var cell = IPython.notebook.insert_cell_above('code');
        cell.set_text(`{template}`);
    ''')