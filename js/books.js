// Dynamic book catalog loading and metadata retrieval

export let BOOKS = [];

export async function loadCatalog() {
  if (BOOKS.length > 0) return BOOKS;
  try {
    const response = await fetch('books/catalog.json', { cache: 'no-cache' });
    BOOKS = await response.json();
    return BOOKS;
  } catch (err) {
    console.error('Failed to load books catalog:', err);
    return [];
  }
}

export async function getBookDetails(bookId) {
  try {
    const response = await fetch(`books/${bookId}/details.json`, { cache: 'no-cache' });
    return await response.json();
  } catch (err) {
    console.error(`Failed to load details for book ${bookId}:`, err);
    return null;
  }
}
