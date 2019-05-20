import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {User} from '../../../models/user';
import {FormControl, FormGroup, Validators} from '@angular/forms';

@Component({
  selector: 'app-user-details',
  templateUrl: './user-details.component.html',
  styleUrls: ['./user-details.component.less']
})
export class UserDetailsComponent implements OnInit {

  userForm: FormGroup;

  constructor(
    public dialogRef: MatDialogRef<UserDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public user: User
  ) { }

  ngOnInit() {
    this.userForm = new FormGroup({
      'username': new FormControl(this.user.username,[
        Validators.required,
      ]),
      'lastName': new FormControl(this.user.last_name,[
        Validators.required,
      ]),
      'firstName': new FormControl(this.user.first_name,[
        Validators.required,
      ])
    });
  }

}
