import {Component, Input, OnInit} from '@angular/core';
import {NavItem} from '../navigation/nav-item';

@Component({
  selector: 'app-nav-list-item',
  templateUrl: './nav-list-item.component.html',
  styleUrls: ['./nav-list-item.component.less']
})
export class NavListItemComponent implements OnInit {
  expanded: boolean;
  @Input() item: NavItem;
  constructor() { }

  ngOnInit() {
  }

  onItemSelected(item: NavItem) {
    if (item.children && item.children.length) {
      this.expanded = !this.expanded;
    }
  }
}
