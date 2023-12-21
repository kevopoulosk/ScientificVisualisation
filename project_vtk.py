import numpy as np
import pandas as pd 
import vtk

# Load the initial positions of neurons
fn_positions = "/Files/rank_0_positions.txt"
positions_data = np.loadtxt(fn_positions, skiprows=7, usecols=(0, 1, 2, 3, 4), dtype={'names': ('local_id', 'x', 'y', 'z', 'area'), 'formats': ('i4', 'f8', 'f8', 'f8', 'U10')})

# Create points for neurons
points = vtk.vtkPoints()
local_ids = []

# Create a dictionary to store actors for each brain area
area_actors = {}

# Create a vtkPoints object to store the connection points
connection_points = vtk.vtkPoints()

# Create a vtkCellArray to store the tubes
tubes = vtk.vtkCellArray()

actor_neurons = vtk.vtkActor()
first = True

for row in positions_data:
    local_id, x, y, z, _ = row
    points.InsertNextPoint(x, y, z)
    local_ids.append(local_id)

def create_connections(connection_points, tubes, source_center, target_center, count):
    """
    This function creates an actor for the connection between the nodes in the form of tubes.
    Returns: connections actor
    """
    connection_points.InsertNextPoint(source_center)
    connection_points.InsertNextPoint(target_center)

    tube = vtk.vtkLine()
    tube.GetPointIds().SetId(0, connection_points.InsertNextPoint(source_center))
    tube.GetPointIds().SetId(1, connection_points.InsertNextPoint(target_center))
    tubes.InsertNextCell(tube)

    # Create a vtkPolyData object for the tubes
    polydata_tubes = vtk.vtkPolyData()
    polydata_tubes.SetPoints(connection_points)
    polydata_tubes.SetLines(tubes)

    max_count = 3000
    max_line_width = 1

    scaling_factor = count / max_count
    scaled_line_width = max_line_width * scaling_factor

    tube_filter = vtk.vtkTubeFilter()
    tube_filter.SetInputData(polydata_tubes)
    tube_filter.SetRadius(scaled_line_width)
    tube_filter.SetNumberOfSides(20)
    tube_filter.Update()

    tube_mapper = vtk.vtkPolyDataMapper()
    tube_mapper.SetInputConnection(tube_filter.GetOutputPort())

    tube_actor = vtk.vtkActor()
    tube_actor.SetMapper(tube_mapper)
    tube_actor.GetProperty().SetColor(0.2, 0.2, 0.2)

    return tube_actor

def create_nodes(color_values):
    """
    This function creates an actor for the nodes.
    Returns: nodes actor
    """
    global actor_neurons, first

    polydata_connections = vtk.vtkPolyData()
    polydata_connections.SetPoints(points)

    # Create mapper for connections
    mapper_connections = vtk.vtkPolyDataMapper()
    mapper_connections.SetInputData(polydata_connections)

    # Create spheres for neurons
    sphere_source = vtk.vtkSphereSource()
    if first:
        sphere_source.SetRadius(70)
        first = False  # Set the radius of the spheres
    else:
        "has entered"
        sphere_source.SetRadius(2)

    # Set scalars for mapping colors to glyphs
    scalars = vtk.vtkDoubleArray()
    scalars.SetNumberOfComponents(1)
    for i in local_ids:
        color_value = color_values[i-1]
        scalars.InsertNextValue(color_value)

    polydata_connections.GetPointData().SetScalars(scalars)

    glyph = vtk.vtkGlyph3D()
    glyph.SetInputData(polydata_connections)  # Use the connections as input for the nodes
    glyph.SetSourceConnection(sphere_source.GetOutputPort())
    glyph.SetColorModeToColorByScalar()

    # Create mapper for neurons
    mapper_neurons = vtk.vtkPolyDataMapper()        
    mapper_neurons.SetInputConnection(glyph.GetOutputPort())

    mapper_neurons.SetScalarRange(0, 1)
    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.AddRGBPoint(0, 0.0, 0.0, 1.0)  # Blue for minimum calcium value
    color_transfer_function.AddRGBPoint(1, 1.0, 0.0, 0.0)  # Red for maximum calcium value
    
    mapper_neurons.SetLookupTable(color_transfer_function)

    actor_neurons.SetMapper(mapper_neurons)

    return actor_neurons, color_transfer_function

