import { Component, OnInit, HostListener, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { User } from '../../../models';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit, OnDestroy {
  currentUser: User | null = null;
  isScrolled = false;
  isMobileMenuOpen = false;
  isUserMenuOpen = false;

  private userSub?: Subscription;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.userSub = this.authService.currentUser$.subscribe((user: User | null) => {
      this.currentUser = user;
    });
  }

  ngOnDestroy(): void {
    this.userSub?.unsubscribe();
  }

  @HostListener('window:scroll', [])
  onWindowScroll(): void {
    this.isScrolled = window.scrollY > 20;
  }

  toggleMobileMenu(): void {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
    if (this.isMobileMenuOpen) {
      this.isUserMenuOpen = false; // ensure user menu closes when mobile opens
    }
  }

  closeMobileMenu(): void {
    this.isMobileMenuOpen = false;
    this.isUserMenuOpen = false; // also ensure user menu closes
  }

  toggleUserMenu(): void {
    this.isUserMenuOpen = !this.isUserMenuOpen;
    if (this.isUserMenuOpen) {
      this.isMobileMenuOpen = false; // avoid conflicts
    }
  }

  closeUserMenu(): void {
    this.isUserMenuOpen = false;
  }

  isAdmin(): boolean {
    return this.currentUser?.role === 'ADMIN';
  }

  logout(): void {
    this.authService.logout();
    this.closeMobileMenu();
    this.closeUserMenu();
    this.router.navigate(['/']);
  }
}
