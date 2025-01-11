import re
from typing import List, Dict
from ipaddress import ip_network
import logging

from napalm.ios import IOSDriver
from napalm.base.helpers import textfsm_extractor

from ..models import RouteDict, MPLSDict, InventoryDict, IPInterfaceDict
from ..base import UMnetNapalmError, UMnetNapalm


IOS_LABEL_VALUES = {
    "": [],
    "No Label": [],
    "Pop Label": ["pop"],
}

logger = logging.getLogger(__name__)


class IOS(UMnetNapalm, IOSDriver):
    """
    IOS Parser
    """

    LABEL_VALUE_MAP = {
        "": [],
        "No Label": [],
        "Pop Label": ["pop"],
    }

    INVENTORY_TO_TYPE = {
        r"Supervisor": "re",
        r"WS-": "linecard",
        r"Transceiver": "optic",
        r"Fan Module": "fan",
        r"[Pp]ower [Ss]upply": "psu",
        r"Uplink Module": "uplink-module",
        r"^Switch \d+$": "stack-member",
        r"StackPort": "optic",
        # on catalyst the optics show up as interface names
        # sometimes the names are abbreviated and sometimes they
        # are not (sigh)
        r"^(Twe|Te|Gi|Two).+\d$": "optic",
        # don't care about these inventory items
        r"(Clock FRU|Daughterboard|Feature Card|Forwarding Card)": None,
        # this is the chassis id of the master of the stack,
        # we
        r"Stack": None,
    }

    I_ABBRS = {
        "Lo":"Loopback",
        "Po":"Port-channel",
        "Fa":"FastEthernet",
        "Ge":"GigabitEthernet",

        # longer matches must go first!
        "Twe":"TwentyFiveGigE",
        "Tw":"TwoGigabitEthernet",

        "Te":"TenGigabitEthernet",
        "Vl":"Vlan",

    }

    PROTOCOL_ABBRS = {
        "L": "local",
        "C": "connected",
        "S": "static",
        "i": "ISIS",
        "B": "BGP",
        "O": "OSPF",
    }

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):

        if not optional_args:
            optional_args = {}
        optional_args["read_timeout_override"] = timeout
        
        super().__init__(hostname, username, password, timeout, optional_args)

        self._i_descrs = None


    def _parse_label_value(self, label) -> list:
        """
        Parses mpls label value into normalized data
        """
        if label in IOS_LABEL_VALUES:
            return IOS_LABEL_VALUES[label]

        return [label]

    def _get_route_labels(self) -> Dict[tuple, str]:
        """
        Runs "show bgp vpnv4 unicast labels" and parses the result.

        The output is a dictionary with (vrf, prefix) as key
        and the outbound label as a value, eg
        output[ ("vrf_VOIP_NGFW", "0.0.0.0/0") ] = "12345"
        """

        raw_labels = self._send_command("show bgp vpnv4 unicast all labels")
        labels = textfsm_extractor(self, "sh_bgp_vpnv4_unicast_all_labels", raw_labels)

        # default route shows up as '0.0.0.0' so we have to munge that
        output = {}
        for l in labels:
            prefix = "0.0.0.0/0" if l["prefix"] == "0.0.0.0" else l["prefix"]
            output[(l["vrf"], ip_network(prefix))] = l["out_label"]

        return output

    @property
    def i_descrs(self):
        """
        Pulls interface descriptions into an internal data structure
        """

        if self._i_descrs is None:
            raw_output = self._send_command("show interface description")
            output = textfsm_extractor(self, "sh_interface_description", raw_output)
            self._i_descrs = {o["interface"]:o["description"] for o in output}
        return self._i_descrs

    def get_ip_interfaces(self) -> List[IPInterfaceDict]:
        """
        Parses 'show ip interface' and 'show ipv6 interface'
        """
        raw_output = self._send_command("show ip interface")
        output = textfsm_extractor(self, "sh_ip_interface", raw_output)

        ip_interfaces = []
        for i in output:

            i_data = {
                "ip_address": i["ip"],
                "interface": i["interface"],
                "description": self.i_descrs.get(self._abbr_i(i["interface"]), ""),
                "mtu": int(i["mtu"]) if i["mtu"] else None,
                "admin_up": i["admin_state"] != "administratively down",
                "oper_up": i["oper_state"] == "up",
                "vrf": i["vrf"] if i["vrf"] else "default",
                "secondary": False,
                "helpers": set(i["helpers"]) if i["helpers"] else [], 
            }
            ip_interfaces.append(i_data)

            for sec_i in i["sec_ip"]:

                sec_data = i_data.copy()
                sec_data["ip_address"] = sec_i
                sec_data["secondary"] = True

                ip_interfaces.append(sec_data)

        raw_output = self._send_command("show ipv6 interface")
        output = textfsm_extractor(self, "sh_ipv6_interface", raw_output)

        for i in output:
            for ip in i["ip"]:
                ip_interfaces.append(
                    {
                    "ip_address": ip,
                    "interface": i["interface"],
                    "description": self.i_descrs.get(self._abbr_i(i["interface"]), ""),
                    "mtu": int(i["mtu"]) if i["mtu"] else None,
                    "admin_up": i["admin_state"] != "administratively down",
                    "oper_up": i["oper_state"] == "up",
                    "vrf": i["vrf"] if i["vrf"] else "default",

                    # IPv6 secondary and helpers not relevant in our environment
                    "secondary": False,
                    "helpers": [], 
                    }
                )

        return ip_interfaces

    def get_active_routes(self) -> List[RouteDict]:
        """
        Parses "show ip route vrf *" for IOS. Will also run
        "show bgp vpnv4 unicast labels" to get label bindings
        """

        output = []

        raw_routes = self._send_command("show ip route vrf *")
        routes = textfsm_extractor(self, "sh_ip_route_vrf_all", raw_routes)

        for route in routes:
            logger.info(f"found proto {route['proto_1']} for route {route}")
            protocol = self._parse_protocol_abbr(route["proto_1"])

            # "learned from" is one of the keys in our route table that determines
            # uniqueness, as such we need to make sure it's set. Usually it's
            # the IP of the advertising router, but for local/direct/static it should
            # get set to 'self'
            if route["nh_ip"]:
                learned_from = route["nh_ip"]
            elif protocol in ["local", "connected", "static"]:
                learned_from = "self"
            else:
                raise UMnetNapalmError(f"Could not determine learned from for {route}")

            output.append(
                {
                    "vrf": route["vrf"] if route["vrf"] else "default",
                    "prefix": route["prefix"],
                    "nh_interface": route["nh_interface"],
                    "learned_from": learned_from,
                    "protocol": self._parse_protocol_abbr(route["proto_1"]),
                    "age": route["age"] if route["age"] else None,
                    "nh_ip": route["nh_ip"],
                    "mpls_label": None,
                    "vxlan_vni": None,
                    "vxlan_endpoint": None,
                    "nh_table": route["vrf"] if route["vrf"] else "default",
                }
            )

        return output

    def get_inventory(self) -> list[InventoryDict]:
        """
        Parses "show inventory" for IOS
        """
        raw_inventory = self._send_command("show inventory")
        inventory = textfsm_extractor(self, "sh_inventory", raw_inventory)

        output = []
        for entry in inventory:
            inventory_type = self._get_inventory_type(entry["name"])

            if not inventory_type:
                continue

            output.append(
                {
                    "type": inventory_type,
                    "name": entry["name"],
                    "part_number": entry["pid"],
                    "serial_number": entry["sn"],
                    "parent": None,
                }
            )

        return output

    def get_mpls_switching(self) -> List[MPLSDict]:
        """
        Parses "show mpls forwarding table" for IOS
        """
        raw_labels = self._send_command("show mpls forwarding-table")
        labels = textfsm_extractor(self, "sh_mpls_forwarding_table", raw_labels)

        output = []
        for entry in labels:
            # extract RD from 'FEC'
            m = re.match(r"([\d\.]+:\d+):(\d+.\d+.\d+.\d+\/\d+)", entry["fec"])
            if m:
                rd = m.group(1)
                fec = m.group(2)
            else:
                rd = None
                fec = entry["fec"]

            aggregate = bool(entry["vrf"])
            nh_interface = entry["vrf"] if entry["vrf"] else entry["nh_interface"]

            output.append(
                {
                    "in_label": entry["in_label"],
                    "fec": fec,
                    "out_label": self._parse_label_value(entry["out_label"]),
                    "nh_ip": entry["nh_ip"],
                    "nh_interface": nh_interface,
                    "rd": rd,
                    "aggregate": aggregate,
                }
            )

        return output
