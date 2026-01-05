import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './components/shared/navbar/navbar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, OnDestroy {
  title = 'EventApp';

  private cursorEl!: HTMLElement | null;
  private moveHandler = (e: MouseEvent) => {
    if (!this.cursorEl) return;
    this.cursorEl.style.transform = `translate(${e.clientX - 10}px, ${e.clientY - 10}px)`;
  };

  private addHoverClasses = () => {
    const interactive = document.querySelectorAll('a, button, .nav-link');
    interactive.forEach(el => {
      el.addEventListener('mouseenter', this.hoverIn);
      el.addEventListener('mouseleave', this.hoverOut);
    });
  };

  private hoverIn = () => {
    if (this.cursorEl) this.cursorEl.classList.add('hover');
  };

  private hoverOut = () => {
    if (this.cursorEl) this.cursorEl.classList.remove('hover');
  };

  ngOnInit(): void {
    this.cursorEl = document.getElementById('cursor');
    window.addEventListener('mousemove', this.moveHandler);
    this.addHoverClasses();
  }

  ngOnDestroy(): void {
    window.removeEventListener('mousemove', this.moveHandler);
    const interactive = document.querySelectorAll('a, button, .nav-link');
    interactive.forEach(el => {
      el.removeEventListener('mouseenter', this.hoverIn);
      el.removeEventListener('mouseleave', this.hoverOut);
    });
  }
}
