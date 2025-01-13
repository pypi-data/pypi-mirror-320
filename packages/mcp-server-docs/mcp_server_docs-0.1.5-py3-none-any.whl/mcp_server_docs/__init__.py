from . import server, explorer
import asyncio
import click


class DictParamType(click.ParamType):
    name = "dictionary"

    def convert(self, value, param, ctx):
        if isinstance(value, dict):
            return value
        try:
            pairs = [pair.split('=') for pair in value.split(',')]
            return {k.strip(): v.strip() for k, v in pairs}
        except ValueError:
            self.fail(
                f"{value!r} is not a valid dictionary format", param, ctx
            )


DICT_TYPE = DictParamType()


@click.command()
@click.argument("repositories", type=DICT_TYPE, required=True)
def main(repositories: dict[str, str]):

    """Main entry point for the package."""
    asyncio.run(server.serve(repositories))


# Optionally expose other important items at package level
__all__ = ['main', 'server', 'explorer']
