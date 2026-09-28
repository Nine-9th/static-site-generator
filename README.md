# Static Site Generator

A Python static site generator that converts Markdown files into HTML pages using a shared template. It copies static assets, preserves the content directory structure, and supports a configurable base path for GitHub Pages.

## Requirements

- Python 3

The generator uses only the Python standard library.

## Local Preview

From the project root, run:

```sh
sh main.sh
```

This builds the site in `docs/` with the root base path (`/`) and starts a local web server. Open [http://localhost:8888](http://localhost:8888). Stop the server with `Ctrl+C`.

To generate the site without starting the server:

```sh
python3 src/main.py
```

## Production Build

Build the site with the GitHub Pages base path configured for this repository:

```sh
sh build.sh
```

The generated site is written to `docs/`. The build script passes `/static-site-generator/` as the base path so root-relative `href` and `src` URLs work when hosted under the repository path.

## Tests

Run the test suite from the project root:

```sh
sh test.sh
```

The test modules are in `src/test/`.

## Project Layout

- `content/` contains Markdown pages. Nested directories are preserved in the generated site; for example, `content/blog/example/index.md` becomes `docs/blog/example/index.html`.
- `static/` contains files such as stylesheets and images, copied into `docs/` during generation.
- `template.html` is the shared page template. Use `{{ Title }}` and `{{ Content }}` as placeholders.
- `src/` contains the generator implementation.
- `src/test/` contains the unit tests.
- `docs/` is the generated site and GitHub Pages publishing directory.

Each Markdown page needs an `h1` title. The generator supports headings, paragraphs, code blocks, blockquotes, ordered and unordered lists, inline bold/italic/code, links, and images.