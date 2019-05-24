import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import interactionPlugin, {Draggable} from '@fullcalendar/interaction';
import {zip} from 'rxjs';
import {Course} from '../../../../models/course';
import {Room} from '../../../../models/room';
import {Requirement} from '../../../../models/requirement';
import {Group} from '../../../../models/group';
import {RequirementService} from '../../../../services/requirement.service';
import {UserService} from '../../../../services/user.service';
import {RoomService} from '../../../../services/room.service';
import {GroupService} from '../../../../services/group.service';
import {CourseService} from '../../../../services/course.service';
import {TimetableComponent} from '../../timetable/timetable.component';
import {TimetableService} from '../../../../services/timetable.service';
import {Event} from '../../../../models/event.model';
import {Collision} from '../../../../models/collision.model';
import {MatDialog} from '@angular/material';
import {EventDetailComponent} from '../../../../components/event-detail/event-detail.component';

@Component({
  selector: 'app-timetable-update-main',
  templateUrl: './timetable-update-main.component.html',
  styleUrls: ['./timetable-update-main.component.less']
})
export class TimetableUpdateMainComponent implements OnInit {
  @ViewChild('groupCalendar') groupCalendar: TimetableComponent;
  @ViewChild('roomCalendar') roomCalendar: TimetableComponent;
  @ViewChild('userCalendar') userCalendar: TimetableComponent;
  courses: Course[];
  teachers: any;
  rooms: Room[];
  requirements: Requirement[];
  groups: Group[];
  events: Event[];
  collisions: any = [];

  newEventsCounter = 0;
  newCollisionsCounter = 0;
  parentCheck: boolean = false;
  childCheck: boolean = false;

  calendarOptions: any = [];

  activeSchema: string;
  activeVersion: string;
  activeActivityCategories;
  activeCourse: Course;
  activeTeacher: any;
  activeGroups: Group[] = [];
  activeRoom: Room;

  @ViewChild('externals') externals: ElementRef;

  constructor(
    private userService: UserService,
    private roomService: RoomService,
    private groupService: GroupService,
    private courseService: CourseService,
    private requirementService: RequirementService,
    private timetableService: TimetableService,
    public dialog: MatDialog
    ) { }

  ngOnInit() {
    this.calendarOptions = {
      height: 'parent',
      events: [
      ],
      editable: true,
      // selectable: true,
      eventClick: true,
      droppable: true,
      plugins: [resourceTimelinePlugin,interactionPlugin],
    };

    // this.getDefaultVersion();
    this.getData(1);
  }

  getDefaultVersion(){
    this.timetableService.getLastScheme().subscribe(version =>{
    });
      // this.timetableService.getTimetableVersions().subscribe((version: any) => {
      //     this.activeVersion = version;
      //     this.getData(version);
      //     return version;
      // });
  }

  getData(version){
    zip(
      this.userService.getAllMap(),
      this.roomService.getAllMap(),
      this.groupService.getAllMap(),
      this.courseService.getCoursesByTeacherMap(),
      this.requirementService.getAll(),
      this.timetableService.getAllEvents(version),
      this.timetableService.getAllCollisions(version),
      this.timetableService.getActivitiesGroup(),
    ).subscribe(([usersData,roomsData, groupsData,coursesData,requirementsData,eventsData,collisionsData,activityCategories]) =>{
    // ).subscribe(([usersData,roomsData, groupsData,coursesData,requirementsData,activityCategories]) =>{
      this.teachers = usersData;
      this.rooms = roomsData;
      this.groups = groupsData;
      this.courses = coursesData;
      this.requirements = requirementsData;
      this.events = eventsData;
      this.events = [];
      this.collisions = collisionsData;
      this.collisions = [];
      this.activeActivityCategories = activityCategories;

      this.parseRequirements();
      this.parseEvents();
      new Draggable(this.externals.nativeElement,{itemSelector: '.fc-event'});
    });
  }

