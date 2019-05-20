import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup} from '@angular/forms';
import {EventInput} from "@fullcalendar/core/structs/event";
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import interactionPlugin from "@fullcalendar/interaction";
import {RequirementService} from '../../../services/requirement.service';

@Component({
  selector: 'app-requirement-form',
  templateUrl: './requirement-form.component.html',
  styleUrls: ['./requirement-form.component.less']
})
export class RequirementFormComponent implements OnInit {

  requirementForm: FormGroup;
  optionsUsers: any;
  optionsSubjects = [];

  types = [
    {id:1, name: "suitable", color:"green"},
    {id:2, name: "unsuitable", color:"yellow"},
    {id:3, name: "unavailable", color:"red"},
  ];
  activeType;

  calendarHeader;
  calendarPlugins;
  calendarEvents: EventInput[];
  resources;
  duration;

  constructor(private dataService: RequirementService
  ){}

  ngOnInit() {
    this.dataService.getUser().subscribe(
      (response: any) => {
        this.optionsUsers = response.reduce(function(r, e) {
          if(!r[e.user.id]){
            r[e.user.id] = [];
            r[e.user.id]["id"] = e.user.id;
            r[e.user.id]["username"] = e.user.username;
            r[e.user.id]["subjects"] = [];
          }
          r[e.user.id]["subjects"].push(e.subject);
          return r;
        }, {});
      });

    this.requirementForm = new FormGroup({
      'teacher_id': new FormControl(),
      'course_id': new FormControl({value: '', disabled: true} ),
      'comment': new FormControl(),
    });
    this.initOptions();
  }

  setCoursesForm(event){
    this.optionsSubjects = this.optionsUsers[event.value]["subjects"];
    this.requirementForm.get('course_id').enable();
  }
  onSubmit(){
    let post = this.requirementForm.value;
    let request  = [];
    request['teacher'] = parseInt(post['teacher_id']);
    request['course'] = parseInt(post['course_id']);
    request['events'] = [];
    for(let event of this.calendarEvents){
      let temp =  {};
      temp['start'] = event.startTime;
      temp['end'] = event.endTime;
      temp['type'] = event.type;
      temp['day'] = parseInt(event.resourceId);
      request['events'].push(temp);
    }
    request['comments'] = [];
    request['comments'].push({"text": post["comment"],"type": 1});
    this.dataService.createRequirement(request);
  }

  handleSelect(arg){
    let deleteEvents = this.calendarEvents.filter(oldEvent => {
      if(arg.resource.id === oldEvent.resourceId){
        let oldTimeStart = new Date();
        let parts = oldEvent.startTime.split(":");
        oldTimeStart.setHours(parts[0],0,0,0);
        let oldTimeEnd = new Date();

        parts = oldEvent.endTime.split(":");
        oldTimeEnd.setHours(parts[0],0,0,0);
        if(oldTimeStart.getTime() < arg.end.getTime() && oldTimeEnd.getTime() > arg.start.getTime()){
          return this.handleOverlap(oldEvent,arg);
        }
      }
    });
    deleteEvents.forEach(oldEvent =>{
      let index = this.calendarEvents.indexOf(oldEvent);
      this.calendarEvents.splice(index,1);
    });
    this.calendarEvents = this.calendarEvents.concat( // add new event data. must create new array
      {
        startTime: arg.start.toLocaleTimeString('sk-SK'),
        endTime: arg.end.toLocaleTimeString('sk-SK'),
        resourceId: arg.resource.id,
        rendering: 'background',
        backgroundColor: this.activeType.color,
        type: this.activeType.id
      }
    );
  }

  handleOverlap(oldEvent,newEvent){
    let oldTimeStart = new Date();
    let parts = oldEvent.startTime.split(":");
    oldTimeStart.setHours(parts[0],0,0,0);

    let oldTimeEnd = new Date();
    parts = oldEvent.endTime.split(":");
    oldTimeEnd.setHours(parts[0],0,0,0);

    if(oldTimeStart.getTime() < newEvent.start.getTime()){
      if(oldTimeEnd.getTime() > newEvent.end.getTime()){
        this.calendarEvents = this.calendarEvents.concat( // add new event data. must create new array
          {
            startTime: newEvent.end.toLocaleTimeString('sk-SK'),
            endTime: oldEvent.endTime,
            resourceId: oldEvent.resourceId,
            rendering: 'background',
            backgroundColor: oldEvent.backgroundColor,
            type: oldEvent.type
          }
        );
      }
      oldEvent.endTime = newEvent.start.toLocaleTimeString('sk-SK');
    }
    else if(oldTimeEnd.getTime() > newEvent.end.getTime()){
      oldEvent.startTime = newEvent.end.toLocaleTimeString('sk-SK');
    }
    else{
      return oldEvent;
    }
  }

  selectType(id){
    this.activeType = this.types.find( type => {
      return type.id === id;
    });
  }

  reset(){
    this.calendarEvents.splice(0);
    this.calendarEvents = this.calendarEvents.concat();
  }

  initOptions() {
    this.calendarHeader = false;
    this.calendarPlugins = [resourceTimelinePlugin,interactionPlugin];

    this.calendarEvents = [];

    this.resources = [
      {id: '1', title: 'Pondelok'},
      {id: '2', title: 'Utorok'},
      {id: '3', title: 'Streda'},
      {id: '4', title: 'Stvrtok'},
      {id: '5', title: 'Piatok'},
    ];
    this.duration = 5;
    this.activeType = this.types.find(function (type) {
      return type.id === 1;
    });
  }
}
