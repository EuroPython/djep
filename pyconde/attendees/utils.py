# -*- coding: utf-8 -*-
import xmlrpclib


def validate_vatid(own_vatid, other_vatid):
    try:
        server = xmlrpclib.Server('https://evatr.bff-online.de/')
        data = {}
        for item in xmlrpclib.loads(server.evatrRPC(own_vatid.replace(' ', ''),
            other_vatid.replace(' ', ''), '', '', '', '', ''))[0]:
            data[item[0]] = item[1]
        return data['ErrorCode'] == '200'
    except:
        return False
