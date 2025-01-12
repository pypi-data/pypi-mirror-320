import json
import webcolors
from IPython.display import display, HTML

# TODO: Add a little spinner gif for while the div is rendering
# TODO: Figure out how to disable vtk.js keyboard bindings (s,w,v,r)
class Plotter():
    template = """
<div id="vtk-container" style="width: WIDTHpx; height: HEIGHTpx; border: 1px solid black;"></div>
<script type="text/javascript">

  function render() {
    var fullScreenRenderer = vtk.Rendering.Misc.vtkFullScreenRenderWindow.newInstance({
      rootContainer: document.getElementById('vtk-container'),
    });

    MESH_TEMPLATE

    renderer.resetCamera();
    var renderWindow = fullScreenRenderer.getRenderWindow();
    renderWindow.render();
  }

  if (typeof vtk === "undefined") {
    var script = document.createElement("script");
    script.src = "https://unpkg.com/vtk.js";
    document.head.appendChild(script);
    script.onload = function() {
      console.log("vtk.js loaded successfully");
      render();
    };
  } else {
    console.log("vtk.js is already loaded");
    render();
  }
</script>
"""
    mesh_template = """
    var object_params_ID = OBJECT_PARAMETERS
    var actor_params_ID = ACTOR_PARAMETERS
    
    var actor_ID = vtk.Rendering.Core.vtkActor.newInstance();
    actor_ID.getProperty().setColor(...actor_params_ID.color);
    actor_ID.getProperty().setEdgeVisibility(actor_params_ID.show_edges);
    
    var mapper_ID = vtk.Rendering.Core.vtkMapper.newInstance();
    var cone_ID = vtk.Filters.Sources.vtkConeSource.newInstance();

    var obj_ID = vtk.Filters.Sources.vtkCylinderSource.newInstance(object_params_ID);

    actor_ID.setMapper(mapper_ID);
    mapper_ID.setInputConnection(obj_ID.getOutputPort());

    var renderer = fullScreenRenderer.getRenderer();
    renderer.addActor(actor_ID);
"""
    def __init__(self, height=400, width=600):
        self.height = height
        self.width = width
        self.meshes = []
        self.next_mesh_id = 1
    def add_mesh(self, mesh, color="black", show_edges=False):
        # Typing the word 'show' here seems to flip the actual realtime display. I don't understand that..
        # It does suggest we could have some realtime updating though (i.e. render continously on cell change
        # Or 'render if it compiles' on cell change
        self.meshes.append([self.next_mesh_id, mesh, color, show_edges])
        self.next_mesh_id = self.next_mesh_id + 1
    def show(self, debug=False):
        rendered_meshes = ""
        for [mesh_id, mesh, color, show_edges] in self.meshes:
            object_params = json.dumps(
                {
                    'height': mesh.height,
                    'radius': mesh.radius,
                    'resolution': mesh.resolution,
                }
            )
            # NOTE: We could move the RGB bits into JS and parse with canvas
            actor_params = json.dumps(
                {
                    'color':list(webcolors.name_to_rgb(color)),
                    'show_edges': show_edges,
                }
            )
            rendered_mesh = self.mesh_template \
                .replace("OBJECT_PARAMETERS", object_params) \
                .replace("ACTOR_PARAMETERS", actor_params) \
                .replace("ID", str(mesh_id))
            rendered_meshes += rendered_mesh
        # print(rendered_mesh)
        output = self.template \
            .replace("HEIGHT", str(self.height)) \
            .replace("WIDTH", str(self.width)) \
            .replace("MESH_TEMPLATE", rendered_meshes)
        if debug:
            print(output)
        display(HTML(output))
        # display(HTML(template.replace("MESH_TEMPLATE", rendered_mesh)))
