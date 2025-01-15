def get_cookie_domain(request):
    if 'HTTP_HOST' in request.META:
        host = request.META['HTTP_HOST']
        if 'stitch.fashion' in host:
            return '.stitch.fashion'
        if 'stitch3d.com' in host:
            return '.stitch3d.com'
    return '.hub3d.pvh.com'

def get_assets_v2_domain(request):
    return '*' + get_cookie_domain(request)
