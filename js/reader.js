import { updateReadingProgress, getCurrentUser } from './auth.js';
import { getBookDetails } from './books.js';

let activeBook = null;
let activeChapterIndex = 0;
let fontSize = 1.15; // in rem
let readerTheme = 'sepia'; // 'light' | 'sepia' | 'dark'

export function getActiveBook() {
  return activeBook;
}

export async function initReader(bookId, startingChapter = 0) {
  activeBook = await getBookDetails(bookId);
  if (!activeBook) return;

  // Fetch bookmark if it exists
  const user = getCurrentUser();
  if (user && user.bookshelf && user.bookshelf[bookId]) {
    activeChapterIndex = user.bookshelf[bookId].lastChapter || 0;
  } else {
    activeChapterIndex = startingChapter;
  }

  applyReaderSettings();
  await renderReaderContent();
}

function applyReaderSettings() {
  const container = document.getElementById('reader-view-container');
  if (!container) return;

  // Clear existing themes
  container.className = 'reader-container';
  container.classList.add(`theme-${readerTheme}`);

  // Apply font size
  const textContainer = container.querySelector('.reader-text-container');
  if (textContainer) {
    textContainer.style.fontSize = `${fontSize}rem`;
  }

  // Update active buttons in UI
  const themeBtns = document.querySelectorAll('[data-reader-theme]');
  themeBtns.forEach(btn => {
    if (btn.getAttribute('data-reader-theme') === readerTheme) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

export async function renderReaderContent() {
  if (!activeBook) return;

  const container = document.getElementById('reader-view-container');
  if (!container) return;

  // Update navbar info
  const titleEl = container.querySelector('.reader-title-info h3');
  const authorEl = container.querySelector('.reader-title-info span');
  if (titleEl) titleEl.textContent = activeBook.title;
  if (authorEl) authorEl.textContent = activeBook.author;

  const chapter = activeBook.chapters[activeChapterIndex];
  const textBody = container.querySelector('.reader-text-body');
  
  if (chapter && textBody) {
    textBody.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 40px;">Loading Chapter Text...</p>`;
    
    try {
      const response = await fetch(`books/${activeBook.id}/chapters/${chapter.file}`);
      if (!response.ok) throw new Error("Could not load chapter file");
      
      const markdown = await response.text();
      // Parse markdown to HTML using marked.js with breaks enabled to preserve poetry/TOC formats
      const htmlContent = marked.parse(markdown, { breaks: true });
      textBody.innerHTML = htmlContent;

      // Intercept link clicks for SPA chapter navigation using event delegation
      if (textBody.dataset.spaLinksAttached !== 'true') {
        textBody.addEventListener('click', (e) => {
          const link = e.target.closest('a');
          if (link) {
            const href = link.getAttribute('href');
            if (href) {
              const filename = href.split('/').pop().split('?')[0].split('#')[0];
              if (filename.toLowerCase().endsWith('.md') || href.includes('chapters/')) {
                e.preventDefault();
                const decodedFilename = decodeURIComponent(filename).toLowerCase();
                const chapIdx = activeBook.chapters.findIndex(c => {
                  return decodeURIComponent(c.file).toLowerCase() === decodedFilename;
                });
                if (chapIdx !== -1) {
                  activeChapterIndex = chapIdx;
                  renderReaderContent();
                } else {
                  console.warn("SPA Navigation failed: could not find chapter file matching", decodedFilename);
                }
              }
            }
          }
        });
        textBody.dataset.spaLinksAttached = 'true';
      }

      // Update progress numbers
      const chapterNumEl = document.getElementById('reader-chapter-num');
      const progressPctEl = document.getElementById('reader-progress-pct');
      const progressFill = document.getElementById('reader-progress-fill');
      
      if (chapterNumEl) {
        chapterNumEl.textContent = `Chapter ${activeChapterIndex + 1} of ${activeBook.chapters.length}`;
      }

      const progressPct = Math.round(((activeChapterIndex + 1) / activeBook.chapters.length) * 100);
      if (progressPctEl) {
        progressPctEl.textContent = `${progressPct}% Read`;
      }
      if (progressFill) {
        progressFill.style.width = `${progressPct}%`;
      }

      // Save progress
      updateReadingProgress(activeBook.id, activeChapterIndex, 0, progressPct);
      
      // Scroll reader body back to top
      const wrapper = container.querySelector('.reader-body-wrapper');
      if (wrapper) wrapper.scrollTop = 0;

    } catch (err) {
      console.error(err);
      textBody.innerHTML = `<p style="text-align: center; color: var(--accent); padding: 40px;">Failed to load chapter text. Please check your connection or retry.</p>`;
    }
  }

  // Handle arrows accessibility
  const prevBtn = document.getElementById('reader-prev-btn');
  const nextBtn = document.getElementById('reader-next-btn');
  
  if (prevBtn) prevBtn.style.visibility = activeChapterIndex > 0 ? 'visible' : 'hidden';
  if (nextBtn) nextBtn.style.visibility = activeChapterIndex < activeBook.chapters.length - 1 ? 'visible' : 'hidden';

  // Load and render user notes for this book/chapter
  renderNotesForActiveChapter();
}

// NAVIGATION
export async function prevChapter() {
  if (activeChapterIndex > 0) {
    activeChapterIndex--;
    await renderReaderContent();
  }
}

export async function nextChapter() {
  if (activeBook && activeChapterIndex < activeBook.chapters.length - 1) {
    activeChapterIndex++;
    await renderReaderContent();
  }
}

// ADJUST SETTINGS
export function changeTheme(newTheme) {
  readerTheme = newTheme;
  applyReaderSettings();
}

export function adjustFontSize(change) {
  fontSize = Math.max(0.85, Math.min(2.0, fontSize + change));
  applyReaderSettings();
}

// USER NOTES MANAGEMENT FOR THE E-READER
function getNotesStorageKey() {
  const user = getCurrentUser();
  const userId = user ? user.id : 'guest';
  return `bakbak_notes_${userId}_${activeBook?.id}`;
}

export function renderNotesForActiveChapter() {
  const notesPanel = document.getElementById('reader-notes-textarea');
  if (!notesPanel || !activeBook) return;

  const allNotes = localStorage.getItem(getNotesStorageKey());
  let bookNotes = allNotes ? JSON.parse(allNotes) : {};
  
  // Render note for active chapter, or default to empty
  notesPanel.value = bookNotes[activeChapterIndex] || "";
}

export function saveNoteForActiveChapter(text) {
  if (!activeBook) return;
  
  const key = getNotesStorageKey();
  const allNotes = localStorage.getItem(key);
  let bookNotes = allNotes ? JSON.parse(allNotes) : {};
  
  if (text.trim() === "") {
    delete bookNotes[activeChapterIndex];
  } else {
    bookNotes[activeChapterIndex] = text;
  }
  
  localStorage.setItem(key, JSON.stringify(bookNotes));
}
