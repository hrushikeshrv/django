from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

import ipaddress


def get_ip(request):
    ip_meta_key = getattr(settings, 'RATELIMIT_IP_META', None)
    if not ip_meta_key:
        ip = request.META['REMOTE_ADDR']
        if not ip:
            raise ImproperlyConfigured(
                'Could not get IP address from request '
                '(REMOTE_ADDR in request is empty)'
            )
    elif callable(ip_meta_key):
        ip = ip_meta_key(request)
    elif isinstance(ip_meta_key, str) and '.' in ip_meta_key:
        ip_getter = import_string(ip_meta_key)
        ip = ip_getter(request)
    elif ip_meta_key in request.META:
        ip = request.META[ip_meta_key]
    else:
        raise ImproperlyConfigured(
            '"Could not get IP address from the IP meta key "%s"' % ip_meta_key
        )

    if ':' in ip:
        mask = getattr(settings, 'RATELIMIT_IPV6_MASK', 64)
    else:
        mask = getattr(settings, 'RATELIMIT_IPV4_MASK', 32)

    network = ipaddress.ip_network(f'{ip}/{mask}', strict=False)
    return str(network.network_address)
