import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { EventService, CategoryService, LocationService, AuthService } from '../../../services';
import { Event, Category, Location } from '../../../models';

@Component({
  selector: 'app-create-event',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-event.component.html',
  styleUrls: ['./create-event.component.css']
})
export class CreateEventComponent implements OnInit {
  event: Partial<Event> = {
    title: '',
    description: '',
    date: '',
    price: 0,
    categoryId: undefined,
    locationId: undefined,
    imageUrl: '',
    link: ''
  };

  categories: Category[] = [];
  locations: Location[] = [];
  loading = false;
  error = '';
  success = false;

  constructor(
    private eventService: EventService,
    private categoryService: CategoryService,
    private locationService: LocationService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser || currentUser.role !== 'ADMIN') {
      this.router.navigate(['/']);
      return;
    }

    this.loadCategories();
    this.loadLocations();
  }

  loadCategories(): void {
    this.categoryService.getAllCategories().subscribe({
      next: (categories) => {
        this.categories = categories;
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  loadLocations(): void {
    this.locationService.getAllLocations().subscribe({
      next: (locations) => {
        this.locations = locations;
      },
      error: (error) => {
        console.error('Error loading locations:', error);
      }
    });
  }

  onSubmit(): void {
    this.error = '';
    this.loading = true;

    if (!this.event.title || !this.event.description || !this.event.date || 
        !this.event.categoryId || !this.event.locationId) {
      this.error = 'Veuillez remplir tous les champs obligatoires';
      this.loading = false;
      return;
    }

    const eventData = {
      ...this.event,
      date: this.event.date?.split('T')[0],
      time: this.event.date?.includes('T') ? this.event.date.split('T')[1] : undefined,
      published: true,
      viewCount: 0
    };

    this.eventService.createEvent(eventData as Event).subscribe({
      next: (createdEvent) => {
        this.success = true;
        this.loading = false;
        setTimeout(() => {
          this.router.navigate(['/events', createdEvent.id]);
        }, 2000);
      },
      error: (error) => {
        console.error('Error creating event:', error);
        this.error = error.error?.message || 'Erreur lors de la création de l\'événement';
        this.loading = false;
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/events']);
  }
}
