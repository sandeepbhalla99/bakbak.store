import { BOOKS, loadCatalog, getBookDetails } from './books.js';
import { 
  getCurrentUser, 
  registerUser, 
  loginUser, 
  logoutUser, 
  getBookshelf, 
  addBookToShelf,
  getUserStats
} from './auth.js';
import { 
  initReader, 
  prevChapter, 
  nextChapter, 
  goToIndex,
  changeTheme, 
  adjustFontSize,
  saveNoteForActiveChapter,
  renderNotesForActiveChapter,
  getActiveBook
} from './reader.js';
import { 
  CHANNELS, 
  getActiveChannel, 
  setActiveChannel, 
  getMessagesForChannel, 
  getReviews, 
  addMessageToChannel, 
  addReview,
  triggerBotReply
} from './community.js';

// DOM selectors
const views = {
  home: document.getElementById('view-home'),
  catalog: document.getElementById('view-catalog'),
  reader: document.getElementById('view-reader'),
  community: document.getElementById('view-community'),
  shelf: document.getElementById('view-shelf')
};

// Global App State
let activeView = 'home';
let selectedReviewRating = 5;

// INITIALIZE APP
document.addEventListener('DOMContentLoaded', async () => {
  await loadCatalog(); // fetch the catalog and populate BOOKS
  setupNavigation();
  setupAuth();
  setupCatalog();
  setupReaderUI();
  setupCommunityUI();
  updateAuthUI();
  renderFeaturedBooks();
  
  // Direct view if hash exists
  const hash = window.location.hash.substring(1);
  if (hash && views[hash]) {
    switchView(hash);
  } else {
    switchView('home');
  }
});

// 1. ROUTING & NAVIGATION
function switchView(viewName) {
  // If shelf is accessed but user is not logged in, prompt login
  if (viewName === 'shelf' && !getCurrentUser()) {
    showModal('auth-modal');
    return;
  }

  activeView = viewName;
  window.location.hash = viewName;

  // Toggle active class on views
  Object.keys(views).forEach(name => {
    if (name === viewName) {
      views[name].classList.add('active');
    } else {
      views[name].classList.remove('active');
    }
  });

  // Toggle active class on nav links
  document.querySelectorAll('#main-nav a').forEach(link => {
    if (link.getAttribute('data-view') === viewName) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Render content specific to the view when loaded
  if (viewName === 'shelf') {
    renderBookshelf();
  } else if (viewName === 'community') {
    renderCommunityChat();
    renderCommunityReviews();
  } else if (viewName === 'home') {
    renderHomeStats();
  }
}

function setupNavigation() {
  document.querySelectorAll('#main-nav a, #view-all-trending-btn').forEach(element => {
    element.addEventListener('click', (e) => {
      const view = e.target.getAttribute('data-view') || 'catalog';
      switchView(view);
    });
  });

  document.getElementById('header-logo').addEventListener('click', () => {
    switchView('home');
  });

  // Listener to handle browser Back/Forward buttons
  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.substring(1);
    if (hash && views[hash] && hash !== activeView) {
      switchView(hash);
    }
  });
}

// 2. AUTHENTICATION UI & MOCK
function setupAuth() {
  const loginBtn = document.getElementById('header-login-btn');
  const signupBtn = document.getElementById('header-signup-btn');
  const authModal = document.getElementById('auth-modal');
  const closeAuthBtn = document.getElementById('close-auth-modal-btn');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const switchToRegister = document.getElementById('switch-to-register');
  const switchToLogin = document.getElementById('switch-to-login');

  loginBtn.addEventListener('click', () => {
    loginForm.style.display = 'flex';
    registerForm.style.display = 'none';
    showModal('auth-modal');
  });

  signupBtn.addEventListener('click', () => {
    loginForm.style.display = 'none';
    registerForm.style.display = 'flex';
    showModal('auth-modal');
  });

  closeAuthBtn.addEventListener('click', () => hideModal('auth-modal'));
  
  // Expose registration modal trigger globally
  window.showRegistrationModal = () => {
    loginForm.style.display = 'none';
    registerForm.style.display = 'flex';
    showModal('auth-modal');
  };

  switchToRegister.addEventListener('click', () => {
    loginForm.style.display = 'none';
    registerForm.style.display = 'flex';
  });

  switchToLogin.addEventListener('click', () => {
    loginForm.style.display = 'flex';
    registerForm.style.display = 'none';
  });

  // Form submits
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error-msg');

    try {
      loginUser(email, password);
      updateAuthUI();
      hideModal('auth-modal');
      if (activeView === 'reader') {
        const activeBook = getActiveBook();
        if (activeBook) {
          initReader(activeBook.id);
        } else {
          switchView('shelf');
        }
      } else {
        switchView('shelf');
      }
      errorEl.style.display = 'none';
      loginForm.reset();
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.style.display = 'block';
    }
  });

  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const phone = document.getElementById('register-phone').value;
    const errorEl = document.getElementById('register-error-msg');

    try {
      registerUser(name, email, password, phone);
      updateAuthUI();
      hideModal('auth-modal');
      if (activeView === 'reader') {
        const activeBook = getActiveBook();
        if (activeBook) {
          initReader(activeBook.id);
        } else {
          switchView('shelf');
        }
      } else {
        switchView('shelf');
      }
      errorEl.style.display = 'none';
      registerForm.reset();
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.style.display = 'block';
    }
  });

  document.getElementById('profile-logout-btn').addEventListener('click', () => {
    logoutUser();
    updateAuthUI();
    switchView('home');
  });
}

