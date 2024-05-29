import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';




@Injectable({
  providedIn: 'root'
})
export class EmbryoService {
  readonly apiUrl = 'http://localhost:5000/analyse-cv';

  constructor(private http: HttpClient) {}

  // analyzeResume(data: FormData): Observable<any> {
  //   return this.http.post(this.apiUrl, data);
  // }
  analyzeEmbryo(data: FormData): Observable<any> {
    return this.http.post(this.apiUrl, data).pipe(
      map((response: any) => {
        // Create a new object that matches your component's expected format
        return {
          // fields: response.fields,
          // match_percentage: response.match_percentage,
          // explanation: response.explanation
        };
      }),
      catchError((error) => {
        // Handle errors appropriately
        console.error('Error fetching data: ', error);
        return throwError(error);
      })
    );
  }

}
