import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { Event, EventFilter, PaginatedResponse, ApiResponse } from '../models';

@Injectable({
  providedIn: 'root'
})
export class EventService {
  private apiUrl = '/api/events';
  private eventsSubject = new BehaviorSubject<Event[]>([]);
  public events$ = this.eventsSubject.asObservable();

  constructor(private http: HttpClient) {}

  getAllEvents(filter?: EventFilter): Observable<PaginatedResponse<Event>> {
    let params = new HttpParams();

    if (filter) {
      Object.keys(filter).forEach(key => {
        const value = filter[key as keyof EventFilter];
        if (value !== undefined && value !== null && value !== '') {
          params = params.set(key, value.toString());
        }
      });
    }

    return this.http.get<PaginatedResponse<Event>>(this.apiUrl, { params });
  }

  getPublishedEvents(): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.apiUrl}/published`).pipe(
      tap(events => this.eventsSubject.next(events))
    );
  }

  getFeaturedEvents(): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.apiUrl}/featured`);
  }

  getEventById(id: number): Observable<Event> {
    return this.http.get<Event>(`${this.apiUrl}/${id}`);
  }

  getEventsByCategory(categoryId: number): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.apiUrl}/category/${categoryId}`);
  }

  getEventsByPeriod(startDate: string, endDate: string): Observable<Event[]> {
    const params = new HttpParams()
      .set('startDate', startDate)
      .set('endDate', endDate);
    return this.http.get<Event[]>(`${this.apiUrl}/period`, { params });
  }

  getEventsByLocation(locationId: number): Observable<Event[]> {
    return this.http.get<Event[]>(`${this.apiUrl}/location/${locationId}`);
  }

  searchEvents(query: string): Observable<Event[]> {
    const params = new HttpParams().set('q', query);
    return this.http.get<Event[]>(`${this.apiUrl}/search`, { params });
  }

  createEvent(event: Event): Observable<Event> {
    return this.http.post<Event>(this.apiUrl, event);
  }

  updateEvent(id: number, event: Event): Observable<Event> {
    return this.http.put<Event>(`${this.apiUrl}/${id}`, event);
  }

  deleteEvent(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  incrementViewCount(id: number): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/${id}/view`, {});
  }

  getUpcomingEvents(limit: number = 10): Observable<Event[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<Event[]>(`${this.apiUrl}/upcoming`, { params });
  }

  getEventsByCity(city: string): Observable<Event[]> {
    const params = new HttpParams().set('city', city);
    return this.http.get<Event[]>(`${this.apiUrl}/by-city`, { params });
  }
}

