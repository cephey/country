def global_context(request):
    return {
        'mobile_url': request.get_host() + 'pda/'
    }
