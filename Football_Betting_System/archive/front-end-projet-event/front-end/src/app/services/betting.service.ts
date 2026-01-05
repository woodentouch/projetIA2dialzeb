import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { Event, Player, Bet, EventFilter } from '../models';

@Injectable({
  providedIn: 'root'
})
export class BettingService {
  private apiUrl = 'http://localhost:8000/api';
  private eventsSubject = new BehaviorSubject<Event[]>([]);
  public events$ = this.eventsSubject.asObservable();

  constructor(private http: HttpClient) {}

  getAllEvents(filter?: EventFilter): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.apiUrl}/events`);
  }

  getEventById(id: number): Observable<Event> {
    return this.http.get<Event>(`${this.apiUrl}/events/${id}`);
  }

  getPlayersByEvent(eventId: number): Observable<Player[]> {
    return this.http.get<Player[]>(`${this.apiUrl}/events/${eventId}/players`);
  }

  // Betting related endpoints
  getAllBets(): Observable<Bet[]> {
    return this.http.get<Bet[]>(`${this.apiUrl}/bets`);
  }

  getUserBets(): Observable<Bet[]> {
    return this.http.get<Bet[]>(`${this.apiUrl}/my-bets`);
  }

  getBetById(id: number): Observable<Bet> {
    return this.http.get<Bet>(`${this.apiUrl}/bets/${id}`);
  }

  placeBet(bet: Bet): Observable<Bet> {
    return this.http.post<Bet>(`${this.apiUrl}/bets`, bet);
  }

  seedTestData(): Observable<any> {
    return this.http.post(`${this.apiUrl}/seed-data`, {});
  }

  loadEvents(): void {
    this.getAllEvents().pipe(
      tap(events => this.eventsSubject.next(events))
    ).subscribe();
  }
}
