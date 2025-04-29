from app.utility.base_world import BaseWorld
from plugins.importer.app.importer_gui import ImporterGUI
from plugins.importer.app.importer_api import ImporterAPI

name = 'Importer'
description = 'The Emulation Plan Importer is a custom plugin for MITRE CALDERA that allows you to import adversary emulation plans in YAML format. The plugin automatically creates adversary profiles and abilities that can be used in the CALDERA framework for red team operations and adversary emulation exercises.'
address = '/plugin/importer/gui'
access = BaseWorld.Access.RED


async def enable(services):
    app = services.get('app_svc').application
    data_svc = services.get('data_svc')
    rest_svc = services.get('rest_svc')
    file_svc = services.get('file_svc')

    importer_gui = ImporterGUI(services, name=name, description=description)
    # Register templates directory
    templates_dir = 'plugins/importer/templates/'
    app.router.add_static('/importer', templates_dir, append_version=True)

    importer_api = ImporterAPI(services)
    # Add API routes here
    app.router.add_route('GET', '/plugin/importer/gui', importer_gui.splash)
    app.router.add_route('POST', '/plugin/importer/upload', importer_api.upload_emulation_plan)

    # Register plugin with server
    BaseWorld.apply_config('plugins.importer', {})
    