  dropEvent(arg){
    this.newEventsCounter++;
    let event = new Event(
      "new"+this.newEventsCounter,
      arg.draggedEl.getAttribute('data-type'),
      this.courses[this.activeCourse.id],
      this.teachers[this.activeTeacher.id],
      this.rooms[this.activeRoom.id],
      arg.resource.id,
      arg.date.getHours(),
      arg.date.getHours()+1,
      this.activeGroups.filter(group=>{return this.groups[group.id]}),
      'new',
      arg.draggedEl.getAttribute('data-color'),
    );

    let calendarEvent = event.generateEventCalendar();

    this.groupCalendar.addEvent(calendarEvent);
    this.roomCalendar.addEvent(calendarEvent);
    this.userCalendar.addEvent(calendarEvent);

    this.events[event.id] = event;

    this.activeTeacher['events'].push(event);
    this.activeRoom['events'].push(event);
    this.activeGroups.forEach(
      (group: Group) =>{
        group.events.push(event)
      }
    );
    this.detectCollisions(event);
  }

  resizeEvent(arg){
    let event = this.events[arg.event.id];
    event.startTime = arg.event.start.getHours();
    event.endTime = arg.event.end.getHours();
    this.events[arg.event.id]['startTime'] = arg.event.start.getHours();
    this.events[arg.event.id]['endTime'] = arg.event.end.getHours();

    let calendarEvent = event.generateEventCalendar();

    this.userCalendar.updateEvent(arg.event,calendarEvent);
    this.roomCalendar.updateEvent(arg.event,calendarEvent);
    this.groupCalendar.updateEvent(arg.event,calendarEvent);

    this.removeEventFromCollisions(event);
    this.detectCollisions(event);
  }

  dragEvent(arg){
    let event = this.events[arg.event.id];
    event.startTime = arg.event.start.getHours();
    event.endTime = arg.event.end.getHours();
    event.day = arg.newResource ? arg.newResource.id :this.events[arg.event.id]['day'];

    this.groupCalendar.updateEvent(arg.event,event.generateEventCalendar());
    this.userCalendar.updateEvent(arg.event,event.generateEventCalendar());
    this.roomCalendar.updateEvent(arg.event,event.generateEventCalendar());


    this.removeEventFromCollisions(event);
    this.detectCollisions(event);
  }

  clickEvent(arg){
    let event = this.events[arg.event.id];

    const dialogRef = this.dialog.open(EventDetailComponent, {
      width: '800px',
      disableClose: true,
      data: {'event': event, 'rooms': this.rooms}
    });

    dialogRef.afterClosed().subscribe(result => {
      if(result){
        this.events[arg.event.id] = result;
      }
      else{
        // this.teachers[arg.event.teacher.id].events.splice(this.teachers[arg.event.teacher.id].event.indexOf(result),1)
        event.teacher.events.splice(event.teacher.events.indexOf(event),1);
        event.rooms.forEach((room:Room) =>{
          room.events.splice(room.events.indexOf(event),1);
        });

        event.groups.forEach((group:Group) =>{
          group.events.splice(group.events.indexOf(event),1);
        });

        delete this.events[arg.event.id];
        this.reloadCourse();
        this.reloadRoom();
        this.groupsChange();
      }
    });

  }

  courseChange(id){
    if(this.activeCourse !== id){
      this.activeCourse = this.courses[id];
      this.activeTeacher = this.teachers[this.courses[id].id_teacher];
    }
    this.reloadCourse();
  }

  reloadCourse(){
    let events = this.activeTeacher.events.map((event: Event) => {
      return event.generateEventCalendar();
    })
    this.userCalendar.setEvents(events);
  }

  roomChange(id){
    if(this.activeCourse != id){
      this.activeRoom = this.rooms[id];
    }
    this.reloadRoom();
  }

  reloadRoom(){
    let events = this.activeRoom.events.map((event: Event) => {
      return event.generateEventCalendar();
    });
    this.roomCalendar.setEvents(events);
  }

  addGroup(id){
    this.activeGroups.push(this.groups[id]);
    this.groupsChange();
  }

  removeGroup(id){
    this.activeGroups.splice(this.activeGroups.map(function(group) {return group.id}).indexOf(id),1);
    this.groupsChange();
  }

  showParent(event){
    this.parentCheck = event.checked;
    this.groupsChange();
  }

  showChild(event){
    this.childCheck = event.checked;
    this.groupsChange();
  }

