from . import BaseCommand
from ...option import BsbOption
from ...reporting import report
from ... import config
import pathlib


class ProjectNewCommand(BaseCommand, name="new"):
    def get_options(self):
        return {}

    def add_parser_arguments(self, parser):
        parser.add_argument(
            "project_name", nargs="?", help="Project name & root folder", default=""
        )
        parser.add_argument(
            "path", nargs="?", default=".", help="Project name & root folder"
        )

    def handler(self, context):
        name = (
            context.arguments.project_name
            or input("Project name [my_model]: ")
            or "my_model"
        )
        root = pathlib.Path(context.arguments.path) / name
        try:
            root.mkdir(exist_ok=False)
        except FileExistsError:
            return report(
                f"Could not create '{root.absolute()}', directory exists.", level=0
            )

        template = input("Config template [template.json]: ") or "template.json"
        config.copy_template(template, output=root / "network_configuration.json")

        # # TODO: decide on "config", "build", "publish"
        for d in (".bsb", name):
            (root / d).mkdir()

        with open(root / name / "__init__.py", "w") as f:
            f.write("\n")
        with open(root / name / "placement.py", "w") as f:
            f.write("from bsb.placement import PlacementStrategy\n")
        with open(root / name / "connectome.py", "w") as f:
            f.write("from bsb.connectivity import ConnectionStrategy\n")

        report(f"Created '{name}' project structure.")
