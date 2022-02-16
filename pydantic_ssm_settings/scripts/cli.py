#!/usr/bin/env python3

from pathlib import Path
import textwrap

import boto3
import click
import dotenv

client = boto3.client("ssm")


@click.command()
@click.argument("dotenv_file", type=click.Path(exists=True))
@click.argument("prefix", type=click.Path())
@click.option(
    "--overwrite",
    "Overwrite",
    default=False,
    help="Overwrite an existing parameter.",
)
@click.option(
    "--type",
    "Type",
    default="SecureString",
    type=click.Choice(["String", "StringList", "SecureString"], case_sensitive=False),
    help="The type of parameter that you want to add to the system.",
)
def load(dotenv_file: click.Path, prefix: click.Path, **kwargs):
    config = dotenv.dotenv_values(dotenv_file)

    print(prefix)

    for k, v in config.items():
        path = Path(prefix) / k.lower()
        try:
            client.put_parameter(
                Name=str(path),
                Description="Created by the dotenv-to-ssm script.",
                Value=v,
                Tags=[
                    {"Key": "author", "Value": "string"},
                ],
                **kwargs,
            )
            print(f"Created {path}")
        except Exception as e:
            error_text = textwrap.indent(str(e), prefix="\t")
            print(f"Failed to create {path}: \n{error_text}")
            print(kwargs)
