"""Browser channels are available consistently on Windows, macOS and Linux."""
from pathlib import Path


def browser_options(config,root):
    choice=config.get('browser','chromium')
    if choice not in ('edge','chrome','chromium'):
        raise ValueError('browser must be edge, chrome, or chromium')
    channel={'edge':'msedge','chrome':'chrome','chromium':'chromium'}[choice]
    suffix={'edge':'','chrome':'-chrome','chromium':'-chromium'}[choice]
    return str(Path(root)/('browser-profile'+suffix)),channel
