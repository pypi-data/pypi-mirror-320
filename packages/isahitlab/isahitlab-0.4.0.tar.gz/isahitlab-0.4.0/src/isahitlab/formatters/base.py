from abc import ABC, abstractmethod
from typing import Dict, List

from isahitlab.helpers.inputs_layout import (
  extract_inputs_by_id_from_layout, extract_inputs_by_types_from_layout)


class BaseFormatter(ABC):
    """Base class for all formatter."""
    
    _type: str = None
    _data_input_id: str = None
    _options: Dict = {}
    _project_configuration: Dict

    def _normalize_task(self, task: Dict):
        """Make form data behaves the same that iat data"""

        if self._data_input_id:
            return {
                **task,
                "resources" : task.get("data",{}).get("body", {}).get(self._data_input_id, {}).get("resources", []),
                "data": {
                    **task.get("data",{}),
                    "body" : task.get("data",{}).get("body", {}).get(self._data_input_id, {})
                } 
            }
        else:
            return task
    
    ### Configuration
    def _init_configuration(self, project_configuration : Dict, options: Dict, compatibility: Dict):

        self._options = options or {}

        project_type = project_configuration['projectType']


        # If not compatibility list provided, everything is compatible
        if "compatible_types" not in compatibility:
            self._project_configuration = project_configuration
            return

        # Prepare compatibility
        compatible_projects = [t for t in compatibility["compatible_types"] if t[0:5] != "form."]
        compatible_form_inputs = [t[5:] for t in compatibility["compatible_types"] if t[0:5] == "form."]
        
        if project_type in compatible_projects:
            self._project_configuration = project_configuration
            self._type = project_type
            return
        
        if project_type == "form" and len(compatible_form_inputs) > 0:
            inputs_layout = project_configuration.get('metadata', {}).get('inputsLayout', None)
            
            # If a specific input_id is spotted
            if options["input_id"]:
                inputs_for_id = extract_inputs_by_id_from_layout(inputs_layout, options["input_id"])
                input_for_id = inputs_for_id[0] if len(inputs_for_id) > 0 else None
                if not input_for_id or input_for_id["type"] not in compatible_form_inputs:
                    raise Exception('No compatible input found for input_id {} (compatible inputs: {})'.format(options["input_id"], ", ".join(compatible_form_inputs)))
                
                self._data_input_id =  input_for_id['id']
                self._project_configuration = input_for_id['config']
                self._type = input_for_id['type']
                return
            else: # Auto select input if there is only one compatible
                compatible_inputs = extract_inputs_by_types_from_layout(inputs_layout, ['tool-iat-rectangle'])

                if len(compatible_inputs) == 0:
                    raise Exception('No compatible input found (compatible inputs: {})'.format(", ".join(compatible_form_inputs)))
                if len(compatible_inputs) > 1:
                    raise Exception('input_id option is required to select the form input')

                self._data_input_id =  compatible_inputs[0]['id']
                self._project_configuration = compatible_inputs[0]['config']
                self._type =  compatible_inputs[0]['type']
                return


        raise Exception('Project type not compatible')
        

    @abstractmethod
    def format_tasks(self, tasks: List[Dict]) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def append_task_to_export(self, task: Dict):
        raise NotImplementedError
    
    @abstractmethod
    def complete_export(self, tasks: List[Dict]):
        raise NotImplementedError