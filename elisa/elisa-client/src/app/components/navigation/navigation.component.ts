import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';
import {navItems} from './menu';
import {NavItem} from './nav-item';
import {AuthService} from '../../services/auth/auth.service';


@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.less']
})
export class NavigationComponent implements OnInit {

  menu: NavItem[] = navItems;
  userName: string;
  constructor(private router: Router,
              private authService: AuthService
  ){ }

  ngOnInit() {
    this.userName = localStorage.getItem('name');
  }

  changeLang(lang: string) {
    if (lang === 'sk') {
      localStorage.setItem('locale', 'sk');
    }
    if (lang === 'en') {
      localStorage.setItem('locale', 'en');
    }
  }
  logout(){
    this.authService.logout();

    this.router.navigate(['login'])
  }
}
