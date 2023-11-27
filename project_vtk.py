import vtk
import numpy as np

# Read data from your file
filename = "/Users/manuelgonzaleznovo/Desktop/project_vtk/rank_0_positions.txt"

# Load data with dtype=float to convert numeric values
data = np.loadtxt(filename, skiprows=7, usecols=(1, 2, 3))

# Create a vtkPoints object to store the 3D points
points = vtk.vtkPoints()

# Add points to the vtkPoints object
for row in data:
    x, y, z = row
    points.InsertNextPoint(x, y, z)

# Create a vtkCellArray to define the structure of the data
verts = vtk.vtkCellArray()

# Add a vertex for each point
for i in range(len(data)):
    verts.InsertNextCell(1)
    verts.InsertCellPoint(i)

# Create a vtkPolyData object to store points and vertices
polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.SetVerts(verts)

# Create a mapper
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)

# Create an actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Set actor properties
actor.GetProperty().SetColor(0.0, 0.0, 0.0)  # Set color to black
actor.GetProperty().SetPointSize(5.0)  # Set point size to 5.0

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

# Add the actor to the renderer
renderer.AddActor(actor)

# Set background color
renderer.SetBackground(1.0, 1.0, 1.0)

# Reset camera and render
renderer.ResetCamera()
render_window.Render()

# Start the interaction
render_window_interactor.Start()