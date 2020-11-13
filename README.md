# AWS Service Roles Manager

A command-line tool for creating and deleting IAM Roles for each AWS service. Each service-specific role will have the `PowerUserAccess` policy attached to it and only be assumable by that service.

## Why

In sandpit accounts, we want to minimise the number of miscellaneous IAM Roles that are created. Users can quickly select these IAM Roles when experimenting with different AWS services without polluting AWS accounts with hundreds or thousands of abandoned IAM Roles.

## Installation

```bash
git clone https://github.com/servian/aws-service-roles-manager
```

```bash
cd aws-service-roles-manager/
```

```bash
pip3 install .
```

## Usage

```bash
Usage: aws-service-roles-manager [OPTIONS]

Options:
  --create / --delete      Create or delete AWS service roles.  [required]
  --role-suffix TEXT       AWS role name suffix.
  --auto-cleanup-api TEXT  AWS Auto Cleanup Create Whitelist API URL.
  --aws-profile TEXT       AWS profile name.
  --help                   Show this message and exit.
```

## Modification

### IAM Policies

Each new IAM Role is attached the `PowerUserAccess` IAM Policy. If you would like to modify this with your own custom IAM Policy, or attach more than one IAM Policy, you can do this within the `src/aws_service_roles_manager/cli.py` by modifying the `policy_arns` list.

### AWS Services

Some AWS services cannot assume roles, and hence they're skipped when running this tool. If you'd like to modify which AWS services IAM Roles are created for, you can do this within the `src/aws_service_roles_manager/cli.py` by modifying the `skip_services` list.

## Permissions

AWS Service Roles Manager requires a user with the following IAM permissions:

| Action                            |
| --------------------------------- |
| iam:AddRoleToInstanceProfile      |
| iam:AttachRolePolicy              |
| iam:CreateInstanceProfile         |
| iam:CreateRole                    |
| iam:DeleteInstanceProfile         |
| iam:DeleteRole                    |
| iam:DetachRolePolicy              |
| iam:GetRole                       |
| iam:ListAttachedRolePolicies      |
| iam:RemoveRoleFromInstanceProfile |
| servicequotas:ListServices        |

## AWS Auto Cleanup

If you're using AWS Auto Cleanup (v1.2.0+) alongside this AWS Service Roles Manager then you know eventually these roles may be deleted by Auto Cleanup. To solve this issue, AWS Service Roles Manager can add each IAM Role to your AWS Auto Cleanup whitelist. Simply pass in your AWS Auto Cleanup Create Whitelist API URL (e.g., `https://api-id.execute-api.region.amazonaws.com/stage/whitelist/entry`) which can be found inside the `serverless.manifest.json` file and AWS Service Roles Manager will take care of the rest.
