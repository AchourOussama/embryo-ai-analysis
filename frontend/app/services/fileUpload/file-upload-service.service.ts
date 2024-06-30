import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders} from '@angular/common/http';
import { API_URL } from 'src/app/env';
import {Observable, Subject} from 'rxjs';


@Injectable({
  providedIn: 'root'
})
export class FileUploadServiceService {

  constructor(private http: HttpClient) { }
  uploadFile(file:File):Observable<any>{

    const formData = new FormData();
    formData.append('image', file );
    let headers = new HttpHeaders({
      'FileName': file.name
       });
  
    return this.http.post(`${API_URL}/upload`,formData)
    

  }
  //for testing
  // getData() {
  //   return this.http.get<any>(`${API_URL}/data`);
  // }
}
