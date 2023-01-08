##->> Configure version info
from .version import __version__

##->> Configure output colours
from .CustomLogger import colors as c

#-> Source: https://www.developmenttools.com/ascii-art-generator
banner = f'''
{c["purple"]} ________   _______    ____________   ____      .__  .__    .___       __                {c["reset"]}
{c["purple"]} \______ \  \      \  /   _____\   \ /   _____  |  | |__| __| ______ _/  |_ ___________  {c["reset"]}
{c["purple"]}  |    |  \ /   |   \ \_____  \ \   Y   /\__  \ |  | |  |/ __ |\__   \   __/  _ \_  __ \ {c["reset"]}
{c["purple"]}  |    `   /    |    \/        \ \     /  / __ \|  |_|  / /_/ | / __ \|  |(  <_> |  | \/ {c["reset"]}
{c["purple"]} /_______  \____|__  /_______  /  \___/  (____  |____|__\____ |(____  |__| \____/|__|    {c["reset"]}
{c["purple"]}         \/        \/        \/               \/             \/     \/                   {c["reset"]}
{c["purple"]} v{__version__} {c["reset"]}
'''

def print_banner() -> None:
    print(banner)
