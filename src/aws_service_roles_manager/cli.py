import asyncio
import json
import requests

import boto3
import click


@click.command()
@click.option(
    "--create/--delete",
    default=True,
    required=True,
    help="Create or delete AWS service roles.",
)
@click.option("--role-suffix", default="power-user", help="AWS role name suffix.")
@click.option("--auto-cleanup-api", help="AWS Auto Cleanup Create Whitelist API URL.")
@click.option("--aws-profile", help="AWS profile name.")
def main(create, role_suffix, auto_cleanup_api, aws_profile):
    if aws_profile not in (None, ""):
        boto3.setup_default_session(profile_name=aws_profile)

    client_service_quotas = boto3.client("service-quotas")
    client_iam = boto3.client("iam")

    skip_services = [
        "application-autoscaling",
        "appmesh",
        "appstream2",
        "AWSCloudMap",
        "cognito",
        "cognito-identity",
        "ecr",
        "fargate",
        "monitoring",
        "polly",
        "shield",
        "vpc",
    ]

    paginator = client_service_quotas.get_paginator("list_services")
    response_iterator = paginator.paginate()

    for page in response_iterator:
        for service in page.get("Services"):
            service_name = service.get("ServiceCode")
            if service_name not in skip_services:
                role_name = f"{service_name}-{role_suffix}"

                if create:
                    create_role(client_iam, service_name, role_name, auto_cleanup_api)
                else:
                    delete_role(client_iam, service_name, role_name, auto_cleanup_api)


def create_role(client_iam, service_name, role_name, auto_cleanup_api):
    policy_arns = ["arn:aws:iam::aws:policy/PowerUserAccess"]
    assume_role_policy = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"Service": f"{service_name}.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    )

    try:
        response = client_iam.get_role(RoleName=role_name).get("Role")
    except:
        pass
    else:
        if response is not None:
            click.secho(f"IAM Role '{role_name}' already exists.", fg="yellow")
            return

    try:
        client_iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=assume_role_policy,
        )
    except:
        click.secho(f"Could not create IAM Role '{role_name}'.", fg="red")
    else:
        click.secho(f"Created new IAM Role '{role_name}'.", fg="green")

        if auto_cleanup_api not in (None, ""):
            try:
                response = requests.post(
                    auto_cleanup_api,
                    params={
                        "resource_id": f"iam:role:{role_name}",
                        "owner": "",
                        "comment": "AWS Service Roles Manager",
                        "permanent": True,
                    },
                    headers={
                        "User-Agent": "AWSServiceRolesManager/0.1",
                    },
                )

                if response.status_code != 201:
                    click.secho(
                        f"Could not add IAM Role '{role_name}' to AWS Auto Cleanup whitelist.",
                        fg="red",
                    )
            except:
                click.secho(
                    f"Could not add IAM Role '{role_name}' to AWS Auto Cleanup whitelist.",
                    fg="red",
                )

        if service_name == "ec2":
            try:
                client_iam.create_instance_profile(InstanceProfileName=role_name)
            except:
                click.secho(
                    f"Could not create IAM Instance Profile '{role_name}'.", fg="red"
                )
            else:
                client_iam.add_role_to_instance_profile(
                    InstanceProfileName=role_name, RoleName=role_name
                )

        for policy_arn in policy_arns:
            try:
                client_iam.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn,
                )
            except:
                click.secho(
                    f"Could not attach IAM Policy '{policy_arn}' to IAM Role '{role_name}'.",
                    fg="red",
                )


def delete_role(client_iam, service_name, role_name, auto_cleanup_api):
    try:
        response = client_iam.get_role(RoleName=role_name).get("Role")
    except:
        click.secho(
            f"Could not retrieve details of IAM Role '{role_name}'.", fg="yellow"
        )
    else:
        if response is not None:
            try:
                policies = client_iam.list_attached_role_policies(
                    RoleName=role_name,
                ).get("AttachedPolicies")
            except:
                click.secho(
                    f"Could not list attached IAM Policies for IAM Role '{role_name}'.",
                    fg="red",
                )
            else:
                for policy in policies:
                    try:
                        client_iam.detach_role_policy(
                            RoleName=role_name,
                            PolicyArn=policy.get("PolicyArn"),
                        )
                    except:
                        click.secho(
                            f"""Could not detach IAM Policy '{policy.get("PolicyArn")}' from IAM Role '{role_name}'.""",
                            fg="red",
                        )

                if service_name == "ec2":
                    try:
                        client_iam.remove_role_from_instance_profile(
                            InstanceProfileName=role_name, RoleName=role_name
                        )
                    except:
                        click.secho(
                            f"Could not remove IAM Role '{role_name}' from IAM Instance Profile '{role_name}'.",
                            fg="red",
                        )
                    else:
                        try:
                            client_iam.delete_instance_profile(
                                InstanceProfileName=role_name
                            )
                        except:
                            click.secho(
                                f"Could not delete IAM Instance Profile '{role_name}'.",
                                fg="red",
                            )

                try:
                    client_iam.delete_role(RoleName=role_name)
                except:
                    click.secho(f"Could not delete IAM Role '{role_name}'.", fg="red")
                else:
                    click.secho(f"Deleted IAM Role '{role_name}'.", fg="green")

                    if auto_cleanup_api not in (None, ""):
                        try:
                            response = requests.delete(
                                auto_cleanup_api,
                                params={"resource_id": f"iam:role:{role_name}"},
                                headers={
                                    "User-Agent": "AWSServiceRolesManager/0.1",
                                },
                            )

                            if response.status_code != 200:
                                click.secho(
                                    f"Could not delete IAM Role '{role_name}' from AWS Auto Cleanup whitelist.",
                                    fg="red",
                                )
                        except:
                            click.secho(
                                f"Could not delete IAM Role '{role_name}' from AWS Auto Cleanup whitelist.",
                                fg="red",
                            )


if __name__ == "__main__":
    main()
