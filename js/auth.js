// Mock user authentication & bookshelf state management

// Helper to get raw localStorage items safely
function getStorageItem(key, defaultValue) {
  const item = localStorage.getItem(key);
  try {
    return item ? JSON.parse(item) : defaultValue;
  } catch (e) {
    return defaultValue;
  }
}

function setStorageItem(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

// 1. SESSION MANAGEMENT
export function getCurrentUser() {
  return getStorageItem('bakbak_current_user', null);
}

export function registerUser(name, email, password) {
  const users = getStorageItem('bakbak_users', []);
  
  if (users.find(u => u.email === email)) {
    throw new Error('An account with this email already exists.');
  }

  const newUser = {
    id: 'user_' + Date.now(),
    name,
    email,
    password, // note: stored as plain text for mock demo purposes
    joinedDate: new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
    bookshelf: {}, // map of bookId -> { status: 'want_to_read' | 'reading' | 'completed', lastChapter: 0, lastParagraph: 0, progressPct: 0 }
    stats: {
      streak: 1,
      lastActive: new Date().toDateString()
    }
  };

  users.push(newUser);
  setStorageItem('bakbak_users', users);
  
  // Auto-login after registration
  setStorageItem('bakbak_current_user', newUser);
  return newUser;
}

export function loginUser(email, password) {
  const users = getStorageItem('bakbak_users', []);
  const user = users.find(u => u.email === email && u.password === password);
  
  if (!user) {
    throw new Error('Invalid email or password.');
  }

  // Update streak if active on a new day
  const today = new Date().toDateString();
  if (!user.stats) {
    user.stats = { streak: 1, lastActive: today };
  } else {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    if (user.stats.lastActive === yesterday.toDateString()) {
      user.stats.streak += 1;
    } else if (user.stats.lastActive !== today) {
      user.stats.streak = 1;
    }
    user.stats.lastActive = today;
  }

  // Save changes to users array
  const updatedUsers = users.map(u => u.id === user.id ? user : u);
  setStorageItem('bakbak_users', updatedUsers);
  
  setStorageItem('bakbak_current_user', user);
  return user;
}

export function logoutUser() {
  localStorage.removeItem('bakbak_current_user');
}

// 2. BOOKSHELF CRUD
export function getBookshelf() {
  const currentUser = getCurrentUser();
  if (!currentUser) return {};
  return currentUser.bookshelf || {};
}

function updateCurrentUserInStorage(updatedUser) {
  setStorageItem('bakbak_current_user', updatedUser);
  
  const users = getStorageItem('bakbak_users', []);
  const updatedUsers = users.map(u => u.id === updatedUser.id ? updatedUser : u);
  setStorageItem('bakbak_users', updatedUsers);
}

export function addBookToShelf(bookId, status = 'want-to-read') {
  const user = getCurrentUser();
  if (!user) throw new Error('Please sign in to save books to your shelf.');

  if (!user.bookshelf) user.bookshelf = {};
  
  if (!user.bookshelf[bookId]) {
    user.bookshelf[bookId] = {
      status: status,
      lastChapter: 0,
      lastParagraph: 0,
      progressPct: 0
    };
  } else {
    user.bookshelf[bookId].status = status;
  }

  updateCurrentUserInStorage(user);
  return user.bookshelf[bookId];
}

export function updateReadingProgress(bookId, chapterIndex, paragraphIndex, progressPct) {
  const user = getCurrentUser();
  if (!user) return;

  if (!user.bookshelf) user.bookshelf = {};
  if (!user.bookshelf[bookId]) {
    user.bookshelf[bookId] = {
      status: 'reading',
      lastChapter: chapterIndex,
      lastParagraph: paragraphIndex,
      progressPct: progressPct
    };
  } else {
    const shelfItem = user.bookshelf[bookId];
    shelfItem.lastChapter = chapterIndex;
    shelfItem.lastParagraph = paragraphIndex;
    shelfItem.progressPct = Math.max(shelfItem.progressPct, progressPct);
    
    // Automatically flag completed if progress is 100%
    if (progressPct >= 100) {
      shelfItem.status = 'completed';
    } else if (shelfItem.status === 'want-to-read') {
      shelfItem.status = 'reading';
    }
  }

  updateCurrentUserInStorage(user);
}

// 3. STATS UTILITIES
export function getUserStats() {
  const user = getCurrentUser();
  if (!user) return { streak: 0, countReading: 0, countCompleted: 0, countWantToRead: 0 };

  const shelf = user.bookshelf || {};
  let countReading = 0;
  let countCompleted = 0;
  let countWantToRead = 0;

  Object.values(shelf).forEach(item => {
    if (item.status === 'reading') countReading++;
    else if (item.status === 'completed') countCompleted++;
    else if (item.status === 'want-to-read') countWantToRead++;
  });

  return {
    streak: user.stats?.streak || 1,
    countReading,
    countCompleted,
    countWantToRead,
    joinedDate: user.joinedDate
  };
}
