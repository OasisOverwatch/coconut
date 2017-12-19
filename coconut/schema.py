import itertools
import functools


class ValidatorException(Exception):
    def __init__(self, reason):
        self.reason = reason


class Validator(object):
    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def validate(self, token):
        pass


class ValidatorsExhausted(Exception):
    pass


class MissingRequiredArgument(Exception):
    def __init__(self, name):
        self.name = 'Missing required argument: ' + name


class Schema(object):
    def __init__(self, validators=[]):
        self.validators = validators

    def validate(self, tokens):
        kwargs = {}
        for token, validator in itertools.zip_longest(tokens, self.validators):
            if token and validator:
                kwargs[validator.name] = validator.validate(token)
            elif validator:
                if validator.default is not None:
                    kwargs[validator.name] = validator.default
                else:
                    raise MissingRequiredArgument(validator.name)
            else:
                raise ValidatorsExhausted
        return kwargs


async def handle_validator_exception(client, message, text):
    await client.send_message(message.channel, text)


def command(schema):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tokens = kwargs.pop('tokens')
            if schema:
                try:
                    new_kwargs = {**kwargs, **schema.validate(tokens)}
                    return await func(*args, **new_kwargs)
                except ValidatorException as e:
                    return await handle_validator_exception(*args, e.reason, **kwargs)
                except ValidatorsExhausted:
                    return await handle_validator_exception(*args, 'Sorry, I don\'t understand what you\'re trying to say', **kwargs)
                except MissingRequiredArgument as e:
                    return await handle_validator_exception(*args, e.name, **kwargs)

        return wrapper
    return decorator
