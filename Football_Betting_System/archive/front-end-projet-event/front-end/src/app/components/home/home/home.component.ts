import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { BettingService } from '../../../services/betting.service';
import { Event } from '../../../models';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  upcomingEvents: Event[] = [];
  loading = true;
  
  get displayEvents(): Event[] {
    return this.upcomingEvents.slice(0, 6);
  }

  constructor(
    private bettingService: BettingService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  private loadData(): void {
    this.loading = true;
    this.bettingService.getAllEvents().subscribe({
      next: (events) => {
        this.upcomingEvents = events || [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading events:', err);
        this.loading = false;
      }
    });
  }

  getEventImage(event: Event): string {
    return `https://via.placeholder.com/400x300?text=${event.team1}+vs+${event.team2}`;
  }

  onImageError(event: any, fallback?: string): void {
    if (event && event.target) {
      event.target.src = `https://via.placeholder.com/400x300?text=Football`;
    }
  }
}


    // Load featured events
    this.eventService.getFeaturedEvents().subscribe({
      next: (events: Event[]) => {
        this.featuredEvents = events.slice(0, 3);
      },
      error: (error: any) => console.error('Error loading featured events:', error)
    });

    // Load categories
    this.categoryService.getAllCategories().subscribe({
      next: (categories: Category[]) => {
        this.categories = categories.slice(0, 6);
      },
      error: (error: any) => console.error('Error loading categories:', error)
    });

    // Load upcoming events
    this.eventService.getUpcomingEvents(6).subscribe({
      next: (events: Event[]) => {
        this.upcomingEvents = events;
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Error loading upcoming events:', error);
        this.loading = false;
      }
    });
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      weekday: 'long',
      day: 'numeric',
      month: 'long'
    });
  }

  formatPrice(price: number): string {
    return new Intl.NumberFormat('fr-FR', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  }

  getCategoryEmoji(categoryName: string): string {
    const emojiMap: { [key: string]: string } = {
      'Musique': '🎵',
      'Festival': '🎪',
      'Concert': '🎤',
      'Théâtre': '🎭',
      'Sport': '⚽',
      'Art': '🎨',
      'Danse': '💃',
      'Humour': '😂',
      'Cinéma': '🎬',
      'Exposition': '🖼️',
      'Conférence': '🎤',
      'Spectacle': '🎪'
    };

    return emojiMap[categoryName] || '🎉';
  }

  trackByEventId(index: number, item: Event): number {
    return item?.id ?? index;
  }

  getEventImage(event: Event): string {
    return event.imageUrl || getEventPlaceholder(event.category?.name);
  }

  onImageError(event: any, categoryName?: string): void {
    handleImageError(event, categoryName);
  }
}
