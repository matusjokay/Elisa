import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {map, share, shareReplay} from 'rxjs/operators';
import {User} from '../models/user';
import {Observable} from 'rxjs';
import { BaseService } from './base-service.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private cachedUsersList$: Observable<Array<User>>;

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

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

  getCachedAllUsers() {
    if (!this.cachedUsersList$) {
      this.cachedUsersList$ = this.requestAllUsers().pipe(
        shareReplay(1)
      );
    }

    return this.cachedUsersList$;
  }

  private requestAllUsers(): Observable<User[]> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get<User[]>(environment.APIUrl + 'users/list_for_role/', { headers: httpOptions });
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
