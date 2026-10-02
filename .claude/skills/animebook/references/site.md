# The site: book folder, contents, bookshelf, publishing

The site is static: HTML, JS, CSS, MP3. No build step, backend, database or accounts; reading progress lives in the browser (`localStorage`). Only `site/` is published.

## Start a book folder

```sh
B=site/<book-slug>
mkdir -p $B/lib $B/ch01 content/ch01 tools
cp SKILL/assets/engine/engine.js SKILL/assets/engine/engine.css $B/lib/
cp SKILL/assets/templates/book.html $B/index.html
cp SKILL/assets/templates/unit-art.js $B/unit-art.js
cp SKILL/assets/templates/chapter.html $B/ch01/index.html
cp SKILL/assets/templates/narration.en.json content/ch01/
cp SKILL/assets/templates/e2e.py tools/e2e_ch01.py
```

Each book keeps its own engine copy, so improving one book never breaks another. A chapter links back to `../` (the book's index) and the index links back to `../` (the bookshelf). With no bookshelf yet, either add `site/index.html` that simply redirects to the book (`<meta http-equiv="refresh" content="0; url=<book-slug>/">`) or delete the two `back-shelf` links from the book's index.

## Cover and contents (`index.html`)

One page: no hash or `#book` shows the cover, `#contents` or `#chNN` the contents; a lesson's home button returns to `#chNN`, and the card grows into the lesson frame through a view transition.

- Edit the title, kicker, lede, the faint chalk phrases on the cover (a few formulas or lines from the book), and the `<title>`.
- `UNITS`: `[unit title, [[chapter title, minutes], …]]`; chapters are numbered in order. Add a chapter when its lesson is ready; also set the previous chapter's `CHAPTER.next = '../chNN/'`.
- `HUES`: one colour per unit, cycling.

## Unit sketches (`unit-art.js`)

Each unit header is a strip of chalkboard with a small drawing of that unit's ideas in the unit colour. It draws itself the first time the unit scrolls into view, then keeps one gentle loop that fits the topic (two terms swapping places, a dot hopping along a line, a balance tilting, a spinner turning). Draw from the book's own content — a timeline for a history unit, a map, a family tree, a key quotation — with paths and text only. Keep the left third light (the title sits there on phones); test at 1440 px and 390 px wide; motion stops under `prefers-reduced-motion`. The classes and loop examples are documented at the top of `unit-art.js` and in the `.unit-art` CSS of `index.html`.

## Guide character

The engine's `mascotEl` draws the guide shown on question cards and the score card (and the cover uses the same drawing). The first book used an infinity sign whose loops are eyes. For a new book, draw a simple SVG character that suits it, in `mascotEl` and in the cover script, with the same moods (blink, hop when right, tilt when wrong). Never use a famous or branded character.

## Bookshelf

`site/index.html` with `lib/bookshelf.js` and `.css` lists the books. Add an entry to `books` in `bookshelf.js`:

```js
{ id: 'history', title: '…', subject: 'History', href: 'history/', coverTitle: ['Line one', 'line two'],
  series: 'An animated book', description: '…', chapters: 24, units: 6,
  artwork: '<svg viewBox="0 0 260 175" class="book-art">…</svg>', features: ['…', '…', '…'] }
```

Only list books that are published; never placeholders.

## Publishing

Only when the user asks. Any static host works; for Cloudflare Pages:

```sh
npx wrangler pages deploy site --project-name <project> --branch main --commit-hash $(git rev-parse --short HEAD)
```

Commit first, deploy the committed state, then confirm the live URL serves the new files (`curl` a changed file with a cache-busting query) and record the deployment id in BOOK.md. Never publish the PDF, `book_pages/` or tools; they live outside `site/`.

## Languages

Narration and on-screen text are written in one language first. A second language comes after the book is done and approved: keep beat ids and question ids stable, add `narration.<lang>.json` and audio per language, and decide with the user how switching behaves mid-lesson before building it.
