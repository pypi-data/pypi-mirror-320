# NetMagic Brocade Device Library

# Python Modules
from itertools import chain
from re import search, sub

# Local Modules
from netmagic.common.types import Vendors
from netmagic.common.classes import (
    CommandResponse, ResponseGroup, Interface,
    InterfaceOptics, InterfaceStatus, InterfaceLLDP,
    InterfaceVLANs, SVI
)
from netmagic.common.utils import get_param_names, brocade_text_to_range
from netmagic.devices.switch import Switch
from netmagic.sessions import Session


class BrocadeSwitch(Switch):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.vendor = Vendors.BROCADE

    def session_preparation(self):
        """
        CLI session preparation either for SSH jumping or serial connections
        """
        super().session_preparation('brocade_fastiron')
        self.command('skip-page-display')

    # CUSTOM FSM METHOD

    # IDENTITY
    def get_running_config(self) -> CommandResponse:
        """
        Returns the running configuration.
        """
        return super().get_running_config()

    def get_interface_status(self, interface: str = None,
                             template: str|bool = None) -> CommandResponse:
        """
        Returns interface status of one or all switchports.
        
        PARAMS:
        `interface`: `str` for the name of getting the full status of a single interface
        `template`: `str` for the path of the TextFSM template to use, else `None`
           will use the default built-in, and `False` will skip parsing 
        """
        command_portion = 'brief wide' if interface is None else f'e {interface}'
        int_status = self.command(f'show interface {command_portion}')

        if template is False:
            return int_status
        
        template = 'show_int' if interface is None else 'show_single_int'
        fsm_data = self.fsm_parse(int_status.response, template)
        int_status.fsm_output = {i['interface']: InterfaceStatus(host = self.hostname, **i) for i in fsm_data}
        
        return int_status
    
    def get_all_interface_status(self) -> ResponseGroup:
        """
        Returns all the detailed entries for interfaces on the device
        """
    
    def get_media(self, template: str|bool = None) -> CommandResponse:
        """
        Returns the media information on the device

        PARAMS:
        `template`: `str` for the path of the TextFSM template to use, else `None`
           will use the default built-in, and `False` will skip parsing 
        """
        media = self.command('show media')

        if template is not False:
            template = 'show_media' if template is None else template
            media.fsm_output = self.fsm_parse(media.response, template)

        return media
    
    def get_optics(self, template: str|bool = None) -> ResponseGroup:
        """
        Returns information about optical transceivers.
        """
        media = self.get_media()
        optical_interfaces = [i['interface'] for i in media.fsm_output if search(r'(?i)sfp', i['medium'])]
        
        optics_responses = [self.command(f'show optic {intf}') for intf in optical_interfaces]
        optics = ResponseGroup(optics_responses, None, 'Brocade Optics Data')
        
        if template is not False:
            template = 'show_optic' if template is None else template
            optics_data = [optics_response.response for optics_response in optics.responses]
            fsm_data = [self.fsm_parse(i, template) for i in optics_data]
            optics.fsm_output = {i['interface']: InterfaceOptics.create(self.hostname, **i) for i in chain(*fsm_data)}

        return optics
    
    def get_lldp(self, template: str|bool = None) -> CommandResponse:
        """
        Returns LLDP neighbor details information.
        """
        lldp = self.command('show lldp neighbor detail')

        # Cases to skip parsing, lldp only shows up in the response if LLDP is not enabled
        if template is False or search(r'lldp', lldp.response):
            return lldp
        
        # Fix anything that has a multi-line field and adding an end record designator
        lldp.response = sub(r'\\\n\s+', '', lldp.response).replace('\n\n','\nEND\n')

        # The built-in template REQUIRES the above pre-processing to work correctly
        template = 'show_lldp_nei_det' if not template else template
        fsm_data = self.fsm_parse(lldp.response, template)
        lldp.fsm_output = {i['interface']: InterfaceLLDP(host = self.hostname, **i) for i in fsm_data}

        return lldp
    
    def get_tdr_data(self, interface_status: CommandResponse = None,
                     only_bad: bool = True, template: str|bool = None):
        """
        Collects TDR data of interfaces
        """
        input_kwargs = {k:v for k,v in locals().items() if k in get_param_names(self.get_tdr_data)}

        tdr_common = 'cable-diagnostics tdr'

        additional_kwargs = {
            'send_tdr_command': f'phy {tdr_common}',
            'show_tdr_command': f'show {tdr_common}',
        }

        response = super().get_tdr_data(**input_kwargs, **additional_kwargs)
        if response:
            response.description = f'{self.hostname} TDR'
            return response
        
    def get_poe_status(self, template: str|bool = None) -> CommandResponse:
        template = 'show_poe' if template is None else template
        return super().get_poe_status('show poe', template)
    
    def get_mac_table(self, template: str|bool = None) -> CommandResponse:
        show_command = 'show mac-address'
        return super().get_mac_table(show_command, template)
    
    def get_interface_vlans(self, template: str|bool = None) -> dict[str, InterfaceVLANs|SVI]:
        template = 'show_run_vlans' if template is None else template
        fsm_data = self.fsm_parse(self.get_running_config().response, template)
        results: dict[str, dict[str, list[str]]] = {}

        def append_to_results(interface: str, vlan: int, tag_type: str):
            if interface not in results:
                results[interface] = {tag_type: [vlan]}
                return
            if tag_type in results[interface]:
                results[interface][tag_type].append(vlan)
            else:
                results[interface][tag_type] = [vlan]

        for line in fsm_data:
            if line['interface'] and line['dual']:
                results[line['interface']]['dual'] = line['dual']
                continue
            for tag_type in ['untags', 'tags']:
                for interface in brocade_text_to_range(line[tag_type]):
                    append_to_results(interface, line['vlan'], tag_type)
            
        for info in results.values():
            for tag_type in ['untags', 'tags']:
                if info.get(tag_type):
                    info['mode'] = 'access' if len(info[tag_type]) == 1 else 'trunk'
                    info[tag_type] = ','.join([i for i in info[tag_type] if i])

        output: dict[str, InterfaceVLANs|SVI] = {}
        for interface, kwargs in results.items():
            # Rename the entry for model compatibility
            if kwargs.get('tags'):
                kwargs['trunk'] = kwargs.pop('tags')
            output[interface] = InterfaceVLANs(host=self.hostname, interface=interface, **kwargs)

        return output
