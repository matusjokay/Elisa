import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {map, share} from 'rxjs/operators';
import {Observable} from 'rxjs';
import {Requirement} from '../models/requirement';
import { BaseService } from './base-service.service';

@Injectable({
  providedIn: 'root'
})
export class RequirementService {

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  getUser(): Observable<any[]>{
    const token = localStorage.getItem('token');
    const version = localStorage.getItem('active_scheme');
    const httpOptions = {
      headers: new HttpHeaders({
        'Authorization': `Bearer ${token}`,
        'Timetable-Version': version
      })
    };

    return this.http.get<any[]>(environment.APIUrl + 'teachers/', httpOptions)
      .pipe(
        map((response: any) => {
          return response.reduce(function(r, e) {
            if(!r[e.user.id]){
              r[e.user.id] = [];
              r[e.user.id]["id"] = e.user.id;
              r[e.user.id]["fullname"] = e.user.fullname;
              r[e.user.id]["subjects"] = [];
            }
            r[e.user.id]["subjects"].push(e.subject);
            return r;
          });
          }
        ),
        share());
  }

  createRequirement(requirement) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.post(`${environment.APIUrl}requirements/`,
      requirement, { headers: httpOptions });
  }

  getAll(): Observable<Requirement[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.get<Requirement[]>(`${environment.APIUrl}requirements/`,
     { headers: httpOptions });
  }

  getRequirement(reqId: number): Observable<Requirement> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.get<Requirement>(`${environment.APIUrl}requirements/${reqId}/`,
      { headers: httpOptions });
  }

  editRequirement(existingRequirement) {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.put(`${environment.APIUrl}requirements/${existingRequirement.id}/`,
      existingRequirement, { headers: httpOptions });
  }
}
