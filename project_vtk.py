import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import vtk

fn_positions = "/Users/konstantinoskevopoulos/Downloads/positions/rank_0_positions.txt"

# TODO: ADD FUNCTION THAT GETS THE POINTS PER SIMULATION
positions_data = np.loadtxt(fn_positions, skiprows=7, usecols=(0, 1, 2, 3))

# Create points for neurons
points = vtk.vtkPoints()
local_ids = []

for row in positions_data:
    local_id, x, y, z = row
    points.InsertNextPoint(x, y, z)
    local_ids.append(local_id)

print(local_ids[:10])

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

# TODO: ADD FUNCTION THAT DOES CONNECTIVITY PER SIMULATION

# Load network connectivity data
# Load network data
fn_network = "/Users/konstantinoskevopoulos/Downloads/network_calcium/rank_0_step_1000000_in_network.txt"
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
