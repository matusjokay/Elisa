import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share} from 'rxjs/operators';
import {Group} from '../models/group';

@Injectable({
  providedIn: 'root'
})
export class GroupService {

  constructor(private http: HttpClient) { }

  getAll(): Observable<Group[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});
    return this.http.get<Group[]>(environment.APIUrl + 'groups/',options).
    pipe(
      map((data: Group[]) =>{
          return data;
        }
      ),share());
  }

  getAllMap(): Observable<Group[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});
    return this.http.get<Group[]>(environment.APIUrl + 'groups/',options).
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
      ),share());
  }

  deleteGroup(group: any) {

  }

  createGroup(post: any) {

  }

  updateGroup(post: any) {

  }
}
