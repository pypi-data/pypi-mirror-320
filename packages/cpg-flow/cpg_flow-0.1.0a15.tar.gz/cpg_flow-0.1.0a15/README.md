<!-- markdownlint-disable MD033 MD024 -->
# 🐙 CPG Flow

<img src="/assets/DNA_CURIOUS_FLOYD_CROPPED.png" height="300" alt="CPG Flow logo" align="right"/>

![Python](https://img.shields.io/badge/-Python-black?style=for-the-badge&logoColor=white&logo=python&color=2F73BF)

[![⚙️ Test Workflow](https://github.com/populationgenomics/cpg-flow/actions/workflows/test.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/test.yaml)
[![🚀 Deploy To Production Workflow](https://github.com/populationgenomics/cpg-flow/actions/workflows/package.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/package.yaml)
[![GitHub Latest Main Release](https://img.shields.io/github/v/release/populationgenomics/cpg-flow?label=main%20release)](https://GitHub.com/populationgenomics/cpg-flow/releases/)
[![GitHub Release](https://img.shields.io/github/v/release/populationgenomics/cpg-flow?include_prereleases&label=latest)](https://GitHub.com/populationgenomics/cpg-flow/releases/)
[![semantic-release: conventional commits](https://img.shields.io/badge/semantic--release-conventional%20commits-Æ1A7DBD?logo=semantic-release&color=1E7FBF)](https://github.com/semantic-release/semantic-release)
[![GitHub license](https://img.shields.io/github/license/populationgenomics/cpg-flow.svg)](https://github.com/populationgenomics/cpg-flow/blob/main/LICENSE)

![Tests](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fpopulationgenomics%2Fcpg-flow%2Frefs%2Fheads%2Falpha%2Fdocs%2Fbadges.yaml&query=%24.test-badge.status&label=Tests&color=%24.test-badge.color)
![Coverage](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fpopulationgenomics%2Fcpg-flow%2Frefs%2Fheads%2Falpha%2Fdocs%2Fbadges.yaml&query=%24.coverage-badge.status&label=Coverage&color=%24.coverage-badge.color)

[![Technical Debt](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=sqale_index&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Duplicated Lines (%)](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=duplicated_lines_density&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Code Smells](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=code_smells&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)

<br />

## 📋 Table of Contents

1. 🐙 [What is this API ?](#what-is-this-api)
2. ✨ [Production and development links](#production-and-development-links)
3. 🔨 [Installation](#installation)
4. 🚀 [Build](#build)
5. 🐳 [Docker](#docker)
6. 💯 [Tests](#tests)
7. ☑️ [Code analysis and consistency](#code-analysis-and-consistency)
8. 📈 [Releases & Changelog](#versions)
9. 🎬 [GitHub Actions](#github-actions)
10. ©️ [License](#license)
11. ❤️ [Contributors](#contributors)

## <a name="what-is-this-api">🐙 What is this API ?</a>

Welcome to CPG Flow!

This API provides a set of tools and workflows for managing population genomics data pipelines, designed to streamline the processing, analysis, and storage of large-scale genomic datasets. It facilitates automated pipeline execution, enabling reproducible research while integrating with cloud-based resources for scalable computation.

CPG Flow supports various stages of genomic data processing, from raw data ingestion to final analysis outputs, making it easier for researchers to manage and scale their population genomics workflows.

## <a name="production-and-development-links">✨ Production and development links</a>

### 🌐 Production

The production version of this API is documented at **[populationgenomics.github.io/cpg-flow/main/cpg_flow.html](https://populationgenomics.github.io/cpg-flow/main/cpg_flow.html)**.

### 🛠️ Development

The development version of this API is available at **[populationgenomics.github.io/cpg-flow/alpha/cpg_flow.html](https://populationgenomics.github.io/cpg-flow/alpha/cpg_flow.html)**.

The documentation is updated automatically when a commit is pushed on the `alpha` (prerelease) or `main` (release) branch.

## <a name="installation">🔨 Installation</a>

The packages are hosted on:

![PyPI](https://img.shields.io/badge/-PyPI-black?style=for-the-badge&logoColor=white&logo=pypi&color=3776AB)

To install this project, you will need to have Python and `uv` installed on your machine:

![uv](https://img.shields.io/badge/-uv-black?style=for-the-badge&logoColor=white&logo=uv&color=3776AB)
![Python](https://img.shields.io/badge/-Python-black?style=for-the-badge&logoColor=white&logo=python&color=3776AB)

We recommend using a virtual environment to manage your dependencies.

Then, run the following commands:

```bash
# Install the package using uv
uv sync

# Or equivalently
make init
```

### 🛠️ Development

To setup for development we recommend using the makefile setup
```bash
make init-dev
```

As this installs the pre-commit hooks for you. To install the local cpg-flow run
```bash
make install-local
```

You can also try out the pre-installed cpg-flow in our Docker, more information in the **[Docker section](#docker)**.

## <a name="build">🚀 Build</a>

To build the project, run the following command:

```bash
make build
```

To make sure that you're actually using the installed build we suggest calling the following to install the build wheel.

```bash
make install-build
```


## <a name="docker">🐳 Docker</a>


## Docker Image Usage for cpg-flow Python Package

### Pulling and Using the Docker Image

These steps are restricted to CPG members only. Anyone will have access to the code in this public repositry and can build a version of cpg-flow themselves. The following requires authentication with the CPG's GCP.

To pull and use the Docker image for the `cpg-flow` Python package, follow these steps:

1. **Authenticate with Google Cloud Registry**:
    ```sh
    gcloud auth configure-docker australia-southeast1-docker.pkg.dev
    ```

2. **Pull the Docker Image**:
    - For alpha releases:
      ```sh
      docker pull australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:0.1.0-alpha.11
      ```
    - For main releases:
      ```sh
      docker pull australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:1.0.0
      ```

3. **Run the Docker Container**:
    ```sh
    docker run -it australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:<tag>
    ```

### Temporary Images for Development

Temporary images are created for each commit and expire in 30 days. These images are useful for development and testing purposes.

- Example of pulling a temporary image:
  ```sh
  docker pull australia-southeast1-docker.pkg.dev/cpg-common/images-tmp/cpg_flow:991cf5783d7d35dee56a7ab0452d54e69c695c4e
  ```

### Accessing Build Images for CPG Members

Members of the CPG can find the build images in the Google Cloud Registry under the following paths:
- Alpha and main releases: `australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow`
- Temporary images: `australia-southeast1-docker.pkg.dev/cpg-common/images-tmp/cpg_flow`

Ensure you have the necessary permissions and are authenticated with Google Cloud to access these images.


### 🧪 Unit and E2E tests

#### Unit Tests

![Tests](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fpopulationgenomics%2Fcpg-flow%2Frefs%2Fheads%2Falpha%2Fdocs%2Fbadges.yaml&query=%24.test-badge.status&label=Tests&color=%24.test-badge.color)

![Coverage](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fpopulationgenomics%2Fcpg-flow%2Frefs%2Fheads%2Falpha%2Fdocs%2Fbadges.yaml&query=%24.coverage-badge.status&label=Coverage&color=%24.coverage-badge.color)


#### E2E Test

We recommend frequently running the manual test workflow found in [test_workflows_shared](https://github.com/populationgenomics/test_workflows_shared)  specifically the `cpg_flow_test` workflow during development to ensure updates work with the CPG production environment.

Docummentation for running the tests are found in the repository readme.


### ▶️ Commands

Before testing, you must follow the **[installation steps](#installation)**.

## <a name="code-analysis-and-consistency">☑️ Code analysis and consistency</a>

### 🔍 Code linting & formatting

![Precommit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

In order to keep the code clean, consistent and free of bad python practices, more than **Over 10 pre-commit hooks are enabled** !

Complete list of all enabled rules is available in the **[.pre-commit-config.yaml file](https://github.com/populationgenomics/cpg-flow/blob/main/.pre-commit-config.yaml)**.

### ▶️ Commands

Before linting, you must follow the [installation steps](#installation).

Then, run the following command

```bash
# Lint
pre-commit run --all-files
```

When setting up local linting for development you can also run the following once:

```bash
# Install the pre-commit hook
pre-commit install

# Or equivalently
make init || make init-dev
```

### 🥇 Project quality scanner

Multiple tools are set up to maintain the best code quality and to prevent vulnerabilities:

![SonarQube](https://img.shields.io/badge/-SonarQube-black?style=for-the-badge&logoColor=white&logo=sonarqube&color=4E9BCD)

SonarQube summary is available **[here](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)**.

[![Coverage](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=coverage&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Duplicated Lines (%)](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=duplicated_lines_density&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Quality Gate Status](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=alert_status&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)

[![Technical Debt](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=sqale_index&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Vulnerabilities](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=vulnerabilities&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Code Smells](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=code_smells&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)

[![Reliability Rating](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=reliability_rating&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Security Rating](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=security_rating&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)
[![Bugs](https://sonarqube.populationgenomics.org.au/api/project_badges/measure?project=populationgenomics_cpg-flow&metric=bugs&token=sqb_bd2c5ce00628492c0af714f727ef6f8e939d235c)](https://sonarqube.populationgenomics.org.au/dashboard?id=populationgenomics_cpg-flow)


## <a name="versions">📈 Releases & Changelog</a>

Releases on **main** branch are generated and published automatically,
pre-releases on the **alpha** branch are also generated and published by:

![Semantic Release](https://img.shields.io/badge/-Semantic%20Release-black?style=for-the-badge&logoColor=white&logo=semantic-release&color=000000)

It uses the **[conventional commit](https://www.conventionalcommits.org/en/v1.0.0/)** strategy.

This is enforced using the **[commitlint](https://github.com/opensource-nepal/commitlint)** pre-commit hook that checks commit messages conform to the conventional commit standard.

We recommend installing and using the tool **[commitizen](https://commitizen-tools.github.io/commitizen/) in order to create commit messages. Once installed, you can use either `cz commit` or `git cz` to create a commitizen generated commit message.

Each change when a new release comes up is listed in the **<a href="https://github.com/populationgenomics/cpg-flow/blob/main/CHANGELOG.md" target="_blank">CHANGELOG.md file</a>**.

Also, you can keep up with changes by watching releases via the **Watch GitHub button** at the top of this page.

#### 🏷️ <a href="https://github.com/populationgenomics/cpg-flow/releases" target="_blank">All releases for this project are available here</a>.

## <a name="github-actions">🎬 GitHub Actions</a>

This project uses **GitHub Actions** to automate some boring tasks.

You can find all the workflows in the **[.github/workflows directory](https://github.com/populationgenomics/cpg-flow/tree/main/.github/workflows).**

### 🎢 Workflows

| Name | Description & Status | Triggered on |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :----------------------------------------------------: |
| **[Docker](https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml)** | Builds and pushes Docker images for the project.<br/><br/>[![Docker](https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml) | `pull_request` on `main, alpha` and `push` on `main, alpha` and `workflow_dispatch` |
| **[Update Badges](https://github.com/populationgenomics/cpg-flow/actions/workflows/update-badges.yaml)** | Updates badges.yaml with test results and coverage.<br/><br/>[![Update Badges](https://github.com/populationgenomics/cpg-flow/actions/workflows/update-badges.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/update-badges.yaml) | `workflow_run` (completed) |
| **[Security Checks](https://github.com/populationgenomics/cpg-flow/actions/workflows/security.yaml)** | Performs security checks using pip-audit.<br/><br/>[![Security Checks](https://github.com/populationgenomics/cpg-flow/actions/workflows/security.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/security.yaml) | `workflow_dispatch` and `push` |
| **[Lint](https://github.com/populationgenomics/cpg-flow/actions/workflows/lint.yaml)** | Runs linting checks using pre-commit hooks.<br/><br/>[![Lint](https://github.com/populationgenomics/cpg-flow/actions/workflows/lint.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/lint.yaml) | `push` |
| **[Package](https://github.com/populationgenomics/cpg-flow/actions/workflows/package.yaml)** | Packages the project and publishes it to PyPI and GitHub Releases.<br/><br/>[![Package](https://github.com/populationgenomics/cpg-flow/actions/workflows/package.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/package.yaml) | `push` on `alpha` and `workflow_dispatch` and `workflow_run` (completed) |
| **[Deploy API Documentation](https://github.com/populationgenomics/cpg-flow/actions/workflows/web-docs.yaml)** | None<br/><br/>[![Deploy API Documentation](https://github.com/populationgenomics/cpg-flow/actions/workflows/web-docs.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/web-docs.yaml) | `workflow_run` (completed) and `workflow_dispatch` |
| **[Renovate](https://github.com/populationgenomics/cpg-flow/actions/workflows/renovate.yaml)** | Runs Renovate to update dependencies.<br/><br/>[![Renovate](https://github.com/populationgenomics/cpg-flow/actions/workflows/renovate.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/renovate.yaml) | `schedule` and `workflow_dispatch` |
| **[Test](https://github.com/populationgenomics/cpg-flow/actions/workflows/test.yaml)** | Runs unit tests and generates coverage reports.<br/><br/>[![Test](https://github.com/populationgenomics/cpg-flow/actions/workflows/test.yaml/badge.svg)](https://github.com/populationgenomics/cpg-flow/actions/workflows/test.yaml) | `push` |


## <a name="license">©️ License</a>

This project is licensed under the [MIT License](http://opensource.org/licenses/MIT).

## <a name="contributors">❤️ Contributors</a>

There is no contributor yet. Want to be the first ?

If you want to contribute to this project, please read the [**contribution guide**](https://github.com/populationgenomics/cpg-flow/blob/master/CONTRIBUTING.md).
