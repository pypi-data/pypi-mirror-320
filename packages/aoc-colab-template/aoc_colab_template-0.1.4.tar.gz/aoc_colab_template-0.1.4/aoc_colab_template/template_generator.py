from IPython.display import Javascript, display

def is_running_in_colab():
    """Check if the code is running in Google Colab
    
    Returns:
        bool: True if running in Colab, raises RuntimeError otherwise
    
    Raises:
        RuntimeError: If not running in Google Colab
    """
    try:
        import google.colab
        print("You are in colab environment")
        return True
    except ImportError:
        raise RuntimeError(
            "This package is designed for Google Colab only.\n"
            "Please run this in a Colab notebook."
        )

def create_template():
    """Create an AOC template in the current Colab notebook"""
    is_running_in_colab()  # Will raise error if not in Colab
    
    print("Creating template...")  # Debug print
    
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
    js = Javascript(f'''
        var cell = IPython.notebook.insert_cell_above('code');
        cell.set_text(`{template}`);
    ''')
    print("About to display JS...")  # Debug print
    display(js)
    print("JS displayed")  # Debug print