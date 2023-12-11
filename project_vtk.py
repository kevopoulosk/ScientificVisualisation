import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import vtk
import pandas as pd
from tqdm import tqdm


# Load the initial positions of neurons
fn_positions = "Desktop/SciVis_Contest_Simulations/rank_0_positions.txt"
positions_data = np.loadtxt(fn_positions, skiprows=7, usecols=(0, 1, 2, 3, 4), dtype={'names': ('local_id', 'x', 'y', 'z', 'area'), 'formats': ('i4', 'f8', 'f8', 'f8', 'U10')})

# Create points for neurons
points = vtk.vtkPoints()
local_ids = []

for row in positions_data:
    local_id, x, y, z, _ = row
    points.InsertNextPoint(x, y, z)
    local_ids.append(local_id)

    
    
    
def VisualizeAreas(local_ids, points, positions_data):
    # Function that visualises the different areas of the brain using Delauney3D filter. 
    # Create a renderer
    renderer = vtk.vtkRenderer()

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName("VTK Visualization")
    render_window.SetSize(800, 600)
    render_window.AddRenderer(renderer)

    # Create a render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Create a dictionary to store actors for each brain area
    area_actors = {}

    # Iterate over distinct brain areas
    for area in set(positions_data['area']):
        
        # Select points belonging to the current area
        area_points = vtk.vtkPoints()
        area_local_ids = [local_id for local_id, _, _, _, a in positions_data if a == area]
        for local_id in area_local_ids:
            index = local_ids.index(local_id)
            x, y, z = points.GetPoint(index)
            area_points.InsertNextPoint(x, y, z)
        
        # Ensure that the area_points array is not empty before creating the convex hull
        if area_points.GetNumberOfPoints() > 0:
            # Create a vtkPolyData object to store the points
            polydata_area = vtk.vtkPolyData()
            polydata_area.SetPoints(area_points)

            # Use vtkDelaunay3D to compute the 3D Delaunay triangulation
            delaunay = vtk.vtkDelaunay3D()
            delaunay.SetInputData(polydata_area)
            delaunay.Update()

            # Create mapper for the 3D Delaunay triangulation
            mapper_area = vtk.vtkDataSetMapper()
            mapper_area.SetInputConnection(delaunay.GetOutputPort())

            # Create actor for the 3D Delaunay triangulation
            actor_area = vtk.vtkActor()
            actor_area.SetMapper(mapper_area)

            # Generate a random color for the brain area
            color = np.random.rand(3)
            actor_area.GetProperty().SetColor(color)

            # Add the actor to the renderer
            renderer.AddActor(actor_area)

            # Store the actor in the dictionary
            area_actors[area] = actor_area

    # Set background color
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Reset camera and render
    renderer.ResetCamera()
    render_window.Render()

    # Start the interaction
    render_window_interactor.Start()    
    
    
    
def InitialConnectivity(positions_data, points):
    # Create cells for neurons
    verts = vtk.vtkCellArray()
    for i in range(len(positions_data)):
        verts.InsertNextCell(1)
        verts.InsertCellPoint(i)

    # Create polydata for neurons
    polydata_neurons = vtk.vtkPolyData()
    polydata_neurons.SetPoints(points)
    polydata_neurons.SetVerts(verts)

    # Create mapper for neurons
    mapper_neurons = vtk.vtkPolyDataMapper()
    mapper_neurons.SetInputData(polydata_neurons)

    # Create actor for neurons
    actor_neurons = vtk.vtkActor()
    actor_neurons.SetMapper(mapper_neurons)
    actor_neurons.GetProperty().SetColor(0.0, 0.0, 0.0)  # Set color to black
    actor_neurons.GetProperty().SetPointSize(5.0)  # Set point size to 5.0


    # Create a renderer
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor_neurons)

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName("VTK Visualization")
    render_window.SetSize(800, 600)
    render_window.AddRenderer(renderer)

    # Create a render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    # Set background color
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Reset camera and render
    renderer.ResetCamera()
    render_window.Render()

    # Start the interaction
    render_window_interactor.Start()
    
    return local_ids


