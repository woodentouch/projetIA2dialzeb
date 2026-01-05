/**
 * Event image placeholders by category
 */
export const EVENT_PLACEHOLDERS: { [key: string]: string } = {
  'Musique': 'https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=1200&q=80',
  'Festival': 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200&q=80',
  'Concert': 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=1200&q=80',
  'Théâtre': 'https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=1200&q=80',
  'Sport': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1200&q=80',
  'Art': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1200&q=80',
  'Danse': 'https://images.unsplash.com/photo-1508700929628-666bc8bd84ea?w=1200&q=80',
  'Humour': 'https://images.unsplash.com/photo-1527224857830-43a7acc85260?w=1200&q=80',
  'Cinéma': 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1200&q=80',
  'Exposition': 'https://images.unsplash.com/photo-1514905552197-0610a4d8fd73?w=1200&q=80',
  'Conférence': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&q=80',
  'Spectacle': 'https://images.unsplash.com/photo-1478147427282-58a87a120781?w=1200&q=80',
  'default': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&q=80'
};

/**
 * Get appropriate placeholder image for an event
 */
export function getEventPlaceholder(categoryName?: string): string {
  if (!categoryName) {
    return EVENT_PLACEHOLDERS['default'];
  }
  return EVENT_PLACEHOLDERS[categoryName] || EVENT_PLACEHOLDERS['default'];
}

/**
 * Handle image error by setting placeholder
 */
export function handleImageError(event: any, categoryName?: string): void {
  const imgElement = event.target as HTMLImageElement;
  imgElement.src = getEventPlaceholder(categoryName);
  imgElement.onerror = null; // Prevent infinite loop
}