def create_areas(area_points):
    """
    This function creates an actor for the areas.
    Returns: areas actor
    """
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
    actor_area.GetProperty().SetOpacity(0.2)

    return actor_area

def VisualizeAreas(local_ids, points, positions_data, show_nodes, timestep, renderer, render_window, interactor, slider, area_actors, connection_points, tubes):

    global actor_neurons

    # Load file and create the dictionary to store the areas
    fn_connections = f"/Files/results_connections_simulations/calcium/connections_calcium_timestep_{timestep}.txt"

    area_connection_counts = pd.read_csv(fn_connections, sep='\s+', header=None)
    area_connection_counts = area_connection_counts.T
    area_connection_counts.columns = area_connection_counts.iloc[0]
    area_connection_counts = area_connection_counts.drop(0)
    area_connection_counts = area_connection_counts.drop(columns=[area_connection_counts.columns[0]])
    area_connection_dict = area_connection_counts.to_dict(orient='list')

    fn_colours = "/Users/manuelgonzaleznovo/Desktop/ScientificVisualisation/colours_calcium_from_monitors.txt"
    colours = pd.read_csv(fn_colours, sep='\t', header=0, usecols=range(1, 7), engine='python')
    color_values = colours.iloc[:, timestep_index].astype(float).values
    
    if show_nodes:
        # Generate the nodes
        actor_neurons, color_transfer_function = create_nodes(color_values)
        renderer.AddActor(actor_neurons)

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
            
            # Create areas
            actor_area = create_areas(area_points)
            
            if show_nodes == False:
                # Add the actor to the renderer
                renderer.AddActor(actor_area)

            # Store the actor in the dictionary
            area_actors[area] = actor_area
    
    #print("Connection counts from each area to all other areas:")
    for source_area, counts in area_connection_dict.items():
        #print(f"From {source_area}: {counts}")

        # Get top 3 most connected areas + their indices
        top_three = sorted(counts, reverse=True)[:2]
        top_three_indices = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)[:2]
        #print(f"Top three {top_three}")
        for target_area, count in zip(top_three_indices, top_three):
            
            if count > 0:
                source_center = area_actors["area_" + str(source_area)].GetCenter()

                # Get the center of the target area
                target_center = area_actors[list(area_actors.keys())[target_area]].GetCenter()

                # Add points to the connection_points array
                tube_actor = create_connections(connection_points, tubes, source_center, target_center, count)

                # Add the actor to the renderer
                renderer.AddActor(tube_actor)    

    if show_nodes:
        # Add colour navbar
        color_bar = vtk.vtkScalarBarActor()
        color_bar.SetLookupTable(color_transfer_function)
        #color_bar.SetTitle("Neuron Calcium Concentration")

        color_bar.GetLabelTextProperty().SetColor(0.0, 0.0, 0.0)  # Set color of the labels
        #color_bar.GetTitleTextProperty().SetColor(0.0, 0.0, 0.0)  # Set color of the title
        color_bar.SetNumberOfLabels(5)  # Adjust the number of labels as needed
        color_bar.SetPosition(0.85, 0.05)
        color_bar.SetWidth(0.1)
        #color_bar.GetTitleTextProperty().SetFontSize(40)
        renderer.AddActor(color_bar)

    # Set background color
    renderer.SetBackground(1.0, 1.0, 1.0)

    # Reset camera and render
    renderer.ResetCamera()
    render_window.Render()

    # Start the interaction
    #interactor.Start()


def update_connections(renderer, area_actors, area_connection_dict, connection_points, tubes, color_values, show_nodes):
    """
    Function to update just the connections after every iteration
    """
    global actor_neurons
    # Clear only the existing connection actors from the renderer
    actors = renderer.GetActors()
    actors.InitTraversal()
    actor = actors.GetNextActor()
    while actor:
        if actor.GetProperty().GetColor() == (0.2, 0.2, 0.2):  # Check if it's a connection actor
            renderer.RemoveActor(actor)
        actor = actors.GetNextActor()

    if show_nodes == True:
        renderer.RemoveActor(actor_neurons)

        actor_neurons, _ = create_nodes(color_values)
        renderer.AddActor(actor_neurons)

    # Create a new set of connections based on the updated data
    for source_area, counts in area_connection_dict.items():
        top_three = sorted(counts, reverse=True)[:2]
        top_three_indices = sorted(range(len(counts)), key=lambda i: counts[i], reverse=True)[:2]
        for target_area, count in zip(top_three_indices, top_three):
            if count > 0:
                source_center = area_actors["area_" + str(source_area)].GetCenter()
                target_center = area_actors[list(area_actors.keys())[target_area]].GetCenter()
                tube_actor = create_connections(connection_points, tubes, source_center, target_center, count)
                renderer.AddActor(tube_actor)

