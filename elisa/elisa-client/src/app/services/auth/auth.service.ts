import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpHeaders} from '@angular/common/http';
import {Account} from '../../models/account.model';
import {environment} from '../../../environments/environment';
import {catchError, map, share, tap} from 'rxjs/operators';
import {BehaviorSubject, Observable, throwError, of} from 'rxjs';
import { BaseService } from '../base-service.service';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  isLogged: BehaviorSubject<boolean>;
  httpHeaders = new HttpHeaders(
    { 'Content-Type': 'application/json'});

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  login(user: Account): Observable<boolean> {
    const loginData = {
      'username': user.username,
      'password': user.password
    };
    return this.http.post(environment.APIUrl + 'login/',
      loginData, { headers: this.httpHeaders , withCredentials: true}
    ).pipe(
      tap((response: any) => {
        this.baseService.setAccess(response.access);
      }
    ));
  }

  logout(): Observable<any> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get(environment.APIUrl + 'users/logout/', { headers: httpOptions }).pipe(
      tap(res => {
        console.log(`Result -> ${res} clearing storage`);
        localStorage.clear();
      })
    );
  }

  public isAuthenticated(): boolean {
    if (this.baseService.getAccess()) {
      return true;
    } else {
      return false;
    }
  }

  public refreshToken(): Observable<any> {
    const httpOptions = this.httpHeaders;
    return this.http
      .post(environment.APIUrl + 'api/token/refresh/', { headers: httpOptions, withCredentials: true})
        .pipe(
          tap(result => {
            console.log(result);
            this.baseService.setAccess(result['access']);
          }),
          map(succes => true),
          catchError((error: HttpErrorResponse) => {
            return of(false);
            // return throwError(error);
        })
      );
  }
}
