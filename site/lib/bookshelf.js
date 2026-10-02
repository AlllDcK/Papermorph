/* The public bookshelf. Add real, published books here; no build step required.
 * This first book shares index.html with its contents, so its counts and saved
 * place come from the rendered chapter cards, never a second chapter list.
 */
'use strict';
(() => {
  const books = [{
    id: 'pre-algebra', title: 'Pre-Algebra & Algebra', subject: 'Mathematics',
    href: '#book', coverTitle: ['Pre-Algebra', '& Algebra'], series: 'An animated workbook',
    description: 'From the first number line to the shape of an equation. See the math unfold, one idea at a time.',
    contents: '#units',
  }];
  const el = (tag, cls, text) => {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  };
  const link = (cls, text, href) => {
    const a = el('a', cls, text);
    a.href = href;
    return a;
  };
  // Original SVG cover artwork: a graph draws itself as a point traces the curve.
  const artwork = `<svg viewBox="0 0 260 175" class="book-art" aria-hidden="true">
    <g fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M25 140H238 M52 158V20" stroke="#a8c6ba" stroke-width="1" opacity=".45"/>
      <path d="M49 80H55 M49 110H55 M105 137V143 M158 137V143 M211 137V143" stroke="#a8c6ba" opacity=".5"/>
      <path d="M52 132C88 131 92 51 128 53S185 137 231 32" stroke="#f2c078" stroke-width="3" class="book-curve" pathLength="1"/>
      <circle cx="128" cy="53" r="5" fill="#f2c078" stroke="#f2c078" class="curve-point"/>
      <path d="M89 81C63 28 178 31 167 80S59 128 89 81C117 39 179 36 182 77S114 123 89 81Z" stroke="#e9eee2" stroke-width="2" opacity=".07"/>
    </g>
    <text x="180" y="155" fill="#d3ded5" opacity=".6" font-size="17" font-family="Georgia,serif" font-style="italic">f(x)</text>
    <text x="24" y="26" fill="#e9eee2" opacity=".6" font-size="22" font-family="Georgia,serif">∞</text>
  </svg>`;
  const container = document.getElementById('shelf-books');
  for (const [index, book] of books.entries()) {
    const contents = document.querySelector(book.contents);
    const chapters = contents.querySelectorAll('.ch');
    const units = contents.querySelectorAll('.unit').length;
    const last = contents.querySelector('.ch.last');
    const finished = contents.querySelectorAll('.ch.done').length;
    const row = el('article', 'shelf-book');
    row.style.setProperty('--book-index', index);
    const display = el('div', 'book-display');
    const cover = link('book-object', '', book.href);
    cover.setAttribute('aria-label', `Open ${book.title}: ${chapters.length} chapters`);
    const pages = el('span', 'book-pages');
    pages.setAttribute('aria-hidden', 'true');
    cover.append(pages);
    const front = el('span', 'book-front');
    front.append(el('span', 'book-series', book.series));
    const title = el('span', 'book-cover-title');
    title.append(el('span', '', book.coverTitle[0]), el('i', '', book.coverTitle[1]));
    front.append(title);
    const picture = el('span', 'book-picture');
    picture.innerHTML = artwork;
    front.append(picture, el('span', 'book-cover-bottom', 'Watch · Explore · Try'));
    cover.append(front);
    display.append(cover, el('span', 'shelf-plank'));
    const info = el('div', 'book-info');
    const category = el('p', 'book-category', book.subject);
    category.prepend(el('span', 'category-mark', String(index + 1).padStart(2, '0')));
    const heading = el('h3', '');
    heading.append(link('book-title-link', book.title, book.href));
    info.append(category, heading, el('p', 'book-description', book.description));
    const facts = el('p', 'book-facts', `${chapters.length} chapters · ${units} units · Narrated lessons`);
    info.append(facts);
    const features = el('ul', 'book-features');
    for (const text of ['Ideas drawn step by step', 'Quick checks inside the animation', 'Practice you can play with']) {
      const li = el('li', '', text);
      li.prepend(el('span', 'feature-tick', '↗'));
      features.append(li);
    }
    info.append(features);
    const actions = el('div', 'book-actions');
    const open = link('shelf-open', 'Explore this book', book.href);
    open.append(el('span', '', '→'));
    actions.append(open);
    if (last) {
      const chapter = last.querySelector('b').textContent;
      actions.append(link('shelf-continue', `Continue chapter ${chapter} →`, last.getAttribute('href')));
      const status = el('p', 'shelf-progress', `${finished} of ${chapters.length} chapters finished`);
      info.append(status);
    }
    info.append(actions);
    row.append(display, info);
    container.append(row);
  }
  document.getElementById('shelf-count').textContent = `${books.length} ${books.length === 1 ? 'book' : 'books'} · A growing collection`;
})();