def update_visualization(obj, event):
    """
    Function needed for the animation
    """
    global timestep_index, timesteps, slider, renderer, render_window, interactor, area_actors, actor_neurons

    show_nodes = True

    if timestep_index < len(timesteps):

        # Load file and create the dictionary to store the areas
        fn_connections = f"/Files/results_connections_simulations/calcium/connections_calcium_timestep_{timesteps[timestep_index]}.txt"

        area_connection_counts = pd.read_csv(fn_connections, sep='\s+', header=None)
        area_connection_counts = area_connection_counts.T
        area_connection_counts.columns = area_connection_counts.iloc[0]
        area_connection_counts = area_connection_counts.drop(0)
        area_connection_counts = area_connection_counts.drop(columns=[area_connection_counts.columns[0]])
        area_connection_dict = area_connection_counts.to_dict(orient='list')

        if show_nodes == True:
            fn_colours = "/Files/colours_calcium_from_monitors.txt"
            colours = pd.read_csv(fn_colours, sep='\t', header=0, usecols=range(1, 7), engine='python')
            color_values = colours.iloc[:, timestep_index].astype(float).values
            print(color_values[0])
        
        print("Timer fired! Update for timestep:", timesteps[timestep_index])

        # Update visualization for the current timestep
        if timestep_index == 0:
            VisualizeAreas(local_ids, points, positions_data, show_nodes, timesteps[timestep_index], renderer, render_window, interactor, slider, area_actors, connection_points, tubes)
        else:
            if show_nodes == True:
                update_connections(renderer, area_actors, area_connection_dict, connection_points, tubes, color_values, show_nodes)
            else:
                update_connections(renderer, area_actors, area_connection_dict, connection_points, tubes, None, show_nodes)

        # Update the slider value to reflect the progress
        slider.SetValue(float(timestep_index) / len(timesteps))

        # Explicitly render the scene
        render_window.Render()

        #if timestep_index != 4:
        timestep_index += 1

        # Increment the timestep index
        interactor.InvokeEvent("UpdateEvent")

    else:
        # Stop the animation when all timesteps are processed
        interactor.ExitCallback() 

timesteps = [0, 250000, 500000, 750000, 1000000]
timestep_index = 0

# Set up VTK components
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("VTK Animation with Progress Bar")
render_window.SetSize(800, 600)
render_window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a slider representation for the progress bar
slider = vtk.vtkSliderRepresentation2D()
slider.SetMinimumValue(0.0)
slider.SetMaximumValue(1.0)
slider.SetValue(0.0)
slider.SetTitleText("Progress")
slider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
slider.GetPoint1Coordinate().SetValue(0.1, 0.9)
slider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
slider.GetPoint2Coordinate().SetValue(0.9, 0.9)

# Change its colour to black
slider.GetTubeProperty().SetColor(0.0, 0.0, 0.0)
slider.GetSliderProperty().SetColor(0.0, 0.0, 0.0)
slider.GetCapProperty().SetColor(0.0, 0.0, 0.0)
slider.GetTitleProperty().SetColor(0.0, 0.0, 0.0)
slider.GetLabelProperty().SetColor(0.0, 0.0, 0.0)

# Create a slider widget
slider_widget = vtk.vtkSliderWidget()
slider_widget.SetInteractor(interactor)
slider_widget.SetRepresentation(slider)
slider_widget.SetAnimationModeToAnimate()
slider_widget.EnabledOn()

# Add the timer event
interactor.AddObserver("TimerEvent", update_visualization)
interactor.CreateRepeatingTimer(6000)  # Set the timer interval in milliseconds

def update_event_callback(obj, event):
    interactor.Render()

interactor.AddObserver("UpdateEvent", update_event_callback)

# Start the interactor
interactor.Start()

