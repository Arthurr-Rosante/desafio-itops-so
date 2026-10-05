import ipaddress, random

def gen_random_ip(v6 = False):
    if(v6):
        return str(ipaddress.IPv6Address(random.randint(0, 2 ** 128)))
    return str(ipaddress.IPv4Address(random.randint(0, 2 ** 32)))