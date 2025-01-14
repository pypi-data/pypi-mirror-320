# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mkdocs_material_adr', 'mkdocs_material_adr.plugins.graph']

package_data = \
{'': ['*'], 'mkdocs_material_adr': ['partials/*', 'stylesheets/*']}

install_requires = \
['pydantic>=2.1.1,<3.0.0']

entry_points = \
{'mkdocs.plugins': ['mkdocs-material-adr/adr = '
                    'mkdocs_material_adr.plugins.graph.plugin:AdrPlugin'],
 'mkdocs.themes': ['mkdocs-material-adr = mkdocs_material_adr']}

setup_kwargs = {
    'name': 'mkdocs-material-adr',
    'version': '1.1.2',
    'description': '',
    'long_description': "# ADR for MkDocs's Material Theme\n\n[ADR](https://lyz-code.github.io/blue-book/adr/) are short text documents that captures an important architectural decision made along with its context and consequences.\n\n\n[Demo](http://blog.kloven.fr/mkdocs-material-adr/)\n\n## Install\n\n```bash\npip install mkdocs-material-adr\n# or\npoetry add mkdocs-material-adr\n```\n\nIn the `mkdocs.yml` file\n\n```yaml\ntheme:\n  # set the name\n  name: mkdocs-material-adr\n\n  # Configuration for the material theme\n  features:\n    - navigation.instant\n\n\nplugins:\n  - mkdocs-material-adr/adr\n```\n\n## Features\n\n### ADR Headers\nInformation about the ADR are displayed in a header\nDefine information about the ADR in the frontmatter.\n\n![Alt text](https://raw.githubusercontent.com/Kl0ven/mkdocs-material-adr/main/docs/assets/header.png)\n\n\n```md\n---\n    title: 0004 Title\n    adr:\n        author: Jean-Loup Monnier\n        created: 01-Aug-2023\n        status:  draft | proposed | rejected | accepted | superseded\n        superseded_by: 0001-test\n        extends:\n            - 0001-first\n            - 0002-second\n---\n```\nYou can change the colors or add new status using css\n\n```css\n/* Background color */\n.c-pill-<lower_case_status_name> {\n    background: #a3a3a3;\n}\n\n/* Dot color */\n.c-pill-<lower_case_status_name>:before {\n    background: #505050;\n}\n```\n\n### ADR Graph\nAuto generated graph.\nTo enable it add `[GRAPH]` in the markdown file you want the graph to be, Then add th following configuration\n\n```yaml\n\n\nplugins:\n  - mkdocs-material-adr/adr:\n      graph_file: index.md # Change this to your file\n\nmarkdown_extensions:\n  - pymdownx.superfences:\n      custom_fences:\n      - name: mermaid\n        class: mermaid\n        format: !!python/name:pymdownx.superfences.fence_code_format\n```\n![Alt text](https://raw.githubusercontent.com/Kl0ven/mkdocs-material-adr/main/docs/assets/graph.png)\n",
    'author': 'jeanloup.monnier',
    'author_email': 'jean-loup.monnier@spikeelabs.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Kl0ven/mkdocs-material-adr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
