import { Component } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { EmbryoService } from '../embryo.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-analyse-embryon',
  templateUrl: './analyse-embryon.component.html',
  styleUrls: ['./analyse-embryon.component.css']
})
export class AnalyseEmbryonComponent {
  selectedFile: File | null = null;
  fileErrorMsg: string = '';
  // analysisResults: any = null;

  constructor(private embryoService: EmbryoService,private toastr: ToastrService) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (validTypes.includes(file.type)) {
        this.selectedFile = file;
      } else {
        this.toastr.error('Unsupported file format. Please upload a PDF or DOCX file.', 'Error!');
        this.selectedFile = null;
      }
    }
  }

  onSubmit(): void {
    if ( !this.selectedFile) {
      this.toastr.error('Please ensure all fields are filled correctly.', 'Missing Information!');
      return;
    }

    const formData = new FormData();
    formData.append('image', this.selectedFile);

    this.embryoService.analyzeEmbryo(formData).subscribe({
      next: (response) => {
        console.log("Received data:", response);
        // this.analysisResults = response;
        this.toastr.success('Your embryo has been successfully analyzed!', 'Success');
      },
      error: (error) => {
        console.error("Error:", error);
        this.toastr.error('An error occurred while analyzing your embryo.', 'Error');
      }
    });
  }

}


