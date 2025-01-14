# `tecton-gen-ai` demos

This contains many of the demo notebooks and data that we have used in customer conversations.

By centralizing these demos, we intend to make it easier to:
- to create new ones based off existing ones
- share them internally
- test against them
- iteratively improve them
- look back at them for reference, and see how they evolved over time


## Creating a new demo

Create demo folder:
```bash
# Create a new demo folder, not inheriting the parent workspace.
# We avoid workspaces here so that each demo can have its own isolated dependency set.
uv init --no-project --no-workspace <demo-name>
````

## Style

We intend for each of these notebooks to run through our code linter and formatter. However, they will have a more relaxed set of rules compared to the library code.
