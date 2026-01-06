# Landing Zone

This repository contains infrastructure-as-code templates and workflows for setting up cloud landing zones.

## Structure

- `definitions/` - Question definitions for configuration
- `workflows/` - Available workflow configurations
- `iac/` - Infrastructure as Code templates
- `scripts/` - Utility scripts
- `answers/` - Sample answer files for workflows

## Getting Started

1. Choose a workflow from the `workflows/` directory
2. Review the workflow's `overview.md` for details
3. Copy the corresponding sample answers file from `answers/`
4. Customize the answers for your environment
5. Run the render script to generate your infrastructure code

## Usage

```bash
python scripts/render_journey.py --workflow <workflow_id> --answers answers/<your_answers>.yaml
```

