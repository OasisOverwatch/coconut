import os
import argparse
import click
from alembic.config import Config as AlembicConfig
from alembic import command


class Config(AlembicConfig):
    def get_template_directory(self):
        package_dir = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(package_dir, 'templates')


def get_config(directory='migrations', x_arg=None, opts=None):
    config = Config(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)
    if config.cmd_opts is None:
        config.cmd_opts = argparse.Namespace()
    for opt in opts or []:
        setattr(config.cmd_opts, opt, True)
    if not hasattr(config.cmd_opts, 'x'):
        if x_arg is not None:
            setattr(config.cmd_opts, 'x', [])
            if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                for x in x_arg:
                    config.cmd_opts.x.append(x)
            else:
                config.cmd_opts.x.append(x_arg)
        else:
            setattr(config.cmd_opts, 'x', None)
    return config


@click.group()
def cli():
    pass


@cli.group()
def db():
    """Perform database micrations"""
    pass


@db.command()
@click.option('-d', '--directory', default='migrations',
              help='migration script directory (default is "migrations")')
def init(directory):
    """Creates a new migration repository."""
    config = Config()
    config.set_main_option('script_location', directory)
    config.config_file_name = os.path.join(directory, 'alembic.ini')
    command.init(config, directory, 'coconut')


@db.command()
@click.option('-d', '--directory', default='migrations',
              help='migration script directory (default is "migrations")')
@click.option('-m', '--message', default=None, help='Revision message')
@click.option('--sql', is_flag=True,
              help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--head', default='head',
              help='Specify head revision or <branchname>@head to base new revision on')
@click.option('--splice', is_flag=True,
              help='Allow a non-head revision as the "head" to splice onto')
@click.option('--branch-label', default=None,
              help='Specify a branch label to apply to the new revision')
@click.option('--version-path', default=None,
              help='Specify specific path from config for version file')
@click.option('--rev-id', default=None,
              help='Specify a hardcoded revision id instead of generating one')
@click.option('-x', '--x-arg', multiple=True,
              help='Additional arguments consumed by custom env.py scripts')
def migrate(directory=None, message=None, sql=False, head='head', splice=False,
            branch_label=None, version_path=None, rev_id=None, x_arg=None):
    """Alias for 'revision --autogenerate'"""
    config = get_config(directory, opts=['autogenerate'], x_arg=x_arg)
    command.revision(config, message, autogenerate=True, sql=sql,
                     head=head, splice=splice, branch_label=branch_label,
                     version_path=version_path, rev_id=rev_id)


@db.command()
@click.option('-d', '--directory', default='migrations',
              help='migration script directory (default is "migrations")')
@click.option('-m', '--message', default=None, help='Merge revision message')
@click.option('--branch-label', default=None,
              help='Specify a branch label to apply to the new revision')
@click.option('--rev-id', default=None,
              help='Specify a hardcoded revision id instead of generating one')
@click.argument('revisions', nargs=-1)
def merge(directory, message, branch_label, rev_id, revisions):
    """Merge two revisions together, creating a new revision file"""
    config = get_config(directory)
    command.merge(config, revisions, message=message, branch_label=branch_label, rev_id=rev_id)


@db.command()
@click.option('-d', '--directory', default='migrations',
              help='migration script directory (default is "migrations")')
@click.option('--sql', is_flag=True,
              help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--tag', default=None,
              help='Arbitrary "tag" name - can be used by custom "env.py scripts')
@click.option('-x', '--x-arg', multiple=True,
              help='Additional arguments consumed by custom env.py scripts')
@click.argument('revision', default='head')
def upgrade(directory=None, revision='head', sql=False, tag=None, x_arg=None):
    """Upgrade to a later version"""
    config = get_config(directory, x_arg=x_arg)
    command.upgrade(config, revision, sql=sql, tag=tag)


@db.command()
@click.option('-d', '--directory', default='migrations',
              help='migration script directory (default is "migrations")')
@click.option('--sql', is_flag=True,
              help='Don\'t emit SQL to database - dump to standard output instead')
@click.option('--tag', default=None,
              help='Arbitrary "tag" name - can be used by custom "env.py scripts')
@click.option('-x', '--x-arg', multiple=True,
              help='Additional arguments consumed by custom env.py scripts')
@click.argument('revision', default='-1')
def downgrade(directory=None, revision='-1', sql=False, tag=None, x_arg=None):
    """Revert to a previous version"""
    config = get_config(directory, x_arg=x_arg)
    if sql and revision == '-1':
        revision = 'head:-1'
    command.downgrade(config, revision, sql=sql, tag=tag)


@db.command()
@click.option('-d', '--directory', default='migrations',
              help='migration script directory (default is "migrations")')
@click.argument('revision', default='head')
def show(directory, revision):
    """Show the revision denoted by the given symbol."""
    config = get_config(directory)
    command.show(config, revision)


if __name__ == '__main__':
    cli()
