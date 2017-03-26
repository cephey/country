def get_text_banner(request):
    """
    my $self = shift;
    return $self->get_text_banner_by_tbn($self->get_tbn_by_uri(@_));
    my $sape = new Forum::Export::Links(
        user => 'c55bf3fc219b9610c2b8abde2d8ed171',
        host => 'forum.msk.ru',
        charset => 'koi8-r',
        timeout => 600,
        filename => $state->data_dir.'/links.db',
        uri => shift || '/index.html',
        remote_ip => '80.93.56.97',
        force_show_code => 1,
    );
    my $links = $sape->get_links( count => 10 );
    return $links=~/\S/ ? $links : undef;
    """
    return ''


def global_context(request):
    return {
        'mobile_url': request.get_host() + 'pda/',
        'rambler_id': '868956' if 'lenin' in request.path else '24858',
        'text_banner': get_text_banner(request)
    }
