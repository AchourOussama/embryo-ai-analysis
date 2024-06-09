import { Component, OnInit } from '@angular/core';
import { EmbryonService } from '../services/embryon.service';
import { HttpClient } from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';

interface EmbryoImageResult {
  image_name: string;
  image_path: string;
  segmented_image_path: string;
  predicted_class: string;
  predicted_probabilities:  any;
  suggested_value: string;
  note: string;
}


interface EmbryoFormData {
  image_path: string;
  value: string;
  note: string;
}

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.css']
})
export class ListComponent implements OnInit {
  analysisResults: EmbryoImageResult[] = [];
  error: string | null = null;
  notes: { [key: string]: string } = {};
  suggestedValues: string[] = ['poor', 'average', 'good'];
  selectedValues: { [key: string]: string } = {};
  isLoading: boolean = false;
  progress: number = 0;
  // predicted_probabilities: {
  //   bad: number;
  //   average: number;
  //   good: number;
  // }  | null=null;

  constructor(private embryonService: EmbryonService, private http: HttpClient, private toastr: ToastrService) { }

  ngOnInit(): void {
    this.isLoading = true;
    this.progress = 20; // Initial progress value
    
    this.embryonService.getEmbryoImagesAndResults().subscribe(
      (data) => {
        this.analysisResults = data;
        console.log(this.analysisResults)

        this.analysisResults=this.parseProbabilities(this.analysisResults)
        console.log(this.analysisResults)
        this.toastr.success('Embryo images and results loaded successfully!', 'Success');
        this.isLoading = false;
      },
      (error) => {
        this.error = 'Failed to load embryo images and results';
        this.toastr.error('Failed to load embryo images and results.', 'Error');
        console.error('Error fetching data', error);
        this.isLoading = false;
      });
    // Simulate progress update
    this.simulateProgress();
  }
  parseProbabilities(results: EmbryoImageResult[]): EmbryoImageResult[] {
    return results.map(result => {
      let formattedProbabilities = null; // Default value if parsing fails or if "No result found"
      if (result.predicted_probabilities !== "No result found") {
        try {
          const parsedProbabilities = JSON.parse(result.predicted_probabilities);
          formattedProbabilities = {
            bad: parsedProbabilities['bad'] ?? null,
            average: parsedProbabilities['average'] ?? null,
            good: parsedProbabilities['good'] ?? null
          };
        } catch (error) {
          console.error('Error parsing predicted probabilities:', error);
        }
      }
      return {
        ...result,
        predicted_probabilities: formattedProbabilities
      };
    });
  }
  
  
  

  getChartColor(key: string): string {
    // Define colors based on key
    const colorMap: { [key: string]: string } = {
      "bad": "#dc3545",
      "average": "#fd7e14",
      "good": "#28a745"
    };
    // Return color based on key
    return colorMap[key as keyof typeof colorMap];
  }

  simulateProgress() {
    const interval = setInterval(() => {
      if (this.isLoading && this.progress < 80) {
        this.progress += 10;
      } else {
        clearInterval(interval);
      }
    }, 500);
  }

  validateAndPostForm(embryo: EmbryoImageResult): void {
    this.embryonService.validateAndPostFormData(embryo, this.selectedValues[embryo.image_path], this.notes[embryo.image_path]);
  }
}