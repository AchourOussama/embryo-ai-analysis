import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { API_URL } from 'src/app/env';


interface EmbryoImageResult {
  image_name:string;
  image_path: string;
  result: string;
}

interface EmbryoFormData {
  image_path: string;
  suggested_value: string;
  note: string;
}
@Injectable({
  providedIn: 'root'
})
export class EmbryonService {

  constructor(private http:HttpClient) { }
  getEmbryoImagesAndResults(): Observable<EmbryoImageResult[]> {
    return this.http.get<EmbryoImageResult[]>(`${API_URL}/images`)  ;
  }

  validateAndPostFormData(embryo: EmbryoImageResult, selectedValue: string, note: string): void {
    if (!selectedValue && !note?.trim()) {
      alert('Please select a value from the dropdown or add a comment.');
      return;
    }

    // const formData=new FormData()
    // formData.append({
    //   image_path: embryo.image_path,
    //   suggested_value: selectedValue,
    //   note: note.trim()

    // })
    const formData: EmbryoFormData = {
      image_path: embryo.image_path,
      suggested_value: selectedValue,
      note: note.trim()
    };
    console.log(formData)
  
    this.http.post(`${API_URL}/update`, formData);
    this.http.post<any>(`${API_URL}/update`, formData).subscribe(
      (response) => {
        alert('Form data submitted successfully!');
        // You can add additional logic here if needed
      },
      (error) => {
        alert('Error submitting form data. Please try again later.');
        console.error('Error submitting form data', error);
      }
    );
  }
  

}
