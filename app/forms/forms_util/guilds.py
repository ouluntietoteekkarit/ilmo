GUILD_OTIT = 'OTiT'
GUILD_SIK = 'SIK'
GUILD_YMP = 'YMP'
GUILD_KONE = 'KONE'
GUILD_PROSE = 'PROSE'
GUILD_OPTIEM = 'OPTIEM'
GUILD_ARK = 'ARK'


class Guild(object):

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


def get_all_guilds():
    return [
        Guild(GUILD_OTIT),
        Guild(GUILD_SIK),
        Guild(GUILD_YMP),
        Guild(GUILD_KONE),
        Guild(GUILD_PROSE),
        Guild(GUILD_OPTIEM),
        Guild(GUILD_ARK)
    ]