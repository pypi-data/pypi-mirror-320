[![pipeline status](https://gitlab.com/kisphp/python-cli-tool/badges/main/pipeline.svg)](https://gitlab.com/kisphp/python-cli-tool/-/commits/main)
[![coverage report](https://gitlab.com/kisphp/python-cli-tool/badges/main/coverage.svg)](https://gitlab.com/kisphp/python-cli-tool/-/commits/main)
[![Latest Release](https://gitlab.com/kisphp/python-cli-tool/-/badges/release.svg)](https://gitlab.com/kisphp/python-cli-tool/-/releases)

## Install

```bash
# Install or update it from pip
pipx install -U kpx

# Install or update it from gitlab
pipx install -U kpx --index-url https://gitlab.com/api/v4/projects/24038501/packages/pypi/simple
```

## Contribute

[Install poetry globally](https://python-poetry.org/docs/#installing-with-the-official-installer)

```shell
curl -sSL https://install.python-poetry.org | python3 -
```

Clone the project

```shell
git clone https://gitlab.com/kisphp/kpx.git 
```

Create virtual env inside the project directory

```shell
cd kpx

# create venv
python3 -m venv venv # first venv is the python module called venv, second one is the name of our local virtual environment
```

Install local dependencies

```shell
poetry install
```

Run application from poetry 

```shell
poetry run -- kpx # this will show the full list of available commands
poetry run -- kpx ec2 # will list all ec2 instances in your aws account
poetry run -- kpx ec2 -f name=gpu,state=running # list ec2 instances with filtered results
```

Exit from virtual environment

```shell
deactivate # type this in the terminal window and click Enter key
```
# `kpx`

KPX application for aws profiles

**Usage**:

```console
$ kpx [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `acm`: List Certificates
* `cfg`: Configure ~/.aws/config file with profiles...
* `cred`: Configure ~/.aws/credentials file with aws...
* `ec2`: List EC2 instances
* `ecr`: List ECR repositories
* `lb`: List Load Balancers
* `n`: List EKS nodes and show some information...
* `nodes`: List EKS nodes and show some information...
* `r53`: List Route53 hosted zones
* `sec`: List secrets and show values
* `secret`: List secrets and show values
* `v`: Show current CLI tool version
* `version`: Show current CLI tool version
* `vpc`: List VPCs and show Cidr blocks or subnets...

## `kpx acm`

List Certificates

**Usage**:

```console
$ kpx acm [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `kpx cfg`

Configure ~/.aws/config file with profiles settings

**Usage**:

```console
$ kpx cfg [OPTIONS] [AWS_PROFILE] [REGION] [OUTPUT]
```

**Arguments**:

* `[AWS_PROFILE]`: [default: default]
* `[REGION]`: [default: us-east-1]
* `[OUTPUT]`: [default: json]

**Options**:

* `--help`: Show this message and exit.

## `kpx cred`

Configure ~/.aws/credentials file with aws credentials

**Usage**:

```console
$ kpx cred [OPTIONS] [AWS_PROFILE] [KEY] [SECRET]
```

**Arguments**:

* `[AWS_PROFILE]`: [default: default]
* `[KEY]`
* `[SECRET]`

**Options**:

* `--help`: Show this message and exit.

## `kpx ec2`

List EC2 instances

**Usage**:

```console
$ kpx ec2 [OPTIONS]
```

**Options**:

* `-f, --filter TEXT`
* `--help`: Show this message and exit.

## `kpx ecr`

List ECR repositories

**Usage**:

```console
$ kpx ecr [OPTIONS] [REPO_NAME]
```

**Arguments**:

* `[REPO_NAME]`

**Options**:

* `--help`: Show this message and exit.

## `kpx lb`

List Load Balancers

**Usage**:

```console
$ kpx lb [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `kpx n`

List EKS nodes and show some information about them

**Usage**:

```console
$ kpx n [OPTIONS]
```

**Options**:

* `-f, --filter TEXT`
* `--help`: Show this message and exit.

## `kpx nodes`

List EKS nodes and show some information about them

**Usage**:

```console
$ kpx nodes [OPTIONS]
```

**Options**:

* `-f, --filter TEXT`
* `--help`: Show this message and exit.

## `kpx r53`

List Route53 hosted zones

**Usage**:

```console
$ kpx r53 [OPTIONS] [ZONE_ID] [FILTER]
```

**Arguments**:

* `[ZONE_ID]`
* `[FILTER]`

**Options**:

* `--help`: Show this message and exit.

## `kpx sec`

List secrets and show values

**Usage**:

```console
$ kpx sec [OPTIONS] [SECRET]
```

**Arguments**:

* `[SECRET]`

**Options**:

* `-a, --all-namespaces`: Show K8S secrets in all namespaces
* `-n, --namespace TEXT`: Select namespace
* `--help`: Show this message and exit.

## `kpx secret`

List secrets and show values

**Usage**:

```console
$ kpx secret [OPTIONS] [SECRET]
```

**Arguments**:

* `[SECRET]`

**Options**:

* `-a, --all-namespaces`: Show K8S secrets in all namespaces
* `-n, --namespace TEXT`: Select namespace
* `--help`: Show this message and exit.

## `kpx v`

Show current CLI tool version

**Usage**:

```console
$ kpx v [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `kpx version`

Show current CLI tool version

**Usage**:

```console
$ kpx version [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `kpx vpc`

List VPCs and show Cidr blocks or subnets for provided VPC ID

**Usage**:

```console
$ kpx vpc [OPTIONS] [VPC_ID]
```

**Arguments**:

* `[VPC_ID]`

**Options**:

* `--help`: Show this message and exit.

