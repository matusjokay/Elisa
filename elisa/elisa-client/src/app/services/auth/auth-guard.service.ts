import { Injectable } from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot} from '@angular/router';
import {AuthService} from './auth.service';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthGuardService implements CanActivate {

  constructor(public auth: AuthService, public router: Router) { }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> {
    const expectedRole = route.data.role;
    // return this.auth.isAuthenticated().pipe(
    //   map(res => {
    //     if (res) {
    //       console.log(res);
    //       console.log('now to check if you have roles to access this');
    //       if (localStorage.getItem('active_role') >= expectedRole) {
    //         return true;
    //       } else {
    //         return false;
    //       }
    //     } else {
    //       this.router.navigate(['login']);
    //     }
    //   }),
    //   catchError(() => {
    //     this.router.navigate(['login']);
    //     return of(false);
    //   })
    // );

    return this.auth.isAuthenticated().then(
      (result) => {
        if (result) {
          console.log(result);
          console.log('now to check if you have roles to access this');
          if (localStorage.getItem('active_role') >= expectedRole) {
            return true;
          } else {
            return false;
          }
        } else {
          return false;
        }
      }
    );
    // return this.auth.isAuthenticated().subscribe(
    //   (next) => {
    //     console.log('Token is still valid user is authentificated');
    //     if (localStorage.getItem('active_role') >= expectedRole) {
    //       return true;
    //     } else {
    //       return false;
    //     }
    //   },
    //   (error) => {
    //     console.error('Users token has expired');
    //     this.router.navigate(['login']);
    //     return false;
    //   }
    // );
    // if (status) {
    //   console.log('Token is still valid user is authentificated');
    //   if (localStorage.getItem('active_role') >= expectedRole) {
    //     return true;
    //   } else {
    //     return false;
    //   }
    // } else {
    //   console.error('Users tokens had expired');
    //   this.router.navigate(['login']);
    //   return false;
    // }
    // if (this.auth.isAuthenticated()) {
    //   // this.router.navigate([{outlets: {primary: 'admin' , adminView: 'dashboard'}}]);
    //   // return false;
    //   if (localStorage.getItem('active_role') >= expectedRole) {
    //     return true;
    //   } else {
    //     return false;
    //   }
    // } else {
    //   this.router.navigate(['login']);
    //   return false;
    // }
    // this.router.navigate(['login'])
    // return false;
  }
}
