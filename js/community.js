import { getCurrentUser } from './auth.js';
import { BOOKS } from './books.js';

// Channels configuration
export const CHANNELS = [
  { id: 'general', name: 'general-chat', desc: 'Chat about books, life, and reading habits.' },
  { id: 'book-club', name: 'classics-club', desc: 'Dedicated discussion for classics and public domain masterpieces.' },
  { id: 'sci-fi-lounge', name: 'sci-fi-lounge', desc: 'Talk about time machines, space, and futuristic fantasy.' }
];

// Seed messages for when the app runs for the first time
const MOCK_MESSAGES = {
  'general': [
    { id: 1, sender: 'BookWorm99', nameInitials: 'BW', message: 'Hello readers! Just registered on Bakbak.store. Love the cosmic layout!', timestamp: '2 hours ago', isSystem: false },
    { id: 2, sender: 'KafkaEsque', nameInitials: 'KE', message: 'Welcome! Have you started reading anything from the catalog yet?', timestamp: '1 hour ago', isSystem: false },
    { id: 3, sender: 'BookWorm99', nameInitials: 'BW', message: 'Yeah, just started Alice in Wonderland. The custom reader is really comfortable on my screen.', timestamp: '45 mins ago', isSystem: false }
  ],
  'book-club': [
    { id: 1, sender: 'JaneAustenFan', nameInitials: 'JA', message: 'Does anyone else feel bad for Gregor Samsa in The Metamorphosis? It is so tragic yet beautifully written.', timestamp: '3 hours ago', isSystem: false },
    { id: 2, sender: 'Philosopher_101', nameInitials: 'P1', message: 'Absolutely. It is the ultimate metaphor for isolation and societal burden.', timestamp: '2 hours ago', isSystem: false }
  ],
  'sci-fi-lounge': [
    { id: 1, sender: 'DrTimeTravel', nameInitials: 'DT', message: 'H.G. Wells really pioneered the concept of time travel. The description of the Morlocks is chilling.', timestamp: 'Yesterday', isSystem: false }
  ]
};

// Seed reviews
const MOCK_REVIEWS = [
  { id: 1, userName: 'AliceFinder', userInitials: 'AF', bookId: 'alice-in-wonderland', bookTitle: "Alice's Adventures in Wonderland", rating: 5, comment: 'A timeless trip down memory lane! Highly recommend reading Chapter 1 in Sepia mode.', timestamp: '3 hours ago' },
  { id: 2, userName: 'SamsaReader', userInitials: 'SR', bookId: 'the-metamorphosis', bookTitle: 'The Metamorphosis', rating: 4, comment: 'Incredibly deep. Kafka writes isolation so well it makes you claustrophobic.', timestamp: '5 hours ago' }
];

// Active State
let activeChannel = 'general';

function getStorageMessages() {
  const current = localStorage.getItem('bakbak_chat_messages');
  if (!current) {
    localStorage.setItem('bakbak_chat_messages', JSON.stringify(MOCK_MESSAGES));
    return MOCK_MESSAGES;
  }
  return JSON.parse(current);
}

function getStorageReviews() {
  const current = localStorage.getItem('bakbak_reviews');
  if (!current) {
    localStorage.setItem('bakbak_reviews', JSON.stringify(MOCK_REVIEWS));
    return MOCK_REVIEWS;
  }
  return JSON.parse(current);
}

// COMMUNITY PUBLIC METHODS
export function getActiveChannel() {
  return activeChannel;
}

export function setActiveChannel(channelId) {
  activeChannel = channelId;
}

export function getMessagesForChannel(channelId) {
  const messages = getStorageMessages();
  return messages[channelId] || [];
}

export function getReviews() {
  return getStorageReviews();
}

export function addMessageToChannel(channelId, text) {
  const user = getCurrentUser();
  const messages = getStorageMessages();

  if (!messages[channelId]) messages[channelId] = [];

  const newMessage = {
    id: 'msg_' + Date.now(),
    sender: user ? user.name : 'Guest Reader',
    nameInitials: user ? user.name.slice(0, 2).toUpperCase() : 'GR',
    message: text,
    timestamp: 'Just now',
    isMyMsg: !!user // if true, CSS can style it as sender
  };

  messages[channelId].push(newMessage);
  localStorage.setItem('bakbak_chat_messages', JSON.stringify(messages));
  
  // Return the new message so UI can update instantly
  return newMessage;
}

export function addReview(bookId, rating, comment) {
  const user = getCurrentUser();
  const reviews = getStorageReviews();
  const book = BOOKS.find(b => b.id === bookId);
  
  if (!book) throw new Error('Book not found.');

  const newReview = {
    id: 'rev_' + Date.now(),
    userName: user ? user.name : 'Anonymous Reader',
    userInitials: user ? user.name.slice(0, 2).toUpperCase() : 'AR',
    bookId: bookId,
    bookTitle: book.title,
    rating: parseInt(rating),
    comment: comment,
    timestamp: 'Just now'
  };

  reviews.unshift(newReview); // add to beginning
  localStorage.setItem('bakbak_reviews', JSON.stringify(reviews));
  return newReview;
}

// Bot reply simulation to make the site feel alive!
const BOT_REPLIES = [
  "That's a really interesting point! Welcome to the club.",
  "I was thinking the exact same thing about that chapter.",
  "Interesting. What do you think of the author's writing style?",
  "Awesome! Let me know when you finish reading the book.",
  "Bakbak is definitely the right place to chat about this. Glad to have you here!"
];

const BOT_NAMES = ['LibrarianBot', 'CosmicReader', 'BookWizard'];

export function triggerBotReply(channelId, onReplyCallback) {
  setTimeout(() => {
    const messages = getStorageMessages();
    const botReplyText = BOT_REPLIES[Math.floor(Math.random() * BOT_REPLIES.length)];
    const botName = BOT_NAMES[Math.floor(Math.random() * BOT_NAMES.length)];
    
    const botMessage = {
      id: 'msg_' + Date.now(),
      sender: botName,
      nameInitials: botName.slice(0, 2).toUpperCase(),
      message: botReplyText,
      timestamp: 'Just now',
      isMyMsg: false
    };

    messages[channelId].push(botMessage);
    localStorage.setItem('bakbak_chat_messages', JSON.stringify(messages));
    
    onReplyCallback(botMessage);
  }, 1500); // 1.5 seconds delay
}
