from collections import defaultdict

META_TYPE_KEY = {
    'int': [
        'rows',
        'columns',
        'layers',
        'mrows',
        'mcolumns',
        'mrowres',
        'mcolumnres',
        'sections',
        'channels',
        'Zscan',
        'startnum',
    ],
    'float': [
        # legacy
        'xres', 'yres', 'zres', 'sectionres',
        # NOV 2024
        'xRes_um', 'yRes_um', 'zscan_resolution_um', 'section_depth',
    ],
}

META_LEGACY_KEY_MAPS = {
    'xres': ['xRes_um'],
    'yres': ['yRes_um'],
    'zres': ['zscan_resolution_um'],
    'sectionres': ['section_depth'],
}


class MosaicDict(defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = list

    def update(self, item):
        key, val = list(item.items())[0]
        if not key or not val:
            pass
        elif key in META_TYPE_KEY['int']:
            self[key] = int(val)
        elif key in META_TYPE_KEY['float']:
            self[key] = float(val)
        elif 'XPos' in key:
            self['XPos'].append(int(val))
        elif 'YPos' in key:
            self['YPos'].append(int(val))
        else:
            self[key] = val

    def legacy_update(self, value_override: dict = None):
        for legacy_key, key_map in META_LEGACY_KEY_MAPS.items():
            if legacy_key not in self:
                for key in key_map:
                    if key in self:
                        if value_override is not None and legacy_key in value_override:
                            self[legacy_key] = value_override[legacy_key]
                        else:
                            self[legacy_key] = self[key]
                        break
