
from inbase import BaseRestful
import logging


class Ethernet(BaseRestful):
    __doc__ = '\n    Get Ethernet/bridge status/info, update Ethernet/bridge config\n    '

    def __init__(self, ip='', port=''):
        if ip and port:
            BaseRestful.__init__(self, ip=ip, port=port)
        else:
            BaseRestful.__init__(self)
        self.eth_status = self.url_base + '/v1/eth/status'
        self.eth_config = self.url_base + '/v1/eth/config'
        self.bridge_status = self.url_base + '/v1/bridge/status'
        self.bridge_config = self.url_base + '/v1/bridge/config'
        self.route_status = self.url_base + '/v1/route/status'
        self.dns_config = self.url_base + '/v1/dns/server/config'

    def get_ethernet_status(self, iface=''):
        """
        get ethernet status
        :param iface:
            "eth1" for 0/1, "eth2" for 0/2
        :return:
            {
                "iface_name": "gigabitethernet 0/1",
                "connect_type": 0,  # 0:static IP, 1:(DHCP), 2:ADSL (PPPOE)
                "ip_addr": "192.168.1.1",
                "netmask": "255.255.255.0",
                "gateway": "0.0.0.0",
                "dns": "0.0.0.0",
                "mtu": 1500,
                "status": 1,                  #  0:Down, 1:Up
                "connect_time": 0,
                "remaining_lease": 0,
                "description": ""
            }
        """
        if iface not in ('eth1', 'eth2'):
            raise KeyError('Invalid iface, it should be eth1 or eth2')
        data = {'iface': iface}
        ethe_status = self.get_url_info((self.eth_status), params=data)
        dns_config = self.get_dns_config()
        route_status = self.get_route_status()
        try:
            if 'primary_dns' in dns_config:
                if 'secondary_dns' in dns_config:
                    pri_dns = dns_config['primary_dns']
                    sec_dns = dns_config['secondary_dns']
                    status, dns = ethe_status['status'], ethe_status['dns']
                    if status:
                        if '0.0.0.0' in dns:
                            ethe_status['dns'] = '{pri_dns} {sec_dns}'.format(pri_dns=pri_dns,
                              sec_dns=sec_dns)
            if len(route_status) > 0:
                iface_name = ethe_status['iface_name']
                for rs in route_status:
                    if 'type' in rs and 'destination' in rs and 'netmask' in rs and 'gateway' in rs and rs['type'] == 'static' and rs['destination'] == '0.0.0.0' and rs['netmask'] == '0.0.0.0' and rs['interface'] == iface_name:
                        ethe_status['gateway'] = rs['gateway']

        except Exception as e:
            try:
                logging.info('get_ethernet_status error: %s' % e)
            finally:
                e = None
                del e

        return ethe_status

    def get_route_status(self):
        """
        get route status
        :return:
            [
                {
                    "type": "static",
                    "destination": "0.0.0.0",
                    "netmask": "0.0.0.0",
                    "gateway": "192.168.3.1",
                    "interface": "gigabitethernet 0/1",
                    "distance_metric": "1/0",
                    "time": ""
                },
            ]
        """
        return self.get_url_info(self.route_status)

    def get_dns_config(self):
        """
        get dns config
        :return:
            {
                "primary_dns": "114.114.114.114",
                "secondary_dns": "8.8.8.8"
            }
        """
        return self.get_url_info(self.dns_config)

    def get_bridge_status(self, brid=None):
        """
        get bridge status
        :param brid: bridge id, int
        :return:
            [
                {
                "iface_name": "bridge 1",
                "ip_addr": "192.168.2.1",
                "netmask": "255.255.255.0",
                "gateway": "0.0.0.0",
                "dns": "0.0.0.0",
                "mtu": 1500,
                "status": 1,
                "connect_time": 0,
                "remaining_lease": 0,
                "description": "",
                "bridge_ifaces": ["dot11radio 1", "gigabitethernet 0/2"]
                }
            ]
        """
        data = {'brid': brid}
        return self.get_url_info((self.bridge_status), params=data)


if __name__ == '__main__':
    ethe = Ethernet()
    get_eth_status = ethe.get_ethernet_status(iface='eth1')
    print('get eth1 status: %s' % get_eth_status)
    get_eth_status = ethe.get_ethernet_status(iface='eth2')
    print('get eth2 status: %s' % get_eth_status)
    get_bridge_status = ethe.get_bridge_status(brid=1)
    print('get_bridge_status : %s' % get_bridge_status)