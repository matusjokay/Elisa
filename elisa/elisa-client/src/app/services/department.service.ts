import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share} from 'rxjs/operators';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Department} from '../models/department';

@Injectable({
  providedIn: 'root'
})
export class DepartmentService {

  constructor(private http: HttpClient) { }

  getAllMap(): Observable<Department[]>{

    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<Department[]>(environment.APIUrl + "departments/",options).pipe(
      map((response: any) => {
          return response.reduce(function(r, e) {
            r[e.id] = e;
            return r;
          }, {});
        }
      ),share());
  }
}
