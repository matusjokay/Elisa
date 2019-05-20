import {Component, Input, OnInit} from '@angular/core';
import {TimetableUpdateMainComponent} from '../timetable-update-main/timetable-update-main.component';

@Component({
  selector: 'app-timetable-update-form',
  templateUrl: './timetable-update-form.component.html',
  styleUrls: ['./timetable-update-form.component.less']
})
export class TimetableUpdateFormComponent implements OnInit {

  @Input() timetableMain: TimetableUpdateMainComponent;

  constructor() { }

  ngOnInit() {
  }

  showParent(event){
    // console.log(event.checked);
  }

  showChild(event){
    // console.log(event.checked);
  }
}
