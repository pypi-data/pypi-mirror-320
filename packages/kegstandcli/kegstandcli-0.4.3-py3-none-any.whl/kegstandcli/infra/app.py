#!/usr/bin/env python3
"""CDK app for Kegstand infrastructure."""

import sys
from pathlib import Path

import aws_cdk as cdk
import boto3
import click
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_cognito as cognito

from kegstandcli.cli.config import get_kegstand_config
from kegstandcli.infra.stacks.rest_api_backend import RestApiBackend
from kegstandcli.infra.stacks.rest_api_gateway import RestApiGateway

app = cdk.App()

# Get the passed context
region = app.node.try_get_context("region")
project_dir = app.node.try_get_context("project_dir")
config_file = app.node.try_get_context("config_file") or "kegstand.toml"
verbose = app.node.try_get_context("verbose") in ["true", "True", True]

# Get the Kegstand config
config = get_kegstand_config(verbose, project_dir, config_file)

click.echo(f"Creating app with config: {config}")

parent_stack_name = config["project"]["name"].replace(" ", "-")
parent_stack = cdk.Stack(
    app,
    parent_stack_name,
    description=f"{config['project']['name']} v.{config['project']['version']}",
    env=cdk.Environment(account=cdk.Aws.ACCOUNT_ID, region=region),
)

# Create stacks/modules
modules = {}

if "cdk" in config:
    click.echo("Creating additional resources [cdk]...")
    # Import the project's infra module
    project_infra_path = Path(project_dir) / config["cdk"]["path_to_infra"]
    sys.path.append(str(project_infra_path))
    from main import custom_infra  # type: ignore

    custom_infra_config = custom_infra(parent_stack, region)
    modules["custom_infra"] = custom_infra_config

if "api_gateway" in config:
    click.echo("Creating stack for [api_gateway]...")

    user_pool = (
        cognito.UserPool.from_user_pool_id(
            parent_stack, "UserPool", config["api_gateway"]["user_pool_id"]
        )
        if "user_pool_id" in config["api_gateway"]
        else None
    )

    click.echo(f"API GW is passed a UserPool?: {user_pool is not None}")

    api_gateway_construct_name = config["api_gateway"]["name"].replace(" ", "-")
    api_gateway_construct = RestApiGateway(
        parent_stack, api_gateway_construct_name, config, user_pool=user_pool
    )

    modules["api_gateway"] = api_gateway_construct

if "api" in config:
    click.echo("Creating stack for [api]...")

    gateway: apigw.IRestApi | None = None

    if "api_gateway_id" in config["api"]:
        rest_api_id = config["api"]["api_gateway_id"]
        # TODO: Move this to utils.py
        # Get the root resource ID from the API Gateway
        apigw_client = boto3.client("apigateway", region_name=region)
        response = apigw_client.get_resources(restApiId=rest_api_id)
        root_resource_id: list[str] = [
            resource["id"] for resource in response["items"] if resource["path"] == "/"
        ]
        if len(root_resource_id) == 0:
            raise click.ClickException("Could not find root resource ID for API Gateway")

        click.echo(f"Found API Gateway root resource ID: {root_resource_id[0]}")

        gateway = apigw.RestApi.from_rest_api_attributes(
            parent_stack,
            "RestApiGatewayReference",
            rest_api_id=rest_api_id,
            root_resource_id=root_resource_id[0],
        )
    elif "api_gateway" in modules:
        gateway = modules["api_gateway"].api

    user_pool = (
        parent_stack.node.try_find_child("UserPool")  # type: ignore
        if "api_gateway" in modules
        else (
            cognito.UserPool.from_user_pool_id(
                parent_stack, "UserPool", config["api"]["user_pool_id"]
            )
            if "user_pool_id" in config["api"]
            else None
        )
    )

    click.echo(f"API is passed a UserPool?: {user_pool is not None}")

    api_construct_name = config["api"]["name"].replace(" ", "-")
    api_construct = RestApiBackend(
        parent_stack,
        api_construct_name,
        config,
        rest_api_gw=gateway,  # type: ignore
        user_pool=user_pool,
    )

    # Add custom environment variables if provided
    if "custom_infra" in modules and "environment_variables" in modules["custom_infra"]:
        for key, value in modules["custom_infra"]["environment_variables"].items():
            api_construct.lambda_function.add_environment(key, value)

    modules["api"] = api_construct

# Finally, we can set custom permissions between stacks if needed
if "cdk" in config:
    from main import permissions  # pylint: disable=import-error

    permissions(parent_stack, modules)

app.synth()
