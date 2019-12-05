import {Component, Inject, OnInit} from '@angular/core';
import {Course} from '../../../models/course';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {RoomService} from '../../../services/room.service';

@Component({
  selector: 'app-room-details',
  templateUrl: './room-details.component.html',
  styleUrls: ['./room-details.component.less']
})
export class RoomDetailsComponent implements OnInit {

  roomForm: FormGroup;
  newRoom: boolean = false;

  constructor(
    public dialogRef: MatDialogRef<RoomDetailsComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private roomService: RoomService,
  ) { }

  ngOnInit() {
    if(!this.data.room){
      this.newRoom = true;
      // this also has to be changed
      this.data.room = new Object();
    }
    this.roomForm = new FormGroup({
      'name': new FormControl(this.data.room.name,[
        Validators.required,
      ]),
      'capacity': new FormControl(this.data.room.capacity,[
        Validators.required,
      ]),
      'category': new FormControl(this.data.room.category,[
        Validators.required,
      ]),
      'department': new FormControl(this.data.room.department,[
        Validators.required, Validators.min(5)
      ]),
    });
  }

  removeCourse() {
    this.roomService.deleteRoom(this.data);
    this.dialogRef.close(true);
  }

  onSubmit(){
    let post = this.roomForm.value;
    if(this.newRoom){
      this.roomService.createRoom(post);
    }
    else{
      this.roomService.updateRoom(post);
    }
    this.dialogRef.close(true);
  }
}
