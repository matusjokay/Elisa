import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';
import {navItems} from './menu';
import {NavItem} from './nav-item';
import {AuthService} from '../../services/auth/auth.service';
import { BaseService } from 'src/app/services/base-service.service';
import { Role, RoleManager } from 'src/app/models/role.model';


@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.less']
})
export class NavigationComponent implements OnInit {

  menu: NavItem[] = navItems;
  userName: string;
  userRoles: number[];
  roleObjects: Role[];
  constructor(private router: Router,
              private authService: AuthService,
              private baseService: BaseService
  ) { }

  ngOnInit() {
    this.userName = this.baseService.getUserName();
    this.userRoles = this.baseService.getUserRoles();
    // go through menu entries and check if user
    // has an authorized view to see a menu item
    this.menu = this.menu.filter(this.hasRole(this.userRoles));
    this.roleObjects = RoleManager.getRoleObjects(this.userRoles);
  }

  hasRole(userRoles) {
    return function(menuItem) {
        return menuItem.forRoles.some(menuRole => userRoles.includes(menuRole));
    };
  }

  changeLang(lang: string) {
    if (lang === 'sk') {
      localStorage.setItem('locale', 'sk');
    }
    if (lang === 'en') {
      localStorage.setItem('locale', 'en');
    }
  }
  logout() {
    this.authService.logout().subscribe(
      (success) => {
        this.router.navigate(['login']);
      }
    );
  }
}
