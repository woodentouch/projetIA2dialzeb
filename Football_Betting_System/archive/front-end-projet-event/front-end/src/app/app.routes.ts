import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home/home.component';
import { EventsListComponent } from './components/events/events-list/events-list.component';
import { EventDetailComponent } from './components/events/event-detail/event-detail.component';
import { LoginComponent } from './components/auth/login/login.component';
import { SignupComponent } from './components/auth/signup/signup.component';
import { ProfileComponent } from './components/user/profile/profile.component';
import { FavoritesComponent } from './components/user/favorites/favorites.component';
import { AboutComponent } from './components/about/about.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'events', component: EventsListComponent },
  { path: 'events/:id', component: EventDetailComponent },
  { path: 'bets', component: FavoritesComponent }, // Reuse favorites component for bets
  { path: 'about', component: AboutComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: '**', redirectTo: '', pathMatch: 'full' }
];