function updateAuthUI() {
  const user = getCurrentUser();
  const headerContainer = document.getElementById('auth-header-container');
  const navShelf = document.getElementById('nav-shelf');

  if (user) {
    navShelf.style.display = 'inline-block';
    headerContainer.innerHTML = `
      <div class="profile-header-btn" id="header-profile-menu">
        <div class="avatar-small">${user.name.slice(0,2).toUpperCase()}</div>
        <span style="font-size: 0.9rem; font-weight: 500;">${user.name}</span>
      </div>
    `;
    
    // Bind profile menu click to go to shelf
    document.getElementById('header-profile-menu').addEventListener('click', () => {
      switchView('shelf');
    });
  } else {
    navShelf.style.display = 'none';
    headerContainer.innerHTML = `
      <button class="btn btn-secondary btn-sm" id="header-login-btn">Sign In</button>
      <button class="btn btn-primary btn-sm" id="header-signup-btn">Join Club</button>
    `;
    // Rebind since elements were replaced
    setupAuth();
  }
}

// 3. BOOK CATALOG & DETAIL PREVIEWS
function setupCatalog() {
  const searchInput = document.getElementById('catalog-search-input');
  const heroSearchInput = document.getElementById('hero-search-input');
  const heroSearchBtn = document.getElementById('hero-search-btn');

  // Load complete catalog
  renderCatalog(BOOKS);

  // Dynamically generate genre filters based on unique genres in BOOKS
  const genreContainer = document.getElementById('genre-filter-container');
  if (genreContainer) {
    const genres = Array.from(new Set(BOOKS.map(book => book.genre).filter(Boolean))).sort();
    let genreHTML = `<h4>Categories</h4>`;
    genreHTML += `<button class="genre-filter-btn active" data-genre="all">All Genres</button>`;
    genres.forEach(genre => {
      genreHTML += `<button class="genre-filter-btn" data-genre="${genre}">${genre}</button>`;
    });
    genreContainer.innerHTML = genreHTML;
  }

  // Filters
  document.querySelectorAll('.genre-filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.genre-filter-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      filterCatalog();
    });
  });

  searchInput.addEventListener('input', filterCatalog);

  // Hero Search redirect
  const doHeroSearch = () => {
    const query = heroSearchInput.value.trim();
    if (query !== "") {
      switchView('catalog');
      searchInput.value = query;
      filterCatalog();
      heroSearchInput.value = "";
    }
  };

  heroSearchBtn.addEventListener('click', doHeroSearch);
  heroSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') doHeroSearch();
  });

  // Modal Closures
  document.getElementById('close-preview-modal-btn').addEventListener('click', () => hideModal('book-preview-modal'));
}

function filterCatalog() {
  const query = document.getElementById('catalog-search-input').value.toLowerCase();
  const activeGenreBtn = document.querySelector('.genre-filter-btn.active');
  const genre = activeGenreBtn ? activeGenreBtn.getAttribute('data-genre') : 'all';

  const filtered = BOOKS.filter(book => {
    const matchesSearch = book.title.toLowerCase().includes(query) || 
                          book.author.toLowerCase().includes(query) || 
                          book.description.toLowerCase().includes(query);
    const matchesGenre = (genre === 'all') || (book.genre === genre);
    return matchesSearch && matchesGenre;
  });

  renderCatalog(filtered);
}

