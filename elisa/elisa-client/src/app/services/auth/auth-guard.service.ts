import { Injectable } from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot} from '@angular/router';
import {AuthService} from './auth.service';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { BaseService } from '../base-service.service';
import { Role } from 'src/app/models/role.model';
import { HttpResponse, HttpErrorResponse } from '@angular/common/http';
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
    // return this.auth.isAuthenticated().pipe(
    //   map(res => {
    //     if (res) {
    //       console.log(res);
    //       console.log('now to check if you have roles to access this');
    //       const roleId: Role = JSON.parse(localStorage.getItem('active_role')).id;
    //       console.log(`roleId -> ${roleId}`);
    //       if (roleId <= expectedRole) {
    //         return true;
    //       } else {
    //         return false;
    //       }
    //     } else if (res === false) {
    //       this.auth.refreshToken();
    //     } else {
    //       this.router.navigate(['login']);
    //     }
    //   }),
    //   catchError(() => {
    //     this.router.navigate(['login']);
    //     return of(false);
    //   })
    // );
    if (this.auth.isAuthenticated()) {
      console.log('token is present no refresh needed');
      console.log('now to check if you have roles to access this');
      // const roleId: Role = JSON.parse(localStorage.getItem('active_role')).id;
      const userRoles = this.baseService.getUserRoles();
      // const isAuthorized = userRoles.some(role => role === expectedRole);
      // const isAuthorized = _.intersection(userRoles, expectedRoles).length === expectedRoles.length;
      const isAuthorized = expectedRoles.some(role => userRoles.includes(role));
      // console.log(`roleId -> ${roleId}`);
      // if (roleId <= expectedRole) {
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
    // return this.auth.isAuthenticated().pipe(
    //   map(res => {
    //     if (res) {
    //       console.log(res);
    //       console.log('now to check if you have roles to access this');
    //       const roleId: Role = JSON.parse(localStorage.getItem('active_role')).id;
    //       console.log(`roleId -> ${roleId}`);
    //       if (roleId <= expectedRole) {
    //         return true;
    //       } else {
    //         return false;
    //       }
    //     } else if (res === false) {
    //       this.auth.refreshToken();
    //     } else {
    //       this.router.navigate(['login']);
    //     }
    //   }),
    //   catchError(() => {
    //     this.router.navigate(['login']);
    //     return of(false);
    //   })
    // );
  }
}
