import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpHeaders} from '@angular/common/http';
import {Account} from '../../models/account.model';
import {environment} from '../../../environments/environment';
import {catchError, map, share} from 'rxjs/operators';
import {BehaviorSubject, Observable, throwError} from 'rxjs';


enum Roles{
  MAIN_TIMETABLE_CREATOR = "3",
  LOCAL_TIMETABLE_CREATOR = "2",
  TEACHER = "1",
}
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  isLogged: BehaviorSubject<boolean>;

  constructor(private http: HttpClient) { }

  login(user: Account): Observable<boolean>{
    let body = {};
    body['username'] = user.username;
    body['password'] = user.password;
    return this.http.post(environment.APIUrl + 'login/',
      body
    ).pipe(
      map((response: any) => {
        localStorage.setItem('token',response.access);
        localStorage.setItem('refresh_token',response.refresh);
        localStorage.setItem('name',response.name);
        let roles = response.role.map(role => {
          return Roles[role];
        });
        localStorage.setItem('roles',roles);
        localStorage.setItem('active_role',String(Math.max(roles)));
        return response;
        }
      ));
  }

  logout(){
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('roles');
    localStorage.removeItem('active_role');
    localStorage.removeItem('name');
  }

  public isAuthenticated(): boolean {

    const token = localStorage.getItem('token');

    if(token){
      return true
    }
    else false;
  }

  public refreshToken(){
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http
      .post(environment.APIUrl + 'api/token/refresh/', {
        refresh: refreshToken
      })
      .pipe(
        share(),
        map((res : any)=> {
          const token = res.access;
          localStorage.setItem('token', token);
          return true;
        }),
        catchError((error: HttpErrorResponse) => {
          return throwError(error);
        })
      ).subscribe();
  }
}
