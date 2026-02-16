def clean_url(url: str) -> str:
    """
    by now, its only intented to remove localisation prefix 'fr'
    :param url:
    :return:
    """
    return url.replace('/fr/', '/')
