import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {Collision} from '../../models/collision.model';

@Component({
  selector: 'app-collision-detail',
  templateUrl: './collision-detail.component.html',
  styleUrls: ['./collision-detail.component.less']
})
export class CollisionDetailComponent implements OnInit{

  columnsToDisplay = ['courseName', 'courseDay', 'courseTime'];

  constructor(
    public dialogRef: MatDialogRef<CollisionDetailComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Collision) {}

  onNoClick(): void {
    this.dialogRef.close();
  }

  ngOnInit(): void {
    console.log(this.data);
  }

}
