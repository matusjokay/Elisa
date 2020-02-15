import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpHeaders} from '@angular/common/http';
import {Account} from '../../models/account.model';
import {environment} from '../../../environments/environment';
import {catchError, map, share, tap} from 'rxjs/operators';
import {BehaviorSubject, Observable, throwError, of} from 'rxjs';


enum Roles {
  MAIN_TIMETABLE_CREATOR = '3',
  LOCAL_TIMETABLE_CREATOR = '2',
  TEACHER = '1',
}
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  isLogged: BehaviorSubject<boolean>;
  httpHeaders = new HttpHeaders({ 'Content-Type': 'application/json'});

  constructor(private http: HttpClient) { }

  login(user: Account): Observable<boolean> {
    const loginData = {
      'username': user.username,
      'password': user.password
    };
    return this.http.post(environment.APIUrl + 'login/',
      loginData, { headers: this.httpHeaders }
    ).pipe(
      tap((response: any) => {
        localStorage.setItem('token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        localStorage.setItem('name', response.name);
        const roles = response.role.map(role => {
          return Roles[role];
        });
        localStorage.setItem('roles', roles);
        localStorage.setItem('active_role', String(Math.max(roles)));
        return response;
        }
      ));
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('roles');
    localStorage.removeItem('active_role');
    localStorage.removeItem('name');
  }

  public async isAuthenticated(): Promise<boolean> {
    const token = localStorage.getItem('token');
    if (token) {
      const body = {
        'token': token
      };
      // return this.http
      //   .post(environment.APIUrl + 'api/token/verify/', body)
      //   .pipe(
      //     map(res => true),
      //     catchError((error: HttpErrorResponse) => {
      //       if (error.status === 401) {
      //         this.refreshToken();
      //       } else {
      //         return throwError(error);
      //       }
      //     }
      //   ));
      const result = await this.http.post(environment.APIUrl + 'api/token/verify/', body).toPromise();
      if (result && result['code'] && result['code'] === 'token_not_valid') {
        return false;
      } else {
        return true;
      }
      // const unauthorized = response['code'];
      // if (unauthorized === 'token_not_valid') {
      //   this.refreshToken();
      //   return false;
      // } else {
      //   return true;
      // }
    } else {
      return false;
    }

    // if (token) {
    //   return true;
    // } else {
    //   return false;
    // }
  }

  public refreshToken(): Observable<any> {
    const refreshToken = localStorage.getItem('refresh_token');
    const body = {
        'refresh': refreshToken
    };
    const httpOptions = this.httpHeaders;
    return this.http
      .post(environment.APIUrl + 'api/token/refresh/', body, { headers: httpOptions })
        .pipe(
          // tap(response => {
          //   // setting the token from response after refreshing
          //   localStorage.setItem('token', response['access']);
          // }),
          catchError((error: HttpErrorResponse) => {
          return throwError(error);
        })
      );
  }
}