function renderCatalog(booksList) {
  const container = document.getElementById('catalog-books-list');
  if (!container) return;

  if (booksList.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted); margin-top: 40px;">No books matched your criteria. Try another search!</p>`;
    return;
  }

  container.innerHTML = booksList.map(book => {
    const ratingHTML = Array(Math.round(book.rating)).fill('★').join('') + Array(5 - Math.round(book.rating)).fill('☆').join('');
    const coverHTML = book.coverImage
      ? `<div class="book-card-cover" style="background-image: url('${book.coverImage}'); background-size: cover; background-position: center; height: 100%; width: 100%;"></div>`
      : `<div class="book-card-cover" style="background: ${book.coverColor}; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center; box-sizing: border-box;">
            <div style="font-weight: 700; font-size: 1.1rem; text-shadow: 0 4px 8px rgba(0,0,0,0.5);">${book.title}</div>
            <div style="font-size: 0.8rem; margin-top: 10px; opacity: 0.8;">${book.author}</div>
          </div>`;
    return `
      <div class="book-card glass glass-hover" data-book-id="${book.id}">
        <div class="book-cover-wrapper">
          ${coverHTML}
          <div class="book-overlay">
            <p>${book.description}</p>
            <span class="badge">${book.genre}</span>
          </div>
        </div>
        <div class="book-info">
          <div class="book-title" title="${book.title}">${book.title}</div>
          <div class="book-author">${book.author}</div>
          <div class="book-card-meta">
            <span class="rating-stars">${ratingHTML}</span>
            <span>${book.rating} (${book.reviewsCount})</span>
          </div>
        </div>
      </div>
    `;
  }).join('');


  // Bind clicks
  container.querySelectorAll('.book-card').forEach(card => {
    card.addEventListener('click', () => {
      const bookId = card.getAttribute('data-book-id');
      openBookDetailPreview(bookId);
    });
  });
}

