import {Component, Inject, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {GroupService} from '../../../services/group.service';
import {Group} from '../../../models/group';

@Component({
  selector: 'app-group-details',
  templateUrl: './group-details.component.html',
  styleUrls: ['./group-details.component.less']
})
export class GroupDetailsComponent implements OnInit {

  groupForm: FormGroup;
  newGroup: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<GroupDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private groupService: GroupService,
  ) { }

  ngOnInit() {
    if(!this.data.group){
      this.newGroup = true;
      this.data.group = new Group();
    }
    this.groupForm = new FormGroup({
      'name': new FormControl(this.data.group.name,[
        Validators.required,
      ]),
      'abbr': new FormControl(this.data.group.abbr,[
        Validators.required,
      ]),
      'parent': new FormControl(this.data.group.parent,[

      ]),
    });
  }

  removeGroup() {
    this.groupService.deleteGroup(this.data.group);
    this.dialogRef.close(true);
  }

  onSubmit(){
    let post = this.groupForm.value;
    if(this.newGroup){
      this.groupService.createGroup(post);
    }
    else{
      this.groupService.updateGroup(post);
    }
    this.dialogRef.close(true);
  }
}
