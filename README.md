# Papermorph

An AI skill that turns books into animated, narrated, interactive web experiences.

[Live bookshelf](https://math.diamonddoge.org/) · [MIT License](LICENSE)

## The Skill

The core of Papermorph is a reusable book-making Skill: [.claude/skills/papermorph/SKILL.md](.claude/skills/papermorph/SKILL.md).

It guides an AI agent through reference preparation, book planning, storyboards, narration, animated chapters, and interactive exercises. It includes production scripts, lesson engines, and templates. Start with `SKILL.md`, then read the references needed for the current stage.

Production tools use `uv`, PDF extraction, Edge TTS, and Playwright as described in the Skill. Generated books run as static websites without a backend or live AI calls.

## Example books

The website in `site/` showcases:

- **Elementary Algebra**: 68 animated, narrated chapters.
- **Elementary Mathematics**: three available chapters, with further production currently paused.

The bookshelf is the project's showcase. Its appearance will continue to evolve as more books are added.

The book cover pages credit their reference textbooks and link to the publishers. Reference PDFs, extracted source pages, private production notes, narration drafts, and unused artwork remain local and are not tracked in this repository. The bookshelf image used by the live website is included.

## Preview

There is no build step. Serve the website over HTTP for audio playback:

```sh
python3 -m http.server 8765 -d site
```

Open `http://localhost:8765/`.

## Deploy

The current website uses Cloudflare Pages project `animebook`, production branch `main`, and domain `math.diamonddoge.org`. Deploy only `site/`:

```sh
npx wrangler pages deploy site --project-name animebook --branch main
```

Maintain public repository documentation in English.
