import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share, shareReplay} from 'rxjs/operators';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Department} from '../models/department';
import { BaseService } from './base-service.service';

@Injectable({
  providedIn: 'root'
})
export class DepartmentService extends BaseService {

  // Trailing suffix of $ is an indicator of an Observable variable
  private cacheDepartmentList$: Observable<Array<Department>>;

  constructor(private http: HttpClient) {
    super();
  }

  getAllMap(): Observable<Department[]>{

    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<Department[]>(environment.APIUrl + 'departments/', options).pipe(
      map((response: any) => {
          return response.reduce(function(r, e) {
            r[e.id] = e;
            return r;
          }, {});
        }
      ),share());
  }

  getCachedDepartments() {
    if (!this.cacheDepartmentList$) {
      this.cacheDepartmentList$ = this.requestDepartments().pipe(
        shareReplay(1) // just create one observable that can multicast
      );
    }

    return this.cacheDepartmentList$;
  }

  private requestDepartments(): Observable<Department[]> {
    const httpOptions = this.getSchemaHeader();
    return this.http.get<Department[]>(environment.APIUrl + 'departments/', { headers: httpOptions });
  }

}
