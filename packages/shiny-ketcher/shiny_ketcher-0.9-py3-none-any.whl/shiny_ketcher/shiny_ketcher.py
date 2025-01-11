from pathlib import PurePath

from htmltools import HTMLDependency, Tag
from shiny import ui
from shiny.module import resolve_id
from shiny.render.renderer import Jsonifiable, Renderer

# This object is used to let Shiny know where the dependencies needed to run
# our component all live. In this case, we're just using a single javascript
# file but we could also include CSS.
shiny_ketcher_deps = HTMLDependency(
    "shiny_ketcher",
    "1.0.0",
    source={
        "package": "shiny_ketcher",
        "subdir": str(PurePath(__file__).parent / "distjs"),
    },
    script={"src": "index.js", "type": "module"},
    stylesheet={"href": "index.css"},
)


# Output component
class render_ketcher(Renderer[str]):
    """
    Render a string-based structure representation into the Ketcher component.
    """

    # The UI used within Shiny Express mode
    def auto_output_ui(self) -> Tag:
        return output_ketcher(self.output_id)

    # # There are no parameters being supplied to the `output_shiny_ketcher` rendering function.
    # # Therefore, we can omit the `__init__()` method.
    # def __init__(self, _fn: Optional[ValueFn[int]] = None, *, extra_arg: str = "bar"):
    #     super().__init__(_fn)
    #     self.extra_arg: str = extra_arg

    # Transforms non-`None` values into a `Jsonifiable` object.
    # If you'd like more control on when and how the value is rendered,
    # please use the `async def render(self)` method.
    async def transform(self, value: str) -> Jsonifiable:
        # Send the results to the client. Make sure that this is a serializable
        # object and matches what is expected in the javascript code.
        return {"value": str(value)}


def output_ketcher(tag_id: str):
    """
    Show the Ketcher output component
    """
    return Tag(
        "shiny-ketcher-output",
        shiny_ketcher_deps,
        id=resolve_id(tag_id),
    )


def ketcher_message_handlers():
    """
    Adds the message handlers to allow users to fetch data from the Ketcher component on-call.
    """
    return ui.tags.script(
        """
        $(function() {
            Shiny.addCustomMessageHandler("get_smiles", function(message) {
                console.log("get_smiles");
                window.ketcher.getSmiles().then(smiles => {
                    console.log(smiles);
                    Shiny.setInputValue('smiles', smiles);
                })
            });
        });
        $(function() {
            Shiny.addCustomMessageHandler("get_molfile", function(message) {
                console.log("get_molfile");
                window.ketcher.getMolfile(molfileFormat="v3000").then(molfile => {
                    console.log(molfile);
                    Shiny.setInputValue('molfile', molfile);
                })
            });
        });
        $(function() {
            Shiny.addCustomMessageHandler("get_svg", function(message) {
                window.ketcher.getMolfile(molfileFormat="v3000").then(molfile => {
                    window.ketcher.generateImage(molfile, options={outputFormat:"svg"}).then(
                        s => s.text()
                    ).then( t => Shiny.setInputValue('svg', t));
                })
            });
        });
        """
    )
