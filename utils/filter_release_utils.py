EXCLUDED_RELEASE_TITLES = [
    'best of',
    'live',
    '(',
    ')',
    'instrumentals',
    'demos',
    'explicit',
]


def excluded_releases(release_title: str) -> bool:
    _title = release_title.lower()
    return any(ert in _title for ert in EXCLUDED_RELEASE_TITLES)
