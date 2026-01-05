import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { LocationService } from '../../../services/location.service';
import { User, Location } from '../../../models';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.css'
})
export class SignupComponent {
  user: Partial<User> = {
    name: '',
    email: '',
    password: ''
  };
  
  selectedLocationId: number | null = null;
  selectedCity: string | null = null;

  confirmPassword = '';
  locations: Location[] = [];
  uniqueCities: string[] = [];
  loading = false;
  error = '';

  constructor(
    private authService: AuthService,
    private locationService: LocationService,
    private router: Router
  ) {
    // Redirect if already logged in
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/']);
    }

    this.loadLocations();
  }

  private loadLocations(): void {
    this.locationService.getAllLocations().subscribe({
      next: (locations: Location[]) => {
        this.locations = locations;
        // Extract unique cities
        const citySet = new Set(locations.map(loc => loc.city));
        this.uniqueCities = Array.from(citySet).sort();
      },
      error: (error: any) => console.error('Error loading locations:', error)
    });
  }

  onSubmit(): void {
    if (!this.validateForm()) {
      return;
    }

    this.loading = true;
    this.error = '';

    // Find a location for the selected city (pick the first one if multiple exist)
    if (this.selectedCity) {
      const location = this.locations.find(loc => loc.city === this.selectedCity);
      if (location) {
        this.user.locationId = location.id;
      }
    }

    this.authService.register(this.user as User).subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (error: any) => {
        this.error = 'Erreur lors de l\'inscription. Veuillez réessayer.';
        this.loading = false;
      }
    });
  }

  private validateForm(): boolean {
    if (!this.user.name?.trim()) {
      this.error = 'Le nom est requis';
      return false;
    }

    if (!this.user.email?.trim()) {
      this.error = 'L\'email est requis';
      return false;
    }

    if (!this.isValidEmail(this.user.email)) {
      this.error = 'Format d\'email invalide';
      return false;
    }

    if (!this.user.password || this.user.password.length < 6) {
      this.error = 'Le mot de passe doit contenir au moins 6 caractères';
      return false;
    }

    if (this.user.password !== this.confirmPassword) {
      this.error = 'Les mots de passe ne correspondent pas';
      return false;
    }

    return true;
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}
