import {HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest, HttpResponse} from '@angular/common/http';
import {Observable, throwError, BehaviorSubject} from 'rxjs';
import {Injectable} from '@angular/core';
import {AuthService} from './services/auth/auth.service';
import {catchError, filter, take, switchMap, map, tap} from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class TokenInterceptor implements HttpInterceptor {
  // boolean variable to check if we are refreshing token or not
  private tokenRefreshInProgress = false;
  // Refresh Token Subject tracks the current token, or is null if no token is currently
  // available (e.g. refresh pending).
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(
      null
  );
  constructor(public auth: AuthService, private router: Router) {}

  intercept(req: HttpRequest<any>,
            next: HttpHandler): Observable<HttpEvent<any>> {
            // next: HttpHandler): Observable<HttpEvent<any>> {
    // const jwt = localStorage.getItem('token');
    // if (jwt) {
    //   const cloned = req.clone({
    //     headers: req.headers.set('Authorization',
    //       `Bearer ${jwt}`)
    //   });
    //   req = cloned;
    // }
    return next.handle(req).pipe(
        catchError((error: HttpErrorResponse) => {
        if (req.url.includes('token/refresh') || req.url.includes('login')) {
          if (req.url.includes('token/refresh')) {
            this.auth.logout();
            this.router.navigate(['login']);
          }

          return throwError(error);
        }
        // if unauthorized
        if (error.status !== 401) {
          return throwError(error);
        } else if (error.status === 401 && this.refreshTokenSubject.value) {
          this.auth.logout();
          this.router.navigate(['login']);
        }
        if (this.tokenRefreshInProgress) {
          return this.refreshTokenSubject
            .pipe(
              filter(result => result !== null),
              take(1),
              switchMap(() => next.handle(this.setAuthentificationToken(req)))
            );
        } else {
          this.tokenRefreshInProgress = true;
          // Set the refreshTokenSubject to null so that subsequent API calls will wait until the new token has been retrieved
          this.refreshTokenSubject.next(null);

          return this.auth.refreshToken().pipe(
            tap((token: any) => {
              console.log('access token obtained through refresh call');
              this.tokenRefreshInProgress = false;
              this.refreshTokenSubject.next(token['access']);
              localStorage.setItem('token', token['access']);

              return next.handle(this.setAuthentificationToken(req));
            })
          );
        }
        // this.auth.refreshToken().subscribe(
        //   (res) => {
        //     const token = res['access'];
        //     localStorage.setItem('token', token);
        //     // maybe not return
        //     return true;
        //   }
        // );
    }));
  }

  setAuthentificationToken(request) {
    // Get access token from Local Storage
    const accessToken = localStorage.getItem('token');

    // If access token is null this means that user is not logged in
    // And we return the original request
    if (!accessToken) {
        return request;
    }

    // We clone the request, because the original request is immutable
    return request.clone({
        setHeaders: {
            Authorization: `Bearer ${accessToken}`
        }
    });
  }
}