  groupsChange(){
    let events = [];
    this.activeGroups.forEach((group: Group)=> {
      group.events.forEach((event: Event) =>{
        let calendarEvent = event.generateEventCalendar();
        if(events.indexOf(calendarEvent) === -1){
          events.push(calendarEvent);
        }
      });
      if(this.parentCheck){
        this.getChildEvents(group)
        let parentGroup: Group = group;
        while(this.groups[parentGroup.parent]){
          parentGroup = this.groups[parentGroup.parent];
          parentGroup.events.forEach((event: Event) =>{
            let calendarEvent = event.generateEventCalendar();
            if(events.indexOf(calendarEvent) === -1){
              events.push(calendarEvent);
            }
          });
        }
      }
      if(this.childCheck){
        let childrenEvents = [];
        group.children.forEach(childGroupId =>{
          this.getChildEvents(this.groups[childGroupId]).forEach(event =>{
            childrenEvents.push(event);
          })
        });
        childrenEvents.forEach(event =>{
          if(events.indexOf(event) === -1){
            events.push(event);
          }
        })
      }
    });
    this.groupCalendar.setEvents(events);
  }

  private getChildEvents(group: Group){
    let calendarEvents = [];
    group.events.forEach((event: Event) =>{
      let calendarEvent = event.generateEventCalendar();
      calendarEvents.push(calendarEvent);
    });
    if(group.children){
      group.children.forEach((childId:number) => {
        calendarEvents.push(this.getChildEvents(this.groups[childId]));
      });
    }
    return calendarEvents;
  }

  private parseRequirements() {
    this.requirements.forEach(obj =>{
      this.teachers[obj.teacherId].requirements[(obj.courseId ? obj.courseId : "all")].push(obj);
    })
  }

  private parseEvents() {

  }

  private detectCollisions(event : Event) {
    event.teacher['events'].forEach(teacherEvent => {
      this.compareEvents(teacherEvent, event, 'teacher');
      }
    );

    event.rooms.forEach(room => {
     room.events.forEach(roomEvent => {
          this.compareEvents(roomEvent, event, 'room');
        }
      );
    });

    event.groups.forEach(group => {
     group.events.forEach(groupEvent => {
          this.compareEvents(groupEvent, event, 'group');
        }
      );
    });
  }

  private compareEvents(event,newEvent,type){
    if(event.day === newEvent.day && event.id != newEvent.id){
      if((event.startTime < newEvent.endTime && event.endTime >= newEvent.endTime)
        || (event.startTime <= newEvent.startTime && event.endTime > newEvent.startTime)
        || (event.startTime > newEvent.startTime && event.endTime < newEvent.endTime)
      ){
        let start = Math.max(event.startTime,newEvent.startTime);
        let end = Math.min(event.endTime,newEvent.endTime);

        let collisions: Collision[] = [];
        if(event.collisions){
          collisions = event.collisions.filter( collision => {
            if((collision.type === type)
                && ((collision.start < end && collision.end >= end)
                    || (collision.start <= start && collision.end > start)
                    || (collision.start > start && collision.end < end))
            ){
              if((collision.events.indexOf(newEvent) === -1)){
                collision.events.push(newEvent);
                newEvent.collisions.push(collision);
                collision.start = Math.max(event.startTime,newEvent.startTime);
                collision.end = Math.min(event.endTime,newEvent.endTime);
                collision.status = "unresolved";
              }
              return collision;
            }
          });
        }
        if (collisions.length === 0){
          let collision: Collision;
          this.newCollisionsCounter++;
          collision = new Collision();
          collision.start = start;
          collision.end = end;
          collision.events = [];
          collision.events.push(event);
          collision.events.push(newEvent);
          newEvent.collisions.push(collision);
          event.collisions.push(collision);
          collision.type = type;
          collision.status = "unresolved";
          this.collisions.push(collision);
        }
      }
    }
  }

  private removeEventFromCollisions(event : Event){
    let collisions = event.collisions;

    collisions.filter(collision => {
      if (collision.removeEvent(event)){
        this.collisions.splice(this.collisions.indexOf(collision),1);
      }
    });
    event.collisions = [];
  }

  saveData(){
  }

  createNewVersion(){
  }

  mergeTimetable(){
  }

  finalizeTimetable(){
  }
}
