import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { EventService, CategoryService, LocationService, AuthService } from '../../../services';
import { Event, Category, Location } from '../../../models';

@Component({
  selector: 'app-edit-event',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-event.component.html',
  styleUrls: ['./edit-event.component.css']
})
export class EditEventComponent implements OnInit {
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
  loadingEvent = true;
  error = '';
  success = false;
  eventId: number = 0;

  constructor(
    private route: ActivatedRoute,
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

    this.route.params.subscribe(params => {
      this.eventId = +params['id'];
      if (this.eventId) {
        this.loadEvent(this.eventId);
      }
    });

    this.loadCategories();
    this.loadLocations();
  }

  loadEvent(id: number): void {
    this.loadingEvent = true;
    this.eventService.getEventById(id).subscribe({
      next: (event) => {
        if (event.date) {
          const dateObj = new Date(event.date);
          const year = dateObj.getFullYear();
          const month = String(dateObj.getMonth() + 1).padStart(2, '0');
          const day = String(dateObj.getDate()).padStart(2, '0');
          const hours = event.time ? event.time.split(':')[0] : '00';
          const minutes = event.time ? event.time.split(':')[1] : '00';
          this.event.date = `${year}-${month}-${day}T${hours}:${minutes}`;
        }
        
        this.event = {
          ...event,
          date: this.event.date
        };
        this.loadingEvent = false;
      },
      error: (error) => {
        console.error('Error loading event:', error);
        this.error = 'Erreur lors du chargement de l\'événement';
        this.loadingEvent = false;
      }
    });
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
      id: this.eventId,
      date: this.event.date?.split('T')[0],
      time: this.event.date?.includes('T') ? this.event.date.split('T')[1] : undefined,
      published: true
    };

    this.eventService.updateEvent(this.eventId, eventData as Event).subscribe({
      next: (updatedEvent) => {
        this.success = true;
        this.loading = false;
        setTimeout(() => {
          this.router.navigate(['/events', updatedEvent.id]);
        }, 2000);
      },
      error: (error) => {
        console.error('Error updating event:', error);
        this.error = error.error?.message || 'Erreur lors de la modification de l\'événement';
        this.loading = false;
      }
    });
  }

  cancel(): void {
    this.router.navigate(['/events', this.eventId]);
  }
}
