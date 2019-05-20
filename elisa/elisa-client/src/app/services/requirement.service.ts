import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {map} from 'rxjs/operators';
import {Observable} from 'rxjs';
import {Requirement} from '../models/requirement';

@Injectable({
  providedIn: 'root'
})
export class RequirementService {

  constructor(private http: HttpClient) { }

  getUser(){
    return this.http.get(environment.APIUrl + "teachers/").pipe(
      map((response: any) => {
          return response;
        }
      ));;
  }

  createRequirement(body){
    this.http.post(environment.APIUrl + "requirements/",
      body
    ).pipe(
      map((response: any) => {
          return response;
        }
      )).subscribe();
  }

  getAll(): Observable<Requirement[]>{
    return this.http.get<Requirement[]>(environment.APIUrl + 'requirements/').
    pipe(
      map((data: Requirement[]) =>{
          return data;
        }
      ));
  }
}
