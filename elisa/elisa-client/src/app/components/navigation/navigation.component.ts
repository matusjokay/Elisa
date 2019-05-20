import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';
import {navItems} from './menu';
import {NavItem} from './nav-item';


@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.less']
})
export class NavigationComponent implements OnInit {

  menu: NavItem[] = navItems;
  constructor(private router: Router) { }

  ngOnInit() {
  }

  changeLang(lang: string) {
    if (lang === 'sk') {
      localStorage.setItem('locale', 'sk');
    }
    if (lang === 'en') {
      localStorage.setItem('locale', 'en');
    }
  }
}
