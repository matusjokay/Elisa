
import {AfterViewInit, Component, ElementRef, EventEmitter, Input, OnInit, Output, ViewChild} from '@angular/core';
import { FullCalendarComponent } from '@fullcalendar/angular';
import * as moment from 'moment';
import {Draggable} from '@fullcalendar/interaction';
@Component({
  selector: 'app-timetable',
  templateUrl: './timetable.component.html',
  styleUrls: ['./timetable.component.less',
    '../../../../../node_modules/@fullcalendar/core/main.css',
    '../../../../../node_modules/@fullcalendar/timeline/main.css',
    '../../../../../node_modules/@fullcalendar/resource-timeline/main.css'
  ]
})
export class TimetableComponent implements OnInit, AfterViewInit{

  @ViewChild('calendar') calendarComponent: FullCalendarComponent;
  @Input() options: any;
  @Input() resourceName: String;
  @Output() dateClick = new EventEmitter();
  @Output() resizeEvent = new EventEmitter();
  @Output() dropEvent = new EventEmitter();
  @Output() dragEvent = new EventEmitter();
  @Output() clickEvent = new EventEmitter();
  resources;
  events: any = [];
  constructor() { }

  ngOnInit() {
    this.resources = [
      {id: 'monday', title: 'Pondelok'},
      {id: 'thursday', title: 'Utorok'},
      {id: 'wednesday', title: 'Streda'},
      {id: 'tuesday', title: 'Stvrtok'},
      {id: 'friday', title: 'Piatok'},
    ];
  }


  ngAfterViewInit(): void {
  }

  handleDateClick(arg){
    this.dateClick.emit(arg);
  }

  handleEventDrop(arg){
    this.dropEvent.emit(arg);
  }

  handleEventResize(arg){
    this.resizeEvent.emit(arg);
  }

  handleDrag(arg){
    this.dragEvent.emit(arg);
  }

  handleEventClick(arg){
    this.clickEvent.emit(arg);
  }

  setEvents(events){
    this.events.splice(0);
    this.events = this.events.concat(events);
  }

  updateEvent(oldEvent, newEvent){
    let index = this.events.findIndex(item => item.id===oldEvent.id);
    this.events.splice(index,1);
    this.events = this.events.concat(newEvent);
  }

  addEvent(event){
    this.events = this.events.concat(event);
  }

  deleteEvent(event){
    let index = this.events.findIndex(item => item.id===event.id);
    this.events.splice(index,1);
  }
}
