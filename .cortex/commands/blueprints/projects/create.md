# Blueprints Projects Create

Create a new project directory structure for organizing blueprint work.

## Usage

```
blueprints projects create <name>
```

## Arguments

- `<name>`: Project name (alphanumeric, underscores, and hyphens only)

## Instructions

Create a new project directory with the standard structure:

```
projects/<name>/
├── answers/
│   └── .gitkeep
└── output/
    ├── iac/
    │   └── sql/
    │       └── .gitkeep
    └── documentation/
        └── .gitkeep
```

## Implementation

1. Validate project name (alphanumeric, underscores, hyphens only)
2. Check if project already exists
3. Create directory structure
4. Create .gitkeep files to preserve empty directories in git

## Output Format

### Success
```
✓ Project 'my-project' created successfully!

Project structure:
  projects/my-project/
  ├── answers/
  └── output/
      ├── iac/sql/
      └── documentation/

Next steps:
1. Initialize answers: blueprints answers init <blueprint-name> --project my-project
2. Build interactively: blueprints build <blueprint-name> --project my-project
```

### Project Already Exists
```
Error: Project 'my-project' already exists.

Use 'blueprints projects describe my-project' to view its contents.
```

### Invalid Name
```
Error: Invalid project name 'my project!'.
Project names can only contain alphanumeric characters, underscores, and hyphens.

Examples of valid names:
  - my-project
  - acme_corp
  - customer123
```

## Error Handling

- Invalid characters in name: Show error with valid name examples
- Project already exists: Show error and suggest describe command
- Permission issues: Show filesystem error

Now execute this by creating the project directory structure.
