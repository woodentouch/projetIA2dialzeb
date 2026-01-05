import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Location } from '../models';

@Injectable({
  providedIn: 'root'
})
export class LocationService {
  private apiUrl = '/api/locations';
  private locationsSubject = new BehaviorSubject<Location[]>([]);
  public locations$ = this.locationsSubject.asObservable();

  constructor(private http: HttpClient) {}

  getAllLocations(): Observable<Location[]> {
    return this.http.get<Location[]>(this.apiUrl).pipe(
      tap(locations => this.locationsSubject.next(locations))
    );
  }

  getLocationById(id: number): Observable<Location> {
    return this.http.get<Location>(`${this.apiUrl}/${id}`);
  }

  getLocationsByCity(city: string): Observable<Location[]> {
    const params = new HttpParams().set('city', city);
    return this.http.get<Location[]>(`${this.apiUrl}/by-city`, { params });
  }

  searchLocations(query: string): Observable<Location[]> {
    const params = new HttpParams().set('q', query);
    return this.http.get<Location[]>(`${this.apiUrl}/search`, { params });
  }

  createLocation(location: Location): Observable<Location> {
    return this.http.post<Location>(this.apiUrl, location);
  }

  updateLocation(id: number, location: Location): Observable<Location> {
    return this.http.put<Location>(`${this.apiUrl}/${id}`, location);
  }

  deleteLocation(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  getUniqueCities(): Observable<string[]> {
    return this.http.get<string[]>(`${this.apiUrl}/cities`);
  }
}

