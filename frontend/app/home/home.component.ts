import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  constructor(private router: Router) {}

  onAnalyzeClick(): void {
    // Here you can also check if the user is logged in
    // And redirect accordingly
    this.router.navigate(['/analyse-embryon']);
  }
}
