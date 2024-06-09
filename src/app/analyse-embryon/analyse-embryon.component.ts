import { Component } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
// import { EmbryoService } from '../embryo.service';
import { FormsModule } from '@angular/forms';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {API_URL} from '../env'
import { FileUploadServiceService } from '../services/fileUpload/file-upload-service.service';

@Component({
  selector: 'app-analyse-embryon',
  templateUrl: './analyse-embryon.component.html',
  styleUrls: ['./analyse-embryon.component.css']
})

export class AnalyseEmbryonComponent {
  selectedFile: File | null = null;
  fileErrorMsg: string = '';
  message: string |null=null;
  imageUrl: string | null=null;
  selectedFiles?: FileList;
  preview = '';
  isLoading: boolean = false;
  startProgressBar : boolean =false;
  progress: number = 0;
  error: string | null = null;

 

  predicted_class: string | null=null;
  predicted_probabilities: {
    bad: number;
    average: number;
    good: number;
  }  | null=null;
  image_segmented_path:string|null=null;
  image_name:string|null=null;

  constructor(private toastr: ToastrService,private fileUploadService:FileUploadServiceService,private http: HttpClient) {}
  ngOnInit() {
    // this.fileUploadService.getData().subscribe((data: any) => {
    //   this.message = data.message;
    //   console.log(this.message)
    // });
    
  }

  onFileSelected(event: any): void {
  
      this.message = '';
      this.preview = '';
      this.progress = 0;
      this.selectedFiles = event.target.files;

      if (this.selectedFiles) {
        const file: File | null = this.selectedFiles.item(0);

        if (file) {
          this.preview = '';
          this.selectedFile = file;

          const reader = new FileReader();

          reader.onload = (e: any) => {
            console.log(e.target.result);
            this.preview = e.target.result;
          };

          reader.readAsDataURL(this.selectedFile);
        }
      }
  }
 
  clearImage() {
    this.selectedFile = null;
    this.predicted_class=null;
    this.predicted_probabilities=null;
    this.preview = '';
    this.image_segmented_path='';

  }

  // getChartColor(index: string): string {
  //   // Define an array of colors
  //   // const colors = ["#dc3545", "#fd7e14", "#28a745"]; // Add more colors if needed

  //   const colors = {
  //     "bad": "#dc3545",
  //     "average": "#fd7e14",
  //     "good": "#0000ff"
  //   };
  //   // Return color based on index
  //   return colors[index];
  // }

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
  onSubmit(): void {
    this.startProgressBar=true;
    this.isLoading = true;
    this.progress = 20;

    
    if(this.selectedFile){
      console.log("file selected")
      this.fileUploadService.uploadFile(this.selectedFile).subscribe((response)=>{
      console.log('File uploaded successfully:', response);
      
      // loading the json object 
      const result=JSON.parse(response.image_with_result.result);
      this.predicted_class=result["predicted_class"];
      this.predicted_probabilities=result["predicted_probabilities"];
      // this.predicted_probabilities = {
      //   "bad": result.predicted_probabilities["bad"],
      //   "average": result.predicted_probabilities["average"],
      //   "good": result.predicted_probabilities["good"]
      // };
      // this.predicted_probabilities = Object.fromEntries(result["predicted_probabilities"]);

      console.log(this.predicted_probabilities)
      const image_name=response.image_with_result.image_name;

      console.log(image_name)
      this.image_segmented_path=`http://localhost:5000/segmented-images/${image_name}`;
      
      console.log("segmented path",this.image_segmented_path)
      this.toastr.success('Embryo image successfully processed!', 'Success');
      this.isLoading = false;
    },
    (error)=>{
      this.toastr.error('Failed to process embryo image', 'Error');
      this.isLoading = false;

      console.log('Error uploading file:', error);

    });
    this.simulateProgress()
  }
  


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

}
