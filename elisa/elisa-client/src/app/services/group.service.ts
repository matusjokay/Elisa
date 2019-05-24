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
        let test = data.reduce(function(r, e) {
          r[e.id] = e;
          r[e.id]["events"] = [];
          r[e.id]["children"] = [];
          return r;
        }, {});
        for(let id in test) {
          if(test[id]["parent"] !== null){
            test[test[id]["parent"]].children.push(id);
          }
        }
        return test;
        }
      ));
  }

  deleteGroup(group: any) {

  }

  createGroup(post: any) {

  }

  updateGroup(post: any) {

  }
}
