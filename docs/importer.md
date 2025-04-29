# CALDERA Emulation Plan Importer

## Overview

The Emulation Plan Importer is a custom plugin for MITRE CALDERA that allows you to import adversary emulation plans in YAML format. The plugin automatically creates adversary profiles and abilities that can be used in the CALDERA framework for red team operations and adversary emulation exercises.

This plugin is particularly useful for security teams who want to quickly implement adversary emulation plans, such as those developed by the MITRE ATT&CK® Evaluations team or other threat intelligence sources.

## Features

- Import YAML-formatted adversary emulation plans
- Automatically create abilities and adversary profiles in CALDERA
- Support for all MITRE ATT&CK tactics and techniques
- Handle various executor types (PowerShell, CMD, Bash, etc.)
- Create placeholder files for required payloads
- Organize abilities by tactic
- Import detailed procedure steps and maintain ordering
- Track sources of behaviors and CTI references

## Installation

1. Clone the repository into the plugins directory of your CALDERA installation:

```bash
cd /path/to/caldera/plugins
git clone https://github.com/yourusername/caldera-emulation-plan-importer.git emulation_plan_importer
```

2. Add the plugin to your CALDERA configuration file (e.g., `conf/default.yml`):

```yaml
plugins:
  - stockpile
  - sandcat
  # other plugins...
  - emulation_plan_importer
```

3. Start or restart your CALDERA server:

```bash
python server.py --insecure
```

## Usage

1. Access the CALDERA web interface (default: `http://localhost:8888`)
2. Navigate to the Emulation Plan Importer via the plugins menu
3. Upload your YAML-formatted emulation plan
4. The plugin will process the file and create the necessary adversary profile and abilities
5. You can then use the imported adversary in CALDERA operations
