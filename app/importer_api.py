import os
import yaml
import uuid
import logging
import aiohttp_jinja2
import asyncio
from aiohttp import web
from datetime import datetime
from app.utility.base_service import BaseService
#from app.objects.c_ability import Ability
#from app.objects.c_adversary import Adversary
#from app.objects.c_executor import Executor
from app.service.auth_svc import for_all_public_methods, check_authorization
from plugins.importer.app.importer_svc import ImporterService


@for_all_public_methods(check_authorization)
class ImporterAPI(BaseService):
    def __init__(self, services):
        self.services = services
        self.auth_svc = services.get('auth_svc')
        self.data_svc = services.get('data_svc')
        self.file_svc = services.get('file_svc')
        self.log = logging.getLogger('importer_api')
        self.abilities_directory = os.path.join('plugins', 'importer', 'data', 'abilities')
        
        # Ensure abilities directory exists
        if not os.path.exists(self.abilities_directory):
            os.makedirs(self.abilities_directory)

    async def upload_emulation_plan(self, request):
        """
        Upload and process a YAML emulation plan
        """
        try:
            # Get the uploaded file
            data = await request.post()
            uploaded_file = data.get('emulation_plan_file')
            
            if not uploaded_file:
                return web.json_response({'status': 'error', 'message': 'No file was uploaded'})
            
            # Read the file content
            file_content = uploaded_file.file.read()
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8')
            
            # Initialize processor
            processor = ImporterService(self.data_svc, self.abilities_directory)
            
            # Process the emulation plan
            self.log.info(f"Processing emulation plan: {uploaded_file.filename}")
            adversary, abilities, stats = await processor.process_emulation_plan(file_content)
            
            # Log statistics
            self.log.info(f"Processed {stats['adversary_name']} with {stats['abilities_count']} abilities in {stats['processing_time']:.2f} seconds")
            
            # Return results
            return web.json_response({
                'status': 'success',
                'message': f'Successfully imported {adversary.name} with {len(adversary.atomic_ordering)} abilities',
                'details': {
                    'adversary_id': adversary.adversary_id,
                    'adversary_name': adversary.name,
                    'abilities_count': len(abilities),
                    'processing_time': f"{stats['processing_time']:.2f} seconds"
                }
            })
        except Exception as e:
            self.log.error(f'Error importing emulation plan: {str(e)}')
            return web.json_response({'status': 'error', 'message': str(e)})
