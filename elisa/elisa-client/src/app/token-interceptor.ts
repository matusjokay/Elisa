import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest, HttpResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject, Subject } from 'rxjs';
import { Injectable } from '@angular/core';
import { AuthService } from './services/auth/auth.service';
import { catchError, filter, take, switchMap, map, tap } from 'rxjs/operators';
import { Router } from '@angular/router';
import { BaseService } from './services/base-service.service';

@Injectable({
  providedIn: 'root'
})
export class TokenInterceptor implements HttpInterceptor {

  constructor(public auth: AuthService,
    private router: Router,
    private baseService: BaseService) { }

  private _refreshSubject: Subject<any> = new Subject<any>();

  private _ifTokenExpired() {
    this._refreshSubject.subscribe({
      complete: () => {
        this._refreshSubject = new Subject<any>();
      }
    });
    if (this._refreshSubject.observers.length === 1) {
      // Hit refresh-token API passing the refresh token stored into the request
      // to get new access token and refresh token pair
      this.auth.refreshToken().subscribe(this._refreshSubject);
    }
    return this._refreshSubject;
  }

  private _checkTokenExpiryErr(error: HttpErrorResponse): boolean {
    return (
      error.status &&
      error.status === 401 &&
      error.error &&
      error.error.code === 'token_not_valid'
    );
  }


  intercept(
    req: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    req = req.clone({
      setHeaders: {
        accept: 'application/json',
        'content-type': 'application/json'
      },
      withCredentials: true
    });
    if (req.url.endsWith('/logout') ||
      req.url.endsWith('/login')) {
      return next.handle(req);
    } else if (req.url.endsWith('/token/refresh/')) {
      return next.handle(req).pipe(
        catchError((error: HttpErrorResponse) => {
          if (error.status === 401) {
            localStorage.clear();
            this.router.navigate(['login']);
            return throwError(error);
          }
        })
      );
    } else {
      return next.handle(req).pipe(
        catchError((error, caught) => {
          if (error instanceof HttpErrorResponse) {
            if (this._checkTokenExpiryErr(error)) {
              return this._ifTokenExpired().pipe(
                switchMap(() => {
                  return next.handle(this.setAuthentificationToken(req));
                })
              );
            } else {
              return throwError(error);
            }
          }
          return caught;
        })
      );
    }
  }

  setAuthentificationToken(request) {
    const token = this.baseService.getAccess();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    // If access token is null this means that user is not logged in
    // And we return the original request
    if (!headers) {
      return request;
    }

    return request.clone({
      headers: headers
    });
  }
}
