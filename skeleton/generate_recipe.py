from typing import Any, Dict

from cpl import core
from cpl import ui
from cpl import dfs
from cpl.core import Msg


def generate_recipe(
        name: str,
        catg_input: str,
        catg_output: str,
    ):
    """Generate a recipe.

    TODO: distinguish TAG and CATG
    """
    
    class MyRecipe(ui.PyRecipe):
        # Fill in recipe information
        _name = name
        _version = "1.0"
        _author = "PIP"
        _email = "hugo@buddelmeijer.nl"
        _copyright = "GPL-3.0-or-later"
        _synopsis = f"Generated {name} recipe."
        _description = (
            f"The {name} recipe creates {catg_output} from {catg_input}.\n"
            "But it only handles headers, no pixels."
        )

        def __init__(self) -> None:
            super().__init__()

            # The recipe will have no parameters
            self.parameters = ui.ParameterList(())

        def run(self, frameset: ui.FrameSet, settings: Dict[str, Any]) -> ui.FrameSet:
            # input
            raw_frames = ui.FrameSet()

            # output
            product_frames = ui.FrameSet()

            output_file = f"{catg_output}.fits"

            # Go through the list of input frames, check the tag and act accordingly
            for frame in frameset:
                if frame.tag == catg_output:
                    # frame.group = ui.Frame.FrameGroup.RAW
                    raw_frames.append(frame)
                    Msg.debug(self.name, f"Got raw frame: {frame.file}.")

            # For demonstration purposes we raise an exception here. Real world
            # recipes should rather print a message (also to have it in the log file)
            # and exit gracefully.
            if len(raw_frames) == 0:
                raise core.DataNotFoundError("No raw frames in frameset.")

            header = None
            processed_images = core.ImageList()

            # Create property list specifying the product tag of the processed image
            product_properties = core.PropertyList()
            product_properties.append(
                core.Property("ESO PRO CATG", core.Type.STRING, catg_output)
            )

            # Save the result image as a standard pipeline product file
            Msg.info(self.name, f"Saving product file as {output_file!r}.")
            dfs.save_image(
                allframes=frameset,
                parlist=self.parameters,
                usedframes=frameset,
                image=None, # combined_image,
                recipe=self.name,
                applist=product_properties,
                pipe_id=f"metis/{self.version!r}",
                filename=output_file,
                header=header,
            )

            # Register the created product
            product_frames.append(
                ui.Frame(
                    file=output_file,
                    tag=catg_output,
                    group=ui.Frame.FrameGroup.PRODUCT,
                    level=ui.Frame.FrameLevel.FINAL,
                    frameType=ui.Frame.FrameType.IMAGE,
                )
            )

            return product_frames

    return MyRecipe


# This works:
#recipe_1 = generate_recipe("hello", "AAA", "BBB")

# But without the name, it does not:
#generate_recipe("hello", "AAA", "BBB")

