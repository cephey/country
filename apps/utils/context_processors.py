def global_context(request):
    return {
        'mobile_url': request.get_host() + 'pda/',
        'rambler_id': '868956' if 'lenin' in request.path else '24858',
    }
