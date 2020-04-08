import {Component, Input, OnInit} from '@angular/core';
import {Collision} from '../../models/collision.model';
import { MatDialog } from '@angular/material/dialog';
import {CollisionDetailComponent} from '../collision-detail/collision-detail.component';

@Component({
  selector: 'app-collision-card',
  templateUrl: './collision-card.component.html',
  styleUrls: ['./collision-card.component.less']
})
export class CollisionCardComponent implements OnInit {
  @Input() collision: Collision;
  constructor(public dialog: MatDialog) { }

  ngOnInit() {
  }

  openCollisionDetail(){
    const dialogRef = this.dialog.open(CollisionDetailComponent, {
      width: '800px',
      data: this.collision
    });

    dialogRef.afterClosed().subscribe(result => {
    });
  }
}
