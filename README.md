# AWS Service Roles Manager

A command-line tool for creating and deleting IAM Roles for each AWS service. Each service specific role will have the `PowerUserAccess` policy attached to it and only be assumable by that service.

## Why

In sandpit accounts, we want to minimise the number of miscelanious IAM Roles that are created. Users can quickly select these IAM Roles when experimenting with different AWS services without polluting AWS accounts with hundreds or thousands of abandoned IAM Roles.

## Installation

```bash
git clone https://github.com/servian/aws-service-roles-manager && cd ./aws-service-roles-manager
```

```bash
pip3 install .
```

## Usage

```bash
Usage: aws-service-roles-manager [OPTIONS]

Options:
  --create / --delete  Create or delete AWS service roles.  [required]
  --role-suffix TEXT   AWS role name suffix.
  --aws-profile TEXT   AWS profile name.
  --help               Show this message and exit.
```

## Modification

### IAM Policies

Each new IAM Role is attached the `PowerUserAccess` IAM Policy. If you would like to modify this with your own custom IAM Policy, or attach more than one IAM Policy, you can do this within the `src/aws_service_roles_manager/cli.py` by modifying the `policy_arns` list.

### AWS Services

Some AWS services cannot assume roles, and hence they're skipped when running this tool. If you'd like to modify which AWS services IAM Roles are created for, you can do this within the `src/aws_service_roles_manager/cli.py` by modifying the `skip_services` list.
