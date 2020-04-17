import { Injectable } from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot} from '@angular/router';
import {AuthService} from './auth.service';
import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { BaseService } from '../base-service.service';
import * as _ from 'lodash';

@Injectable({
  providedIn: 'root'
})
export class AuthGuardService implements CanActivate {

  constructor(public auth: AuthService,
     public router: Router,
     private baseService: BaseService) { }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> {
    const expectedRoles = route.data.roles;
    if (this.auth.isAuthenticated()) {
      const userRoles = this.baseService.getUserRoles();
      const isAuthorized = expectedRoles.some(role => userRoles.includes(role.id));
      console.log(`is user authorized? ${isAuthorized}`);
      if (isAuthorized) {
        return of(true);
      } else {
        return of(false);
      }
    } else {
      return this.auth.refreshToken().pipe(
        map(res => {
          if (res) {
            return true;
          } else {
            return false;
          }
        })
      );
    }
  }
}
