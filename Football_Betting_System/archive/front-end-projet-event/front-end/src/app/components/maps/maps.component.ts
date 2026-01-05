import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EventService } from '../../services/event.service';
import { Event, EventFilter } from '../../models';
import { Router } from '@angular/router';

// Use Leaflet via CDN global
declare const L: any;

@Component({
  selector: 'app-maps',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './maps.component.html',
  styleUrls: ['./maps.component.css']
})
export class MapsComponent implements OnInit, OnDestroy {
  events: Event[] = [];
  filteredEvents: Event[] = [];
  loading = false;
  error: string | null = null;

  filters: EventFilter = {
    startDate: '',
    endDate: '',
  };

  private map: any;
  private markersLayer: any;

  constructor(private eventService: EventService, private router: Router) {}

  ngOnInit(): void {
    this.setDefaultDateRange();

    // Slight delay to ensure Leaflet assets are ready if loaded via CDN
    setTimeout(() => {
      this.initMap();
      this.loadEvents();
    }, 0);
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  get mapHeightPx(): string {
    const n = this.filteredEvents.length || 0;
    const height = Math.max(360, Math.min(700, 360 + n * 8));
    return `${height}px`;
  }

  applyFilters(): void {
    this.ensureValidRange();
    this.refreshFilteredEvents();
    this.renderMarkers();
  }

  clearFilters(): void {
    this.setDefaultDateRange();
    this.applyFilters();
  }

  private initMap(): void {
    if (this.map) return;

    // Default center (Paris) until we fit markers
    this.map = L.map('events-map', {
      zoomControl: true,
      scrollWheelZoom: true,
    }).setView([48.8566, 2.3522], 12);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);

    this.markersLayer = L.layerGroup().addTo(this.map);
  }

  private loadEvents(): void {
    this.loading = true;
    this.error = null;

    this.ensureValidRange();

    this.eventService.getPublishedEvents().subscribe({
      next: (events) => {
        this.events = events || [];
        this.refreshFilteredEvents();
        this.loading = false;
        this.renderMarkers();
      },
      error: () => {
        this.loading = false;
        this.error = 'Impossible de charger les événements.';
      }
    });
  }

  private renderMarkers(): void {
    if (!this.map || !this.markersLayer) return;

    this.markersLayer.clearLayers();

    const coords: [number, number][] = [];

    for (const ev of this.filteredEvents) {
      const lat = this.normalizeCoordinate(ev.location?.latitude);
      const lng = this.normalizeCoordinate(ev.location?.longitude);
      if (lat !== null && lng !== null) {
        const marker = L.marker([lat, lng], { icon: this.createMarkerIcon() });
        const title = ev.title || 'Événement';
        const date = ev.date ? new Date(ev.date).toLocaleDateString() : '';
        const place = ev.location?.name || ev.location?.city || '';
        const gmapsUrl = `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
        const detailUrl = ev.id ? `/events/${ev.id}` : '/events';

        const content = `
          <div class="map-popup">
            <div class="popup-meta">
              <div class="meta-title">${this.escapeHtml(title)}</div>
              <div class="meta-location">${this.escapeHtml(place)}</div>
              <div class="meta-date">${date}</div>
            </div>
            <div class="popup-actions">
              <a href="${detailUrl}" class="btn-view" data-event-id="${ev.id ?? ''}">Voir plus</a>
              <a href="${gmapsUrl}" target="_blank" rel="noopener" class="btn-open">Ouvrir sur Google Maps</a>
            </div>
          </div>
        `;

        marker.bindPopup(content, {
          closeButton: false,
          offset: [0, -12],
          className: 'lux-popup'
        });

        this.attachPopupInteractions(marker, ev);

        marker.addTo(this.markersLayer);
        coords.push([lat, lng]);
      }
    }

    // Fit map to markers
    if (coords.length === 1) {
      this.map.setView(coords[0], 12);
    } else if (coords.length > 1) {
      const bounds = L.latLngBounds(coords);
      this.map.fitBounds(bounds, { padding: [40, 40] });
    }

    // Trigger a resize to ensure proper rendering when container height changes
    setTimeout(() => this.map.invalidateSize(), 0);
  }

  private refreshFilteredEvents(): void {
    const start = this.filters.startDate ? new Date(this.filters.startDate) : null;
    const end = this.filters.endDate ? new Date(this.filters.endDate) : null;

    this.filteredEvents = this.events.filter(ev => {
      if (!ev.date) return false;
      const eventDate = new Date(ev.date);
      if (start && eventDate < start) return false;
      if (end && eventDate > end) return false;

      const lat = this.normalizeCoordinate(ev.location?.latitude);
      const lng = this.normalizeCoordinate(ev.location?.longitude);
      return lat !== null && lng !== null;
    });

    if (this.filteredEvents.length === 0) {
      this.error = 'Aucun événement disponible sur cette période.';
    } else {
      this.error = null;
    }
  }

  private normalizeCoordinate(value: number | string | undefined): number | null {
    if (value === undefined || value === null) {
      return null;
    }
    const numeric = typeof value === 'string' ? Number(value) : value;
    return isNaN(numeric) ? null : numeric;
  }

  private setDefaultDateRange(): void {
    const today = new Date();
    const nextYear = new Date(today);
    nextYear.setFullYear(today.getFullYear() + 1);
    this.filters.startDate = this.formatDate(today);
    this.filters.endDate = this.formatDate(nextYear);
  }

  private ensureValidRange(): void {
    if (this.filters.startDate && this.filters.endDate) {
      const start = new Date(this.filters.startDate);
      const end = new Date(this.filters.endDate);
      if (start > end) {
        const temp = this.filters.startDate;
        this.filters.startDate = this.filters.endDate;
        this.filters.endDate = temp;
      }
    } else if (!this.filters.startDate || !this.filters.endDate) {
      this.setDefaultDateRange();
    }
  }

  private formatDate(d: Date): string {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }

  private escapeHtml(input: string): string {
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  private createMarkerIcon(): any {
    return L.divIcon({
      className: 'map-marker-icon',
      html: '<span class="marker-ring"><span class="marker-core"></span></span>',
      iconSize: [30, 30],
      iconAnchor: [15, 28],
      popupAnchor: [0, -24]
    });
  }

  private attachPopupInteractions(marker: any, event: Event): void {
    marker.on('mouseover', () => {
      marker.__hovering = true;
      marker.openPopup();
    });

    marker.on('mouseout', () => {
      marker.__hovering = false;
      this.schedulePopupClose(marker);
    });

    marker.on('popupopen', () => {
      const popupEl = marker.getPopup()?.getElement();
      if (!popupEl) return;

      const viewBtn = popupEl.querySelector('.btn-view');
      if (viewBtn) {
        const handler = (clickEvt: MouseEvent) => {
          clickEvt.preventDefault();
          if (event.id) {
            this.router.navigate(['/events', event.id]);
          }
        };
        viewBtn.addEventListener('click', handler, { once: true });
      }

      popupEl.addEventListener('mouseenter', () => {
        marker.__hovering = true;
      });

      popupEl.addEventListener('mouseleave', () => {
        marker.__hovering = false;
        this.schedulePopupClose(marker);
      });
    });

    marker.on('popupclose', () => {
      marker.__hovering = false;
    });
  }

  private schedulePopupClose(marker: any): void {
    setTimeout(() => {
      if (!marker.__hovering) {
        marker.closePopup();
      }
    }, 120);
  }
}
