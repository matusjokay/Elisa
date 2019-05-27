import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {map, share} from 'rxjs/operators';
import {User} from '../models/user';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private http: HttpClient) { }

  getAll(): Observable<User[]>{
    return this.http.get<User[]>(environment.APIUrl + 'users/').
    pipe(
      map((data: any) =>{
        return data;
        }
      ),share());
  }

  getAllMap(): Observable<User>{
    return this.http.get<User>(environment.APIUrl + 'users/').
    pipe(
      map((data: any) =>{
        return data.reduce(function(r, e) {
          r[e.id] = e;
          r[e.id].requirements = {};
          r[e.id].events = [];
          return r;
        }, {});
        }
      ),share());
  }

  deleteUser(user: User) {
    return this.http.delete(environment.APIUrl + 'users/' + user.id + '/').
    pipe(
      map((response: any) => {
          return response;
        }
      )).subscribe();
  }

  createUser(post: any) {
    
  }

  updateUser(post: any) {
    
  }
}
