import { Component } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { EmbryoService } from '../embryo.service';
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
  progress = 0;
  preview = '';
  embryo_result: string |null=null;

  constructor(private embryoService: EmbryoService,private toastr: ToastrService,private fileUploadService:FileUploadServiceService,private http: HttpClient) {}
  ngOnInit() {
    this.fileUploadService.getData().subscribe((data: any) => {
      this.message = data.message;
      console.log(this.message)
    });
    
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
    this.embryo_result=null;
    this.preview = '';

  }
  onSubmit(): void {
    
    if(this.selectedFile){
      console.log("file selected")
      this.fileUploadService.uploadFile(this.selectedFile).subscribe((response)=>{
      console.log('File uploaded successfully:', response);
      this.embryo_result=response.image_with_result.result;
      console.log('result:',this.embryo_result)
      },
      (error)=>{
        console.log('Error uploading file:', error);
      });

    }

  }

}
