import { Component, OnInit } from '@angular/core';
import resourceTimelinePlugin from '@fullcalendar/resource-timeline';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.less']
})
export class HomeComponent implements OnInit {

  calendarOptions: any;
  constructor() { }

  ngOnInit() {
    this.calendarOptions = {
      height: 'parent',
      contentHeight: 'auto',
      events: [
      ],
      selectable:'false',
      eventStartEditable: 'false',
      plugins: [resourceTimelinePlugin],
    };
  }
}
