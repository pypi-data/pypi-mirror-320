import os
import re

import yaml

# Path to the workflows directory
WORKFLOWS_DIR = '.github/workflows'
README_FILE = 'README.md'
DESCRIPTION_FILE = 'docs/workflow_descriptions.yaml'

REPO_URL = 'https://github.com/populationgenomics/cpg-flow'


def load_descriptions(description_file):
    with open(description_file) as f:
        descriptions = yaml.safe_load(f)
        return descriptions


def parse_workflows(directory, description_file):
    descriptions = load_descriptions(description_file)
    workflows = []
    for filename in os.listdir(directory):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(directory, filename)
            with open(filepath) as file:
                try:
                    data = yaml.load(file, Loader=yaml.BaseLoader)
                    workflow_name = data.get('name', 'Unnamed Workflow')
                    triggers = parse_triggers(data.get('on'))
                    description = descriptions.get(filename)
                    workflows.append(
                        {
                            'file': filename,
                            'name': workflow_name,
                            'triggers': triggers,
                            'description': description,
                        },
                    )
                except yaml.YAMLError as e:
                    print(f'Error parsing {filename}: {e}')
    return workflows


def parse_triggers(on_field):
    if isinstance(on_field, dict):  # Handle complex `on` field
        triggers = []
        for trigger, details in on_field.items():
            if isinstance(details, dict):  # Check for branches or paths
                branches = details.get('branches', [])
                events = details.get('types', [])
                if branches:
                    triggers.append(f"`{trigger}` on `{', '.join(branches)}`")
                elif events:
                    triggers.append(f"`{trigger}` ({', '.join(events)})")
                else:
                    triggers.append(f'`{trigger}`')
            else:
                triggers.append(f'`{trigger}`')
        return ' and '.join(triggers)
    if isinstance(on_field, list):  # Handle `on: [event1, event2]`
        return ', '.join([f'`{event}`' for event in on_field])
    if isinstance(on_field, str):  # Handle `on: event`
        return f'`{on_field}`'
    return '`manual`'  # Default if `on` is missing


def generate_markdown(workflows):
    markdown = '| Name | Description & Status | Triggered on |\n'
    markdown += '| :---------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :----------------------------------------------------: |\n'
    for workflow in workflows:
        file_url = f"{REPO_URL}/actions/workflows/{workflow['file']}"
        badge_url = f'{file_url}/badge.svg'
        workflow_name = f"**[{workflow['name']}]({file_url})**"
        description_status = f"{workflow['description']}<br/><br/>[![{workflow['name']}]({badge_url})]({file_url})"
        markdown += f"| {workflow_name} | {description_status} | {workflow['triggers']} |\n"
    return markdown


def update_readme(readme_file):
    with open(readme_file) as file:
        content = file.read()

    content = update_workflow_table(content)
    content = update_readme_links(content)

    with open(readme_file, 'w') as file:
        file.write(content)

    print(f'Readme updated: {readme_file}')


def update_workflow_table(content):
    if os.path.exists(WORKFLOWS_DIR):
        workflows = parse_workflows(WORKFLOWS_DIR, DESCRIPTION_FILE)
        workflows_md_table = generate_markdown(workflows)

    if not workflows:
        print('No workflows found in the directory.')
        return content

    start_marker = '### 🎢 Workflows'
    end_marker = '## <a name="license">©️ License</a>'

    start_index = content.find(start_marker)
    end_index = content.find(end_marker)

    if start_index == -1 or end_index == -1:
        print('Markers not found in README.md')
        return content

    return content[: start_index + len(start_marker)] + '\n\n' + workflows_md_table + '\n\n' + content[end_index:]


def update_readme_links(content):
    slash = r'(%2F|\/)'
    pattern = rf'(cpg-flow{slash}refs{slash}heads{slash}\w+{slash})'

    # Find all the raw content links and replace the branch name with the current branch
    current_branch = os.popen('git rev-parse --abbrev-ref HEAD').read().strip()
    print(f'Current branch: {current_branch}')

    print('URL Matches:')
    print([x[0] for x in re.findall(pattern, content)])

    return re.sub(pattern, f'cpg-flow%2Frefs%2Fheads%2F{current_branch}%2F', content)


if __name__ == '__main__':
    update_readme(README_FILE)
