// Football Betting Models
export interface Event {
  id?: number;
  team1: string;
  team2: string;
  date?: string;
  status?: string;
  odds_team1?: number;
  odds_draw?: number;
  odds_team2?: number;
  result?: string;
  imageUrl?: string;
  featured?: boolean;
  isFavorite?: boolean;
}

export interface Player {
  id?: number;
  event_id?: number;
  name: string;
  team: string;
  number?: number;
  position?: string;
  photo_url?: string;
  attack?: number;
  defense?: number;
  speed?: number;
  strength?: number;
  dexterity?: number;
  stamina?: number;
}

export interface Bet {
  id?: number;
  event_id: number;
  user_id?: string;
  bet_type: string;
  amount: number;
  odds: number;
  status?: string;
  created_at?: string;
  result_at?: string;
}

export interface Category {
  id?: number;
  name: string;
  description?: string;
  color?: string;
}

export interface Location {
  id?: number;
  name: string;
  city: string;
  country?: string;
}

export interface User {
  id?: number;
  name: string;
  email: string;
  password?: string;
  avatarUrl?: string;
  role?: 'USER' | 'ADMIN';
}

export interface EventFilter {
  search?: string;
  status?: string;
  sortBy?: 'date' | 'odds' | 'popularity';
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
  first: boolean;
  last: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: string[];
}

export type EventStatus = 'draft' | 'published' | 'cancelled' | 'sold_out';
export type UserRole = 'user' | 'admin' | 'organizer';
