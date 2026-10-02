# The site: book folder, contents, bookshelf, publishing

The site is static: HTML, JS, CSS, MP3. No build step, backend, database or accounts; reading progress lives in the browser (`localStorage`). Only `site/` is published.

## Start a book folder

Set `SKILL` to the installed skill folder. Run once for a new slug; use an existing book's actual files when resuming:

```sh
BOOK_ID=history
BOOK_SITE="site/$BOOK_ID"
BOOK_WORK="books/$BOOK_ID"
mkdir -p "$BOOK_SITE/lib" "$BOOK_SITE/ch01" "$BOOK_WORK/chapters" "content/$BOOK_ID/ch01" "tools/$BOOK_ID"
cp "$SKILL/assets/engine/engine.js" "$SKILL/assets/engine/engine.css" "$BOOK_SITE/lib/"
cp "$SKILL/assets/templates/book.html" "$BOOK_SITE/index.html"
cp "$SKILL/assets/templates/unit-art.js" "$BOOK_SITE/unit-art.js"
cp "$SKILL/assets/templates/chapter.html" "$BOOK_SITE/ch01/index.html"
cp "$SKILL/assets/templates/narration.en.json" "content/$BOOK_ID/ch01/narration.en.json"
```

Use the agreed primary language: rename the narration source, load `audio/<lang>/timings.js`, and set `CHAPTER.language` to match (default `en`). Choose the voice and translate the template's visible UI text as needed before the pilot.

Each book has its own engine, source materials, narration and optional tests. The engine and cover derive the same progress key from the book's URL folder. Keep existing books on their current paths; their legacy progress remains intact.

A chapter returns to its book's index; the cover/contents returns to the bookshelf. With no bookshelf yet, create a minimal `site/index.html` linking to the book's cover. When adding a bookshelf, use underlined text and a small arrow for the entry; preserve cover → contents → chapter navigation.

## Cover and contents (`index.html`)

One page: no hash or `#book` shows the cover, `#contents` or `#chNN` the contents; a lesson's home button returns to `#chNN`, and the card grows into the lesson frame through a view transition.

- Edit the title, kicker, lede, the faint chalk phrases on the cover (a few formulas or lines from the book), and the `<title>`.
- `UNITS`: `[unit title, [[chapter title, minutes], …]]`; chapters are numbered in order. Add a chapter when its lesson is ready; also set the previous chapter's `CHAPTER.next = '../chNN/'`.
- `HUES`: one colour per unit, cycling.

## Unit sketches (`unit-art.js`)

Give each unit a small sketch of its own ideas, drawn in the unit colour, with one gentle topic-related loop. Use the agreed asset approach. Keep the left third light for the title on phones; check the finished contents at 1440 px and 390 px once. The template handles reduced motion; classes and loop examples are in `unit-art.js` and the `.unit-art` CSS.

## Guide character

Keep the existing infinity guide by default. For an agreed custom guide, adapt `mascotEl` and the cover drawing together, retaining blink, happy hop and wrong-answer tilt states.

## Bookshelf

`site/index.html` with `lib/bookshelf.js` and `.css` lists the books. Add an entry to `books` in `bookshelf.js`:

```js
{ id: 'history', title: '…', subject: 'History', href: 'history/', coverTitle: ['Line one', 'line two'],
  series: 'An animated book', description: '…', chapters: 24, units: 6,
  artwork: '<svg viewBox="0 0 260 175" class="book-art">…</svg>', features: ['…', '…', '…'] }
```

List ready books. Folder-based entries use their own counts and artwork; their saved place is available on the book cover.

## Publishing

Use the user's publishing authorization. Any static host works; for Cloudflare Pages:

```sh
npx wrangler pages deploy site --project-name <project> --branch main --commit-hash $(git rev-parse --short HEAD)
```

Commit first, deploy the committed state, then confirm the live URL serves a changed file with a cache-busting query. Record commit, URL and deployment id in `books/<book>/releases.md`. Publish only `site/`.

## Languages

Narration and on-screen text are written in one language first. A second language comes after the book is done and approved: keep beat ids and question ids stable, add `narration.<lang>.json` and audio per language, and decide with the user how switching behaves mid-lesson before building it.
