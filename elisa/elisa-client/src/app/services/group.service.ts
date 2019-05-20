import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map} from 'rxjs/operators';
import {Group} from '../models/group';

@Injectable({
  providedIn: 'root'
})
export class GroupService {

  constructor(private http: HttpClient) { }

  getAll(): Observable<Group[]>{
    return this.http.get<Group[]>(environment.APIUrl + 'groups/').
    pipe(
      map((data: Group[]) =>{
          return data;
        }
      ));
  }

  getAllMap(): Observable<Group[]>{
    return this.http.get<Group[]>(environment.APIUrl + 'groups/').
    pipe(
      map((data: any) =>{
        return data.reduce(function(r, e) {
          r[e.id] = e;
          r[e.id]["events"] = [];
          return r;
        }, {});
        }
      ));
  }
}
