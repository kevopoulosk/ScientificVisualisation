# Scientific Visualisation

## Description
In this repository, you will find our submission to the Scivis Contest of 2023. In particular, this year’s contest deals with the simulation of activity within the human brain, especially the changes within its network structure.

## How to run
To run the code and produce our animation, it is neccesary to have Python installed with all the modules specified in the `requirements.txt` file using the following command:
- `pip install -r requirements.txt`

Then, by typping into your predefined terminal the command `python project_vtk.py` you would be able to run the file. The behaviour of the program can be modified by setting the `show_nodes` to True/False to visualize the corresponding nodes or the different areas. To do so, you should modify the value inside the main function call in the script:
- `if __name__ == "__main__":
    main(True)  # Set to True or False as needed`

In order to visualise the lineplots presented in the report, you just need to run the file: `SciVis_brainplasticity.py`.

  
