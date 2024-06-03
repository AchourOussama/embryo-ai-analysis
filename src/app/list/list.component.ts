import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent implements OnInit {
  analysisResults: any = null;
  notes: string = '';

  constructor() { }

  ngOnInit(): void {
    // Fetch the results and display them
    // This example assumes that the analysis results are stored in local storage
    this.analysisResults = JSON.parse(localStorage.getItem('analysisResults') || '{}');
  }
}