function renderFeaturedBooks() {
  const container = document.getElementById('featured-books-list');
  if (!container) return;

  const featured = BOOKS.slice(0, 4);
  container.innerHTML = featured.map(book => {
    const ratingHTML = Array(Math.round(book.rating)).fill('★').join('') + Array(5 - Math.round(book.rating)).fill('☆').join('');
    const coverHTML = book.coverImage
      ? `<div class="book-card-cover" style="background-image: url('${book.coverImage}'); background-size: cover; background-position: center; height: 100%; width: 100%;"></div>`
      : `<div class="book-card-cover" style="background: ${book.coverColor}; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center; box-sizing: border-box;">
            <div style="font-weight: 700; font-size: 1.1rem; text-shadow: 0 4px 8px rgba(0,0,0,0.5);">${book.title}</div>
            <div style="font-size: 0.8rem; margin-top: 10px; opacity: 0.8;">${book.author}</div>
          </div>`;
    return `
      <div class="book-card glass glass-hover" data-book-id="${book.id}">
        <div class="book-cover-wrapper">
          ${coverHTML}
          <div class="book-overlay">
            <p>${book.description}</p>
            <span class="badge">${book.genre}</span>
          </div>
        </div>
        <div class="book-info">
          <div class="book-title" title="${book.title}">${book.title}</div>
          <div class="book-author">${book.author}</div>
          <div class="book-card-meta">
            <span class="rating-stars">${ratingHTML}</span>
            <span>${book.rating}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');


  container.querySelectorAll('.book-card').forEach(card => {
    card.addEventListener('click', () => {
      const bookId = card.getAttribute('data-book-id');
      openBookDetailPreview(bookId);
    });
  });
}

async function openBookDetailPreview(bookId) {
  const bookSummary = BOOKS.find(b => b.id === bookId);
  if (!bookSummary) return;

  const book = await getBookDetails(bookId);
  if (!book) return;

  const user = getCurrentUser();
  const shelf = getBookshelf();
  const isBookOnShelf = shelf[bookId];
  let shelfStatusSelect = '';

  if (user) {
    shelfStatusSelect = `
      <div class="form-group" style="margin-bottom: 16px;">
        <label style="margin-bottom: 6px; font-weight: 600;">Bookshelf Status</label>
        <select id="modal-shelf-status-select" style="background: rgba(255,255,255,0.08); color: white; border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 6px; outline: none; width: 100%;">
          <option value="none" ${!isBookOnShelf ? 'selected' : ''}>Not on Shelf</option>
          <option value="want-to-read" ${isBookOnShelf?.status === 'want-to-read' ? 'selected' : ''}>Plan to Read</option>
          <option value="reading" ${isBookOnShelf?.status === 'reading' ? 'selected' : ''}>Currently Reading</option>
          <option value="completed" ${isBookOnShelf?.status === 'completed' ? 'selected' : ''}>Completed</option>
        </select>
      </div>
    `;
  } else {
    shelfStatusSelect = `<p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;"><span id="modal-login-prompt" style="color: var(--primary); cursor: pointer; font-weight: 600; text-decoration: underline;">Sign In</span> to save books to your bookshelf.</p>`;
  }

  const ratingHTML = Array(Math.round(book.rating || 4.5)).fill('★').join('') + Array(5 - Math.round(book.rating || 4.5)).fill('☆').join('');

  const previewCoverHTML = book.coverImage
    ? `<div style="background-image: url('${book.coverImage}'); background-size: cover; background-position: center; border-radius: 12px; height: 280px; border: 1px solid var(--border-color); box-shadow: 0 10px 20px rgba(0,0,0,0.4);"></div>`
    : `<div style="background: ${book.coverColor}; display: flex; flex-direction: column; justify-content: center; align-items: center; border-radius: 12px; height: 280px; text-align: center; border: 1px solid var(--border-color); box-shadow: 0 10px 20px rgba(0,0,0,0.4);">
        <div style="font-weight: 800; font-size: 1.4rem; padding: 20px; line-height: 1.3; text-shadow: 0 4px 10px rgba(0,0,0,0.6);">${book.title}</div>
        <div style="font-size: 0.95rem; opacity: 0.8;">${book.author}</div>
      </div>`;

  const modalLayout = document.getElementById('book-preview-layout');
  modalLayout.innerHTML = `
    ${previewCoverHTML}
    <div class="book-details-info">
      <h2>${book.title}</h2>
      <div class="book-details-author">by ${book.author}</div>
      
      <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 16px;">
        <span class="book-details-genre">${book.genre}</span>
        <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">${ratingHTML} ${book.rating || 4.5}</span>
        <span style="font-size: 0.85rem; color: var(--text-muted);">${book.chapters.length} chapters</span>
      </div>

      <p class="book-details-description">${book.description}</p>
      
      <div style="margin-top: auto;">
        ${shelfStatusSelect}
        
        <div class="book-details-actions">
          <button class="btn btn-primary" id="modal-start-reading-btn">Start Reading</button>
          <button class="btn btn-secondary" id="modal-back-btn">Back</button>
        </div>
      </div>
    </div>
  `;


  showModal('book-preview-modal');

  // Event handlers for detail buttons
  document.getElementById('modal-back-btn').addEventListener('click', () => hideModal('book-preview-modal'));
  
  // Prompt login click if guest
  const loginPrompt = document.getElementById('modal-login-prompt');
  if (loginPrompt) {
    loginPrompt.addEventListener('click', () => {
      hideModal('book-preview-modal');
      const loginForm = document.getElementById('login-form');
      const registerForm = document.getElementById('register-form');
      loginForm.style.display = 'flex';
      registerForm.style.display = 'none';
      showModal('auth-modal');
    });
  }

  // Shelf status selector mapping
  const statusSelect = document.getElementById('modal-shelf-status-select');
  if (statusSelect) {
    statusSelect.addEventListener('change', (e) => {
      const selectedStatus = e.target.value;
      if (selectedStatus === 'none') {
        // delete from shelf helper if we wanted to (currently mock preserves it)
      } else {
        addBookToShelf(bookId, selectedStatus);
      }
    });
  }

  // E-Reader trigger
  document.getElementById('modal-start-reading-btn').addEventListener('click', () => {
    hideModal('book-preview-modal');
    // Ensure book is on Currently Reading if user logged in
    if (getCurrentUser()) {
      addBookToShelf(bookId, 'reading');
    }
    switchView('reader');
    initReader(bookId);
  });
}

// 4. BOOKSHELF RENDERER & ACTIONS
function renderBookshelf() {
  const user = getCurrentUser();
  if (!user) return;

  // Render Left profile info
  const avatar = document.getElementById('profile-avatar');
  avatar.textContent = user.name.slice(0, 1).toUpperCase();
  document.getElementById('profile-display-name').textContent = user.name;
  document.getElementById('profile-display-email').textContent = user.email;
  document.getElementById('profile-joined-date').textContent = `Joined ${user.joinedDate || 'recently'}`;

  // Stats boxes
  const stats = getUserStats();
  document.getElementById('profile-stat-streak').textContent = stats.streak;
  document.getElementById('profile-stat-reading').textContent = stats.countReading;
  document.getElementById('profile-stat-completed').textContent = stats.countCompleted;
  document.getElementById('profile-stat-wish').textContent = stats.countWantToRead;

  // Active filter tab
  const activeTabEl = document.querySelector('.shelf-tab.active');
  const activeTab = activeTabEl ? activeTabEl.getAttribute('data-shelf-tab') : 'all';

  const userShelf = getBookshelf();
  const container = document.getElementById('shelf-books-list');
  
  if (!container) return;

  const shelfIds = Object.keys(userShelf);
  const shelfBooks = BOOKS.filter(b => shelfIds.includes(b.id));

  // Filter based on selected bookshelf state tab
  const filteredBooks = shelfBooks.filter(book => {
    const item = userShelf[book.id];
    if (activeTab === 'all') return true;
    return item.status === activeTab;
  });

  if (filteredBooks.length === 0) {
    container.innerHTML = `<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted); margin-top: 40px;">No books on this shelf yet. Add some from the Catalog!</p>`;
    return;
  }

  container.innerHTML = filteredBooks.map(book => {
    const shelfItem = userShelf[book.id];
    const progress = shelfItem.progressPct || 0;
    
    let statusText = 'Plan to Read';
    if (shelfItem.status === 'reading') statusText = 'Reading';
    else if (shelfItem.status === 'completed') statusText = 'Completed';

    const shelfCoverHTML = book.coverImage
      ? `<div style="background-image: url('${book.coverImage}'); background-size: cover; background-position: center; border-radius: 6px; height: 110px; border: 1px solid var(--border-color);"></div>`
      : `<div style="background: ${book.coverColor}; border-radius: 6px; height: 110px; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 10px; text-align: center; font-size: 0.75rem; border: 1px solid var(--border-color);">
          <div style="font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.5);">${book.title}</div>
        </div>`;

    return `
      <div class="shelf-item glass" data-book-id="${book.id}">
        ${shelfCoverHTML}
        <div class="shelf-item-details">
          <div class="shelf-item-title">${book.title}</div>
          <div class="shelf-item-author">${book.author}</div>
          
          <div class="shelf-progress-bar">
            <div class="shelf-progress-fill" style="width: ${progress}%;"></div>
          </div>
          <div class="shelf-progress-text">${progress}% Read (${statusText})</div>

          <div class="shelf-actions">
            <button class="btn btn-primary btn-sm shelf-resume-btn">Resume</button>
            <button class="btn btn-secondary btn-sm shelf-remove-btn">Remove</button>
          </div>
        </div>
      </div>
    `;
  }).join('');


  // Bind Shelf Card clicks
  container.querySelectorAll('.shelf-resume-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const card = e.target.closest('.shelf-item');
      const bookId = card.getAttribute('data-book-id');
      switchView('reader');
      initReader(bookId);
    });
  });

  container.querySelectorAll('.shelf-remove-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const card = e.target.closest('.shelf-item');
      const bookId = card.getAttribute('data-book-id');
      
      // Remove helper logic
      const u = getCurrentUser();
      if (u && u.bookshelf) {
        delete u.bookshelf[bookId];
        setStorageItem('bakbak_current_user', u);
        
        // update users list
        const users = JSON.parse(localStorage.getItem('bakbak_users') || '[]');
        const updatedUsers = users.map(userItem => userItem.id === u.id ? u : userItem);
        localStorage.setItem('bakbak_users', JSON.stringify(updatedUsers));
        
        renderBookshelf();
      }
    });
  });
}

