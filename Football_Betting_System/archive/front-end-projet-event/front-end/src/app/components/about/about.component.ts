import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

interface ValueCard {
  title: string;
  description: string;
}

interface TeamMember {
  name: string;
  role: string;
  bio: string;
  imageUrl: string;
}

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent {
  readonly introHighlight = 'Événements pensés comme des expériences totales';

  values: ValueCard[] = [
    {
      title: 'Curation exigeante',
      description: 'Chaque événement est sélectionné pour son impact émotionnel, son esthétique et sa capacité à offrir un moment rare.'
    },
    {
      title: 'Design premium',
      description: 'Une expérience digitale pensée comme un écrin : interfaces éthérées, visuels immersifs, parcours sans friction.'
    },
    {
      title: 'Human first',
      description: 'Nous croyons aux rencontres. Notre équipe accompagne organisateurs et communautés pour créer du lien.'
    }
  ];

  team: TeamMember[] = [
    {
      name: 'Ali FASSY FEHRY',
      role: 'Head of Partnerships',
      bio: 'À la croisée du business et de la culture, Ali tisse les alliances qui donnent accès aux scènes les plus convoitées.',
      imageUrl: 'https://cdn2.cvdesignr.com/u/users/656c8a506e67f/1e18c76d1f2d0768f7473b55593b5ff6c9dca492.png'
    },
    {
      name: 'Abdellah SOFI',
      role: 'Product Lead',
      bio: 'Ingénieur produit passionné, Abdellah orchestre la plateforme EventApp pour qu’elle reste fluide, fiable et élégante.',
      imageUrl: 'https://cdn2.cvdesignr.com/u/users/656c8a506e67f/a53c5747458360a99e2607d5306af55386b3b0fd.jpeg'
    }
  ];

  stats = [
    { label: 'Événements accompagnés', value: '120+' },
    { label: 'Partenaires culturels', value: '45' },
    { label: 'Taux de satisfaction', value: '4.9 / 5' }
  ];
}
