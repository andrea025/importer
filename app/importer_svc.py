import os
import yaml
import uuid
import logging
from datetime import datetime
from app.objects.c_ability import Ability
from app.objects.c_adversary import Adversary
#from app.objects.c_executor import Executor


class ImporterService:
    def __init__(self, data_svc, abilities_directory):
        self.data_svc = data_svc
        self.abilities_directory = abilities_directory
        self.log = logging.getLogger('emulation_plan_processor')
        
    async def process_emulation_plan(self, yaml_content):
        """
        Process an emulation plan YAML and create abilities and adversaries
        
        Args:
            yaml_content (str): The YAML content as a string
            
        Returns:
            tuple: (adversary, list of abilities, stats)
        """
        try:
            # Parse YAML content
            emulation_plan = yaml.safe_load(yaml_content)
            if not emulation_plan:
                raise ValueError("Empty or invalid YAML content")
                
            # Start processing
            start_time = datetime.now()
            self.log.info(f"Starting emulation plan processing at {start_time}")
            
            # Extract adversary information
            adversary_info = self._extract_adversary_info(emulation_plan)
            self.log.info(f"Found adversary: {adversary_info.get('adversary_name')}")
            
            # Create abilities
            abilities = await self._create_abilities(emulation_plan)
            self.log.info(f"Created {len(abilities)} abilities")
            
            # Create adversary
            adversary = await self._create_adversary(adversary_info, abilities)
            self.log.info(f"Created adversary profile with {len(adversary.atomic_ordering)} abilities")
            
            # Collect statistics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            stats = {
                'processing_time': processing_time,
                'abilities_count': len(abilities),
                'adversary_name': adversary.name,
                'adversary_id': adversary.adversary_id
            }
            
            return adversary, abilities, stats
            
        except Exception as e:
            self.log.error(f"Error processing emulation plan: {str(e)}")
            raise

    def _extract_adversary_info(self, emulation_plan):
        """Extract adversary information from the emulation plan"""
        # First try to find the emulation_plan_details section
        for item in emulation_plan:
            if isinstance(item, dict) and 'emulation_plan_details' in item:
                return item['emulation_plan_details']
        
        # If not found, look for individual items
        adversary_info = {
            'id': str(uuid.uuid4()),
            'adversary_name': 'Unknown Adversary',
            'adversary_description': 'Imported from emulation plan'
        }
        
        # Try to find name in the first item if it's not a procedure
        for item in emulation_plan:
            if isinstance(item, dict):
                if 'name' in item and 'platforms' not in item:
                    adversary_info['adversary_name'] = item['name']
                if 'description' in item and 'platforms' not in item:
                    adversary_info['adversary_description'] = item['description']
        
        return adversary_info

    async def _create_abilities(self, emulation_plan):
        """Create abilities from the emulation plan"""
        abilities = []
        
        # Process each item in the emulation plan
        for item in emulation_plan:
            if isinstance(item, dict) and 'id' in item and 'name' in item and 'platforms' in item:
                try:
                    ability = await self._create_single_ability(item)
                    abilities.append(ability)
                    self.log.debug(f"Created ability: {ability.name} ({ability.ability_id})")
                except Exception as e:
                    self.log.error(f"Error creating ability {item.get('name', 'Unknown')}: {str(e)}")
        
        return abilities

    async def _create_single_ability(self, ability_data):
        """Create a single ability from ability data"""
        # Extract basic information
        ability_id = ability_data.get('id', str(uuid.uuid4()))
        name = ability_data.get('name', 'Unnamed Ability')
        description = ability_data.get('description', '')
        
        # Extract ATT&CK information
        tactic = ability_data.get('tactic', '')
        technique_data = ability_data.get('technique', {})
        technique_id = technique_data.get('attack_id', '')
        technique_name = technique_data.get('name', '')
        
        # Create executors
        executors = []
        for platform, platform_executors in ability_data.get('platforms', {}).items():
            for executor_name, executor_details in platform_executors.items():
                # Process command and cleanup
                command = executor_details.get('command', '')
                cleanup = executor_details.get('cleanup', '')
                
                # Process payloads
                payloads = executor_details.get('payloads', [])
                
                # Create executor object
                executor = Executor(
                    name=executor_name,
                    platform=platform,
                    command=command,
                    cleanup=cleanup,
                    payloads=payloads
                )
                executors.append(executor)
                
                # Register payloads with placeholders if needed
                for payload in payloads:
                    self._ensure_payload_exists(payload)
        
        # Create ability object
        ability = Ability(
            ability_id=ability_id,
            name=name,
            description=description,
            tactic=tactic,
            technique_id=technique_id,
            technique_name=technique_name,
            executors=executors,
            requirements=ability_data.get('requirements', []),
            repeatable=ability_data.get('repeatable', False),
            timeout=ability_data.get('timeout', 60),
            access=ability_data.get('access', {}),
            additional_info={}
        )
        
        # Add source information if available
        if 'cti_source' in ability_data:
            ability.additional_info['cti_source'] = ability_data['cti_source']
        
        # Add procedure information if available
        if 'procedure_group' in ability_data:
            ability.additional_info['procedure_group'] = ability_data['procedure_group']
        if 'procedure_step' in ability_data:
            ability.additional_info['procedure_step'] = ability_data['procedure_step']
        
        # Store ability
        await self.data_svc.store(ability)
        
        # Save ability to disk
        self._save_ability_to_file(ability)
        
        return ability

    def _ensure_payload_exists(self, payload_name):
        """Create a placeholder for a payload if it doesn't exist"""
        payload_dir = os.path.join('data', 'payloads')
        if not os.path.exists(payload_dir):
            os.makedirs(payload_dir)
            
        payload_path = os.path.join(payload_dir, payload_name)
        if not os.path.exists(payload_path):
            with open(payload_path, 'w') as f:
                f.write(f"# Placeholder for payload: {payload_name}\n")
                f.write("# Replace this with the actual payload content\n")
                f.write(f"# Created by Emulation Plan Importer at {datetime.now()}\n")

    def _save_ability_to_file(self, ability):
        """Save ability to disk as a YAML file"""
        # Create directory structure
        tactic_dir = os.path.join(self.abilities_directory, ability.tactic.lower())
        if not os.path.exists(tactic_dir):
            os.makedirs(tactic_dir)
            
        # Create ability YAML
        ability_yaml = {
            'id': ability.ability_id,
            'name': ability.name,
            'description': ability.description,
            'tactic': ability.tactic,
            'technique': {
                'attack_id': ability.technique_id,
                'name': ability.technique_name
            },
            'platforms': {}
        }
        
        # Add executors
        for executor in ability.executors:
            if executor.platform not in ability_yaml['platforms']:
                ability_yaml['platforms'][executor.platform] = {}
                
            exec_data = {
                'command': executor.command
            }
            
            if executor.cleanup:
                exec_data['cleanup'] = executor.cleanup
                
            if executor.payloads:
                exec_data['payloads'] = executor.payloads
                
            ability_yaml['platforms'][executor.platform][executor.name] = exec_data
        
        # Add additional info
        if ability.additional_info:
            for key, value in ability.additional_info.items():
                ability_yaml[key] = value
                
        # Write to file
        file_path = os.path.join(tactic_dir, f"{ability.ability_id}.yml")
        with open(file_path, 'w') as f:
            yaml.dump(ability_yaml, f, default_flow_style=False)
            
    async def _create_adversary(self, adversary_info, abilities):
        """Create an adversary from the extracted info and abilities"""
        adversary_id = adversary_info.get('id', str(uuid.uuid4()))
        name = adversary_info.get('adversary_name', 'Imported Adversary')
        description = adversary_info.get('adversary_description', 'Imported from emulation plan')
        
        # Order abilities by procedure step if available
        ordered_abilities = sorted(
            abilities, 
            key=lambda x: x.additional_info.get('procedure_step', '999')
        )
        
        # Create adversary
        adversary = Adversary(
            adversary_id=adversary_id,
            name=name,
            description=description,
            atomic_ordering=[a.ability_id for a in ordered_abilities]
        )
        
        # Store adversary
        await self.data_svc.store(adversary)
        
        return adversary