// Helper duplicates to avoid writing raw LocalStorage logic repeatedly
function setStorageItem(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

// Bind shelf tabs toggle
document.querySelectorAll('.shelf-tab').forEach(tab => {
  tab.addEventListener('click', (e) => {
    document.querySelectorAll('.shelf-tab').forEach(t => t.classList.remove('active'));
    e.target.classList.add('active');
    renderBookshelf();
  });
});

// 5. E-READER CONTROLS & SIDEBAR
function setupReaderUI() {
  const container = document.getElementById('reader-view-container');
  if (!container) return;

  // Bottom pagination buttons
  document.getElementById('reader-prev-btn').addEventListener('click', prevChapter);
  document.getElementById('reader-next-btn').addEventListener('click', nextChapter);

  // Close reader button
  document.getElementById('reader-close-btn').addEventListener('click', () => {
    switchView('catalog');
  });

  // Jump to Index button
  document.getElementById('reader-index-btn').addEventListener('click', () => {
    goToIndex();
  });


  // Font size adjustments
  document.getElementById('reader-font-minus').addEventListener('click', () => adjustFontSize(-0.1));
  document.getElementById('reader-font-plus').addEventListener('click', () => adjustFontSize(0.1));

  // Theme switches
  document.querySelectorAll('[data-reader-theme]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const selectedTheme = e.target.getAttribute('data-reader-theme');
      changeTheme(selectedTheme);
    });
  });

  // Auto-saves text notes in the sidebar
  const notesTextarea = document.getElementById('reader-notes-textarea');
  if (notesTextarea) {
    notesTextarea.addEventListener('input', (e) => {
      saveNoteForActiveChapter(e.target.value);
    });
  }
}

