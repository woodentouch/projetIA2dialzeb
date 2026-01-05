import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Favorite } from '../models';

@Injectable({
  providedIn: 'root'
})
export class FavoriteService {
  private apiUrl = '/api/favorites';
  private favoritesSubject = new BehaviorSubject<Favorite[]>([]);
  public favorites$ = this.favoritesSubject.asObservable();

  constructor(private http: HttpClient) {}

  getUserFavorites(userId: number): Observable<Favorite[]> {
    return this.http.get<Favorite[]>(`${this.apiUrl}/user/${userId}`).pipe(
      tap(favorites => this.favoritesSubject.next(favorites))
    );
  }

  addToFavorites(userId: number, eventId: number): Observable<Favorite> {
    return this.http.post<Favorite>(this.apiUrl, { userId, eventId }).pipe(
      tap(newFavorite => {
        const currentFavorites = this.favoritesSubject.value;
        this.favoritesSubject.next([...currentFavorites, newFavorite]);
      })
    );
  }

  removeFromFavorites(favoriteId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${favoriteId}`).pipe(
      tap(() => {
        const currentFavorites = this.favoritesSubject.value;
        const updatedFavorites = currentFavorites.filter(fav => fav.id !== favoriteId);
        this.favoritesSubject.next(updatedFavorites);
      })
    );
  }

  isFavorite(userId: number, eventId: number): Observable<boolean> {
    return this.http.get<boolean>(`${this.apiUrl}/check/${userId}/${eventId}`);
  }

  toggleFavorite(userId: number, eventId: number): Observable<{ isFavorite: boolean; favorite?: Favorite }> {
    return this.http.post<{ isFavorite: boolean; favorite?: Favorite }>(`${this.apiUrl}/toggle`, {
      userId,
      eventId
    });
  }
}

