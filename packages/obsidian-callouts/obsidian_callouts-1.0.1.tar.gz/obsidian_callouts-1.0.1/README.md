<!--
SPDX-FileCopyrightText: © 2025 Serhii “GooRoo” Olendarenko

SPDX-License-Identifier: BSD-3-Clause
-->

# [Obsidian][obsidian] callouts for Python-Markdown

[![Made by Ukrainian](https://img.shields.io/static/v1?label=Made%20by&message=Ukrainian&labelColor=1f5fb2&color=fad247&style=flat-square)](https://savelife.in.ua/en/donate-en/#donate-army-card-once)
[![License](https://img.shields.io/github/license/GooRoo/obsidian-callouts?style=flat-square)](LICENSE)

This is an extension for [Python-Markdown][python-markdown] which allows you to use Obsidian-style callouts:

```markdown
> [!warning]
> Here's a callout block.

> [!tip] Callouts can have custom titles
> Like this one.
```

It will be rendered kinda like this:

> [!WARNING]
> Here's a callout block.

> [!TIP] Callouts can have custom titles
> Like this one.

For a full reference, please, see [the Obsidian's documentation](https://help.obsidian.md/Editing+and+formatting/Callouts) on this.

## Usage

Simply enable the extension like this:

```python
import markdown

md = markdown.Markdown(extensions=['obsidian_callouts'])
print(md.convertFile('page.md'))
```

## MkDocs

It can be used with [MkDocs][mkdocs] as following:

```yaml
# mkdocs.yml
markdown_extensions:
  - obsidian_callouts
```

It is also installed along with my [**mkdocs-obsidian-bridge**](https://github.com/GooRoo/mkdocs-obsidian-bridge).

## Credits

During the implementation of this plugin, I was using the official [Python-Markdown][python-markdown] as an inspiration and the example.

[mkdocs]: https://www.mkdocs.org
[obsidian]: https://obsidian.md
[python-markdown]: https://python-markdown.github.io/