// 6. COMMUNITY CHAT ROOM & REVIEW SUBMIT
function setupCommunityUI() {
  // Render channels list
  const channelList = document.getElementById('community-channels-list');
  if (channelList) {
    channelList.innerHTML = CHANNELS.map(ch => `
      <button class="comm-channel-btn ${ch.id === getActiveChannel() ? 'active' : ''}" data-channel-id="${ch.id}">${ch.name}</button>
    `).join('');

    channelList.querySelectorAll('.comm-channel-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        channelList.querySelectorAll('.comm-channel-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        const channelId = e.target.getAttribute('data-channel-id');
        setActiveChannel(channelId);
        
        // Update header details
        const chDetails = CHANNELS.find(c => c.id === channelId);
        document.getElementById('chat-active-channel-name').textContent = `#${chDetails.name}`;
        document.getElementById('chat-active-channel-desc').textContent = chDetails.desc;
        
        renderCommunityChat();
      });
    });
  }

  // Chat message input submission
  const msgInput = document.getElementById('chat-message-input');
  const sendBtn = document.getElementById('chat-send-btn');

  const handleSend = () => {
    const text = msgInput.value.trim();
    if (text === "") return;

    if (!getCurrentUser()) {
      showModal('auth-modal');
      return;
    }

    const currentChannel = getActiveChannel();
    const newMsg = addMessageToChannel(currentChannel, text);
    
    // Append message directly to feed to maintain scroll position
    appendMsgToFeed(newMsg);
    msgInput.value = "";

    // Simulated Bot response triggered 1.5 seconds later
    triggerBotReply(currentChannel, (botMsg) => {
      if (getActiveChannel() === currentChannel) {
        appendMsgToFeed(botMsg);
      }
    });
  };

  sendBtn.addEventListener('click', handleSend);
  msgInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  // Review Dialog Actions
  const writeReviewBtn = document.getElementById('comm-write-review-btn');
  const reviewModal = document.getElementById('review-modal');
  const closeReviewBtn = document.getElementById('close-review-modal-btn');
  const reviewForm = document.getElementById('write-review-form');
  const bookSelect = document.getElementById('review-book-select');

  writeReviewBtn.addEventListener('click', () => {
    if (!getCurrentUser()) {
      showModal('auth-modal');
      return;
    }
    // Load options dropdown list
    bookSelect.innerHTML = BOOKS.map(b => `<option value="${b.id}">${b.title}</option>`).join('');
    showModal('review-modal');
  });

  closeReviewBtn.addEventListener('click', () => hideModal('review-modal'));

  // Star select hover/click indicators
  const ratingStars = document.querySelectorAll('#star-rating-input span');
  ratingStars.forEach(star => {
    star.addEventListener('click', (e) => {
      const val = parseInt(e.target.getAttribute('data-star'));
      selectedReviewRating = val;
      
      ratingStars.forEach(s => {
        const starVal = parseInt(s.getAttribute('data-star'));
        if (starVal <= val) {
          s.classList.add('active');
        } else {
          s.classList.remove('active');
        }
      });
    });
  });

  // Initial star selection highlight
  ratingStars.forEach(s => {
    if (parseInt(s.getAttribute('data-star')) <= selectedReviewRating) {
      s.classList.add('active');
    }
  });

  reviewForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const bookId = bookSelect.value;
    const comment = document.getElementById('review-comment-textarea').value;

    addReview(bookId, selectedReviewRating, comment);
    
    // reset form
    reviewForm.reset();
    selectedReviewRating = 5;
    ratingStars.forEach(s => s.classList.add('active')); // default star state reset

    hideModal('review-modal');
    renderCommunityReviews();
  });
}