def NetworkConnectivity(local_ids, step_num=1000000, sim_id="calcium"):
    
    # Load network and connectivity data
    fn_network = f"Desktop/SciVis_Contest_Simulations/connectivity_{sim_id}/rank_0_step_{int(step_num)}_in_network.txt"
    network_data = np.loadtxt(fn_network, skiprows=4, usecols=(1, 3))

    # Create lines for connections
    lines = vtk.vtkCellArray()
    for row in network_data:
        target_local_id, source_local_id = map(int, row)
        target_id = local_ids.index(target_local_id)
        source_id = local_ids.index(source_local_id)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, target_id)
        line.GetPointIds().SetId(1, source_id)
        lines.InsertNextCell(line)

    # Create polydata for connections
    polydata_connections = vtk.vtkPolyData()
    polydata_connections.SetPoints(points)
    polydata_connections.SetLines(lines)

    # Create mapper for connections
    mapper_connections = vtk.vtkPolyDataMapper()
    mapper_connections.SetInputData(polydata_connections)

    # Create actor for connections
    actor_connections = vtk.vtkActor()
    actor_connections.SetMapper(mapper_connections)
    actor_connections.GetProperty().SetColor(0.8, 0.8, 0.8)  # Set color to gray
    actor_connections.GetProperty().SetLineWidth(4)  # Set line width

    # Create spheres for neurons
    sphere_source = vtk.vtkSphereSource()
    sphere_source.SetRadius(1.4)  # Set the radius of the spheres

    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(polydata_connections)  # Use the connections as input for the nodes
    glyph.SetSourceConnection(sphere_source.GetOutputPort())

    # Create mapper for neurons
    mapper_neurons = vtk.vtkPolyDataMapper()
    mapper_neurons.SetInputConnection(glyph.GetOutputPort())

    # Create actor for neurons
    actor_neurons = vtk.vtkActor()
    actor_neurons.SetMapper(mapper_neurons)
    actor_neurons.GetProperty().SetColor(1.0, 0.0, 0.0)  # Set color to red

    # Create a renderer
    renderer = vtk.vtkRenderer()

    # Create a render window
    render_window = vtk.vtkRenderWindow()
    render_window.SetWindowName("VTK Visualization")
    render_window.SetSize(800, 600)
    render_window.AddRenderer(renderer)

    # Create a render window interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Add the actors to the renderer
    renderer.AddActor(actor_connections)
    renderer.AddActor(actor_neurons)

    # Set background color
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Reset camera and render
    renderer.ResetCamera()
    render_window.Render()

    # Start the interaction
    render_window_interactor.Start()

def PlasticityChanges(sim):
    # load the data
    data_plasticity = f"Desktop/SciVis_Contest_Simulations/rank_0_plasticity_changes_{sim}.txt"

    # preprocess the data
    df = pd.read_csv(data_plasticity, delimiter=' ')
    df['#step:'] = df['#step:'].str.replace(':', '').astype(int)

    # visualise the creations/deletions/netto
#         plt.figure(figsize=(10,7))
#         plt.semilogy(df["#step:"], df["creations"], label='Creations')
#         plt.semilogy(df["#step:"], df["deletions"], label='Deletions')
#         plt.loglog(df["#step:"], df["netto"], label = 'Net')
#         plt.xlabel("(t) Timesteps")
#         plt.legend(loc='best')
#         plt.ylabel("Creation of synapses")
#         plt.title(f"Creation of Synapses for the simulation {sim}")


    fig, axs = plt.subplots(3,1, figsize=(10,7))
    axs[0].semilogy(df["#step:"], df["creations"])
    axs[0].set_title(f'Creation of synapses for simulation {sim}')
    axs[0].set_ylabel('New synapses created')
    axs[0].set_xlabel("Timesteps (t)")

    axs[1].semilogy(df["#step:"], df["deletions"])
    axs[1].set_title(f'Deletion of synapses for simulation {sim}')
    axs[1].set_ylabel('Deleted synapses')
    axs[1].set_xlabel("Timesteps (t)")

    axs[2].semilogy(df["#step:"], df["netto"])
    axs[2].set_title(f'Net Amount of synapses for simulation {sim}')
    axs[2].set_ylabel('Net amount')
    axs[2].set_xlabel("Timesteps (t)")
    plt.tight_layout()
    



# visualise the initial brain neurons. These neurons are the same for all simulations
local_ids = InitialConnectivity(positions_data, points)
VisualizeAreas(local_ids, points, positions_data)

# For 5 timesteps of the simulations (equally spaced in time), plot the brain connectivity. 
Sims = ['calcium', 'disable', 'stimulus', 'nonetwork']
for sim in Sims:
    PlasticityChanges(sim)
    
    timesteps = np.linspace(0, 1e6, 5)
    pbar = tqdm(total=len(timesteps), position=0, leave=True)
    for time in timesteps:
        NetworkConnectivity(local_ids, step_num=time, sim_id = sim)
        pbar.update()
    pbar.close()



