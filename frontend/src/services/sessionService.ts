import 'react-native-get-random-values'; // Must be imported before uuid
import AsyncStorage from '@react-native-async-storage/async-storage';
import { v4 as uuidv4 } from 'uuid';

const SESSION_ID_KEY = 'app_session_id';
const USER_ID_KEY = 'app_user_id';

export class SessionService {
  private static instance: SessionService;
  private sessionId: string | null = null;
  private userId: string | null = null;

  private constructor() {}

  public static getInstance(): SessionService {
    if (!SessionService.instance) {
      SessionService.instance = new SessionService();
    }
    return SessionService.instance;
  }

  /**
   * Initialize session on app startup
   * Generates new session ID and persists user ID if it doesn't exist
   */
  public async initializeSession(): Promise<void> {
    try {
      // Always generate a new session ID on app startup
      this.sessionId = uuidv4();
      await AsyncStorage.setItem(SESSION_ID_KEY, this.sessionId);

      // Get or create user ID (persistent across sessions)
      this.userId = await AsyncStorage.getItem(USER_ID_KEY);
      if (!this.userId) {
        this.userId = uuidv4();
        await AsyncStorage.setItem(USER_ID_KEY, this.userId);
      }

      console.log('Session initialized:', {
        sessionId: this.sessionId,
        userId: this.userId,
      });
    } catch (error) {
      console.error('Failed to initialize session:', error);
      // Fallback to in-memory values
      this.sessionId = uuidv4();
      this.userId = uuidv4();
    }
  }

  /**
   * Get current session ID
   */
  public async getSessionId(): Promise<string> {
    if (!this.sessionId) {
      // Try to get from storage first
      this.sessionId = await AsyncStorage.getItem(SESSION_ID_KEY);
      
      // If still null, initialize session
      if (!this.sessionId) {
        await this.initializeSession();
      }
    }
    return this.sessionId!;
  }

  /**
   * Get current user ID
   */
  public async getUserId(): Promise<string> {
    if (!this.userId) {
      // Try to get from storage first
      this.userId = await AsyncStorage.getItem(USER_ID_KEY);
      
      // If still null, initialize session
      if (!this.userId) {
        await this.initializeSession();
      }
    }
    return this.userId!;
  }

  /**
   * Start a new session (useful for logout/login scenarios)
   */
  public async startNewSession(): Promise<void> {
    this.sessionId = uuidv4();
    await AsyncStorage.setItem(SESSION_ID_KEY, this.sessionId);
    console.log('New session started:', this.sessionId);
  }

  /**
   * Clear session data (useful for logout)
   */
  public async clearSession(): Promise<void> {
    this.sessionId = null;
    this.userId = null;
    await AsyncStorage.multiRemove([SESSION_ID_KEY, USER_ID_KEY]);
    console.log('Session cleared');
  }
}

export const sessionService = SessionService.getInstance(); 