function renderCommunityChat() {
  const container = document.getElementById('chat-messages-container');
  if (!container) return;

  const currentChannel = getActiveChannel();
  const msgs = getMessagesForChannel(currentChannel);
  const user = getCurrentUser();

  container.innerHTML = msgs.map(m => {
    const isMyMsg = (user && m.sender === user.name) || m.isMyMsg;
    return `
      <div class="chat-bubble ${isMyMsg ? 'my-message' : ''}">
        <div class="avatar-chat">${m.nameInitials}</div>
        <div class="chat-msg-content">
          <div class="chat-msg-header">
            <span class="chat-username">${m.sender}</span>
            <span class="chat-timestamp">${m.timestamp}</span>
          </div>
          <div class="chat-msg-text">${m.message}</div>
        </div>
      </div>
    `;
  }).join('');

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

function appendMsgToFeed(msg) {
  const container = document.getElementById('chat-messages-container');
  if (!container) return;

  const user = getCurrentUser();
  const isMyMsg = (user && msg.sender === user.name) || msg.isMyMsg;

  const chatEl = document.createElement('div');
  chatEl.className = `chat-bubble ${isMyMsg ? 'my-message' : ''}`;
  chatEl.innerHTML = `
    <div class="avatar-chat">${msg.nameInitials}</div>
    <div class="chat-msg-content">
      <div class="chat-msg-header">
        <span class="chat-username">${msg.sender}</span>
        <span class="chat-timestamp">${msg.timestamp}</span>
      </div>
      <div class="chat-msg-text">${msg.message}</div>
    </div>
  `;
  container.appendChild(chatEl);
  container.scrollTop = container.scrollHeight;
}

function renderCommunityReviews() {
  const container = document.getElementById('community-reviews-list');
  if (!container) return;

  const reviews = getReviews();
  container.innerHTML = reviews.map(rev => {
    const stars = Array(rev.rating).fill('★').join('') + Array(5 - rev.rating).fill('☆').join('');
    return `
      <div class="review-item">
        <div class="review-book-title">${rev.bookTitle}</div>
        <div class="review-meta">
          <span>By ${rev.userName}</span>
          <span style="color: #fbbf24;">${stars}</span>
        </div>
        <div class="review-text">${rev.comment}</div>
      </div>
    `;
  }).join('');
}

// 7. HOME STATS DISPLAY
function renderHomeStats() {
  const stats = getUserStats();
  
  // Dynamic display depending on whether user is logged in
  const pagesReadEl = document.getElementById('stat-pages-read');
  const streakEl = document.getElementById('stat-active-readers');
  const discussionsEl = document.getElementById('stat-discussions');

  if (getCurrentUser()) {
    // Show user reading summaries in stats indicators
    const currentShelf = getBookshelf();
    let sumProgress = 0;
    Object.values(currentShelf).forEach(itm => {
      sumProgress += (itm.progressPct || 0);
    });
    
    // estimated pages calculation
    const pagesCountVal = Math.round(sumProgress * 1.25);
    pagesReadEl.textContent = pagesCountVal;
    
    streakEl.textContent = stats.streak;
    document.querySelector('#stat-active-readers + p').textContent = "Day Active Streak";
  } else {
    pagesReadEl.textContent = '9,831';
    streakEl.textContent = '1,248';
    document.querySelector('#stat-active-readers + p').textContent = "Club Members";
  }
}

// UTILITY MODAL HELPERS
function showModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) {
    el.style.display = 'flex';
    setTimeout(() => el.classList.add('active'), 10);
  }
}

function hideModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) {
    el.classList.remove('active');
    setTimeout(() => el.style.display = 'none', 300);
  }
}
