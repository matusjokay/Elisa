import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpHeaders} from '@angular/common/http';
import {Account} from '../../models/account.model';
import {environment} from '../../../environments/environment';
import {catchError, map, share} from 'rxjs/operators';
import {BehaviorSubject, Observable, throwError} from 'rxjs';

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

    return this.http.post(environment.APIUrl + environment.LoginUrl,
      body
    ).pipe(
      map((response: any) => {
        localStorage.setItem('token',response.access);
        localStorage.setItem('refresh_token',response.refresh);
        localStorage.setItem('role',"3");
          return response;
        }
      ));
  }

  logout(){
    localStorage.removeItem('token');
    localStorage.removeItem('role');
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
