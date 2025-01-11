from IPython.display import Javascript, display

def is_running_in_colab():
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
    is_running_in_colab()
    
    print("Creating template...")
    
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
    
    js = Javascript('''
        const template = `''' + template + '''`;
        const cellId = google.colab.kernel.invokeFunction(
            'notebook.CreateCell', 
            [{'cellType': 'code', 'source': template}], 
            {}
        );
    ''')
    
    print("About to display JS...")
    display(js)
    print("JS displayed")