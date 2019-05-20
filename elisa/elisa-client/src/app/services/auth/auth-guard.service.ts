import { Injectable } from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot} from '@angular/router';
import {AuthService} from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuardService implements CanActivate{

  constructor(public auth: AuthService, public router: Router) { }

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    const expectedRole = route.data.role;
    if(localStorage.getItem('role') >= expectedRole){
      return true;
    }
    if(this.auth.isAuthenticated()){
      this.router.navigate([{outlets: {primary: 'admin' ,adminView: 'dashboard'}}])
      return false;
    }
    this.router.navigate(['login'])
    return false;
  }
}
