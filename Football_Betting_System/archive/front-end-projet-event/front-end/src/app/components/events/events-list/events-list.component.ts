import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { BettingService } from '../../../services/betting.service';
import { Event, Player } from '../../../models';

@Component({
  selector: 'app-events-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './events-list.component.html',
  styleUrls: ['./events-list.component.css', '../events-luxury.component.css']
})
export class EventsListComponent implements OnInit {
  events: Event[] = [];
  filteredEvents: Event[] = [];
  selectedEvent: Event | null = null;
  selectedPlayers: Player[] = [];
  
  loading = true;
  viewMode: 'grid' | 'list' = 'grid';
  
  searchTerm = '';

  constructor(
    private bettingService: BettingService
  ) {}

  ngOnInit(): void {
    this.loadEvents();
  }

  loadEvents(): void {
    this.loading = true;
    this.bettingService.getAllEvents().subscribe({
      next: (events) => {
        this.events = events || [];
        this.filterEvents();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading events:', error);
        this.loading = false;
      }
    });
  }

  filterEvents(): void {
    this.filteredEvents = this.events.filter(event => {
      const searchLower = this.searchTerm.toLowerCase();
      return (
        event.team1.toLowerCase().includes(searchLower) ||
        event.team2.toLowerCase().includes(searchLower)
      );
    });
  }

  onSearchChange(): void {
    this.filterEvents();
  }

  selectEvent(event: Event): void {
    this.selectedEvent = event;
    if (event.id) {
      this.bettingService.getPlayersByEvent(event.id).subscribe({
        next: (players) => {
          this.selectedPlayers = players || [];
        },
        error: (error) => {
          console.error('Error loading players:', error);
        }
      });
    }
  }

  getEventImage(event: Event): string {
    return `https://via.placeholder.com/400x300?text=${event.team1}+vs+${event.team2}`;
  }

  onImageError(event: any): void {
    if (event && event.target) {
      event.target.src = 'https://via.placeholder.com/400x300?text=Football';
    }
  }
}
      }
    });

    this.loadInitialData();
  }

  private loadUserFavorites(userId: number): void {
    this.favoriteService.getUserFavorites(userId).subscribe({
      next: (favorites) => {
        const favoriteEventIds = favorites.map(f => f.eventId);
        this.events.forEach(event => {
          if (event.id) {
            event.isFavorite = favoriteEventIds.includes(event.id);
          }
        });
        this.applyClientSideFilters();
      },
      error: (error) => console.error('Error loading favorites:', error)
    });
  }

  private loadInitialData(): void {
    this.loading = true;

    this.categoryService.getAllCategories().subscribe({
      next: (categories: Category[]) => {
        this.categories = categories;
      },
      error: (error: any) => console.error('Error loading categories:', error)
    });

    this.locationService.getUniqueCities().subscribe({
      next: (cities: string[]) => {
        this.uniqueCities = cities;
      },
      error: (error: any) => console.error('Error loading cities:', error)
    });

    this.loadEvents();
  }

  loadEvents(): void {
    this.loading = true;
    
    this.eventService.getPublishedEvents().subscribe({
      next: (events: Event[]) => {
        this.events = events;
        if (this.currentUser && this.currentUser.id) {
          this.loadUserFavorites(this.currentUser.id);
        } else {
          this.applyClientSideFilters();
        }
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Error loading events:', error);
        this.loading = false;
      }
    });
  }

  private applyClientSideFilters(): void {
    let filtered = [...this.events];

    if (this.filters.search) {
      const searchLower = this.filters.search.toLowerCase();
      filtered = filtered.filter(event =>
        event.title?.toLowerCase().includes(searchLower) ||
        event.description?.toLowerCase().includes(searchLower) ||
        event.location?.city?.toLowerCase().includes(searchLower)
      );
    }

    if (this.filters.categoryId) {
      filtered = filtered.filter(event =>
        event.category?.id === Number(this.filters.categoryId)
      );
    }

    if (this.filters.city) {
      filtered = filtered.filter(event =>
        event.location?.city === this.filters.city
      );
    }

    if (this.filters.minPrice !== undefined && this.filters.minPrice !== null) {
      filtered = filtered.filter(event =>
        event.price !== undefined && event.price >= this.filters.minPrice!
      );
    }
    if (this.filters.maxPrice !== undefined && this.filters.maxPrice !== null) {
      filtered = filtered.filter(event =>
        event.price !== undefined && event.price <= this.filters.maxPrice!
      );
    }

    if (this.filters.startDate) {
      const filterDate = new Date(this.filters.startDate);
      filtered = filtered.filter(event => {
        if (!event.date) return false;
        const eventDate = new Date(event.date);
        return eventDate >= filterDate;
      });
    }

    filtered.sort((a, b) => {
      const order = this.filters.sortOrder === 'desc' ? -1 : 1;
      
      if (this.filters.sortBy === 'date') {
        const dateA = a.date ? new Date(a.date).getTime() : 0;
        const dateB = b.date ? new Date(b.date).getTime() : 0;
        return (dateA - dateB) * order;
      } else if (this.filters.sortBy === 'price') {
        return ((a.price || 0) - (b.price || 0)) * order;
      } else if (this.filters.sortBy === 'popularity') {
        return ((a.viewCount || 0) - (b.viewCount || 0)) * order;
      } else if (this.filters.sortBy === 'relevance') {
        if (this.filters.search) {
          const searchLower = this.filters.search.toLowerCase();
          const aInTitle = a.title?.toLowerCase().includes(searchLower) ? 1 : 0;
          const bInTitle = b.title?.toLowerCase().includes(searchLower) ? 1 : 0;
          return (bInTitle - aInTitle) * order;
        }
      }
      return 0;
    });

    this.totalElements = filtered.length;
    this.totalPages = Math.ceil(filtered.length / this.pageSize);
    const start = this.currentPage * this.pageSize;
    const end = start + this.pageSize;
    this.filteredEvents = filtered.slice(start, end);
  }

  applyFilters(): void {
    this.currentPage = 0;
    this.applyClientSideFilters();
  }

  clearFilters(): void {
    this.filters = {
      search: '',
      categoryId: undefined,
      city: '',
      minPrice: undefined,
      maxPrice: undefined,
      startDate: '',
      sortBy: 'date',
      sortOrder: 'asc'
    };
    this.applyFilters();
  }

  toggleFilters(): void {
    this.showFilters = !this.showFilters;
  }

  toggleViewMode(): void {
    this.viewMode = this.viewMode === 'grid' ? 'list' : 'grid';
  }

  onFavoriteToggle(event: Event): void {
    if (!this.currentUser || !event.id) return;

    this.favoriteService.toggleFavorite(this.currentUser.id!, event.id).subscribe({
      next: (result: any) => {
        (event as any).isFavorite = result.isFavorite;
      },
      error: (error: any) => console.error('Error toggling favorite:', error)
    });
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
    });
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  }

  getEventStatus(event: Event): string {
    const now = new Date();
    const eventDate = new Date(event.date || '');

    if (eventDate < now) return 'passed';
    if (eventDate.toDateString() === now.toDateString()) return 'today';
    return 'upcoming';
  }

  trackByEventId(index: number, event: Event): number {
    return event.id!;
  }

  loadMore(): void {
    if (this.currentPage < this.totalPages - 1) {
      this.currentPage++;
      this.applyClientSideFilters();
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
  }

  getEventImage(event: Event): string {
    return event.imageUrl || getEventPlaceholder(event.category?.name);
  }

  onImageError(event: any, categoryName?: string): void {
    handleImageError(event, categoryName);
  }
}
