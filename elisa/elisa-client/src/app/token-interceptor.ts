import {HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest, HttpResponse} from '@angular/common/http';
import {Observable, throwError} from 'rxjs';
import {Injectable} from '@angular/core';
import {AuthService} from './services/auth/auth.service';
import {catchError} from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {

  constructor(public auth: AuthService, private router: Router) {}

  intercept(req: HttpRequest<any>,
            next: HttpHandler): Observable<HttpEvent<any>> {
            // next: HttpHandler): Observable<HttpEvent<any>> {
    const jwt = localStorage.getItem('token');
    if (jwt) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization',
          "Bearer " + jwt)
      });
      req = cloned;
    }
    return next.handle(req).pipe(catchError((error: HttpErrorResponse) => {
      if(error.status === 401){
        this.auth.refreshToken();
      }
      return throwError(error);
    }));
  }
}
