import akantu as aka
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import subprocess
from mpl_toolkits.axes_grid1 import make_axes_locatable  


def write_mesh(w, l, h1, h2, R, s):
    """Write the gmsh file for the specific problem"""
    
    # Points {x, y, z, h}
    mesh_file = f"""
    Point(1) = {{0, 0, 0, {h2} }};
    Point(2) = {{ {w}, 0, 0, {h2} }};
    Point(3) = {{ {w}, {l}, 0, {h2} }};
    Point(4) = {{ 0,   {l}, 0, {h2} }};
    Point(5) = {{ 0,   {(l+s)/2.}, 0, {h1} }};
    Point(6) = {{ {R},   {l/2.}, 0, {h1} }};
    Point(7) = {{ 0,   {(l-s)/2.}, 0, {h1} }};
    """
    # Lines and plane surface
    mesh_file += """
    Line(1) = {1, 2};
    Line(2) = {2, 3};
    Line(3) = {3, 4};
    Line(4) = {4, 5};
    Line(5) = {5, 6};
    Line(6) = {6, 7};
    Line(7) = {7, 1};
    Line Loop(8) = {1, 2, 3, 4, 5, 6, 7};
    Plane Surface(9) = {8};
    """
    # Physical subparts
    mesh_file += """
    Physical Surface(10) = {9};
    Physical Line("XBlocked") = {2};
    Physical Line("YBlocked") = {1};
    Physical Line("Traction") = {3};
    """
    
    # Write gmesh file
    open('plate.geo', 'w').write(mesh_file)
    ret = subprocess.run("gmsh -2 -order 1 -o plate.msh plate.geo", shell=True, stdout=subprocess.DEVNULL)
    if ret.returncode:
        print("Beware, gmsh could not run: mesh is not regenerated")
        
    # Read the mesh with akantu
    spatial_dimension = 2    
    mesh_file = 'plate.msh'
    mesh = aka.Mesh(spatial_dimension)
    mesh.read(mesh_file)
    
    return(mesh)


def plot_mesh(mesh):
    # extract the mesh
    conn = mesh.getConnectivity(aka._triangle_3)
    nodes = mesh.getNodes()
    triangles = tri.Triangulation(nodes[:, 0], nodes[:, 1], conn)

    # plot the result
    plt.axes().set_aspect('equal')
    # plots the pristine state
    t = plt.triplot(triangles, '--', lw=.8)
        

def solve_FEM(mesh, traction):
    """Solve FEM problem with akantu, applying traction on given mesh"""
    
    # creating the solid mechanics model
    model = aka.SolidMechanicsModel(mesh)

    # initialize a static solver
    model.initFull(_analysis_method=aka._static)

    # set the displacement/Dirichlet boundary conditions
    model.applyBC(aka.FixedValue(0.0, aka._x), "XBlocked")
    model.applyBC(aka.FixedValue(0.0, aka._y), "YBlocked")

    # set the force/Neumann boundary conditions
    model.getExternalForce()[:] = 0
    trac = [0, 10] # Newtons/m^2
    model.applyBC(aka.FromTraction(trac), "Traction")

    # configure the linear algebra solver
    solver = model.getNonLinearSolver()
    solver.set("max_iterations", 2)
    solver.set("threshold", 1e-10)
    solver.set("convergence_type", aka.SolveConvergenceCriteria.residual)

    # compute the solution
    model.solveStep()
    
    return(model)


def plot_displacements(mesh, model):
    
    # extract the mesh
    conn = mesh.getConnectivity(aka._triangle_3)
    nodes = mesh.getNodes()
    triangles = tri.Triangulation(nodes[:, 0], nodes[:, 1], conn)
    
    # extract the displacements
    u = model.getDisplacement()
    
    # plot the result
    plt.axes().set_aspect('equal')
    # plots the pristine state
    t = plt.triplot(triangles, '--', lw=.8)
    # plots an exagerating view of the strained mesh
    t = plt.triplot(nodes[:, 0]+u[:,0]*2e9, nodes[:, 1]+u[:,1]*2e9, triangles=conn)
      

def plot_stress(mesh, model, max_stress=None, zoom=False):
    
    # extract the mesh
    conn = mesh.getConnectivity(aka._triangle_3)
    nodes = mesh.getNodes()
    triangles = tri.Triangulation(nodes[:, 0], nodes[:, 1], conn)
    
    # plot stress field
    
    plt.axes().set_aspect('equal')
    if zoom: plt.axis([1.5, 2.5, 1.75, 2.25])
    
    stress_field = model.getMaterial(0).getStress(aka._triangle_3)
    if max_stress is None:
        stress_disp = plt.tripcolor(triangles, np.linalg.norm(stress_field, axis=1), cmap='jet')
    else:
        stress_disp = plt.tripcolor(triangles, np.linalg.norm(stress_field, axis=1), vmax=max_stress, cmap='jet')
        
    ax = plt.gca()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    
    cbar = plt.colorbar(stress_disp, cax=cax)
    cbar.set_label('Stress magnitude [Pa]')
    print('Maximum stress (norm) = {:.1f} Pa'.format(np.max(np.linalg.norm(stress_field, axis=1))))
