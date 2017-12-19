from coconut.schema import Validator, ValidatorException


class BlizzardID(object):
    def __init__(self, name, num):
        self.name = name
        self.num = num

    def __repr__(self):
        return self.join()

    def join(self, char='-'):
        return char.join([self.name, self.num])


class BlizzardIDValidator(Validator):
    def validate(self, token):
        if bool(token.count('#') == 1) ^ bool(token.count('-') == 1):
            token = token.replace('#', '-')
            return BlizzardID(*token.split('-'))
        raise ValidatorException('Token missing required separator (- or #)')
