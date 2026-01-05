import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { FavoriteService } from '../../../services/favorite.service';
import { EventService } from '../../../services/event.service';
import { User, Event, Favorite } from '../../../models';

@Component({
  selector: 'app-favorites',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './favorites.component.html',
  styleUrls: ['./favorites.component.css']
})
export class FavoritesComponent implements OnInit {
  user: User | null = null;
  favorites: Favorite[] = [];
  events: Event[] = [];
  loading = true;

  constructor(
    private authService: AuthService,
    private favoriteService: FavoriteService,
    private eventService: EventService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    if (!this.user || !this.user.id) {
      this.router.navigate(['/login']);
      return;
    }

    this.loadFavorites();
  }

  loadFavorites(): void {
    if (!this.user || !this.user.id) return;

    this.loading = true;
    this.favoriteService.getUserFavorites(this.user.id).subscribe({
      next: (favorites) => {
        this.favorites = favorites;
        this.loadFavoriteEvents();
      },
      error: (error) => {
        console.error('Error loading favorites:', error);
        this.loading = false;
      }
    });
  }

  loadFavoriteEvents(): void {
    const eventIds = this.favorites.map(f => f.eventId);
    if (eventIds.length === 0) {
      this.loading = false;
      return;
    }

    this.eventService.getPublishedEvents().subscribe({
      next: (events) => {
        this.events = events.filter((e: Event) => e.id && eventIds.includes(e.id));
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading events:', error);
        this.loading = false;
      }
    });
  }

  removeFromFavorites(event: Event): void {
    if (!event.id) return;

    const favorite = this.favorites.find(f => f.eventId === event.id);
    if (!favorite || !favorite.id) return;

    this.favoriteService.removeFromFavorites(favorite.id).subscribe({
      next: () => {
        this.events = this.events.filter(e => e.id !== event.id);
        this.favorites = this.favorites.filter(f => f.id !== favorite.id);
      },
      error: (error) => {
        console.error('Error removing favorite:', error);
      }
    });
  }

  viewEventDetails(eventId?: number): void {
    if (eventId) {
      this.router.navigate(['/events', eventId]);
    }
  }

  formatDate(dateString?: string): string {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  }

  formatPrice(price?: number): string {
    if (!price) return 'Gratuit';
    return `${price}€`;
  }
}
