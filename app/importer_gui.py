import logging
from aiohttp_jinja2 import template

from app.utility.base_service import BaseService
from app.service.auth_svc import for_all_public_methods, check_authorization
from plugins.importer.app.importer_svc import ImporterService


@for_all_public_methods(check_authorization)
class ImporterGUI(BaseService):

    def __init__(self, services, name, description):
        self.name = name
        self.description = description
        self.services = services
        # self.importer_svc = ImporterService(services)

        self.auth_svc = services.get('auth_svc')
        self.log = logging.getLogger('importer_gui')

    @template('importer.html')
    async def splash(self, request):
        """
        Show the main plugin page
        """
        return {}

    # Add functions here that the front-end will use
