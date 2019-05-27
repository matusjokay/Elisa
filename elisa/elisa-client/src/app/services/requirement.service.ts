import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {map, share} from 'rxjs/operators';
import {Observable} from 'rxjs';
import {Requirement} from '../models/requirement';

@Injectable({
  providedIn: 'root'
})
export class RequirementService {

  constructor(private http: HttpClient) { }

  getUser(): Observable<any[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<any[]>(environment.APIUrl + "teachers/",options)
      .pipe(
        map((response: any) => {
          console.log(response);
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

  createRequirement(body){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    console.log(body);
    this.http.post(environment.APIUrl + "requirements/",
      body,
      options
    ).pipe(
      map((response: any) => {
          return response;
        }
      )).subscribe();
  }

  getAll(): Observable<Requirement[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<Requirement[]>(environment.APIUrl + 'requirements/',options).
    pipe(
      map((data: Requirement[]) =>{
          return data;
        }
      ),share());
  }
}
