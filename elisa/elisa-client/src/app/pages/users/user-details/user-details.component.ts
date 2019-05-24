import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {User} from '../../../models/user';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {UserService} from '../../../services/user.service';

@Component({
  selector: 'app-user-details',
  templateUrl: './user-details.component.html',
  styleUrls: ['./user-details.component.less']
})
export class UserDetailsComponent implements OnInit {

  userForm: FormGroup;
  role: string;
  newUser: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<UserDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: User,
    private userService: UserService,
  ) { }

  ngOnInit() {
    if(!this.data){
      this.newUser = true;
      this.data = new User();
    }
    this.userForm = new FormGroup({
      'username': new FormControl(this.data.username,[
        Validators.required,
      ]),
      'lastName': new FormControl(this.data.last_name,[
        Validators.required,
      ]),
      'firstName': new FormControl(this.data.first_name,[
        Validators.required,
      ]),
      'role': new FormControl(this.role,[
        Validators.required,
      ])
    });
  }

  removeUser() {
    this.userService.deleteUser(this.data);
    this.dialogRef.close(true);
  }

  onSubmit(){
    let post = this.userForm.value;
    if(this.newUser){
      this.userService.createUser(post);
    }
    else{
      this.userService.updateUser(post);
    }
    this.dialogRef.close(true);
  }
}
