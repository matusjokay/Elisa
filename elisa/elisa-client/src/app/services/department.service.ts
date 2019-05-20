import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map} from 'rxjs/operators';
import {HttpClient} from '@angular/common/http';
import {Department} from '../models/department';

@Injectable({
  providedIn: 'root'
})
export class DepartmentService {

  constructor(private http: HttpClient) { }

  getAllMap(): Observable<Department[]>{
    return this.http.get<Department[]>(environment.APIUrl + "departments/").pipe(
      map((response: any) => {
          return response.reduce(function(r, e) {
            r[e.id] = e;
            return r;
          }, {});
        }
      ));
  }
}
