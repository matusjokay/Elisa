import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {Room} from '../../models/room';

@Component({
  selector: 'app-event-detail',
  templateUrl: './event-detail.component.html',
  styleUrls: ['./event-detail.component.less']
})
export class EventDetailComponent implements OnInit{

  activeRoom: Room;
  dataSource: Room[];
  columnsToDisplay = ['name', 'category', 'capacity', 'actions'];

  constructor(
    public dialogRef: MatDialogRef<EventDetailComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any) {}

  ngOnInit(): void {
    this.dataSource = this.data.event.rooms;
  }

  roomChange(value){
    this.activeRoom = value;
  }

  addRoom() {
    console.log(this);
    if(this.data.event.rooms.indexOf(this.activeRoom) === -1){
      this.data.event.rooms.push(this.activeRoom);
      this.data.rooms[this.activeRoom.id].events.push(this.data.event);
      this.dataSource = [...this.data.event.rooms];
    }
  }

  removeRoom(row){
      console.log(row);
    if(this.data.event.rooms.length > 1){
      this.data.rooms[row.id].events.splice(this.data.rooms[row.id].events.indexOf(this.data.event),1);
      this.data.event.rooms.splice(this.data.event.rooms.indexOf(row),1);
      this.dataSource = [...this.data.event.rooms];
    }
  }
}
