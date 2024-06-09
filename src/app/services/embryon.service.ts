import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { API_URL } from 'src/app/env';


interface EmbryoImageResult {
  image_name: string;
  image_path:string;
  segmented_image_path:string;
  predicted_class: string;
  predicted_probabilities:string;
  suggested_value: string;
  note: string;
}

interface EmbryoFormData {
  image_name: string;
  predicted_class: string;
  predicted_probabilities:string;
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


    const formData: EmbryoFormData = {
      image_name: embryo.image_name,
      predicted_class:embryo.predicted_class,
      predicted_probabilities:JSON.stringify(embryo.predicted_probabilities),
      suggested_value: selectedValue,
      note: note.trim()
    };
    console.log("this is ",formData)
  
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
